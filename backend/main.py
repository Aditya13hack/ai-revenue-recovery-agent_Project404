"""
FastAPI application — backend server for the AI Revenue Recovery Agent.

Serves the dashboard API endpoints and voice playback.
"""

import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional

from backend.config import APP_HOST, APP_PORT, AUDIO_OUTPUT_DIR
from backend.database.connection import init_db, get_db_dependency
from backend.database.models import Case, ActionProposal as ActionProposalModel, CampaignBudget, BudgetTransaction, AuditEvent
from backend.audit.timeline import get_case_timeline, get_case_summary
from backend.metrics.calculator import compute_batch_metrics


# ─────────────────── APP SETUP ───────────────────

app = FastAPI(
    title="AI Revenue Recovery Agent",
    description="Razorpay AI Buildathon 2026 — Track 03",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


# ─────────────────── HEALTH ───────────────────

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "AI Revenue Recovery Agent"}


# ─────────────────── METRICS ───────────────────

@app.get("/api/metrics")
def get_metrics(db: Session = Depends(get_db_dependency)):
    metrics = compute_batch_metrics(db)
    return metrics.model_dump()


# ─────────────────── CASES ───────────────────

@app.get("/api/cases")
def list_cases(
    outcome: Optional[str] = Query(None, description="Filter by outcome"),
    channel: Optional[str] = Query(None, description="Filter by assigned channel"),
    value_tier: Optional[str] = Query(None, description="Filter by value tier"),
    risk_profile: Optional[str] = Query(None, description="Filter by risk profile"),
    payment_type: Optional[str] = Query(None, description="Filter by payment type"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db_dependency),
):
    query = db.query(Case)

    if outcome:
        query = query.filter(Case.outcome == outcome)
    if channel:
        query = query.filter(Case.assigned_channel == channel)
    if value_tier:
        query = query.filter(Case.value_tier == value_tier)
    if risk_profile:
        query = query.filter(Case.risk_profile == risk_profile)
    if payment_type:
        query = query.filter(Case.payment_type == payment_type)

    total = query.count()
    cases = query.order_by(Case.id).offset((page - 1) * per_page).limit(per_page).all()

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "cases": [
            {
                "id": c.id,
                "customer_name": c.customer_name,
                "customer_phone": c.customer_phone,
                "payment_type": c.payment_type,
                "payment_amount": c.payment_amount,
                "failure_reason": c.failure_reason,
                "value_tier": c.value_tier,
                "risk_profile": c.risk_profile,
                "difficulty_label": c.difficulty_label,
                "assigned_channel": c.assigned_channel,
                "contact_attempts": c.contact_attempts,
                "payment_retries": c.payment_retries,
                "consecutive_refusals": c.consecutive_refusals,
                "do_not_contact": c.do_not_contact,
                "total_discount_given": c.total_discount_given,
                "extension_days_given": c.extension_days_given,
                "outcome": c.outcome,
                "amount_recovered": c.amount_recovered,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None,
            }
            for c in cases
        ],
    }


@app.get("/api/cases/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db_dependency)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    return {
        "id": case.id,
        "customer_name": case.customer_name,
        "customer_phone": case.customer_phone,
        "payment_type": case.payment_type,
        "payment_amount": case.payment_amount,
        "failure_reason": case.failure_reason,
        "value_tier": case.value_tier,
        "risk_profile": case.risk_profile,
        "difficulty_label": case.difficulty_label,
        "assigned_channel": case.assigned_channel,
        "contact_attempts": case.contact_attempts,
        "payment_retries": case.payment_retries,
        "consecutive_refusals": case.consecutive_refusals,
        "do_not_contact": case.do_not_contact,
        "total_discount_given": case.total_discount_given,
        "extension_days_given": case.extension_days_given,
        "outcome": case.outcome,
        "amount_recovered": case.amount_recovered,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "detected_at": case.detected_at.isoformat() if case.detected_at else None,
        "resolved_at": case.resolved_at.isoformat() if case.resolved_at else None,
    }


# ─────────────────── TIMELINE ───────────────────

@app.get("/api/cases/{case_id}/timeline")
def get_timeline(case_id: str, db: Session = Depends(get_db_dependency)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    timeline = get_case_timeline(db, case_id)
    return {
        "case_id": case_id,
        "events": [event.model_dump() for event in timeline],
    }


@app.get("/api/cases/{case_id}/summary")
def get_summary(case_id: str, db: Session = Depends(get_db_dependency)):
    summary = get_case_summary(db, case_id)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return summary


# ─────────────────── BUDGET ───────────────────

@app.get("/api/budget")
def get_budget(db: Session = Depends(get_db_dependency)):
    budget = db.query(CampaignBudget).first()
    if not budget:
        return {"error": "No budget record found"}

    transactions = db.query(BudgetTransaction).order_by(BudgetTransaction.created_at).all()

    return {
        "total_budget": budget.total_budget,
        "spent": budget.spent,
        "remaining": budget.remaining,
        "is_exhausted": budget.is_exhausted,
        "exhausted_at_case": budget.exhausted_at_case,
        "transactions": [
            {
                "case_id": t.case_id,
                "amount": t.amount,
                "budget_before": t.budget_before,
                "budget_after": t.budget_after,
                "description": t.description,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in transactions
        ],
    }


# ─────────────────── VOICE ───────────────────

@app.get("/api/cases/{case_id}/audio")
def get_audio(case_id: str, db: Session = Depends(get_db_dependency)):
    audio_dir = AUDIO_OUTPUT_DIR
    
    # 1. Direct match (e.g. CASE-001.mp3 or DEMO-HAPPY_PATH.mp3)
    for ext in (".mp3", ".wav"):
        audio_file = audio_dir / f"{case_id}{ext}"
        if audio_file.exists():
            return FileResponse(
                str(audio_file),
                media_type="audio/mpeg" if ext == ".mp3" else "audio/wav",
            )
    
    # 2. Dynamic fallback matching the case status in database
    case = db.query(Case).filter(Case.id == case_id).first()
    scenario = "DEMO-HAPPY_PATH.mp3"
    
    if case:
        if case.outcome in ("escalated", "unresolved") or case.do_not_contact:
            scenario = "DEMO-ESCALATE_BLOCK.mp3"
        elif case.total_discount_given > 0 or case.outcome == "partially_recovered":
            scenario = "DEMO-MODIFY_MOMENT.mp3"
        else:
            scenario = "DEMO-HAPPY_PATH.mp3"
            
    fallback_file = audio_dir / scenario
    if fallback_file.exists():
        return FileResponse(str(fallback_file), media_type="audio/mpeg")

    raise HTTPException(status_code=404, detail=f"No audio found for {case_id}")


# ─────────────────── DECISIONS ───────────────────

@app.get("/api/decisions")
def list_decisions(
    decision_type: Optional[str] = Query(None),
    db: Session = Depends(get_db_dependency),
):
    query = db.query(ActionProposalModel)
    if decision_type:
        query = query.filter(ActionProposalModel.decision == decision_type)

    proposals = query.order_by(ActionProposalModel.created_at).all()

    return {
        "total": len(proposals),
        "decisions": [
            {
                "id": p.id,
                "case_id": p.case_id,
                "action_type": p.action_type,
                "discount_pct": p.discount_pct,
                "extension_days": p.extension_days,
                "reasoning": p.reasoning,
                "decision": p.decision,
                "decision_reason": p.decision_reason,
                "rule_triggered": p.rule_triggered,
                "modified_discount_pct": p.modified_discount_pct,
                "modified_extension_days": p.modified_extension_days,
                "budget_remaining": p.budget_remaining,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in proposals
        ],
    }


# ─────────────────── RUN ───────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=APP_HOST, port=APP_PORT, reload=True)
