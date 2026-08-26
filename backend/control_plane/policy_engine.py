"""
Policy Engine — the core deterministic control plane.

Every proposed action from the LLM reasoning layer passes through here
before execution. This module is the heart of the project's differentiator:
the AI proposes, the control plane decides.

This is NOT an AI model. It is pure, deterministic Python logic — and that
distinction is what makes the system auditable and explainable.
"""

from backend.reasoning.schemas import ActionProposal, ControlPlaneDecision, ActionType, DecisionType
from backend.database.models import Case
from backend.control_plane.rules_config import MerchantPolicyConfig
from backend.control_plane.budget_tracker import BudgetTracker
from backend.control_plane.stopping_rules import evaluate_all_stopping_rules


def validate_action(
    proposal: ActionProposal,
    case: Case,
    config: MerchantPolicyConfig,
    budget_tracker: BudgetTracker,
) -> ControlPlaneDecision:
    """
    Main policy engine entry point.

    Evaluates a proposed action against the full decision waterfall:
        1. Do-Not-Contact → BLOCK
        2. Sensitive data request → BLOCK
        3. Contact attempt limit → BLOCK
        4. Consecutive refusals → ESCALATE
        5. Payment retry limit → BLOCK
        6. Extension limit → MODIFY
        7. Discount limit → MODIFY
        8. Budget check → MODIFY or BLOCK
        9. All pass → EXECUTE

    Returns a ControlPlaneDecision with the exact rule that triggered.
    """
    return evaluate_all_stopping_rules(case, proposal, config, budget_tracker)
