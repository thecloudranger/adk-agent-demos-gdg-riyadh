"""Run a few conversations against the deployed Agent Engine so the console
Sessions + Observability/Traces pages have data to walk through.

Run after agent_engine_deploy.py:  python deploy/seed_sessions.py
"""
import os

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "YOUR_PROJECT_ID")

import vertexai
from vertexai import agent_engines

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
here = os.path.dirname(__file__)
engine_id = open(os.path.join(here, ".engine_id")).read().strip()

vertexai.init(project=PROJECT, location="us-central1")
remote = agent_engines.get(engine_id)
print("engine:", engine_id)

PROMPTS = [
    "Find me a flight from Dubai to Riyadh and a hotel under 700 SAR.",
    "Plan a day in Riyadh — flight from Cairo and something cultural to do.",
    "I land in Riyadh tomorrow, suggest an outdoor activity and a 3-star hotel.",
]

for i, prompt in enumerate(PROMPTS, 1):
    uid = f"ops-demo-{i}"
    session = remote.create_session(user_id=uid)
    sid = session["id"]
    print(f"\n[{i}] session={sid}\n  Q: {prompt}")
    tools, final = [], ""
    for event in remote.stream_query(user_id=uid, session_id=sid, message=prompt):
        for part in (event.get("content", {}) or {}).get("parts", []) or []:
            if "function_call" in part and part["function_call"]:
                tools.append(part["function_call"]["name"])
            if part.get("text"):
                final = part["text"]
    print("  tools:", tools)
    print("  A:", final[:160])

print("\nDone — Sessions + Traces should now show data in the console.")
