import pytest
from backend.database.models import Case
from backend.reasoning.schemas import ActionProposal, ActionType
from backend.control_plane.rules_config import MerchantPolicyConfig
from backend.control_plane.budget_tracker import BudgetTracker
from backend.control_plane.stopping_rules import (
    check_do_not_contact,
    check_sensitive_data_request,
    check_max_contact_attempts,
    check_consecutive_refusals,
    check_max_payment_retries,
    check_max_extension_days,
    check_max_discount,
    check_budget_exhaustion
)

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

def test_check_do_not_contact():
    case = Case(id="c1", do_not_contact=True)
    blocked, rule, reason = check_do_not_contact(case)
    assert blocked is True
    assert rule == "do_not_contact"

def test_check_sensitive_data_request():
    proposal = ActionProposal(action_type=ActionType.SEND_REMINDER, message_content="Please share your OTP.", reasoning="test")
    blocked, rule, reason = check_sensitive_data_request(proposal)
    assert blocked is True
    assert rule == "sensitive_data_request"

def test_check_max_contact_attempts(config):
    case = Case(id="c1", contact_attempts=3)
    blocked, rule, reason = check_max_contact_attempts(case, config)
    assert blocked is True
    assert rule == "max_contact_attempts"

def test_check_consecutive_refusals(config):
    case = Case(id="c1", consecutive_refusals=2)
    blocked, rule, reason = check_consecutive_refusals(case, config)
    assert blocked is True
    assert rule == "consecutive_refusals"

def test_check_max_payment_retries(config):
    case = Case(id="c1", payment_retries=2)
    proposal = ActionProposal(action_type=ActionType.REQUEST_RETRY, reasoning="test")
    blocked, rule, reason = check_max_payment_retries(case, proposal, config)
    assert blocked is True
    assert rule == "max_payment_retries"

def test_check_max_extension_days(config):
    proposal = ActionProposal(action_type=ActionType.OFFER_EXTENSION, extension_days=10, reasoning="test")
    blocked, rule, reason, new_ext = check_max_extension_days(proposal, config)
    assert blocked is True
    assert rule == "max_extension_days"
    assert new_ext == 7

def test_check_max_discount(config):
    proposal = ActionProposal(action_type=ActionType.OFFER_DISCOUNT, discount_pct=20.0, reasoning="test")
    blocked, rule, reason, new_disc = check_max_discount(proposal, config)
    assert blocked is True
    assert rule == "max_discount_pct"
    assert new_disc == 15.0

def test_check_budget_exhaustion():
    class DummyTracker:
        def is_exhausted(self):
            return True
    tracker = DummyTracker()
    proposal = ActionProposal(action_type=ActionType.OFFER_DISCOUNT, discount_pct=10.0, reasoning="test")
    blocked, rule, reason = check_budget_exhaustion(tracker, proposal)
    assert blocked is True
    assert rule == "budget_exhaustion"
