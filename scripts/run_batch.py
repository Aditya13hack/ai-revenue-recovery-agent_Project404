"""
Batch runner - processes cases through the full recovery pipeline.

Usage:
    python -m scripts.run_batch
    python -m scripts.run_batch --limit 10   # Process only first 10 cases
"""

import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database.connection import init_db, get_db
from backend.database.models import Case
from backend.control_plane.budget_tracker import BudgetTracker
from backend.control_plane.rules_config import MerchantPolicyConfig
from backend.orchestrator.graph import process_case
from backend.metrics.calculator import compute_batch_metrics, print_metrics
from backend.config import CAMPAIGN_BUDGET


def run_batch(limit=None):
    print("\n[START] RevGuard - Batch Run", flush=True)
    print("=" * 60, flush=True)

    config = MerchantPolicyConfig.from_config()
    budget_tracker = BudgetTracker(CAMPAIGN_BUDGET)

    with get_db() as session:
        query = session.query(Case).order_by(Case.id)
        if limit:
            query = query.limit(limit)
        cases = query.all()

        total = len(cases)
        case_ids = [c.id for c in cases]  # Capture IDs while in session

    print(f"[INFO] Processing {total} cases...", flush=True)
    print(f"[INFO] Campaign Budget: Rs.{CAMPAIGN_BUDGET:,.0f}", flush=True)
    print(f"[INFO] Policy: max_discount={config.max_discount_pct}%, "
          f"max_contacts={config.max_contact_attempts}, "
          f"max_retries={config.max_payment_retries}", flush=True)
    print("-" * 60, flush=True)

    start_time = time.time()
    successes = 0
    failures = 0

    for i, case_id in enumerate(case_ids, 1):
        try:
            with get_db() as session:
                result = process_case(case_id, session, budget_tracker, config)

                outcome = result.get("final_outcome", "unknown")
                error = result.get("error")

                if error:
                    status = f"ERROR: {error}"
                    failures += 1
                else:
                    marker = {
                        "recovered": "[OK]",
                        "partially_recovered": "[PARTIAL]",
                        "escalated": "[ESCALATED]",
                        "unresolved": "[UNRESOLVED]",
                    }.get(outcome, "[??]")
                    status = f"{marker} {outcome}"
                    successes += 1

                channel = result.get("triage_result")
                channel_str = channel.assigned_channel.value if channel else "N/A"

                budget_state = budget_tracker.get_state()
                budget_remaining = budget_state.get("remaining", 0)

                print(f"  [{i:3d}/{total}] {case_id} | {channel_str:<18s} | {status:<28s} | Budget: Rs.{budget_remaining:,.0f}", flush=True)

        except Exception as e:
            failures += 1
            print(f"  [{i:3d}/{total}] {case_id} | EXCEPTION: {str(e)[:60]}", flush=True)
            continue

    elapsed = time.time() - start_time
    print("-" * 60, flush=True)
    print(f"[TIME] Batch completed in {elapsed:.1f}s ({successes} success, {failures} failures)", flush=True)

    with get_db() as session:
        metrics = compute_batch_metrics(session)
    print_metrics(metrics)

    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the recovery batch pipeline")
    parser.add_argument("--limit", type=int, default=None, help="Process only N cases")
    args = parser.parse_args()

    run_batch(limit=args.limit)
