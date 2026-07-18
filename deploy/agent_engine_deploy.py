"""Deploy the concierge (typed, multi-agent) to Vertex AI Agent Engine.

This is the OPS-story deploy: it populates the Agent Platform console pages the
deck shows — Deployments (Agent Runtime), Sessions, Observability → Traces +
multi-agent topology graph, Evaluation, Agent Registry, Agent Identity.

Agent Engine is regional, so this uses gemini-2.5-flash in us-central1 (not the
global-only 3.5-flash). Voice stays on Cloud Run — Agent Engine is req/response,
not bidi audio.

Run:  python deploy/agent_engine_deploy.py
Prints the ReasoningEngine resource name; also writes it to deploy/.engine_id
"""
import os
import sys

# Force the text/regional config BEFORE importing the agent (ROOT_MODEL resolves
# from env at import time).
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT", "YOUR_PROJECT_ID")
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
os.environ["TEXT_MODEL"] = "gemini-2.5-flash"
os.environ.pop("VOICE_MODEL", None)  # unset -> concierge root uses TEXT_MODEL

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

from agents.demo2_concierge.agent import root_agent

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
BUCKET = os.getenv("STAGING_BUCKET", f"gs://{PROJECT}-agent-engine-staging")

vertexai.init(project=PROJECT, location="us-central1", staging_bucket=BUCKET)

print(f"Deploying '{root_agent.name}' (model={root_agent.model}) to Agent Engine...")
app = AdkApp(agent=root_agent, enable_tracing=True)  # tracing -> Observability page

remote = agent_engines.create(
    agent_engine=app,
    display_name="gdg-concierge-ops",
    description="ADK trip concierge (coordinator + flight/hotel/activities) — GDG ops demo",
    requirements=["google-cloud-aiplatform[adk,agent_engines]"],
    extra_packages=["agents"],
)

print("\nDEPLOYED:", remote.resource_name)
with open(os.path.join(os.path.dirname(__file__), ".engine_id"), "w") as f:
    f.write(remote.resource_name)
