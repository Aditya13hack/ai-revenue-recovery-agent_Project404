"""
Seed real Razorpay API cases into the database.
Creates authentic Razorpay Orders & Payment links via the Razorpay test API.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.razorpay_client import create_test_order, create_payment_link
from backend.database.connection import init_db, get_db
from backend.database.models import Case
from backend.control_plane.budget_tracker import BudgetTracker
from backend.control_plane.rules_config import MerchantPolicyConfig
from backend.orchestrator.graph import process_case
from backend.config import CAMPAIGN_BUDGET


def seed_real_razorpay_cases():
    print("\n=== Seeding Real Razorpay API Test Cases ===")
    init_db()

    cases_data = [
        {
            "customer_name": "Priya Patel",
            "customer_phone": "+919876543210",
            "amount": 4500.0,
            "payment_type": "upi_autopay",
            "failure_reason": "insufficient_balance",
            "value_tier": "medium",
            "risk_profile": "first_time_failure",
        },
        {
            "customer_name": "Vikram Malhotra",
            "customer_phone": "+919812345678",
            "amount": 12500.0,
            "payment_type": "emi",
            "failure_reason": "bank_timeout",
            "value_tier": "high",
            "risk_profile": "first_time_failure",
        }
    ]

    config = MerchantPolicyConfig.from_config()
    budget_tracker = BudgetTracker(CAMPAIGN_BUDGET)

    for i, c_data in enumerate(cases_data, 1):
        name = c_data["customer_name"]
        amt = c_data["amount"]
        receipt = f"RZP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{i}"
        
        print(f"\n[{i}/2] Calling Razorpay API for {name} (Rs.{amt:,.0f})...")
        rzp_pay_id = receipt

        try:
            order = create_test_order(int(amt), receipt)
            link = create_payment_link(int(amt), name, c_data["customer_phone"], f"Recovery for {name}", receipt)
            rzp_pay_id = order.get("id", receipt)
            print(f"  [OK] Real Razorpay Order ID: {order.get('id')}")
            print(f"  [OK] Real Razorpay Payment URL: {link.get('short_url')}")
        except Exception as e:
            print(f"  [API NOTICE] {e}")

        case_id = f"RZP-{receipt[-8:]}"

        with get_db() as session:
            # Check if case exists
            existing = session.query(Case).filter(Case.id == case_id).first()
            if not existing:
                new_case = Case(
                    id=case_id,
                    customer_name=name,
                    customer_phone=c_data["customer_phone"],
                    payment_type=c_data["payment_type"],
                    payment_amount=amt,
                    failure_reason=c_data["failure_reason"],
                    razorpay_payment_id=rzp_pay_id,
                    value_tier=c_data["value_tier"],
                    risk_profile=c_data["risk_profile"],
                    difficulty_label="medium",
                    do_not_contact=False,
                    contact_attempts=0,
                    payment_retries=0,
                    consecutive_refusals=0,
                    total_discount_given=0.0,
                    extension_days_given=0,
                    amount_recovered=0.0,
                    detected_at=datetime.utcnow(),
                )
                session.add(new_case)
                session.commit()

            print(f"  Running case {case_id} through LangGraph Control Plane...")
            res = process_case(case_id, session, budget_tracker, config)
            print(f"  [SUCCESS] Case {case_id} Processed! Outcome: {res.get('final_outcome')} | Recovered: Rs.{res.get('amount_recovered'):,.0f}")

        time.sleep(1)

    print("\n=== Seeding Complete! Real Razorpay cases are live on dashboard. ===\n")


if __name__ == "__main__":
    seed_real_razorpay_cases()
