"""Demo 1 — a BASIC single ADK agent with tools.

Talk point: model = ~10% of the work. The agent = model + instructions + TOOLS.
Watch the trace panel in `adk web`: every answer that needs real-world data
fires a tool call. That tool boundary is the whole game.

Self-contained: tools return canned data, so it works offline / on any laptop.
"""
import os
from datetime import datetime, timedelta, timezone

from google.adk.agents import Agent

TEXT_MODEL = os.getenv("TEXT_MODEL", "gemini-2.5-flash")

# --- Tools: plain Python functions. ADK reads the signature + docstring to
#     build the tool schema the model sees. Type hints + docstrings matter. ---

_WEATHER = {
    "riyadh": "Sunny, 41°C, light wind.",
    "dammam": "Hazy, 43°C, humid.",
    "jeddah": "Humid, 38°C, sea breeze.",
    "london": "Overcast, 14°C, drizzle.",
}


def get_weather(city: str) -> dict:
    """Return the current weather for a city.

    Args:
        city: City name, e.g. "Riyadh".

    Returns:
        dict with status and a human-readable report.
    """
    report = _WEATHER.get(city.strip().lower())
    if report:
        return {"status": "ok", "city": city, "report": report}
    return {"status": "error", "message": f"No weather station for '{city}'."}


# City -> UTC offset (hours). Keeps the demo dependency-free.
_TZ = {"riyadh": 3, "dammam": 3, "jeddah": 3, "london": 1, "new york": -4}


def get_current_time(city: str) -> dict:
    """Return the current local time for a city.

    Args:
        city: City name, e.g. "Riyadh".

    Returns:
        dict with status and the local time string.
    """
    offset = _TZ.get(city.strip().lower())
    if offset is None:
        return {"status": "error", "message": f"Unknown timezone for '{city}'."}
    now = datetime.now(timezone.utc) + timedelta(hours=offset)
    return {
        "status": "ok",
        "city": city,
        "time": now.strftime("%Y-%m-%d %H:%M") + f" (UTC{offset:+d})",
    }


root_agent = Agent(
    name="demo1_assistant",
    model=TEXT_MODEL,
    description="A basic assistant that reports weather and local time.",
    instruction=(
        "You are a friendly assistant for GDG Cloud Riyadh attendees. "
        "Use the get_weather and get_current_time tools to answer questions "
        "about weather and time. Always call a tool for those — never guess. "
        "Be concise. If a tool returns an error, say so plainly."
    ),
    tools=[get_weather, get_current_time],
)
