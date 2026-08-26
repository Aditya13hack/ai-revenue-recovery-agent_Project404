"""
Pydantic schemas for structured communication between components.
These schemas enforce type safety at every boundary:
  LLM → Control Plane → Execution → Audit

Every component imports from here — this is the single source of truth
for data shapes flowing through the system.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


# ===================================================================
# Enums — used by both Pydantic schemas and SQLAlchemy models
# ===================================================================

class PaymentType(str, Enum):
    UPI_AUTOPAY = "upi_autopay"
    EMI = "emi"
    SUBSCRIPTION = "subscription"


class FailureReason(str, Enum):
    INSUFFICIENT_BALANCE = "insufficient_balance"
    BANK_TIMEOUT = "bank_timeout"
    EXPIRED_INSTRUMENT = "expired_instrument"
    CUSTOMER_INACTION = "customer_inaction"
    UNKNOWN = "unknown"


class ValueTier(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskProfile(str, Enum):
    FIRST_TIME = "first_time_failure"
    REPEAT = "repeat_failure"
    PRIOR_REFUSAL = "prior_refusal"
    PRIOR_PROMISE = "prior_promise_to_pay"


class ChannelType(str, Enum):
    VOICE = "voice"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    SILENT_RETRY = "silent_retry"
    HUMAN_ESCALATION = "human_escalation"


class ActionType(str, Enum):
    OFFER_EXTENSION = "offer_extension"
    OFFER_DISCOUNT = "offer_discount"
    REQUEST_RETRY = "request_retry"
    PROMISE_TO_PAY = "promise_to_pay"
    SEND_REMINDER = "send_reminder"
    ESCALATE = "escalate"
    END_CALL = "end_call"


class DecisionType(str, Enum):
    EXECUTE = "execute"
    MODIFY = "modify"
    ESCALATE = "escalate"
    BLOCK = "block"


class CaseOutcome(str, Enum):
    RECOVERED = "recovered"
    PARTIALLY_RECOVERED = "partially_recovered"
    ESCALATED = "escalated"
    UNRESOLVED = "unresolved"
    DO_NOT_CONTACT = "do_not_contact"


class AuditEventType(str, Enum):
    DETECTION = "detection"
    DIAGNOSIS = "diagnosis"
    TRIAGE = "triage"
    PROPOSAL = "proposal"
    CONTROL_PLANE_DECISION = "control_plane_decision"
    EXECUTION = "execution"
    MEASUREMENT = "measurement"
    BUDGET_UPDATE = "budget_update"
    CONVERSATION = "conversation"
    ESCALATION = "escalation"


# ===================================================================
# Schemas — structured data flowing between components
# ===================================================================

class CaseContext(BaseModel):
    """Context about a case, passed to the LLM for reasoning."""
    case_id: str
    customer_name: str
    payment_type: PaymentType
    payment_amount: float
    failure_reason: FailureReason
    value_tier: ValueTier
    risk_profile: RiskProfile
    contact_attempts: int = 0
    payment_retries: int = 0
    consecutive_refusals: int = 0
    do_not_contact: bool = False
    previous_actions: list[str] = Field(default_factory=list)


class ActionProposal(BaseModel):
    """
    Structured action proposal from the LLM reasoning layer.
    The LLM fills this out; the control plane validates it.
    """
    action_type: ActionType
    discount_pct: Optional[float] = Field(None, ge=0, le=100)
    discount_amount: Optional[float] = Field(None, ge=0)
    extension_days: Optional[int] = Field(None, ge=0)
    promise_date: Optional[str] = None
    message_content: Optional[str] = None
    reasoning: str = Field(..., description="LLM's explanation for why this action")


class ControlPlaneDecision(BaseModel):
    """
    Decision from the deterministic control plane.
    Always includes the reason and the rule that triggered it.
    """
    decision: DecisionType
    reason: str
    rule_triggered: str
    original_proposal: ActionProposal
    modified_proposal: Optional[ActionProposal] = None
    budget_remaining: float = 0.0


class TriageResult(BaseModel):
    """Result of the triage/classification step."""
    case_id: str
    assigned_channel: ChannelType
    priority_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str


class ConversationTurn(BaseModel):
    """A single turn in the customer conversation."""
    speaker: Literal["agent", "customer"]
    text: str
    language: Literal["hindi", "english", "hinglish"] = "hinglish"
    timestamp: Optional[datetime] = None


class ConversationScript(BaseModel):
    """Full conversation script for voice generation."""
    case_id: str
    turns: list[ConversationTurn]
    control_plane_decisions: list[ControlPlaneDecision]
    final_outcome: CaseOutcome


class BatchMetrics(BaseModel):
    """Aggregate metrics for the full batch run (Section 10 of spec)."""
    total_cases: int
    total_revenue_at_risk: float
    gross_revenue_recovered: float
    total_discounts_given: float
    net_revenue_recovered: float
    autonomous_recovery_rate: float
    human_assisted_recovery_rate: float
    blocked_action_count: int
    modified_action_count: int
    escalation_count: int
    false_positive_block_cost: float
    escalation_rate: float
    average_recovery_time_seconds: float
    budget_exhaustion_case_index: Optional[int] = None
    recovery_rate: float  # net_recovered / at_risk


class CaseTimelineEvent(BaseModel):
    """A single event in a case's audit timeline."""
    timestamp: datetime
    event_type: AuditEventType
    description: str
    details: Optional[dict] = None
    decision: Optional[DecisionType] = None
    reason: Optional[str] = None
