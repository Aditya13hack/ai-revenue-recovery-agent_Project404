from pydantic import BaseModel
import backend.config as config

class MerchantPolicyConfig(BaseModel):
    max_discount_pct: float
    max_contact_attempts: int
    max_payment_retries: int
    max_extension_days: int
    refusal_escalation_threshold: int
    campaign_budget: float
    budget_incentive_cutoff_pct: float

    @classmethod
    def from_config(cls) -> "MerchantPolicyConfig":
        return cls(
            max_discount_pct=config.MAX_DISCOUNT_PCT,
            max_contact_attempts=config.MAX_CONTACT_ATTEMPTS,
            max_payment_retries=config.MAX_PAYMENT_RETRIES,
            max_extension_days=config.MAX_EXTENSION_DAYS,
            refusal_escalation_threshold=config.REFUSAL_ESCALATION_THRESHOLD,
            campaign_budget=config.CAMPAIGN_BUDGET,
            budget_incentive_cutoff_pct=config.BUDGET_INCENTIVE_CUTOFF_PCT,
        )
