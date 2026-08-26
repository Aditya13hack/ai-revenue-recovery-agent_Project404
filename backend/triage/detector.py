from backend.database.models import Case
from backend.reasoning.schemas import ValueTier, FailureReason

def detect_at_risk(case: Case) -> dict:
    """
    Revenue-at-risk detection - identifies and flags failed payments.
    Calculates a risk_score (0.0-1.0).
    """
    score = 0.0
    
    if case.value_tier == ValueTier.HIGH.value:
        score += 0.4
    elif case.value_tier == ValueTier.MEDIUM.value:
        score += 0.2
        
    if case.failure_reason == FailureReason.INSUFFICIENT_BALANCE.value:
        score += 0.3
    elif case.failure_reason == FailureReason.EXPIRED_INSTRUMENT.value:
        score += 0.4
    elif case.failure_reason == FailureReason.CUSTOMER_INACTION.value:
        score += 0.2
        
    # Time since failure would typically add to score, 
    # but for simplicity we cap it at what we have based on fields available
    
    score = min(score, 1.0)
    
    return {
        "case_id": case.id,
        "amount_at_risk": case.payment_amount,
        "risk_score": score,
        "needs_immediate_attention": score >= 0.7
    }
