from backend.database.models import Case
from backend.reasoning.schemas import (
    TriageResult,
    ChannelType,
    RiskProfile,
    FailureReason,
    ValueTier
)

def classify_channel(case: Case) -> TriageResult:
    """
    Channel routing classifier.
    """
    # - HUMAN_ESCALATION: prior_refusal risk profile -> skip automation
    if case.risk_profile == RiskProfile.PRIOR_REFUSAL.value:
        return TriageResult(
            case_id=case.id,
            assigned_channel=ChannelType.HUMAN_ESCALATION,
            priority_score=0.9,
            reasoning="Customer has prior refusal, escalating to human agent."
        )
        
    # - SILENT_RETRY: bank_timeout failure reason AND first occurrence
    if (case.failure_reason == FailureReason.BANK_TIMEOUT.value and 
        case.risk_profile == RiskProfile.FIRST_TIME.value):
        return TriageResult(
            case_id=case.id,
            assigned_channel=ChannelType.SILENT_RETRY,
            priority_score=0.1,
            reasoning="First time bank timeout, silent retry is optimal."
        )
        
    # - VOICE: high_value AND (first_time OR repeat_failure) AND amount > 5000
    if (case.value_tier == ValueTier.HIGH.value and 
        case.risk_profile in [RiskProfile.FIRST_TIME.value, RiskProfile.REPEAT.value] and 
        case.payment_amount > 5000):
        return TriageResult(
            case_id=case.id,
            assigned_channel=ChannelType.VOICE,
            priority_score=0.8,
            reasoning="High value payment failure, needs voice contact."
        )
        
    # - VOICE: medium_value AND first_time AND amount > 3000
    if (case.value_tier == ValueTier.MEDIUM.value and 
        case.risk_profile == RiskProfile.FIRST_TIME.value and 
        case.payment_amount > 3000):
        return TriageResult(
            case_id=case.id,
            assigned_channel=ChannelType.VOICE,
            priority_score=0.6,
            reasoning="Medium value first-time failure, needs voice contact."
        )
        
    # - SMS/WHATSAPP: everything else
    return TriageResult(
        case_id=case.id,
        assigned_channel=ChannelType.SMS,
        priority_score=0.3,
        reasoning="Standard case, falling back to SMS/WhatsApp."
    )
