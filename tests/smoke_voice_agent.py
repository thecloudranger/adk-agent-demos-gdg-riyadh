"""End-to-end Live smoke test for Demo 2 through ADK's run_live path.

Proves the FULL wow-demo pipeline headlessly (no mic):
  native-audio root  --live-->  AgentTool sub-agent  -->  audio spoken back.

Run:
    GOOGLE_CLOUD_LOCATION=us-central1 \
    VOICE_MODEL=gemini-live-2.5-flash-native-audio \
    TEXT_MODEL=gemini-2.5-flash \
    python tests/smoke_voice_agent.py
"""
import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
# Force the voice config regardless of .env's text block.
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
os.environ.setdefault("VOICE_MODEL", "gemini-live-2.5-flash-native-audio")
os.environ.setdefault("TEXT_MODEL", "gemini-2.5-flash")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from google.adk.agents.live_request_queue import LiveRequestQueue  # noqa: E402
from google.adk.agents.run_config import RunConfig  # noqa: E402
from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai import types  # noqa: E402

from agents.demo2_concierge.agent import root_agent as demo2  # noqa: E402


async def main():
    print(f"Live agent: root={demo2.model} tools={[t.name for t in demo2.tools]}")
    runner = InMemoryRunner(agent=demo2, app_name="voice")
    session = await runner.session_service.create_session(app_name="voice", user_id="u")

    queue = LiveRequestQueue()
    queue.send_content(
        content=types.Content(
            role="user",
            parts=[types.Part(text="Find me a flight from Dubai to Riyadh.")],
        )
    )

    tool_calls, audio_bytes = [], 0
    run_config = RunConfig(response_modalities=["AUDIO"])

    done = asyncio.Event()

    async def drive():
        nonlocal audio_bytes
        async for event in runner.run_live(
            session=session, live_request_queue=queue, run_config=run_config
        ):
            for part in (event.content.parts if event.content else []) or []:
                if part.function_call:
                    tool_calls.append(part.function_call.name)
                if part.inline_data and part.inline_data.data:
                    audio_bytes += len(part.inline_data.data)
            # Proof collected (delegation fired + audio streamed back): signal
            # and let the driving task be cancelled cleanly below.
            if tool_calls and audio_bytes > 0:
                done.set()
                return

    task = asyncio.create_task(drive())
    try:
        await asyncio.wait_for(done.wait(), timeout=90)
    except asyncio.TimeoutError:
        pass
    task.cancel()
    try:
        await task
    except (asyncio.CancelledError, Exception):
        pass
    queue.close()

    print(f"  tool/agent calls: {tool_calls}")
    print(f"  audio bytes spoken back: {audio_bytes}")
    ok = bool(tool_calls) and audio_bytes > 0
    print("==>", "VOICE-AGENT PASS" if ok else "VOICE-AGENT FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
