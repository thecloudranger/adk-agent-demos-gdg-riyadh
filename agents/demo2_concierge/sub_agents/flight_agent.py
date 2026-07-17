"""Flight specialist sub-agent. Runs as a text agent, wrapped as a tool by root."""
import os

from google.adk.agents import Agent

TEXT_MODEL = os.getenv("TEXT_MODEL", "gemini-2.5-flash")

_FLIGHTS = {
    ("dubai", "riyadh"): [
        {"airline": "Saudia", "flight": "SV553", "dep": "08:15", "arr": "09:35", "sar": 620},
        {"airline": "flynas", "flight": "XY122", "dep": "14:40", "arr": "16:00", "sar": 480},
    ],
    ("cairo", "riyadh"): [
        {"airline": "Saudia", "flight": "SV302", "dep": "02:10", "arr": "05:55", "sar": 910},
    ],
    ("london", "riyadh"): [
        {"airline": "Saudia", "flight": "SV116", "dep": "09:30", "arr": "18:20", "sar": 2450},
        {"airline": "BA", "flight": "BA131", "dep": "20:15", "arr": "05:05", "sar": 2610},
    ],
}


def search_flights(origin: str, destination: str) -> dict:
    """Search available flights between two cities.

    Args:
        origin: Departure city, e.g. "Dubai".
        destination: Arrival city, e.g. "Riyadh".

    Returns:
        dict with a list of flight options (airline, flight no., times, price in SAR).
    """
    key = (origin.strip().lower(), destination.strip().lower())
    options = _FLIGHTS.get(key)
    if not options:
        return {
            "status": "none",
            "message": f"No sample flights {origin}->{destination}. "
            "Try Dubai, Cairo, or London to Riyadh.",
        }
    return {"status": "ok", "origin": origin, "destination": destination, "options": options}


flight_agent = Agent(
    name="flight_agent",
    model=TEXT_MODEL,
    description="Finds flights between cities and reports options with prices.",
    instruction=(
        "You are a flight specialist. Use search_flights to find options. "
        "Report the best 1-2 by price and time, in one short sentence each. "
        "Prices are in Saudi Riyal (SAR)."
    ),
    tools=[search_flights],
)
