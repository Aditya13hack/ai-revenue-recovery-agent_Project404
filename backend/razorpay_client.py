"""
Razorpay API Client — wraps the official razorpay Python SDK.

Provides:
  - Connection verification (health check)
  - Order creation (for demo)
  - Payment link creation
  - Payment fetch
  - Webhook signature verification
"""

import hmac
import hashlib
import razorpay
from backend.config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET


def get_client() -> razorpay.Client:
    """Get an authenticated Razorpay client."""
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        raise ValueError("RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET must be set in .env")
    return razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


def verify_connection() -> dict:
    """Verify Razorpay API keys work by fetching account info."""
    client = get_client()
    last_error = None
    for attempt in range(3):
        try:
            result = client.payment.all({"count": 1})
            return {
                "status": "connected",
                "key_id": RAZORPAY_KEY_ID,
                "mode": "test" if "test" in RAZORPAY_KEY_ID else "live",
                "items_count": result.get("count", 0),
            }
        except Exception as e:
            last_error = e
            import time
            time.sleep(1)

    return {
        "status": "error",
        "key_id": RAZORPAY_KEY_ID,
        "error": str(last_error),
    }


def create_test_order(amount_inr: float, receipt: str, notes: dict = None) -> dict:
    """
    Create a Razorpay Order in test mode.
    Amount is in INR (will be converted to paise internally).
    """
    client = get_client()
    order_data = {
        "amount": int(amount_inr * 100),  # Razorpay expects paise
        "currency": "INR",
        "receipt": receipt,
        "notes": notes or {},
    }
    return client.order.create(data=order_data)


def create_payment_link(
    amount_inr: float,
    customer_name: str,
    customer_phone: str,
    description: str,
    receipt: str,
) -> dict:
    """
    Create a Razorpay Payment Link (test mode).
    This generates a real URL the customer can click to pay.
    """
    client = get_client()
    link_data = {
        "amount": int(amount_inr * 100),
        "currency": "INR",
        "description": description,
        "customer": {
            "name": customer_name,
            "contact": customer_phone,
        },
        "notify": {"sms": False, "email": False},  # Don't spam in test mode
        "reminder_enable": False,
        "notes": {
            "source": "ai_recovery_agent",
            "receipt": receipt,
        },
        "callback_url": "http://localhost:8000/api/webhook/razorpay/redirect",
        "callback_method": "get",
    }
    return client.payment_link.create(data=link_data)


def fetch_payment(payment_id: str) -> dict:
    """Fetch a specific payment by ID."""
    client = get_client()
    return client.payment.fetch(payment_id)


def fetch_order(order_id: str) -> dict:
    """Fetch a specific order by ID."""
    client = get_client()
    return client.order.fetch(order_id)


def verify_webhook_signature(body: str, signature: str, secret: str = None) -> bool:
    """
    Verify that a webhook request actually came from Razorpay.
    Uses HMAC SHA256 comparison.
    """
    if secret is None:
        secret = RAZORPAY_KEY_SECRET

    expected = hmac.HMAC(
        key=secret.encode("utf-8"),
        msg=body.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
