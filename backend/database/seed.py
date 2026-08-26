"""Database seeder - creates tables and populates with synthetic data."""

import collections
from backend.database.connection import reset_db, get_db
from backend.dataset.generator import generate_and_seed


def seed_database():
    print("Resetting database...")
    reset_db()

    print("Generating and seeding cases...")
    with get_db() as session:
        cases = generate_and_seed(session)

        # Build summary INSIDE the session while cases are still bound
        total = len(cases)
        types_count = collections.Counter(c.payment_type for c in cases)
        tiers_count = collections.Counter(c.value_tier for c in cases)
        risks_count = collections.Counter(c.risk_profile for c in cases)
        difficulties = collections.Counter(c.difficulty_label for c in cases)
        total_amount = sum(c.payment_amount for c in cases)

    print(f"\n[OK] Successfully generated {total} cases.")
    print(f"[$$] Total Revenue at Risk: Rs.{total_amount:,.2f}")

    print("\n--- Dataset Summary ---")
    print("\nPayment Types:")
    for k, v in sorted(types_count.items()):
        print(f"  {k}: {v} ({v/total*100:.0f}%)")

    print("\nValue Tiers:")
    for k, v in sorted(tiers_count.items()):
        print(f"  {k}: {v} ({v/total*100:.0f}%)")

    print("\nRisk Profiles:")
    for k, v in sorted(risks_count.items()):
        print(f"  {k}: {v} ({v/total*100:.0f}%)")

    print("\nDifficulty Labels:")
    for k, v in sorted(difficulties.items()):
        print(f"  {k}: {v} ({v/total*100:.0f}%)")


if __name__ == "__main__":
    seed_database()
