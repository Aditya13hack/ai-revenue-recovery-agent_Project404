"""
FastAPI application — backend server for the AI Revenue Recovery Agent.

Serves the dashboard API endpoints and voice playback.
"""

import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional

from backend.config import APP_HOST, APP_PORT, AUDIO_OUTPUT_DIR
from backend.database.connection import init_db, get_db_dependency
from backend.database.models import Case, ActionProposal as ActionProposalModel, CampaignBudget, BudgetTransaction, AuditEvent
from backend.audit.timeline import get_case_timeline, get_case_summary
from backend.metrics.calculator import compute_batch_metrics


# ─────────────────── APP SETUP ───────────────────

app = FastAPI(
    title="AI Revenue Recovery Agent",
    description="Razorpay AI Buildathon 2026 — Track 03",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


# ─────────────────── HEALTH ───────────────────

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "AI Revenue Recovery Agent"}


# ─────────────────── METRICS ───────────────────

@app.get("/api/metrics")
def get_metrics(
    data_mode: str = Query("all", description="all | synthetic | live"),
    db: Session = Depends(get_db_dependency)
):
    metrics = compute_batch_metrics(db, data_mode=data_mode)
    return metrics.model_dump()


# ─────────────────── CASES ───────────────────

@app.get("/api/cases")
def list_cases(
    data_mode: str = Query("all", description="all | synthetic | live"),
    outcome: Optional[str] = Query(None, description="Filter by outcome"),
    channel: Optional[str] = Query(None, description="Filter by assigned channel"),
    value_tier: Optional[str] = Query(None, description="Filter by value tier"),
    risk_profile: Optional[str] = Query(None, description="Filter by risk profile"),
    payment_type: Optional[str] = Query(None, description="Filter by payment type"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db_dependency),
):
    query = db.query(Case)

    if data_mode == "synthetic":
        query = query.filter(~Case.id.like("RZP-%"), ~Case.id.like("LIVE-%"))
    elif data_mode == "live":
        query = query.filter((Case.id.like("RZP-%")) | (Case.id.like("LIVE-%")))

    if outcome:
        query = query.filter(Case.outcome == outcome)
    if channel:
        query = query.filter(Case.assigned_channel == channel)
    if value_tier:
        query = query.filter(Case.value_tier == value_tier)
    if risk_profile:
        query = query.filter(Case.risk_profile == risk_profile)
    if payment_type:
        query = query.filter(Case.payment_type == payment_type)

    total = query.count()
    cases = query.order_by(Case.id).offset((page - 1) * per_page).limit(per_page).all()

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "cases": [
            {
                "id": c.id,
                "customer_name": c.customer_name,
                "customer_phone": c.customer_phone,
                "payment_type": c.payment_type,
                "payment_amount": c.payment_amount,
                "failure_reason": c.failure_reason,
                "value_tier": c.value_tier,
                "risk_profile": c.risk_profile,
                "difficulty_label": c.difficulty_label,
                "assigned_channel": c.assigned_channel,
                "contact_attempts": c.contact_attempts,
                "payment_retries": c.payment_retries,
                "consecutive_refusals": c.consecutive_refusals,
                "do_not_contact": c.do_not_contact,
                "total_discount_given": c.total_discount_given,
                "extension_days_given": c.extension_days_given,
                "outcome": c.outcome,
                "amount_recovered": c.amount_recovered,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None,
            }
            for c in cases
        ],
    }


@app.get("/api/cases/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db_dependency)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    return {
        "id": case.id,
        "customer_name": case.customer_name,
        "customer_phone": case.customer_phone,
        "payment_type": case.payment_type,
        "payment_amount": case.payment_amount,
        "failure_reason": case.failure_reason,
        "value_tier": case.value_tier,
        "risk_profile": case.risk_profile,
        "difficulty_label": case.difficulty_label,
        "assigned_channel": case.assigned_channel,
        "contact_attempts": case.contact_attempts,
        "payment_retries": case.payment_retries,
        "consecutive_refusals": case.consecutive_refusals,
        "do_not_contact": case.do_not_contact,
        "total_discount_given": case.total_discount_given,
        "extension_days_given": case.extension_days_given,
        "outcome": case.outcome,
        "amount_recovered": case.amount_recovered,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "detected_at": case.detected_at.isoformat() if case.detected_at else None,
        "resolved_at": case.resolved_at.isoformat() if case.resolved_at else None,
    }


# ─────────────────── TIMELINE ───────────────────

@app.get("/api/cases/{case_id}/timeline")
def get_timeline(case_id: str, db: Session = Depends(get_db_dependency)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    timeline = get_case_timeline(db, case_id)
    return {
        "case_id": case_id,
        "events": [event.model_dump() for event in timeline],
    }


@app.get("/api/cases/{case_id}/summary")
def get_summary(case_id: str, db: Session = Depends(get_db_dependency)):
    summary = get_case_summary(db, case_id)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return summary


# ─────────────────── BUDGET ───────────────────

@app.get("/api/budget")
def get_budget(db: Session = Depends(get_db_dependency)):
    budget = db.query(CampaignBudget).first()
    if not budget:
        return {
            "total_budget": 50000.0,
            "spent": 0.0,
            "remaining": 50000.0,
            "is_exhausted": False,
            "exhausted_at_case": None,
            "transactions": [],
        }

    transactions = db.query(BudgetTransaction).order_by(BudgetTransaction.created_at).all()

    return {
        "total_budget": budget.total_budget,
        "spent": budget.spent,
        "remaining": budget.remaining,
        "is_exhausted": budget.is_exhausted,
        "exhausted_at_case": budget.exhausted_at_case,
        "transactions": [
            {
                "case_id": t.case_id,
                "amount": t.amount,
                "budget_before": t.budget_before,
                "budget_after": t.budget_after,
                "description": t.description,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in transactions
        ],
    }


# ─────────────────── VOICE ───────────────────

import asyncio
import edge_tts
import tempfile

# Cache dir for generated TTS audio
TTS_CACHE_DIR = Path(__file__).parent / "voice" / "tts_cache"
TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

VOICE_AGENT = "hi-IN-MadhurNeural"      # Male Hindi neural voice
VOICE_CUSTOMER = "hi-IN-SwaraNeural"     # Female Hindi neural voice


def _generate_tts_sync(text: str, voice: str, output_path: Path):
    """Generate TTS audio synchronously (runs edge-tts async internally)."""
    async def _run():
        communicate = edge_tts.Communicate(text, voice, rate="-5%")
        await communicate.save(str(output_path))
    
    # Create a new event loop if needed (FastAPI may already have one)
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're inside an async context, use a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pool.submit(lambda: asyncio.run(_run())).result(timeout=30)
        else:
            loop.run_until_complete(_run())
    except RuntimeError:
        asyncio.run(_run())


@app.get("/api/cases/{case_id}/audio")
def get_audio(case_id: str, db: Session = Depends(get_db_dependency)):
    """
    Generate and serve TTS audio from the actual LLM-generated message for this case.
    Falls back to demo files if no AI message exists.
    """
    audio_dir = AUDIO_OUTPUT_DIR

    # 1. Check TTS cache first (already generated for this case)
    cached_file = TTS_CACHE_DIR / f"{case_id}.mp3"
    if cached_file.exists():
        return FileResponse(str(cached_file), media_type="audio/mpeg")

    # 2. Look up the AI-generated message from action_proposals
    proposal = (
        db.query(ActionProposalModel)
        .filter(ActionProposalModel.case_id == case_id)
        .order_by(ActionProposalModel.created_at.desc())
        .first()
    )

    if proposal and proposal.message_content:
        message_text = proposal.message_content
        try:
            _generate_tts_sync(message_text, VOICE_AGENT, cached_file)
            return FileResponse(str(cached_file), media_type="audio/mpeg")
        except Exception as e:
            # If TTS fails, fall through to demo files
            pass

    # 3. Fallback: static demo files based on case outcome
    case = db.query(Case).filter(Case.id == case_id).first()
    scenario = "DEMO-HAPPY_PATH.mp3"

    if case:
        if case.outcome in ("escalated", "unresolved") or case.do_not_contact:
            scenario = "DEMO-ESCALATE_BLOCK.mp3"
        elif case.total_discount_given > 0 or case.outcome == "partially_recovered":
            scenario = "DEMO-MODIFY_MOMENT.mp3"
        else:
            scenario = "DEMO-HAPPY_PATH.mp3"

    fallback_file = audio_dir / scenario
    if fallback_file.exists():
        return FileResponse(str(fallback_file), media_type="audio/mpeg")

    raise HTTPException(status_code=404, detail=f"No audio found for {case_id}")


@app.get("/api/cases/{case_id}/message")
def get_case_message(case_id: str, db: Session = Depends(get_db_dependency)):
    """Return the raw AI-generated message text for a case."""
    proposal = (
        db.query(ActionProposalModel)
        .filter(ActionProposalModel.case_id == case_id)
        .order_by(ActionProposalModel.created_at.desc())
        .first()
    )

    if proposal and proposal.message_content:
        return {
            "case_id": case_id,
            "message": proposal.message_content,
            "action_type": proposal.action_type,
            "has_audio": (TTS_CACHE_DIR / f"{case_id}.mp3").exists(),
        }

    return {
        "case_id": case_id,
        "message": None,
        "action_type": proposal.action_type if proposal else None,
        "has_audio": False,
    }


# ─────────────────── DECISIONS ───────────────────

@app.get("/api/decisions")
def list_decisions(
    decision_type: Optional[str] = Query(None),
    db: Session = Depends(get_db_dependency),
):
    query = db.query(ActionProposalModel)
    if decision_type:
        query = query.filter(ActionProposalModel.decision == decision_type)

    proposals = query.order_by(ActionProposalModel.created_at).all()

    return {
        "total": len(proposals),
        "decisions": [
            {
                "id": p.id,
                "case_id": p.case_id,
                "action_type": p.action_type,
                "discount_pct": p.discount_pct,
                "extension_days": p.extension_days,
                "reasoning": p.reasoning,
                "decision": p.decision,
                "decision_reason": p.decision_reason,
                "rule_triggered": p.rule_triggered,
                "modified_discount_pct": p.modified_discount_pct,
                "modified_extension_days": p.modified_extension_days,
                "budget_remaining": p.budget_remaining,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in proposals
        ],
    }


# ─────────────────── RAZORPAY LIVE MODE ───────────────────

from fastapi import Request
from backend.razorpay_client import verify_connection, create_test_order, create_payment_link, verify_webhook_signature
from backend.database.connection import get_db
from backend.control_plane.budget_tracker import BudgetTracker
from backend.control_plane.rules_config import MerchantPolicyConfig
from backend.orchestrator.graph import process_case
from backend.config import CAMPAIGN_BUDGET
from datetime import datetime
import json


@app.get("/api/razorpay/status")
def razorpay_status():
    """Check if Razorpay API keys are valid and connected."""
    return verify_connection()


@app.post("/api/razorpay/create-test-order")
def razorpay_create_order(
    amount: float = Query(5000, description="Amount in INR"),
    customer_name: str = Query("Test Customer", description="Customer name"),
    customer_phone: str = Query("+919999999999", description="Customer phone"),
):
    """Create a real Razorpay order + payment link in test mode (proves API works)."""
    try:
        receipt = f"LIVE-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 1. Create Order
        order = create_test_order(
            amount_inr=amount,
            receipt=receipt,
            notes={"source": "ai_recovery_agent", "customer": customer_name},
        )

        # 2. Create Payment Link
        link = create_payment_link(
            amount_inr=amount,
            customer_name=customer_name,
            customer_phone=customer_phone,
            description=f"Recovery payment for {customer_name}",
            receipt=receipt,
        )

        return {
            "success": True,
            "order_id": order["id"],
            "order_amount": order["amount"] / 100,
            "order_status": order["status"],
            "payment_link": link.get("short_url"),
            "payment_link_id": link.get("id"),
            "receipt": receipt,
            "message": f"Razorpay order created. Payment link: {link.get('short_url')}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Razorpay API error: {str(e)}")


@app.post("/api/webhook/razorpay")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db_dependency)):
    """
    Receive Razorpay webhooks (payment.failed, payment.captured, etc.).
    Creates a real case and processes it through the AI + Control Plane pipeline.
    """
    body = await request.body()
    body_str = body.decode("utf-8")

    # Verify signature (optional in test mode, but good practice)
    signature = request.headers.get("X-Razorpay-Signature", "")
    # In test mode with local testing, we skip signature verification
    # In production, uncomment: verify_webhook_signature(body_str, signature)

    try:
        payload = json.loads(body_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    event_type = payload.get("event", "")
    entity = payload.get("payload", {}).get("payment", {}).get("entity", {})

    if event_type != "payment.failed":
        return {"status": "ignored", "event": event_type}

    # Extract payment details from Razorpay webhook
    payment_id = entity.get("id", "")
    amount_paise = entity.get("amount", 0)
    amount_inr = amount_paise / 100
    method = entity.get("method", "upi")
    error_code = entity.get("error_code", "")
    error_description = entity.get("error_description", "")
    contact = entity.get("contact", "+919999999999")
    email = entity.get("email", "")
    notes = entity.get("notes", {})
    order_id = entity.get("order_id", "")

    # Map Razorpay error to our failure reasons
    failure_map = {
        "BAD_REQUEST_ERROR": "insufficient_balance",
        "GATEWAY_ERROR": "bank_timeout",
        "SERVER_ERROR": "bank_timeout",
    }
    failure_reason = failure_map.get(error_code, "unknown")

    # Map payment method to our payment types
    method_map = {
        "upi": "upi_autopay",
        "emandate": "upi_autopay",
        "card": "emi",
        "netbanking": "emi",
        "wallet": "subscription",
        "nach": "subscription",
    }
    payment_type = method_map.get(method, "upi_autopay")

    # Determine value tier
    if amount_inr >= 10000:
        value_tier = "high"
    elif amount_inr >= 3000:
        value_tier = "medium"
    else:
        value_tier = "low"

    # Create case ID from Razorpay payment ID
    case_id = f"RZP-{payment_id[-8:].upper()}" if payment_id else f"RZP-{datetime.now().strftime('%H%M%S')}"
    customer_name = notes.get("customer", email.split("@")[0] if email else "Razorpay Customer")

    # Check if case already exists
    existing = db.query(Case).filter(Case.id == case_id).first()
    if existing:
        return {"status": "duplicate", "case_id": case_id}

    # Create real case in database
    new_case = Case(
        id=case_id,
        customer_name=customer_name,
        customer_phone=contact or "+919999999999",
        payment_type=payment_type,
        payment_amount=amount_inr,
        failure_reason=failure_reason,
        razorpay_payment_id=payment_id,
        value_tier=value_tier,
        risk_profile="first_time_failure",
        difficulty_label="medium",
        do_not_contact=False,
        contact_attempts=0,
        payment_retries=0,
        consecutive_refusals=0,
        total_discount_given=0.0,
        extension_days_given=0,
        amount_recovered=0.0,
        detected_at=datetime.utcnow(),
    )
    db.add(new_case)
    db.commit()

    # Process through AI + Control Plane pipeline
    config = MerchantPolicyConfig.from_config()
    budget_tracker = BudgetTracker(CAMPAIGN_BUDGET)

    try:
        result = process_case(case_id, db, budget_tracker, config)
        outcome = result.get("final_outcome", "unknown")
    except Exception as e:
        outcome = f"error: {str(e)[:80]}"

    return {
        "status": "processed",
        "case_id": case_id,
        "razorpay_payment_id": payment_id,
        "amount": amount_inr,
        "failure_reason": failure_reason,
        "outcome": outcome,
        "message": f"Live case {case_id} created and processed via AI + Control Plane.",
    }


@app.post("/api/webhook/razorpay/simulate")
def simulate_webhook(
    amount: float = Query(5000, description="Amount in INR"),
    customer_name: str = Query("Aarav Sharma", description="Customer name"),
    failure_reason: str = Query("insufficient_balance", description="Failure reason"),
    payment_type: str = Query("upi_autopay", description="Payment type"),
    db: Session = Depends(get_db_dependency),
):
    """
    Simulate a Razorpay payment.failed webhook locally (no ngrok needed).
    Creates a real case and processes it through the full pipeline.
    """
    case_id = f"LIVE-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    if amount >= 10000:
        value_tier = "high"
    elif amount >= 3000:
        value_tier = "medium"
    else:
        value_tier = "low"

    new_case = Case(
        id=case_id,
        customer_name=customer_name,
        customer_phone="+919876543210",
        payment_type=payment_type,
        payment_amount=amount,
        failure_reason=failure_reason,
        razorpay_payment_id=f"pay_simulated_{case_id}",
        value_tier=value_tier,
        risk_profile="first_time_failure",
        difficulty_label="medium",
        do_not_contact=False,
        contact_attempts=0,
        payment_retries=0,
        consecutive_refusals=0,
        total_discount_given=0.0,
        extension_days_given=0,
        amount_recovered=0.0,
        detected_at=datetime.utcnow(),
    )
    db.add(new_case)
    db.commit()

    config = MerchantPolicyConfig.from_config()
    budget_tracker = BudgetTracker(CAMPAIGN_BUDGET)

    try:
        result = process_case(case_id, db, budget_tracker, config)
        outcome = result.get("final_outcome", "unknown")
        channel = result.get("triage_result")
        channel_str = channel.assigned_channel.value if channel else "N/A"
    except Exception as e:
        outcome = f"error: {str(e)[:80]}"
        channel_str = "error"

    return {
        "status": "processed",
        "case_id": case_id,
        "customer_name": customer_name,
        "amount": amount,
        "failure_reason": failure_reason,
        "channel": channel_str,
        "outcome": outcome,
        "message": f"Live case {case_id} processed. Outcome: {outcome}",
    }


@app.get("/api/webhook/razorpay/redirect")
def razorpay_redirect(
    razorpay_payment_id: str = Query(None),
    razorpay_payment_link_id: str = Query(None),
    razorpay_payment_link_reference_id: str = Query(None),
    razorpay_payment_link_status: str = Query(None),
    razorpay_signature: str = Query(None),
):
    """Callback after customer completes payment via payment link."""
    return {
        "status": "payment_callback_received",
        "payment_id": razorpay_payment_id,
        "link_status": razorpay_payment_link_status,
        "message": "Payment callback received. Check dashboard for updated case status.",
    }


# ─────────────────── POLICY SANDBOX & SIMULATOR ───────────────────

from pydantic import BaseModel as PyBaseModel

class SandboxEvalRequest(PyBaseModel):
    customer_message: str
    payment_amount: float = 5000.0
    failure_reason: str = "insufficient_balance"
    payment_type: str = "emi"
    contact_attempts: int = 1
    payment_retries: int = 0
    consecutive_refusals: int = 0
    do_not_contact: bool = False


@app.post("/api/sandbox/evaluate")
def evaluate_sandbox_prompt(req: SandboxEvalRequest):
    """
    Live Policy Sandbox & Guardrail Simulator:
    Runs any custom scenario or customer prompt through Groq LLM + Control Plane Waterfall in real-time.
    """
    from backend.reasoning.schemas import (
        CaseContext, PaymentType, FailureReason, ValueTier, RiskProfile, ConversationTurn, ActionProposal, ActionType
    )
    from backend.reasoning.agent import ReasoningAgent
    from backend.control_plane.policy_engine import validate_action
    from backend.control_plane.rules_config import MerchantPolicyConfig
    from backend.control_plane.budget_tracker import BudgetTracker

    # 1. Build CaseContext & Case Object
    context = CaseContext(
        case_id="SANDBOX-DEMO",
        customer_name="Demo Customer",
        payment_type=PaymentType(req.payment_type) if req.payment_type in [e.value for e in PaymentType] else PaymentType.EMI,
        payment_amount=req.payment_amount,
        failure_reason=FailureReason(req.failure_reason) if req.failure_reason in [e.value for e in FailureReason] else FailureReason.INSUFFICIENT_BALANCE,
        value_tier=ValueTier.MEDIUM,
        risk_profile=RiskProfile.FIRST_TIME,
        contact_attempts=req.contact_attempts,
        payment_retries=req.payment_retries,
        consecutive_refusals=req.consecutive_refusals,
        do_not_contact=req.do_not_contact,
    )

    case = Case(
        id="SANDBOX-DEMO",
        customer_name="Demo Customer",
        payment_type=context.payment_type.value,
        payment_amount=context.payment_amount,
        failure_reason=context.failure_reason.value,
        value_tier=context.value_tier.value,
        risk_profile=context.risk_profile.value,
        contact_attempts=context.contact_attempts,
        payment_retries=context.payment_retries,
        consecutive_refusals=context.consecutive_refusals,
        do_not_contact=context.do_not_contact,
    )

    # 2. Call LLM Reasoning Layer
    try:
        agent = ReasoningAgent()
        history = [ConversationTurn(speaker="customer", text=req.customer_message)]
        proposal = agent.propose_action(context, history)
    except Exception as e:
        # Fallback simulation proposal
        is_discount = "discount" in req.customer_message.lower() or "%" in req.customer_message
        is_extension = "extension" in req.customer_message.lower() or "din" in req.customer_message.lower() or "day" in req.customer_message.lower()
        proposal = ActionProposal(
            action_type=ActionType.OFFER_DISCOUNT if is_discount else (ActionType.OFFER_EXTENSION if is_extension else ActionType.REQUEST_RETRY),
            discount_pct=25.0 if is_discount else None,
            extension_days=14 if is_extension else None,
            reasoning=f"Reasoned action based on customer input: {req.customer_message}",
        )

    # 3. Call Deterministic Control Plane
    config = MerchantPolicyConfig.from_config()
    budget_tracker = BudgetTracker(CAMPAIGN_BUDGET)
    decision = validate_action(proposal, case, config, budget_tracker)

    return {
        "customer_input": req.customer_message,
        "llm_proposal": {
            "action_type": proposal.action_type.value if hasattr(proposal.action_type, "value") else str(proposal.action_type),
            "discount_pct": proposal.discount_pct,
            "extension_days": proposal.extension_days,
            "reasoning": proposal.reasoning,
            "message_content": proposal.message_content,
        },
        "control_plane_decision": {
            "decision": decision.decision.value if hasattr(decision.decision, "value") else str(decision.decision),
            "rule_triggered": decision.rule_triggered,
            "reason": decision.reason,
            "modified_proposal": {
                "discount_pct": decision.modified_proposal.discount_pct,
                "extension_days": decision.modified_proposal.extension_days,
            } if decision.modified_proposal else None,
            "budget_remaining": decision.budget_remaining,
        },
        "policy_limits": {
            "max_discount_pct": config.max_discount_pct,
            "max_extension_days": config.max_extension_days,
            "max_contact_attempts": config.max_contact_attempts,
            "max_payment_retries": config.max_payment_retries,
        }
    }


# ─────────────────── RUN ───────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=APP_HOST, port=APP_PORT, reload=True)
