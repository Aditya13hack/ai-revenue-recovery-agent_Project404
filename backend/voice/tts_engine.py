"""
Voice conversation script generator and TTS engine.

Generates pre-recorded demo calls from real system outputs:
  1. Takes a case + conversation turns + control plane decisions
  2. Generates Hinglish dialogue scripts
  3. Converts to audio using edge-tts (Microsoft Edge free TTS)
"""

import asyncio
import os
from pathlib import Path
from typing import List

import edge_tts

from backend.config import TTS_VOICE_AGENT, TTS_VOICE_CUSTOMER, AUDIO_OUTPUT_DIR
from backend.reasoning.schemas import ConversationTurn


async def generate_speech(text: str, voice: str, output_path: str) -> None:
    """Generate speech audio from text using edge-tts."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


async def generate_conversation_audio(
    case_id: str,
    turns: List[ConversationTurn],
    output_dir: Path = None,
) -> str:
    """
    Generate a merged audio file for a full conversation.
    Each turn is generated as a separate audio clip, then they are
    referenced in order for playback.
    """
    if output_dir is None:
        output_dir = AUDIO_OUTPUT_DIR

    output_dir.mkdir(parents=True, exist_ok=True)

    audio_files = []
    for i, turn in enumerate(turns):
        voice = TTS_VOICE_AGENT if turn.speaker == "agent" else TTS_VOICE_CUSTOMER
        filename = f"{case_id}_turn_{i:02d}_{turn.speaker}.mp3"
        filepath = output_dir / filename

        await generate_speech(turn.text, voice, str(filepath))
        audio_files.append(str(filepath))

    # Create a simple manifest file listing all turn audio files in order
    manifest_path = output_dir / f"{case_id}_manifest.txt"
    with open(manifest_path, "w", encoding="utf-8") as f:
        for audio_file in audio_files:
            f.write(audio_file + "\n")

    return str(manifest_path)


# Pre-built demo conversation scripts
DEMO_CONVERSATIONS = {
    "happy_path": [
        ConversationTurn(speaker="agent", text="Namaste! Main PayEase company se bol rahi hoon. Kya main Aarav Sharma ji se baat kar sakti hoon?", language="hinglish"),
        ConversationTurn(speaker="customer", text="Haan ji, main Aarav bol raha hoon. Boliye.", language="hinglish"),
        ConversationTurn(speaker="agent", text="Aarav ji, aapka UPI Autopay payment of rupees paanch hazaar chhe sau pending hai. Bank server timeout ki wajah se payment fail ho gaya tha. Kya aap abhi retry karna chahenge?", language="hinglish"),
        ConversationTurn(speaker="customer", text="Oh achha, haan mujhe yaad hai. Haan main abhi retry kar deta hoon.", language="hinglish"),
        ConversationTurn(speaker="agent", text="Bahut badhiya Aarav ji! Main retry initiate kar rahi hoon. Aapko ek notification aayega. Kya aur koi help chahiye?", language="hinglish"),
        ConversationTurn(speaker="customer", text="Nahi, bas itna hi. Thank you.", language="hinglish"),
        ConversationTurn(speaker="agent", text="Thank you Aarav ji. Aapka din shubh rahe!", language="hinglish"),
    ],
    "modify_moment": [
        ConversationTurn(speaker="agent", text="Namaste Priya ji! Main PayEase se call kar rahi hoon. Aapka EMI payment of rupees baara hazaar pending hai.", language="hinglish"),
        ConversationTurn(speaker="customer", text="Haan, mujhe pata hai. Abhi mere paas itne paise nahi hain. Kuch discount mil sakta hai kya?", language="hinglish"),
        ConversationTurn(speaker="agent", text="Main samajh sakti hoon Priya ji. Main aapke liye discount check karti hoon... Humari policy ke hisaab se, hum aapko maximum pandrah percent discount de sakte hain. Yaani aapko rupees das hazaar do sau hi pay karna hoga. Kya yeh theek rahega?", language="hinglish"),
        ConversationTurn(speaker="customer", text="Pandrah percent? Hmm thoda aur ho sakta hai kya? Bees percent?", language="hinglish"),
        ConversationTurn(speaker="agent", text="Priya ji, maximum allowed discount pandrah percent hai. Isse zyada hum offer nahi kar sakte. Lekin hum aapko teen din ka extension bhi de sakte hain. Payment kal tak kar dein toh pandrah percent discount apply ho jayega.", language="hinglish"),
        ConversationTurn(speaker="customer", text="Achha theek hai, kal tak kar dungi with fifteen percent discount. Done.", language="hinglish"),
        ConversationTurn(speaker="agent", text="Perfect Priya ji! Main yeh promise-to-pay record kar leti hoon. Kal tak payment karne par pandrah percent discount milega. Thank you!", language="hinglish"),
    ],
    "escalate_block": [
        ConversationTurn(speaker="agent", text="Namaste Rahul ji! Main PayEase se bol rahi hoon. Aapka subscription payment pending hai.", language="hinglish"),
        ConversationTurn(speaker="customer", text="Haan dekhiye, maine pehle bhi bola tha ki mujhe yeh service cancel karni hai. Main pay nahi karna chahta.", language="hinglish"),
        ConversationTurn(speaker="agent", text="Samajh gayi Rahul ji. Kya main aapko koi alternative offer karun? Hum extension ya discount provide kar sakte hain.", language="hinglish"),
        ConversationTurn(speaker="customer", text="Nahi nahi, mujhe kuch nahi chahiye. Please aage se mujhe call mat karo.", language="hinglish"),
        ConversationTurn(speaker="agent", text="Bilkul Rahul ji, main aapki request note kar leti hoon. Hum aapko aage se contact nahi karenge. Agar kabhi zaroorat ho toh aap humse direct reach out kar sakte hain. Dhanyavaad!", language="hinglish"),
    ],
    "budget_exhaustion": [
        ConversationTurn(speaker="agent", text="Namaste Kavya ji! Main PayEase recovery team se hoon. Aapka EMI payment of rupees saat hazaar pending hai.", language="hinglish"),
        ConversationTurn(speaker="customer", text="Haan, insufficient balance ki wajah se fail hua tha. Koi discount milega kya?", language="hinglish"),
        ConversationTurn(speaker="agent", text="Kavya ji, main check karti hoon... Is samay hamare recovery budget mein incentives available nahi hain. Lekin hum aapko saat din ka extension de sakte hain bina kisi extra charge ke. Kya aap next week tak payment kar sakti hain?", language="hinglish"),
        ConversationTurn(speaker="customer", text="Achha discount nahi hai... Theek hai, next Monday tak kar dungi.", language="hinglish"),
        ConversationTurn(speaker="agent", text="Thank you Kavya ji! Maine aapka promise-to-pay next Monday ke liye record kar liya hai. Payment reminder bhi aa jayega. Dhanyavaad!", language="hinglish"),
    ],
}


async def generate_all_demo_audio():
    """Generate audio for all pre-built demo conversations."""
    output_dir = AUDIO_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    for scenario_name, turns in DEMO_CONVERSATIONS.items():
        print(f"  Generating audio for: {scenario_name}")
        case_id = f"DEMO-{scenario_name.upper()}"
        await generate_conversation_audio(case_id, turns, output_dir)
        print(f"    -> Generated {len(turns)} audio clips")


def generate_demo_calls():
    """Synchronous wrapper for generating all demo audio."""
    print("\n=== Generating Demo Voice Recordings ===\n")
    asyncio.run(generate_all_demo_audio())
    print(f"\n=== Audio files saved to: {AUDIO_OUTPUT_DIR} ===\n")


if __name__ == "__main__":
    generate_demo_calls()
