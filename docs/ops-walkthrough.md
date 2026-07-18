# Console ops walkthrough (after the demo)

Two ops surfaces. The **Agent Engine** one matches the deck's Scale/Govern/Optimize
slides; the **Cloud Run** one is the real infra your Cloud Run demos run on.

Project: `YOUR_PROJECT_ID` · region `us-central1`.

---

## A. Agent Platform — Agent Engine  (matches the deck)

We deploy the concierge to **Agent Engine** (`deploy/agent_engine_deploy.py`,
service `gdg-concierge-ops`, tracing on) specifically so these pages have data.
Run a few conversations first (the deploy script's follow-up seeds sessions/traces).

Console → **Agent Platform** (Vertex AI). Left nav mirrors the deck's four pillars:

| Deck pillar | Console page | What to point at |
|---|---|---|
| **Scale** | Agents → **Deployments** | The `gdg-concierge-ops` row on Agent Runtime — "this is the managed runtime, not a VM we manage." |
| Scale | **Sessions** | Per-user conversation state — short-term memory, no custom DB. |
| Scale | **Memory Bank** | Long-term memory store (empty unless enabled) — mention as the persistence layer. |
| **Optimize** | Deployment → **Traces** (Session view) | Per-session ops table: avg duration, agent invocations, **model calls, tool calls, token usage**. Then click a session → **Graph** → the multi-agent DAG: `invoke_agent concierge → call_llm → execute_tool flight_agent → invoke_agent flight_agent → execute_tool search_flights`. Toggle **Timeline** for the waterfall. The deck's "Agent observability" slide, live. |
| Optimize | **Topology** tab | The whole multi-agent graph in one view. |
| Optimize | **Evaluation** | Run/inspect evals — multi-turn autoraters. |
| — | **Playground** tab | Run the agent live *inside the console* (no local tools). |

> Traces land in the **Agent Platform trace store** (this Traces tab), NOT the
> classic Cloud Trace `traces.list` API — don't go looking there.
>
> Before the talk, click **"Enable prompt-response logging"** on the Traces tab.
> By default spans capture only a skeleton; enabling it shows the actual prompts +
> tool-call params inside each span — much better for a walkthrough.
| **Govern** | **Agent Registry** | Register the agent → central catalog of agents/MCP servers/endpoints. |
| Govern | **Agent Identity** | The auto-assigned **SPIFFE** identity for the deployed agent (deck's "Agent Identity" slide). |
| Govern | **Policies / Gateways / Security** | Model Armor, tool-use policies — show the pages even if unconfigured. |
| **Build** | **ADK**, **Agent Garden**, **MCP Servers** | Where the agent came from; Agent Garden sample library. |

**The single best click:** Deployments → `gdg-concierge-ops` → **Observability** →
open a trace → switch to the **Graph** view. That's the multi-agent topology the
deck sells, with your own agent's data.

---

## B. Cloud Run ops  (where the demo actually runs)

Console → **Cloud Run** → `gdg-agent-demos` (and `gdg-voice-concierge`, `gdg-agent-skin`):

- **Metrics** — request count, latency p50/p95/p99, container instances, CPU/mem,
  concurrency. Show a spike right after the live demo.
- **Logs** — per-request logs + agent stdout (tool calls, model calls).
- **Revisions** — each deploy = an immutable revision; traffic splitting / rollback.
- **YAML / Details** — the env vars (model, location), the runtime service account.

Supporting pages:
- **Cloud Build → History** — the `gcloud run deploy --source` builds (Dockerfile → image).
- **Artifact Registry → `cloud-run-source-deploy`** — the built container images.
- **IAM** — the Cloud Run runtime SA that calls Vertex (least-privilege story).

---

## Talking point: two runtimes, one ADK

Same ADK agent code runs on **Cloud Run** (what you demoed — full control, WebSocket
voice) and **Agent Engine** (managed runtime + built-in Sessions/Memory/Observability/
Eval/Identity). "Local = cloud": the agent you ran in `adk web` is the same object
deployed both ways. That's the portability story.

## Cleanup
```bash
# Agent Engine
python -c "import vertexai; from vertexai import agent_engines; \
vertexai.init(project='YOUR_PROJECT_ID', location='us-central1'); \
agent_engines.get(open('deploy/.engine_id').read().strip()).delete(force=True)"
# Cloud Run
gcloud run services delete gdg-agent-demos gdg-voice-concierge gdg-agent-skin \
  --region us-central1 --project YOUR_PROJECT_ID
```
