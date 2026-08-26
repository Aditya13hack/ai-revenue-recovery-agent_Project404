import threading
from typing import Dict, Any
from backend.database.connection import get_db
from backend.database.models import CampaignBudget, BudgetTransaction
import backend.config as config

class BudgetTracker:
    def __init__(self, total_budget: float):
        self.lock = threading.Lock()
        with get_db() as db:
            budget = db.query(CampaignBudget).first()
            if not budget:
                budget = CampaignBudget(
                    total_budget=total_budget,
                    spent=0.0,
                    remaining=total_budget,
                    is_exhausted=False
                )
                db.add(budget)
    
    def consume(self, amount: float, case_id: str, description: str) -> bool:
        with self.lock:
            with get_db() as db:
                budget = db.query(CampaignBudget).first()
                if not budget:
                    return False
                
                if budget.remaining < amount:
                    return False
                
                budget_before = budget.remaining
                budget.spent += amount
                budget.remaining -= amount
                
                cutoff_value = budget.total_budget * (config.BUDGET_INCENTIVE_CUTOFF_PCT / 100.0)
                if budget.remaining < cutoff_value:
                    budget.is_exhausted = True
                    if not budget.exhausted_at_case:
                        budget.exhausted_at_case = case_id
                
                transaction = BudgetTransaction(
                    case_id=case_id,
                    amount=amount,
                    budget_before=budget_before,
                    budget_after=budget.remaining,
                    description=description
                )
                db.add(transaction)
                return True
                
    def remaining(self) -> float:
        with self.lock:
            with get_db() as db:
                budget = db.query(CampaignBudget).first()
                return budget.remaining if budget else 0.0
                
    def is_exhausted(self) -> bool:
        with self.lock:
            with get_db() as db:
                budget = db.query(CampaignBudget).first()
                if not budget:
                    return True
                return budget.is_exhausted
                
    def get_state(self) -> Dict[str, Any]:
        with self.lock:
            with get_db() as db:
                budget = db.query(CampaignBudget).first()
                if not budget:
                    return {}
                return {
                    "total_budget": budget.total_budget,
                    "spent": budget.spent,
                    "remaining": budget.remaining,
                    "is_exhausted": budget.is_exhausted,
                    "exhausted_at_case": budget.exhausted_at_case
                }
