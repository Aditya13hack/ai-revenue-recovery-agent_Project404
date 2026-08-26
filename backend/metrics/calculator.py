"""
Aggregate metrics calculator for the full batch run.
Computes all 11 metrics defined in the project spec (Section 10).
"""

from sqlalchemy.orm import Session
from backend.database.models import Case, ActionProposal, CampaignBudget
from backend.reasoning.schemas import BatchMetrics


def compute_batch_metrics(session: Session) -> BatchMetrics:
    """
    Compute honest, unpadded metrics across the full synthetic batch.
    No cherry-picking - every case is included.
    """
    cases = session.query(Case).all()
    total_cases = len(cases)

    if total_cases == 0:
        return BatchMetrics(
            total_cases=0, total_revenue_at_risk=0, gross_revenue_recovered=0,
            total_discounts_given=0, net_revenue_recovered=0,
            autonomous_recovery_rate=0, human_assisted_recovery_rate=0,
            blocked_action_count=0, modified_action_count=0, escalation_count=0,
            false_positive_block_cost=0, escalation_rate=0,
            average_recovery_time_seconds=0, budget_exhaustion_case_index=None,
            recovery_rate=0,
        )

    # --- Revenue metrics ---
    total_revenue_at_risk = sum(c.payment_amount for c in cases)

    recovered_cases = [c for c in cases if c.outcome in ("recovered", "partially_recovered")]
    gross_revenue_recovered = sum(c.amount_recovered for c in recovered_cases)
    total_discounts_given = sum(c.total_discount_given for c in cases)
    net_revenue_recovered = gross_revenue_recovered - total_discounts_given

    # --- Recovery rates ---
    autonomous_recovered = [
        c for c in recovered_cases if c.assigned_channel != "human_escalation"
    ]
    human_assisted = [
        c for c in recovered_cases if c.assigned_channel == "human_escalation"
    ]
    autonomous_recovery_rate = len(autonomous_recovered) / total_cases if total_cases else 0
    human_assisted_recovery_rate = len(human_assisted) / total_cases if total_cases else 0

    # --- Control plane metrics ---
    proposals = session.query(ActionProposal).all()

    blocked_count = sum(1 for p in proposals if p.decision == "block")
    modified_count = sum(1 for p in proposals if p.decision == "modify")
    escalation_count = sum(
        1 for p in proposals if p.decision == "escalate"
    ) + len([c for c in cases if c.outcome == "escalated"])

    # False-positive block cost: cases where control plane blocked but ground truth was "easy"
    easy_blocked_cases = [
        c for c in cases
        if c.difficulty_label == "easy" and c.outcome in ("unresolved", "escalated")
    ]
    false_positive_block_cost = sum(c.payment_amount for c in easy_blocked_cases)

    escalated_cases = [c for c in cases if c.outcome == "escalated"]
    escalation_rate = len(escalated_cases) / total_cases if total_cases else 0

    # --- Time metrics ---
    recovery_times = []
    for c in recovered_cases:
        if c.detected_at and c.resolved_at:
            delta = (c.resolved_at - c.detected_at).total_seconds()
            recovery_times.append(delta)
    avg_recovery_time = sum(recovery_times) / len(recovery_times) if recovery_times else 0

    # --- Budget exhaustion ---
    budget = session.query(CampaignBudget).first()
    budget_exhaustion_case_index = None
    if budget and budget.exhausted_at_case:
        for i, c in enumerate(cases):
            if c.id == budget.exhausted_at_case:
                budget_exhaustion_case_index = i
                break

    recovery_rate = net_revenue_recovered / total_revenue_at_risk if total_revenue_at_risk else 0

    return BatchMetrics(
        total_cases=total_cases,
        total_revenue_at_risk=round(total_revenue_at_risk, 2),
        gross_revenue_recovered=round(gross_revenue_recovered, 2),
        total_discounts_given=round(total_discounts_given, 2),
        net_revenue_recovered=round(net_revenue_recovered, 2),
        autonomous_recovery_rate=round(autonomous_recovery_rate, 4),
        human_assisted_recovery_rate=round(human_assisted_recovery_rate, 4),
        blocked_action_count=blocked_count,
        modified_action_count=modified_count,
        escalation_count=escalation_count,
        false_positive_block_cost=round(false_positive_block_cost, 2),
        escalation_rate=round(escalation_rate, 4),
        average_recovery_time_seconds=round(avg_recovery_time, 2),
        budget_exhaustion_case_index=budget_exhaustion_case_index,
        recovery_rate=round(recovery_rate, 4),
    )


def print_metrics(metrics: BatchMetrics) -> None:
    """Pretty-print batch metrics to the console."""
    print("\n" + "=" * 60)
    print("   AI REVENUE RECOVERY AGENT - BATCH METRICS")
    print("=" * 60)
    print(f"  Total Cases Processed:        {metrics.total_cases}")
    print(f"  Total Revenue at Risk:        Rs.{metrics.total_revenue_at_risk:,.2f}")
    print(f"  Gross Revenue Recovered:      Rs.{metrics.gross_revenue_recovered:,.2f}")
    print(f"  Discounts/Incentives Given:   Rs.{metrics.total_discounts_given:,.2f}")
    print(f"  Net Revenue Recovered:        Rs.{metrics.net_revenue_recovered:,.2f}")
    print(f"  Recovery Rate:                {metrics.recovery_rate * 100:.1f}%")
    print("-" * 60)
    print(f"  Autonomous Recovery Rate:     {metrics.autonomous_recovery_rate * 100:.1f}%")
    print(f"  Human-Assisted Recovery Rate: {metrics.human_assisted_recovery_rate * 100:.1f}%")
    print(f"  Escalation Rate:              {metrics.escalation_rate * 100:.1f}%")
    print("-" * 60)
    print(f"  Blocked Actions:              {metrics.blocked_action_count}")
    print(f"  Modified Actions:             {metrics.modified_action_count}")
    print(f"  Total Escalations:            {metrics.escalation_count}")
    print(f"  False-Positive Block Cost:    Rs.{metrics.false_positive_block_cost:,.2f}")
    print("-" * 60)
    print(f"  Avg Recovery Time:            {metrics.average_recovery_time_seconds:.1f}s")
    if metrics.budget_exhaustion_case_index is not None:
        print(f"  Budget Exhausted at Case:     #{metrics.budget_exhaustion_case_index}")
    else:
        print(f"  Budget Exhausted:             No")
    print("=" * 60 + "\n")
