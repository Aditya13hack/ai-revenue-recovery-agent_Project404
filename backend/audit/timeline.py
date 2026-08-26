import json
from backend.database.models import AuditEvent, Case
from backend.reasoning.schemas import CaseTimelineEvent, AuditEventType

def get_case_timeline(session, case_id: str) -> list[CaseTimelineEvent]:
    events = session.query(AuditEvent).filter(AuditEvent.case_id == case_id).order_by(AuditEvent.created_at).all()
    timeline = []
    for ev in events:
        details = None
        if ev.output_data:
            try:
                details = json.loads(ev.output_data)
            except:
                details = {'raw': ev.output_data}
                
        timeline.append(CaseTimelineEvent(
            timestamp=ev.created_at,
            event_type=AuditEventType(ev.event_type),
            description=ev.description,
            details=details,
            decision=ev.decision,
            reason=ev.reason
        ))
    return timeline

def get_case_summary(session, case_id: str) -> dict:
    case = session.query(Case).filter(Case.id == case_id).first()
    if not case:
        return {}
        
    timeline = get_case_timeline(session, case_id)
    proposals = [e for e in timeline if e.event_type == AuditEventType.PROPOSAL]
    decisions = [e for e in timeline if e.event_type == AuditEventType.CONTROL_PLANE_DECISION]
    
    return {
        "case_id": case.id,
        "customer_name": case.customer_name,
        "payment_amount": case.payment_amount,
        "failure_reason": case.failure_reason,
        "assigned_channel": case.assigned_channel,
        "outcome": case.outcome,
        "amount_recovered": case.amount_recovered,
        "total_discount_given": case.total_discount_given,
        "timeline_events_count": len(timeline),
        "proposals_count": len(proposals),
        "decisions_count": len(decisions)
    }
