import pytest
import threading
from backend.database.connection import init_db, get_db
from backend.control_plane.budget_tracker import BudgetTracker
from backend.database.models import CampaignBudget, BudgetTransaction

@pytest.fixture(autouse=True)
def setup_teardown_db():
    init_db()
    yield

def test_consume_reduces_balance():
    tracker = BudgetTracker(total_budget=1000.0)
    success = tracker.consume(200.0, "case_1", "Discount")
    assert success is True
    assert tracker.remaining() == 800.0
    
    with get_db() as db:
        tx = db.query(BudgetTransaction).first()
        assert tx is not None
        assert tx.amount == 200.0
        assert tx.budget_after == 800.0

def test_consume_returns_false_when_insufficient():
    tracker = BudgetTracker(total_budget=1000.0)
    success = tracker.consume(1200.0, "case_1", "Huge Discount")
    assert success is False
    assert tracker.remaining() == 1000.0

def test_is_exhausted_when_below_threshold():
    tracker = BudgetTracker(total_budget=1000.0)
    # config.BUDGET_INCENTIVE_CUTOFF_PCT is usually 5%
    # So cutoff is 50.0
    tracker.consume(900.0, "case_1", "Discount 1")
    assert not tracker.is_exhausted()
    
    tracker.consume(60.0, "case_2", "Discount 2")
    # remaining is 40.0, which is < 50.0
    assert tracker.is_exhausted()
    
    state = tracker.get_state()
    assert state["is_exhausted"] is True
    assert state["exhausted_at_case"] == "case_2"

def test_thread_safety():
    tracker = BudgetTracker(total_budget=1000.0)
    
    def worker():
        for _ in range(10):
            tracker.consume(10.0, "case_t", "Thread Discount")
            
    threads = []
    for _ in range(10):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    assert tracker.remaining() == 0.0 # 100 * 10 = 1000 consumed
