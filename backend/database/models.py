"""
SQLAlchemy ORM models for the Revenue Recovery Agent database.

Tables:
  - cases: Individual failed-payment recovery cases
  - action_proposals: Every action the LLM proposed + control plane decision
  - audit_events: Full timeline of every event per case
  - campaign_budget: Global recovery campaign budget state
  - budget_transactions: Itemized budget consumption log
"""

from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Case(Base):
    """A single failed-payment recovery case."""
    __tablename__ = "cases"

    id = Column(String, primary_key=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)

    # Payment details
    payment_type = Column(String, nullable=False)      # upi_autopay / emi / subscription
    payment_amount = Column(Float, nullable=False)
    failure_reason = Column(String, nullable=False)     # insufficient_balance / bank_timeout / ...
    razorpay_payment_id = Column(String, nullable=True) # From Razorpay test mode, if available

    # Customer classification
    value_tier = Column(String, nullable=False)         # high / medium / low
    risk_profile = Column(String, nullable=False)       # first_time_failure / repeat_failure / ...
    difficulty_label = Column(String, nullable=True)     # easy / medium / hard (ground truth)

    # Channel routing
    assigned_channel = Column(String, nullable=True)    # voice / sms / silent_retry / human_escalation

    # State tracking (updated as the loop runs)
    contact_attempts = Column(Integer, default=0)
    payment_retries = Column(Integer, default=0)
    consecutive_refusals = Column(Integer, default=0)
    do_not_contact = Column(Boolean, default=False)
    total_discount_given = Column(Float, default=0.0)
    extension_days_given = Column(Integer, default=0)

    # Final outcome
    outcome = Column(String, nullable=True)             # recovered / partially_recovered / escalated / ...
    amount_recovered = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    detected_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    action_proposals = relationship("ActionProposal", back_populates="case", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="case", cascade="all, delete-orphan")


class ActionProposal(Base):
    """
    Every action the LLM proposed, together with the control plane's
    decision on that proposal.  One case can have multiple proposals
    (e.g. the AI tries a discount, gets MODIFY'd, then tries an extension).
    """
    __tablename__ = "action_proposals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)

    # What the LLM proposed
    action_type = Column(String, nullable=False)         # offer_discount / offer_extension / ...
    discount_pct = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)
    extension_days = Column(Integer, nullable=True)
    promise_date = Column(String, nullable=True)
    reasoning = Column(Text, nullable=False)
    message_content = Column(Text, nullable=True)       # LLM-generated Hinglish message for customer
    # Control plane decision
    decision = Column(String, nullable=True)             # execute / modify / escalate / block
    decision_reason = Column(Text, nullable=True)
    rule_triggered = Column(String, nullable=True)
    modified_discount_pct = Column(Float, nullable=True)
    modified_discount_amount = Column(Float, nullable=True)
    modified_extension_days = Column(Integer, nullable=True)

    # Budget snapshot at decision time
    budget_remaining = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="action_proposals")


class AuditEvent(Base):
    """
    Complete, ordered timeline event for a case.
    Every node in the processing loop emits one or more of these.
    """
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)

    event_type = Column(String, nullable=False)   # detection / diagnosis / triage / proposal / ...
    node_name = Column(String, nullable=True)      # LangGraph node that emitted this
    description = Column(Text, nullable=False)
    input_data = Column(Text, nullable=True)       # JSON blob
    output_data = Column(Text, nullable=True)      # JSON blob
    decision = Column(String, nullable=True)
    reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="audit_events")


class CampaignBudget(Base):
    """
    Global recovery budget for the entire campaign / batch.
    There is exactly ONE row in this table at any time.
    """
    __tablename__ = "campaign_budget"

    id = Column(Integer, primary_key=True, autoincrement=True)
    total_budget = Column(Float, nullable=False)
    spent = Column(Float, default=0.0)
    remaining = Column(Float, nullable=False)
    is_exhausted = Column(Boolean, default=False)
    exhausted_at_case = Column(String, nullable=True)   # case_id where budget ran out

    updated_at = Column(DateTime, default=datetime.utcnow)


class BudgetTransaction(Base):
    """Itemized log of every incentive that consumed part of the budget."""
    __tablename__ = "budget_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    amount = Column(Float, nullable=False)
    budget_before = Column(Float, nullable=False)
    budget_after = Column(Float, nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
