"""Hotel specialist sub-agent."""
import os

from google.adk.agents import Agent

TEXT_MODEL = os.getenv("TEXT_MODEL", "gemini-2.5-flash")

_HOTELS = {
    "riyadh": [
        {"name": "Fairmont Riyadh", "area": "Olaya / KAFD", "sar_night": 1100, "stars": 5},
        {"name": "Voco Riyadh", "area": "King Fahd Rd", "sar_night": 650, "stars": 4},
        {"name": "Boudl Al Malaz", "area": "Al Malaz", "sar_night": 320, "stars": 3},
    ],
    "jeddah": [
        {"name": "Rosewood Jeddah", "area": "Corniche", "sar_night": 980, "stars": 5},
    ],
}


def search_hotels(city: str, max_price_sar: int = 100000) -> dict:
    """Search hotels in a city under an optional nightly price cap.

    Args:
        city: City name, e.g. "Riyadh".
        max_price_sar: Max nightly price in SAR. Defaults to no cap.

    Returns:
        dict with matching hotels (name, area, nightly price SAR, stars).
    """
    hotels = _HOTELS.get(city.strip().lower())
    if not hotels:
        return {"status": "none", "message": f"No sample hotels for '{city}'. Try Riyadh or Jeddah."}
    matches = [h for h in hotels if h["sar_night"] <= max_price_sar]
    if not matches:
        return {"status": "none", "message": f"No hotels in {city} under {max_price_sar} SAR."}
    return {"status": "ok", "city": city, "options": matches}


hotel_agent = Agent(
    name="hotel_agent",
    model=TEXT_MODEL,
    description="Finds hotels in a city, optionally within a nightly budget.",
    instruction=(
        "You are a hotel specialist. Use search_hotels. Recommend 1-2 options "
        "matching the traveler's budget if given. Prices are per night in SAR. "
        "Keep it to one short sentence per hotel."
    ),
    tools=[search_hotels],
)
