import random
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from backend.config import CAMPAIGN_BUDGET
from backend.reasoning.schemas import (
    PaymentType,
    FailureReason,
    ValueTier,
    RiskProfile,
)
from backend.database.models import Case, CampaignBudget

INDIAN_NAMES = [
    "Aarav Sharma", "Vivaan Patel", "Aditya Singh", "Vihaan Kumar", "Arjun Rao",
    "Sai Krishna", "Riyansh Gupta", "Ayaan Reddy", "Krishna Menon", "Ishaan Verma",
    "Shaurya Deshmukh", "Atharv Kulkarni", "Aarush Joshi", "Kian Iyer", "Darsh Nair",
    "Ananya Sharma", "Myra Patel", "Aadhya Singh", "Kiara Kumar", "Prisha Rao",
    "Diya Krishna", "Avni Gupta", "Pihu Reddy", "Navya Menon", "Aarohi Verma",
    "Riya Deshmukh", "Isha Kulkarni", "Kavya Joshi", "Anika Iyer", "Saanvi Nair",
    "Rahul Dravid", "Sachin Tendulkar", "Virat Kohli", "Rohit Sharma", "Shikhar Dhawan",
    "Rishabh Pant", "Hardik Pandya", "Jasprit Bumrah", "Ravindra Jadeja", "Ajinkya Rahane",
    "Priyanka Chopra", "Deepika Padukone", "Alia Bhatt", "Katrina Kaif", "Kareena Kapoor",
    "Anushka Sharma", "Shraddha Kapoor", "Disha Patani", "Kriti Sanon", "Taapsee Pannu",
    "Karthik Subramanian", "Venkatesh Prasad", "Ramesh Babu", "Suresh Gopi", "Prakash Raj"
]

def generate_cases() -> List[Case]:
    random.seed(42)
    cases = []
    
    for i in range(1, 201):
        case_id = f"CASE-{i:03d}"
        customer_name = random.choice(INDIAN_NAMES)
        
        # phone
        first_digit = random.choice(['6', '7', '8', '9'])
        rest_digits = "".join([str(random.randint(0, 9)) for _ in range(9)])
        customer_phone = f"{first_digit}{rest_digits}"
        
        # Payment type: 40% UPI Autopay, 35% EMI, 25% Subscription
        payment_type = random.choices(
            [PaymentType.UPI_AUTOPAY, PaymentType.EMI, PaymentType.SUBSCRIPTION],
            weights=[40, 35, 25]
        )[0]
        
        # Failure reason
        failure_reason = random.choices(
            [FailureReason.INSUFFICIENT_BALANCE, FailureReason.BANK_TIMEOUT, FailureReason.EXPIRED_INSTRUMENT, FailureReason.CUSTOMER_INACTION, FailureReason.UNKNOWN],
            weights=[40, 20, 15, 15, 10]
        )[0]
        
        # Value tier
        value_tier = random.choices(
            [ValueTier.HIGH, ValueTier.MEDIUM, ValueTier.LOW],
            weights=[20, 50, 30]
        )[0]
        
        if value_tier == ValueTier.HIGH:
            payment_amount = round(random.uniform(10000, 25000), 2)
        elif value_tier == ValueTier.MEDIUM:
            payment_amount = round(random.uniform(2000, 10000), 2)
        else:
            payment_amount = round(random.uniform(199, 2000), 2)
            
        # Risk profile
        risk_profile = random.choices(
            [RiskProfile.FIRST_TIME, RiskProfile.REPEAT, RiskProfile.PRIOR_REFUSAL, RiskProfile.PRIOR_PROMISE],
            weights=[50, 30, 10, 10]
        )[0]
        
        # Difficulty label
        if risk_profile == RiskProfile.PRIOR_REFUSAL:
            difficulty_label = 'hard'
        elif risk_profile == RiskProfile.FIRST_TIME and value_tier == ValueTier.HIGH:
            difficulty_label = 'easy'
        elif risk_profile == RiskProfile.REPEAT:
            difficulty_label = random.choice(['medium', 'hard'])
        else:
            difficulty_label = random.choice(['easy', 'medium'])
            
        case = Case(
            id=case_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            payment_type=payment_type.value,
            payment_amount=payment_amount,
            failure_reason=failure_reason.value,
            value_tier=value_tier.value,
            risk_profile=risk_profile.value,
            difficulty_label=difficulty_label,
            detected_at=datetime.utcnow()
        )
        cases.append(case)
        
    return cases

def generate_and_seed(session: Session) -> List[Case]:
    cases = generate_cases()
    session.add_all(cases)
    
    # Initialize campaign budget
    budget = CampaignBudget(
        total_budget=CAMPAIGN_BUDGET,
        remaining=CAMPAIGN_BUDGET
    )
    session.add(budget)
    
    session.commit()
    return cases
