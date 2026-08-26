from typing import TypedDict, Optional, List, Any
from backend.reasoning.schemas import (
    CaseContext, TriageResult, ConversationTurn, ActionProposal, ControlPlaneDecision
)


class RecoveryState(TypedDict, total=False):
    """State object flowing through the LangGraph recovery pipeline."""
    # Core data
    case_id: str
    case_context: Optional[CaseContext]
    triage_result: Optional[TriageResult]
    conversation_history: List[ConversationTurn]
    current_proposal: Optional[ActionProposal]
    control_plane_decision: Optional[ControlPlaneDecision]
    all_decisions: List[dict]
    final_outcome: Optional[str]
    amount_recovered: float
    error: Optional[str]

    # Injected dependencies (passed through the graph)
    _session: Any
    _logger: Any
    _budget_tracker: Any
    _config: Any
    _agent: Any
