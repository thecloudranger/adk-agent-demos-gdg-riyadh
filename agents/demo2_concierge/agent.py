"""Demo 2 — the WOW: a VOICE-driven MULTI-AGENT trip concierge.

Architecture (robust for voice):
  root_agent  (VOICE_MODEL, a Gemini Live model — does the mic/audio)
    ├─ flight_agent      \\
    ├─ hotel_agent        > each a plain text agent, exposed to root as an AgentTool
    └─ activities_agent  /

Only the ROOT needs a Live model. Sub-agents stay simple text agents wrapped as
tools, so delegation is reliable under bidi audio streaming. In `adk web` the
trace panel shows root -> flight_agent -> search_flights etc. as you speak.

Talk point: one agent, or a team? This is the "team + delegation" layer of the
agent stack — the orchestration row.
"""
import os

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .sub_agents import activities_agent, flight_agent, hotel_agent

# Root drives the mic, so it needs a Live-capable model. Falls back to a text
# model if VOICE_MODEL is unset (e.g. when demoing typed-only).
ROOT_MODEL = os.getenv("VOICE_MODEL") or os.getenv("TEXT_MODEL", "gemini-2.5-flash")

root_agent = Agent(
    name="concierge",
    model=ROOT_MODEL,
    description="A trip concierge that coordinates flight, hotel, and activities specialists.",
    instruction=(
        "You are a warm, concise trip concierge for travelers coming to Saudi Arabia. "
        "You do NOT answer flight, hotel, or activity questions yourself — you delegate:\n"
        "  - Flights  -> call the flight_agent tool.\n"
        "  - Hotels   -> call the hotel_agent tool.\n"
        "  - Things to do -> call the activities_agent tool.\n"
        "For a full trip request, call the relevant specialists in turn, then give a "
        "short combined plan. Ask a brief clarifying question only if you must "
        "(e.g. origin city or budget). Keep spoken replies short and natural."
    ),
    tools=[
        AgentTool(agent=flight_agent),
        AgentTool(agent=hotel_agent),
        AgentTool(agent=activities_agent),
    ],
)
