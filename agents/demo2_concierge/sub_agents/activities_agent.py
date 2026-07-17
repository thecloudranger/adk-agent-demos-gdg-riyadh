"""Activities / things-to-do specialist sub-agent."""
import os

from google.adk.agents import Agent

TEXT_MODEL = os.getenv("TEXT_MODEL", "gemini-2.5-flash")

_ACTIVITIES = {
    "riyadh": [
        {"name": "Diriyah / At-Turaif (UNESCO)", "type": "heritage", "hours": "4-6pm"},
        {"name": "Edge of the World day trip", "type": "outdoor", "hours": "full day"},
        {"name": "Kingdom Centre Sky Bridge", "type": "views", "hours": "evening"},
        {"name": "Boulevard World", "type": "entertainment", "hours": "evening"},
        {"name": "National Museum of Saudi Arabia", "type": "culture", "hours": "10am-2pm"},
    ],
    "jeddah": [
        {"name": "Al-Balad historic district", "type": "heritage", "hours": "afternoon"},
        {"name": "Jeddah Corniche + King Fahd Fountain", "type": "outdoor", "hours": "evening"},
    ],
}


def suggest_activities(city: str, interest: str = "any") -> dict:
    """Suggest things to do in a city, optionally filtered by interest.

    Args:
        city: City name, e.g. "Riyadh".
        interest: One of heritage, outdoor, culture, entertainment, views, or "any".

    Returns:
        dict with a list of suggested activities.
    """
    acts = _ACTIVITIES.get(city.strip().lower())
    if not acts:
        return {"status": "none", "message": f"No suggestions for '{city}'. Try Riyadh or Jeddah."}
    if interest.strip().lower() not in ("any", ""):
        filtered = [a for a in acts if a["type"] == interest.strip().lower()]
        acts = filtered or acts
    return {"status": "ok", "city": city, "suggestions": acts}


activities_agent = Agent(
    name="activities_agent",
    model=TEXT_MODEL,
    description="Suggests things to do and see in a city.",
    instruction=(
        "You are a local activities guide. Use suggest_activities. Recommend 2-3 "
        "spots, each in one short sentence with the best time to go. "
        "Lean into Saudi heritage and outdoors when relevant."
    ),
    tools=[suggest_activities],
)
