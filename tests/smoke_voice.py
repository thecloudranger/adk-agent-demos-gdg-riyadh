"""Voice/Live smoke test — proves the Live model actually opens a bidi audio
session and streams audio back, on real Vertex AI. No mic needed: we send a
text turn and assert we receive audio bytes + a completed turn.

Run:  python tests/smoke_voice.py
"""
import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from google import genai
from google.genai import types

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
MODEL = os.getenv("VOICE_MODEL", "gemini-live-2.5-flash-native-audio")


async def main():
    print(f"Live connect: model={MODEL} location={LOCATION} project={PROJECT}")
    client = genai.Client(vertexai=True, project=PROJECT, location=LOCATION)
    config = types.LiveConnectConfig(response_modalities=["AUDIO"])

    audio_bytes = 0
    turn_done = False
    async with client.aio.live.connect(model=MODEL, config=config) as session:
        await session.send_client_content(
            turns=types.Content(
                role="user",
                parts=[types.Part(text="Say the single word: Riyadh.")],
            )
        )
        async for message in session.receive():
            sc = message.server_content
            if sc and sc.model_turn:
                for part in sc.model_turn.parts:
                    if part.inline_data and part.inline_data.data:
                        audio_bytes += len(part.inline_data.data)
            if sc and sc.turn_complete:
                turn_done = True
                break

    print(f"  received audio bytes: {audio_bytes}")
    print(f"  turn_complete: {turn_done}")
    ok = audio_bytes > 0 and turn_done
    print("==>", "VOICE PASS" if ok else "VOICE FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
