"""
Application configuration — loads from environment variables with sensible defaults.
All merchant policy limits are centralized here so the control plane
has a single source of truth.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")


# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "")

# ---------------------------------------------------------------------------
# LLM Configuration
# ---------------------------------------------------------------------------
LLM_MODEL: str = os.getenv("LLM_MODEL", "groq/compound-mini")
LLM_FALLBACK_PROVIDER: str = os.getenv("LLM_FALLBACK_PROVIDER", "ollama")
LLM_FALLBACK_MODEL: str = os.getenv("LLM_FALLBACK_MODEL", "llama3.1:8b")

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{PROJECT_ROOT / 'recovery_agent.db'}",
)

# ---------------------------------------------------------------------------
# Merchant Policy Limits  (Control Plane reads these — never the LLM)
# ---------------------------------------------------------------------------
CAMPAIGN_BUDGET: float = float(os.getenv("CAMPAIGN_BUDGET", "50000"))
MAX_DISCOUNT_PCT: float = float(os.getenv("MAX_DISCOUNT_PCT", "15"))
MAX_CONTACT_ATTEMPTS: int = int(os.getenv("MAX_CONTACT_ATTEMPTS", "3"))
MAX_PAYMENT_RETRIES: int = int(os.getenv("MAX_PAYMENT_RETRIES", "2"))
MAX_EXTENSION_DAYS: int = int(os.getenv("MAX_EXTENSION_DAYS", "7"))
REFUSAL_ESCALATION_THRESHOLD: int = int(os.getenv("REFUSAL_ESCALATION_THRESHOLD", "2"))
BUDGET_INCENTIVE_CUTOFF_PCT: float = float(os.getenv("BUDGET_INCENTIVE_CUTOFF_PCT", "5"))

# ---------------------------------------------------------------------------
# Voice / TTS Configuration
# ---------------------------------------------------------------------------
TTS_VOICE_AGENT: str = os.getenv("TTS_VOICE_AGENT", "hi-IN-SwaraNeural")
TTS_VOICE_CUSTOMER: str = os.getenv("TTS_VOICE_CUSTOMER", "hi-IN-MadhurNeural")
AUDIO_OUTPUT_DIR: Path = PROJECT_ROOT / "backend" / "voice" / "audio_assets"

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
