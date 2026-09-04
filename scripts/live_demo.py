"""
Live Demo Script — demonstrates real Razorpay API integration.

This script:
  1. Verifies Razorpay API connection
  2. Creates a real test order on Razorpay
  3. Creates a payment link
  4. Simulates a payment.failed webhook locally
  5. Shows the case being processed by AI + Control Plane

Usage:
    python -m scripts.live_demo                  # Full demo
    python -m scripts.live_demo --verify-only    # Just check connection
    python -m scripts.live_demo --create-order   # Create order + payment link
    python -m scripts.live_demo --simulate       # Simulate webhook + process
"""

import sys
import time
import argparse
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.razorpay_client import verify_connection, create_test_order, create_payment_link
from backend.database.connection import init_db, get_db
from backend.database.models import Case
from backend.control_plane.budget_tracker import BudgetTracker
from backend.control_plane.rules_config import MerchantPolicyConfig
from backend.orchestrator.graph import process_case
from backend.config import CAMPAIGN_BUDGET, RAZORPAY_KEY_ID


def print_header():
    print("\n" + "=" * 65)
    print("   RAZORPAY LIVE MODE DEMO")
    print("   AI Revenue Recovery Agent x Razorpay Test API")
    print("=" * 65)


def step_verify():
    print("\n[STEP 1] Verifying Razorpay API connection (may take a few seconds)...", flush=True)
    result = verify_connection()

    if result["status"] == "connected":
        print(f"  [OK] Connected to Razorpay", flush=True)
        print(f"  Key ID:  {result['key_id']}", flush=True)
        print(f"  Mode:    {result['mode'].upper()}", flush=True)
        return True
    else:
        print(f"  Connection failed.", flush=True)
        print(f"  [FAIL] Connection failed: {result.get('error', 'Unknown')}", flush=True)
        return False


def step_create_order(amount=5000, customer_name="Aarav Sharma"):
    print(f"\n[STEP 2] Creating Razorpay order (Rs.{amount:,.0f} for {customer_name})...", flush=True)

    receipt = f"DEMO-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    try:
        order = create_test_order(
            amount_inr=amount,
            receipt=receipt,
            notes={"source": "ai_recovery_agent", "customer": customer_name},
        )
        print(f"  [OK] Order created!", flush=True)
        print(f"  Order ID:     {order['id']}", flush=True)
        print(f"  Amount:       Rs.{order['amount'] / 100:,.0f}", flush=True)
        print(f"  Status:       {order['status']}", flush=True)
        print(f"  Receipt:      {receipt}", flush=True)
    except Exception as e:
        print(f"  [FAIL] Order creation failed: {e}", flush=True)
        return None, None

    try:
        link = create_payment_link(
            amount_inr=amount,
            customer_name=customer_name,
            customer_phone="+919876543210",
            description=f"Recovery payment for {customer_name} - {receipt}",
            receipt=receipt,
        )
        print(f"\n  [OK] Payment link created!", flush=True)
        print(f"  Link ID:      {link.get('id')}", flush=True)
        print(f"  Payment URL:  {link.get('short_url')}", flush=True)
        print(f"\n  ** This is a REAL Razorpay payment link. **", flush=True)
        print(f"  ** In test mode, you can use test card: 4111 1111 1111 1111 **", flush=True)
    except Exception as e:
        print(f"  [FAIL] Payment link failed: {e}", flush=True)
        link = None

    return order, link


def step_simulate_webhook(amount=5000, customer_name="Aarav Sharma", failure_reason="insufficient_balance"):
    print(f"\n[STEP 3] Simulating payment.failed webhook...", flush=True)
    print(f"  Customer: {customer_name}", flush=True)
    print(f"  Amount:   Rs.{amount:,.0f}", flush=True)
    print(f"  Failure:  {failure_reason}", flush=True)

    init_db()

    case_id = f"LIVE-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    if amount >= 10000:
        value_tier = "high"
    elif amount >= 3000:
        value_tier = "medium"
    else:
        value_tier = "low"

    with get_db() as session:
        new_case = Case(
            id=case_id,
            customer_name=customer_name,
            customer_phone="+919876543210",
            payment_type="upi_autopay",
            payment_amount=amount,
            failure_reason=failure_reason,
            razorpay_payment_id=f"pay_simulated_{case_id}",
            value_tier=value_tier,
            risk_profile="first_time_failure",
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

    print(f"\n  [OK] Case {case_id} created in database", flush=True)

    print(f"\n[STEP 4] Processing through AI + Control Plane...", flush=True)
    t0 = time.time()

    config = MerchantPolicyConfig.from_config()
    budget_tracker = BudgetTracker(CAMPAIGN_BUDGET)

    with get_db() as session:
        try:
            result = process_case(case_id, session, budget_tracker, config)

            outcome = result.get("final_outcome", "unknown")
            channel = result.get("triage_result")
            channel_str = channel.assigned_channel.value if channel else "N/A"
            proposal = result.get("current_proposal")
            decision = result.get("control_plane_decision")

            elapsed = time.time() - t0

            print(f"\n  {'=' * 50}", flush=True)
            print(f"  LIVE CASE RESULT", flush=True)
            print(f"  {'=' * 50}", flush=True)
            print(f"  Case ID:        {case_id}", flush=True)
            print(f"  Channel:        {channel_str}", flush=True)
            print(f"  Outcome:        {outcome}", flush=True)
            print(f"  Time:           {elapsed:.2f}s", flush=True)

            if proposal:
                print(f"\n  AI Proposal:", flush=True)
                print(f"    Action:       {proposal.action_type.value}", flush=True)
                reasoning = proposal.reasoning[:80].encode("ascii", "replace").decode("ascii")
                print(f"    Reasoning:    {reasoning}...", flush=True)
                if proposal.message_content:
                    msg = proposal.message_content[:80].encode("ascii", "replace").decode("ascii")
                    print(f"    Message:      {msg}...", flush=True)

            if decision:
                print(f"\n  Control Plane:", flush=True)
                print(f"    Decision:     {decision.decision.value}", flush=True)
                print(f"    Rule:         {decision.rule_triggered}", flush=True)
                reason = decision.reason[:80].encode("ascii", "replace").decode("ascii")
                print(f"    Reason:       {reason}", flush=True)

            print(f"  {'=' * 50}", flush=True)
            return True

        except Exception as e:
            print(f"  [FAIL] Processing error: {e}", flush=True)
            return False


def run_demo(verify_only=False, create_order=False, simulate=False, full=False):
    print_header()

    connected = step_verify()
    if not connected:
        print("\n[!] Fix your Razorpay keys in .env and try again.", flush=True)
        return

    if verify_only:
        print("\n[DONE] Razorpay connection verified.", flush=True)
        return

    if create_order or full:
        order, link = step_create_order()

    if simulate or full:
        step_simulate_webhook()

    print("\n" + "-" * 65, flush=True)
    print("  DEMO COMPLETE", flush=True)
    print("  Open http://localhost:8000/docs to see all Razorpay API endpoints", flush=True)
    print("  Open http://localhost:5173 to see the live case on the dashboard", flush=True)
    print("-" * 65 + "\n", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Razorpay Live Mode Demo")
    parser.add_argument("--verify-only", action="store_true", help="Only verify API connection")
    parser.add_argument("--create-order", action="store_true", help="Create a test order + payment link")
    parser.add_argument("--simulate", action="store_true", help="Simulate webhook + AI processing")
    args = parser.parse_args()

    if args.verify_only:
        run_demo(verify_only=True)
    elif args.create_order:
        run_demo(create_order=True)
    elif args.simulate:
        run_demo(simulate=True)
    else:
        run_demo(full=True)
