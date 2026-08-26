import pytest
from backend.database.models import Case
from backend.reasoning.schemas import ActionProposal, ActionType, DecisionType
from backend.control_plane.rules_config import MerchantPolicyConfig
from backend.control_plane.policy_engine import validate_action
from backend.control_plane.budget_tracker import BudgetTracker
from backend.database.connection import init_db, drop_db

@pytest.fixture(autouse=True)
def setup_teardown_db():
    drop_db()
    init_db()
    yield
    drop_db()

@pytest.fixture
def config():
    return MerchantPolicyConfig(
        max_discount_pct=15.0,
        max_contact_attempts=3,
        max_payment_retries=2,
        max_extension_days=7,
        refusal_escalation_threshold=2,
        campaign_budget=50000.0,
        budget_incentive_cutoff_pct=5.0
    )

@pytest.fixture
def budget_tracker():
    return BudgetTracker(total_budget=50000.0)

@pytest.fixture
def base_case():
    return Case(id="c1", do_not_contact=False, contact_attempts=0, consecutive_refusals=0, payment_retries=0)

@pytest.fixture
def base_proposal():
    return ActionProposal(action_type=ActionType.SEND_REMINDER, reasoning="test")

def test_execute_when_all_within_limits(base_case, base_proposal, config, budget_tracker):
    decision = validate_action(base_proposal, base_case, config, budget_tracker)
    assert decision.decision == DecisionType.EXECUTE

def test_block_on_do_not_contact(base_case, base_proposal, config, budget_tracker):
    base_case.do_not_contact = True
    decision = validate_action(base_proposal, base_case, config, budget_tracker)
    assert decision.decision == DecisionType.BLOCK
    assert decision.rule_triggered == "do_not_contact"

def test_block_on_sensitive_data(base_case, base_proposal, config, budget_tracker):
    base_proposal.message_content = "Give me your credit card."
    decision = validate_action(base_proposal, base_case, config, budget_tracker)
    assert decision.decision == DecisionType.BLOCK
    assert decision.rule_triggered == "sensitive_data_request"

def test_block_on_max_contact_attempts(base_case, base_proposal, config, budget_tracker):
    base_case.contact_attempts = 4
    decision = validate_action(base_proposal, base_case, config, budget_tracker)
    assert decision.decision == DecisionType.BLOCK
    assert decision.rule_triggered == "max_contact_attempts"

def test_escalate_on_consecutive_refusals(base_case, base_proposal, config, budget_tracker):
    base_case.consecutive_refusals = 3
    decision = validate_action(base_proposal, base_case, config, budget_tracker)
    assert decision.decision == DecisionType.ESCALATE
    assert decision.rule_triggered == "consecutive_refusals"

def test_block_on_max_payment_retries(base_case, config, budget_tracker):
    base_case.payment_retries = 3
    proposal = ActionProposal(action_type=ActionType.REQUEST_RETRY, reasoning="retry")
    decision = validate_action(proposal, base_case, config, budget_tracker)
    assert decision.decision == DecisionType.BLOCK
    assert decision.rule_triggered == "max_payment_retries"

def test_modify_on_extension_days_exceeding_limit(base_case, config, budget_tracker):
    proposal = ActionProposal(action_type=ActionType.OFFER_EXTENSION, extension_days=10, reasoning="extend")
    decision = validate_action(proposal, base_case, config, budget_tracker)
    assert decision.decision == DecisionType.MODIFY
    assert decision.rule_triggered == "max_extension_days"
    assert decision.modified_proposal.extension_days == 7

def test_modify_on_discount_exceeding_limit(base_case, config, budget_tracker):
    proposal = ActionProposal(action_type=ActionType.OFFER_DISCOUNT, discount_pct=25.0, reasoning="discount")
    decision = validate_action(proposal, base_case, config, budget_tracker)
    assert decision.decision == DecisionType.MODIFY
    assert decision.rule_triggered == "max_discount_pct"
    assert decision.modified_proposal.discount_pct == 15.0

def test_modify_on_budget_exhaustion(base_case, config, budget_tracker):
    budget_tracker.consume(48000.0, "c0", "consume most")
    proposal = ActionProposal(action_type=ActionType.OFFER_DISCOUNT, discount_pct=10.0, reasoning="discount")
    decision = validate_action(proposal, base_case, config, budget_tracker)
    assert decision.decision == DecisionType.MODIFY
    assert decision.rule_triggered == "budget_exhaustion"
    assert decision.modified_proposal.discount_pct == 0.0

def test_priority_ordering(base_case, config, budget_tracker):
    # do_not_contact beats everything, e.g. max contact attempts or sensitive data
    base_case.do_not_contact = True
    base_case.contact_attempts = 10
    proposal = ActionProposal(action_type=ActionType.OFFER_DISCOUNT, discount_pct=25.0, message_content="credit card", reasoning="test")
    decision = validate_action(proposal, base_case, config, budget_tracker)
    assert decision.decision == DecisionType.BLOCK
    assert decision.rule_triggered == "do_not_contact"
