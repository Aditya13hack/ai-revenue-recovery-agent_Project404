# AI Revenue Recovery Agent
## Razorpay AI Buildathon 2026 | Track 03 - AI Revenue Recovery

> **AI proposes. Control Plane decides. System executes.**

An AI-powered revenue recovery agent for failed payments (UPI Autopay, EMIs, subscriptions) with a **deterministic control plane** ensuring every action is bounded, auditable, and explainable.

---

## Key Differentiator

This is NOT a simple calling bot. It is a complete **recovery control loop** with two systems that must never be merged:

1. **Reasoning Layer (LLM)** - Proposes what action to take
2. **Control Plane (Pure Python)** - Decides what is *allowed* to happen

Every LLM proposal passes through the control plane before execution. The control plane is deterministic, auditable, and never depends on the AI.

## Architecture

```
Failed Payment → Detection → Diagnosis → Triage → LLM Reasoning → Control Plane → Execution → Measurement
                                                        ↓
                                              EXECUTE / MODIFY / ESCALATE-BLOCK
```

## Tech Stack (Zero Cost)

| Component | Technology |
|-----------|-----------|
| LLM | Groq free tier (Llama 3.1 8B) |
| Orchestration | LangGraph |
| Backend | FastAPI + SQLite |
| Frontend | React + Vite + Tailwind CSS |
| Voice | edge-tts (Microsoft Edge TTS) |
| Payments | Razorpay Test Mode |
| **Total Cost** | **Rs.0** |

## Quick Start

### 1. Clone & Setup
```bash
git clone <repo-url>
cd Project404

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
copy .env.example .env
```
Edit `.env` and add your API keys:
- **GROQ_API_KEY**: Get from https://console.groq.com/keys
- **RAZORPAY_KEY_ID** & **RAZORPAY_KEY_SECRET**: Get from Razorpay Dashboard (Test Mode)

### 3. Generate Dataset
```bash
python -m scripts.generate_dataset
```
Generates 200 synthetic failed-payment cases with realistic distributions.

### 4. Run Recovery Batch
```bash
python -m scripts.run_batch           # Process all 200 cases
python -m scripts.run_batch --limit 10  # Process 10 cases (quick test)
```

### 5. Generate Demo Voice Recordings
```bash
python -m scripts.generate_voice
```

### 6. Start Backend Server
```bash
python -m backend.main
# or: uvicorn backend.main:app --reload
```
API available at http://localhost:8000 | Docs at http://localhost:8000/docs

### 7. Start Frontend
```bash
cd frontend
npm install
npm run dev
```
Dashboard available at http://localhost:5173

## Project Structure

```
Project404/
├── backend/
│   ├── main.py                     # FastAPI server
│   ├── config.py                   # Centralized configuration
│   ├── database/                   # SQLAlchemy models & connection
│   ├── dataset/                    # Synthetic data generator
│   ├── triage/                     # Detection & channel routing
│   ├── reasoning/                  # LLM agent & prompts
│   ├── control_plane/              # Policy engine (CORE DIFFERENTIATOR)
│   │   ├── policy_engine.py        # EXECUTE/MODIFY/ESCALATE-BLOCK logic
│   │   ├── budget_tracker.py       # Campaign budget tracking
│   │   ├── stopping_rules.py       # All 8 stopping rules
│   │   └── rules_config.py         # Merchant policy limits
│   ├── orchestrator/               # LangGraph pipeline
│   ├── voice/                      # TTS engine & demo recordings
│   ├── audit/                      # Timeline & event logging
│   └── metrics/                    # Batch metrics calculator
├── frontend/                       # React + Tailwind dashboard
├── scripts/                        # CLI tools
└── tests/                          # Unit & integration tests
```

## Control Plane Decision Framework

| Decision | Meaning | Example |
|----------|---------|---------|
| **EXECUTE** | Within all limits | AI proposes 8% discount, cap is 15% -> executed |
| **MODIFY** | Exceeds a limit, safely adjusted | AI proposes 20% discount -> capped to 15% |
| **ESCALATE** | Hard limit, needs human | Customer refused twice -> human queue |
| **BLOCK** | Cannot proceed | "Don't call me again" -> permanent stop |

## Stopping Rules

| Rule | Limit | Scope |
|------|-------|-------|
| Max contact attempts | 3 | Per case |
| Max payment retries | 2 | Per case |
| Max extension period | 7 days | Per case |
| Max discount | 15% | Per case |
| Human escalation | After 2 refusals | Per case |
| Do-not-contact | Immediate stop | Per case |
| Budget exhaustion | Rs.50,000 cap | Campaign |
| Sensitive data | Never permitted | Always |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/metrics` | Aggregate batch metrics |
| `GET /api/cases` | Filterable case list |
| `GET /api/cases/{id}` | Case detail |
| `GET /api/cases/{id}/timeline` | Full audit trail |
| `GET /api/budget` | Budget state & transactions |
| `GET /api/decisions` | Control plane decisions |
| `GET /api/cases/{id}/audio` | Voice recording playback |

## License

Built for Razorpay AI Buildathon 2026.
