"""
LangGraph StateGraph: Detect → Diagnose → Triage → Reason → Validate → Execute → Measure
"""

from datetime import datetime
from langgraph.graph import StateGraph, END
from backend.orchestrator.state import RecoveryState
from backend.database.models import Case, ActionProposal as ActionProposalModel
from backend.audit.logger import AuditLogger
from backend.reasoning.schemas import (
    CaseContext, PaymentType, FailureReason, ValueTier, RiskProfile,
    ChannelType, ActionType, DecisionType, ActionProposal,
)
from backend.control_plane.policy_engine import validate_action
from backend.control_plane.rules_config import MerchantPolicyConfig
from backend.control_plane.budget_tracker import BudgetTracker
from backend.triage.classifier import classify_channel
from backend.reasoning.agent import ReasoningAgent


# ─────────────────────────── NODES ───────────────────────────


def detect_node(state: RecoveryState) -> RecoveryState:
    session = state.get("_session")
    case_id = state["case_id"]
    logger: AuditLogger | None = state.get("_logger")

    case = session.query(Case).filter(Case.id == case_id).first()
    if not case:
        state["error"] = f"Case {case_id} not found"
        return state

    context = CaseContext(
        case_id=case.id,
        customer_name=case.customer_name,
        payment_type=PaymentType(case.payment_type),
        payment_amount=case.payment_amount,
        failure_reason=FailureReason(case.failure_reason),
        value_tier=ValueTier(case.value_tier),
        risk_profile=RiskProfile(case.risk_profile),
        contact_attempts=case.contact_attempts,
        payment_retries=case.payment_retries,
        consecutive_refusals=case.consecutive_refusals,
        do_not_contact=case.do_not_contact,
    )

    state["case_context"] = context
    if logger:
        logger.log_detection(case_id, context.model_dump())
    return state


def diagnose_node(state: RecoveryState) -> RecoveryState:
    logger: AuditLogger | None = state.get("_logger")
    ctx = state["case_context"]

    diagnosis = {
        "failure_reason": ctx.failure_reason.value,
        "value_tier": ctx.value_tier.value,
        "risk_profile": ctx.risk_profile.value,
        "payment_amount": ctx.payment_amount,
        "analysis": f"Customer {ctx.customer_name} has a {ctx.failure_reason.value} failure "
                    f"on a ₹{ctx.payment_amount:.0f} {ctx.payment_type.value} payment. "
                    f"Risk profile: {ctx.risk_profile.value}.",
    }

    if logger:
        logger.log_diagnosis(state["case_id"], diagnosis)
    return state


def triage_node(state: RecoveryState) -> RecoveryState:
    session = state.get("_session")
    logger: AuditLogger | None = state.get("_logger")

    case = session.query(Case).filter(Case.id == state["case_id"]).first()
    result = classify_channel(case)

    state["triage_result"] = result



    case.assigned_channel = result.assigned_channel.value
    case.contact_attempts += 1

    if logger:
        logger.log_triage(state["case_id"], result.model_dump())
    return state


def reason_node(state: RecoveryState) -> RecoveryState:
    logger: AuditLogger | None = state.get("_logger")
    agent: ReasoningAgent = state.get("_agent")

    if agent is None:
        agent = ReasoningAgent()

    try:
        proposal = agent.propose_action(
            state["case_context"],
            state.get("conversation_history", []),
        )
    except Exception as e:
        # Fallback: propose a simple reminder if LLM fails
        proposal = ActionProposal(
            action_type=ActionType.SEND_REMINDER,
            reasoning=f"LLM call failed ({e}), defaulting to reminder.",
        )

    state["current_proposal"] = proposal
    if logger:
        logger.log_proposal(state["case_id"], proposal)
    return state


def validate_node(state: RecoveryState) -> RecoveryState:
    session = state.get("_session")
    logger: AuditLogger | None = state.get("_logger")
    budget_tracker: BudgetTracker = state.get("_budget_tracker")
    config: MerchantPolicyConfig = state.get("_config")

    case = session.query(Case).filter(Case.id == state["case_id"]).first()

    decision = validate_action(
        proposal=state["current_proposal"],
        case=case,
        config=config,
        budget_tracker=budget_tracker,
    )

    state["control_plane_decision"] = decision
    state["all_decisions"] = state.get("all_decisions", []) + [
        {
            "proposal": state["current_proposal"].model_dump(),
            "decision": decision.model_dump(),
        }
    ]



    prop = state["current_proposal"]
    mod_prop = decision.modified_proposal
    proposal_record = ActionProposalModel(
        case_id=state["case_id"],
        action_type=prop.action_type.value if hasattr(prop.action_type, "value") else str(prop.action_type),
        discount_pct=prop.discount_pct,
        discount_amount=prop.discount_amount,
        extension_days=prop.extension_days,
        promise_date=prop.promise_date,
        reasoning=prop.reasoning,
        message_content=prop.message_content,
        decision=decision.decision.value if hasattr(decision.decision, "value") else str(decision.decision),
        decision_reason=decision.reason,
        rule_triggered=decision.rule_triggered,
        modified_discount_pct=mod_prop.discount_pct if mod_prop else None,
        modified_discount_amount=mod_prop.discount_amount if mod_prop else None,
        modified_extension_days=mod_prop.extension_days if mod_prop else None,
        budget_remaining=decision.budget_remaining,
    )
    session.add(proposal_record)

    if logger:
        logger.log_decision(state["case_id"], decision)
    return state


def execute_node(state: RecoveryState) -> RecoveryState:
    session = state.get("_session")
    logger: AuditLogger | None = state.get("_logger")
    budget_tracker: BudgetTracker = state.get("_budget_tracker")
    decision = state.get("control_plane_decision")
    case = session.query(Case).filter(Case.id == state["case_id"]).first()
    ctx = state["case_context"]

    # Handle Silent Retry path directly from Triage
    if decision is None:
        case.payment_retries += 1
        state["amount_recovered"] = ctx.payment_amount
        action_details = {"action_type": "silent_retry", "decision": "execute"}
        if logger:
            logger.log_execution(state["case_id"], action_details)
        return state

    action = decision.modified_proposal if decision.modified_proposal else decision.original_proposal
    action_details = {"action_type": action.action_type.value, "decision": decision.decision.value}

    if action.action_type == ActionType.OFFER_DISCOUNT:
        discount_pct = action.discount_pct or 0.0
        discount_amount = round(ctx.payment_amount * discount_pct / 100, 2)
        action_details["discount_pct"] = discount_pct
        action_details["discount_amount"] = discount_amount



        if budget_tracker and discount_amount > 0:
            budget_tracker.consume(
                discount_amount, state["case_id"],
                f"Discount of {discount_pct}% = ₹{discount_amount}",
            )

        case.total_discount_given += discount_amount
        state["amount_recovered"] = ctx.payment_amount - discount_amount

    elif action.action_type == ActionType.OFFER_EXTENSION:
        ext_days = action.extension_days or 0
        case.extension_days_given += ext_days
        action_details["extension_days"] = ext_days
        state["amount_recovered"] = ctx.payment_amount  # full recovery expected

    elif action.action_type == ActionType.REQUEST_RETRY:
        case.payment_retries += 1
        state["amount_recovered"] = ctx.payment_amount

    elif action.action_type == ActionType.PROMISE_TO_PAY:
        action_details["promise_date"] = action.promise_date
        state["amount_recovered"] = ctx.payment_amount

    elif action.action_type == ActionType.SEND_REMINDER:
        state["amount_recovered"] = ctx.payment_amount * 0.5  # partial expectation

    elif action.action_type in (ActionType.ESCALATE, ActionType.END_CALL):
        state["amount_recovered"] = 0.0

    if logger:
        logger.log_execution(state["case_id"], action_details)
    return state


def measure_node(state: RecoveryState) -> RecoveryState:
    session = state.get("_session")
    logger: AuditLogger | None = state.get("_logger")

    case = session.query(Case).filter(Case.id == state["case_id"]).first()



    triage = state.get("triage_result")
    decision = state.get("control_plane_decision")

    if triage and triage.assigned_channel == ChannelType.HUMAN_ESCALATION:
        outcome = "escalated"
        amount = 0.0
    elif triage and triage.assigned_channel == ChannelType.SILENT_RETRY:
        outcome = "recovered"
        amount = case.payment_amount
    elif decision and decision.decision in (DecisionType.ESCALATE, DecisionType.BLOCK):
        if decision.decision == DecisionType.ESCALATE:
            outcome = "escalated"
        else:
            outcome = "unresolved"
        amount = 0.0
    elif state.get("amount_recovered", 0) > 0:
        if state["amount_recovered"] >= case.payment_amount * 0.9:
            outcome = "recovered"
        else:
            outcome = "partially_recovered"
        amount = state["amount_recovered"]
    else:
        outcome = "unresolved"
        amount = 0.0

    state["final_outcome"] = outcome



    case.outcome = outcome
    case.amount_recovered = amount
    case.resolved_at = datetime.utcnow()

    if logger:
        logger.log_measurement(state["case_id"], {
            "outcome": outcome,
            "amount_recovered": amount,
            "total_discount_given": case.total_discount_given,
            "contact_attempts": case.contact_attempts,
        })
    return state


# ─────────────────────── CONDITIONAL EDGES ───────────────────


def after_triage(state: RecoveryState) -> str:
    """Route based on assigned channel."""
    channel = state["triage_result"].assigned_channel
    if channel == ChannelType.HUMAN_ESCALATION:
        return "measure"
    elif channel == ChannelType.SILENT_RETRY:
        return "execute"
    return "reason"


def after_validate(state: RecoveryState) -> str:
    """Route based on control plane decision."""
    decision = state["control_plane_decision"].decision
    if decision in (DecisionType.EXECUTE, DecisionType.MODIFY):
        return "execute"
    return "measure"


# ─────────────────────── GRAPH BUILDER ───────────────────────


def build_recovery_graph():
    """Build and compile the LangGraph StateGraph."""
    workflow = StateGraph(RecoveryState)

    # Add nodes
    workflow.add_node("detect", detect_node)
    workflow.add_node("diagnose", diagnose_node)
    workflow.add_node("triage", triage_node)
    workflow.add_node("reason", reason_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("measure", measure_node)

    # Linear edges
    workflow.set_entry_point("detect")
    workflow.add_edge("detect", "diagnose")
    workflow.add_edge("diagnose", "triage")

    # After triage: branch by channel
    workflow.add_conditional_edges(
        "triage", after_triage,
        {"measure": "measure", "execute": "execute", "reason": "reason"},
    )

    # Reason always goes to validate
    workflow.add_edge("reason", "validate")

    # After validate: branch by decision
    workflow.add_conditional_edges(
        "validate", after_validate,
        {"execute": "execute", "measure": "measure"},
    )

    # Execute always goes to measure (single-turn for now)
    workflow.add_edge("execute", "measure")

    # Measure ends the graph
    workflow.add_edge("measure", END)

    return workflow.compile()


def process_case(case_id: str, session, budget_tracker, config) -> dict:
    """Process a single case through the full recovery graph."""
    graph = build_recovery_graph()
    logger = AuditLogger(session)

    try:
        agent = ReasoningAgent()
    except Exception:
        agent = None  # Will use fallback in reason_node

    initial_state = {
        "case_id": case_id,
        "case_context": None,
        "triage_result": None,
        "conversation_history": [],
        "current_proposal": None,
        "control_plane_decision": None,
        "all_decisions": [],
        "final_outcome": None,
        "amount_recovered": 0.0,
        "error": None,
        "_session": session,
        "_logger": logger,
        "_budget_tracker": budget_tracker,
        "_config": config,
        "_agent": agent,
    }

    final_state = graph.invoke(initial_state)
    return final_state
