from typing import Tuple, Optional
from backend.database.models import Case
from backend.reasoning.schemas import ActionProposal, ActionType, DecisionType, ControlPlaneDecision
from backend.control_plane.rules_config import MerchantPolicyConfig
from backend.control_plane.budget_tracker import BudgetTracker

def check_do_not_contact(case: Case) -> Tuple[bool, str, str]:
    if case.do_not_contact:
        return True, "do_not_contact", "Customer requested no further contact."
    return False, "", ""

def check_sensitive_data_request(proposal: ActionProposal) -> Tuple[bool, str, str]:
    if proposal.message_content:
        lower_msg = proposal.message_content.lower()
        sensitive_words = ["credit card", "cvv", "password", "otp", "pin"]
        for word in sensitive_words:
            if word in lower_msg:
                return True, "sensitive_data_request", f"Message contains sensitive request: {word}"
    return False, "", ""

def check_max_contact_attempts(case: Case, config: MerchantPolicyConfig) -> Tuple[bool, str, str]:
    if case.contact_attempts >= config.max_contact_attempts:
        return True, "max_contact_attempts", f"Exceeded max contact attempts ({config.max_contact_attempts})."
    return False, "", ""

def check_consecutive_refusals(case: Case, config: MerchantPolicyConfig) -> Tuple[bool, str, str]:
    if case.consecutive_refusals >= config.refusal_escalation_threshold:
        return True, "consecutive_refusals", f"Consecutive refusals ({case.consecutive_refusals}) reached escalation threshold."
    return False, "", ""

def check_max_payment_retries(case: Case, proposal: ActionProposal, config: MerchantPolicyConfig) -> Tuple[bool, str, str]:
    if proposal.action_type == ActionType.REQUEST_RETRY:
        if case.payment_retries >= config.max_payment_retries:
            return True, "max_payment_retries", f"Exceeded max payment retries ({config.max_payment_retries})."
    return False, "", ""

def check_max_extension_days(proposal: ActionProposal, config: MerchantPolicyConfig) -> Tuple[bool, str, str, Optional[int]]:
    if proposal.action_type == ActionType.OFFER_EXTENSION and proposal.extension_days is not None:
        if proposal.extension_days > config.max_extension_days:
            return True, "max_extension_days", f"Extension days ({proposal.extension_days}) exceeds max limit ({config.max_extension_days}).", config.max_extension_days
    return False, "", "", None

def check_max_discount(proposal: ActionProposal, config: MerchantPolicyConfig) -> Tuple[bool, str, str, Optional[float]]:
    if proposal.action_type == ActionType.OFFER_DISCOUNT and proposal.discount_pct is not None:
        if proposal.discount_pct > config.max_discount_pct:
            return True, "max_discount_pct", f"Discount percentage ({proposal.discount_pct}) exceeds max limit ({config.max_discount_pct}).", config.max_discount_pct
    return False, "", "", None

def check_budget_exhaustion(budget_tracker: BudgetTracker, proposal: ActionProposal) -> Tuple[bool, str, str]:
    if proposal.action_type in (ActionType.OFFER_DISCOUNT, ActionType.OFFER_EXTENSION):
        if budget_tracker.is_exhausted():
            return True, "budget_exhaustion", "Campaign budget is exhausted."
    return False, "", ""

def evaluate_all_stopping_rules(case: Case, proposal: ActionProposal, config: MerchantPolicyConfig, budget_tracker: BudgetTracker) -> ControlPlaneDecision:
    # 1. Do-Not-Contact
    blocked, rule, reason = check_do_not_contact(case)
    if blocked:
        return ControlPlaneDecision(decision=DecisionType.BLOCK, reason=reason, rule_triggered=rule, original_proposal=proposal, budget_remaining=budget_tracker.remaining())
        
    # 2. Sensitive data
    blocked, rule, reason = check_sensitive_data_request(proposal)
    if blocked:
        return ControlPlaneDecision(decision=DecisionType.BLOCK, reason=reason, rule_triggered=rule, original_proposal=proposal, budget_remaining=budget_tracker.remaining())
        
    # 3. Contact limit
    blocked, rule, reason = check_max_contact_attempts(case, config)
    if blocked:
        return ControlPlaneDecision(decision=DecisionType.BLOCK, reason=reason, rule_triggered=rule, original_proposal=proposal, budget_remaining=budget_tracker.remaining())
        
    # 4. Consecutive refusals -> ESCALATE
    escalated, rule, reason = check_consecutive_refusals(case, config)
    if escalated:
        return ControlPlaneDecision(decision=DecisionType.ESCALATE, reason=reason, rule_triggered=rule, original_proposal=proposal, budget_remaining=budget_tracker.remaining())
        
    # 5. Payment retry limit
    blocked, rule, reason = check_max_payment_retries(case, proposal, config)
    if blocked:
        return ControlPlaneDecision(decision=DecisionType.BLOCK, reason=reason, rule_triggered=rule, original_proposal=proposal, budget_remaining=budget_tracker.remaining())
        
    # 6. Extension limit
    modified, rule, reason, new_ext = check_max_extension_days(proposal, config)
    if modified:
        mod_prop = proposal.model_copy()
        mod_prop.extension_days = new_ext
        return ControlPlaneDecision(decision=DecisionType.MODIFY, reason=reason, rule_triggered=rule, original_proposal=proposal, modified_proposal=mod_prop, budget_remaining=budget_tracker.remaining())
        
    # 7. Discount limit
    modified, rule, reason, new_disc = check_max_discount(proposal, config)
    if modified:
        mod_prop = proposal.model_copy()
        mod_prop.discount_pct = new_disc
        return ControlPlaneDecision(decision=DecisionType.MODIFY, reason=reason, rule_triggered=rule, original_proposal=proposal, modified_proposal=mod_prop, budget_remaining=budget_tracker.remaining())
        
    # 8. Budget check
    budget_exhausted, rule, reason = check_budget_exhaustion(budget_tracker, proposal)
    if budget_exhausted:
        if proposal.action_type == ActionType.OFFER_DISCOUNT:
            mod_prop = proposal.model_copy()
            mod_prop.discount_pct = 0.0
            mod_prop.discount_amount = 0.0
            return ControlPlaneDecision(decision=DecisionType.MODIFY, reason=reason, rule_triggered=rule, original_proposal=proposal, modified_proposal=mod_prop, budget_remaining=budget_tracker.remaining())
        else:
            return ControlPlaneDecision(decision=DecisionType.BLOCK, reason=reason, rule_triggered=rule, original_proposal=proposal, budget_remaining=budget_tracker.remaining())
            
    # 9. All pass
    return ControlPlaneDecision(decision=DecisionType.EXECUTE, reason="All checks passed.", rule_triggered="none", original_proposal=proposal, budget_remaining=budget_tracker.remaining())
