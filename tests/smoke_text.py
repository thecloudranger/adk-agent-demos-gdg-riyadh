"""Text smoke test — proves both agents run and fire tools on real Vertex AI.

Run (from repo root, venv active, .env filled):
    python tests/smoke_text.py

Exits non-zero if either agent fails to call its tools or produce a reply.
"""
import asyncio
import os
import sys

# Make `agents` importable and load .env before importing agents.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai import types  # noqa: E402

from agents.demo1_assistant.agent import root_agent as demo1  # noqa: E402
from agents.demo2_concierge.agent import root_agent as demo2  # noqa: E402


async def run(agent, prompt):
    runner = InMemoryRunner(agent=agent, app_name="smoke")
    session = await runner.session_service.create_session(
        app_name="smoke", user_id="u"
    )
    tool_calls, final = [], ""
    async for event in runner.run_async(
        user_id="u",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=prompt)]),
    ):
        for part in (event.content.parts if event.content else []) or []:
            if part.function_call:
                tool_calls.append(part.function_call.name)
        if event.is_final_response() and event.content:
            final = "".join(p.text or "" for p in event.content.parts)
    return tool_calls, final.strip()


async def main():
    print(f"model text={os.getenv('TEXT_MODEL')} voice={os.getenv('VOICE_MODEL')}")
    ok = True

    print("\n[Demo 1] 'Weather and current time in Riyadh?'")
    calls, final = await run(demo1, "What's the weather and current time in Riyadh?")
    print("  tool calls:", calls)
    print("  reply:", final[:200])
    if not calls or not final:
        ok = False
        print("  FAIL: expected tool calls + reply")

    print("\n[Demo 2] 'Flight from Dubai to Riyadh and a hotel under 700 SAR?'")
    calls, final = await run(
        demo2, "Find a flight from Dubai to Riyadh and a hotel under 700 SAR."
    )
    print("  tool/agent calls:", calls)
    print("  reply:", final[:300])
    if not calls or not final:
        ok = False
        print("  FAIL: expected sub-agent tool calls + reply")

    print("\n==>", "ALL PASS" if ok else "FAILURES")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
