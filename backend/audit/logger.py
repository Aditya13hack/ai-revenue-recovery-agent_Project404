import json
from datetime import datetime
from backend.database.models import AuditEvent, Case, ActionProposal as ActionProposalModel
from backend.reasoning.schemas import AuditEventType, ActionProposal, ControlPlaneDecision

class AuditLogger:
    def __init__(self, session):
        self.session = session
        
    def _to_json_str(self, data):
        if data is None:
            return None
        if hasattr(data, 'model_dump'):
            return json.dumps(data.model_dump())
        return json.dumps(data)
        
    def log_event(self, case_id: str, event_type: AuditEventType, description: str, node_name: str = None, input_data=None, output_data=None, decision=None, reason=None):
        event = AuditEvent(
            case_id=case_id,
            event_type=event_type.value,
            description=description,
            node_name=node_name,
            input_data=self._to_json_str(input_data),
            output_data=self._to_json_str(output_data),
            decision=decision.value if hasattr(decision, 'value') else decision,
            reason=reason
        )
        self.session.add(event)
        return event

    def log_detection(self, case_id: str, case_details: dict):
        self.log_event(case_id, AuditEventType.DETECTION, "Case detected", "detect_node", output_data=case_details)

    def log_diagnosis(self, case_id: str, diagnosis: dict):
        self.log_event(case_id, AuditEventType.DIAGNOSIS, "Case diagnosed", "diagnose_node", output_data=diagnosis)

    def log_triage(self, case_id: str, triage_result: dict):
        self.log_event(case_id, AuditEventType.TRIAGE, "Case triaged", "triage_node", output_data=triage_result)

    def log_proposal(self, case_id: str, proposal: ActionProposal):
        self.log_event(case_id, AuditEventType.PROPOSAL, "Action proposed by LLM", "reason_node", output_data=proposal)

    def log_decision(self, case_id: str, decision: ControlPlaneDecision):
        self.log_event(case_id, AuditEventType.CONTROL_PLANE_DECISION, "Control plane made a decision", "validate_node", 
                       input_data=decision.original_proposal, output_data=decision, 
                       decision=decision.decision, reason=decision.reason)

    def log_execution(self, case_id: str, action_taken: dict):
        self.log_event(case_id, AuditEventType.EXECUTION, "Action executed", "execute_node", output_data=action_taken)

    def log_measurement(self, case_id: str, outcome: dict):
        self.log_event(case_id, AuditEventType.MEASUREMENT, "Outcome measured", "measure_node", output_data=outcome)
