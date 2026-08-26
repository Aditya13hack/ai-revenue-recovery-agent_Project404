"""
CLI script to generate demo voice recordings.

Usage:
    python -m scripts.generate_voice
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.voice.tts_engine import generate_demo_calls

if __name__ == "__main__":
    generate_demo_calls()
