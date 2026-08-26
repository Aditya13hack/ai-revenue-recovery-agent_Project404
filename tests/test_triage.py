import pytest
from backend.database.models import Case
from backend.triage.detector import detect_at_risk
from backend.triage.classifier import classify_channel
from backend.reasoning.schemas import ChannelType

def test_voice_routing_high_value():
    case = Case(
        id="CASE-TEST-1",
        customer_name="Test",
        customer_phone="9999999999",
        payment_type="emi",
        payment_amount=6000.0,
        failure_reason="insufficient_balance",
        value_tier="high",
        risk_profile="first_time_failure",
        difficulty_label="easy"
    )
    result = classify_channel(case)
    assert result.assigned_channel == ChannelType.VOICE
    
def test_human_escalation_prior_refusal():
    case = Case(
        id="CASE-TEST-2",
        customer_name="Test",
        customer_phone="9999999999",
        payment_type="emi",
        payment_amount=1000.0,
        failure_reason="insufficient_balance",
        value_tier="low",
        risk_profile="prior_refusal",
        difficulty_label="hard"
    )
    result = classify_channel(case)
    assert result.assigned_channel == ChannelType.HUMAN_ESCALATION
    
def test_silent_retry_bank_timeout():
    case = Case(
        id="CASE-TEST-3",
        customer_name="Test",
        customer_phone="9999999999",
        payment_type="emi",
        payment_amount=1000.0,
        failure_reason="bank_timeout",
        value_tier="low",
        risk_profile="first_time_failure",
        difficulty_label="easy"
    )
    result = classify_channel(case)
    assert result.assigned_channel == ChannelType.SILENT_RETRY
    
def test_sms_fallback():
    case = Case(
        id="CASE-TEST-4",
        customer_name="Test",
        customer_phone="9999999999",
        payment_type="emi",
        payment_amount=500.0,
        failure_reason="insufficient_balance",
        value_tier="low",
        risk_profile="first_time_failure",
        difficulty_label="easy"
    )
    result = classify_channel(case)
    assert result.assigned_channel == ChannelType.SMS
    
def test_detector():
    case = Case(
        id="CASE-TEST-5",
        customer_name="Test",
        customer_phone="9999999999",
        payment_type="emi",
        payment_amount=15000.0,
        failure_reason="expired_instrument",
        value_tier="high",
        risk_profile="first_time_failure"
    )
    res = detect_at_risk(case)
    assert res["needs_immediate_attention"] == True
    assert res["risk_score"] >= 0.7
