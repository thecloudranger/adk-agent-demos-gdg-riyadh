# ADK Agent Demos — GDG Cloud Riyadh (Gemini Enterprise Agent Platform)

Two self-contained [ADK](https://adk.dev) agent demos for a talk on **building and
deploying agents on Google Cloud**. Clone → one script → run. No external data,
no BigQuery — reproducible on any laptop.

| # | Demo | What it shows | Surface |
|---|------|---------------|---------|
| 1 | **Basic assistant** | One agent + tools. Watch the trace panel: every answer fires a tool call. | `adk web` + **live Cloud Run URL** |
| 2 | **Voice trip concierge** | A **multi-agent** system (coordinator → flight / hotel / activities sub-agents), driven by **your voice** (Gemini Live, native audio). | `adk web` mic |

> The talk **showcases** these — it does not build them live (that's the follow-up
> session). This repo is the pre-built, tested artifact.

---

## Verified facts (project `YOUR_PROJECT_ID`, 2026-07-17)

Everything below was tested against the real project, not assumed:

- **`gemini-3.5-flash`** (newest available) is served **only on the `global`
  Vertex endpoint** — it 404s in `us-central1`. → text agents use `location=global`.
- **Gemini Live API (voice)** is served **only in a region** we tested at
  **`us-central1`**, with model **`gemini-live-2.5-flash-native-audio`**.
  Not on `global`, not in `me-central2`.
- Native-audio Live model **does fire function tools** (verified) → voice can
  drive multi-agent delegation. It has **no text output** — voice = audio only.
- `me-central2` (Dammam) does **not** serve the Live API / Agent Engine — the two
  demos run in `us-central1` / `global`. Sovereignty stays a slide talking point
  (see [`docs/region-notes.md`](docs/region-notes.md)).

---

## Quickstart

Prereqs: `gcloud` (authed), `uv`, Python ≥3.10, a GCP project with
`aiplatform.googleapis.com` enabled.

```bash
git clone https://github.com/thecloudranger/adk-agent-demos-gdg-riyadh
cd adk-agent-demos-gdg-riyadh

gcloud auth application-default login          # once
./setup.sh                                     # venv + google-adk + API check
source .venv/bin/activate
```

Then pick a mode below.

### Demo 1 + Demo 2 (typed) — newest model, global

```bash
# .env defaults are already set to global + gemini-3.5-flash
adk web agents
# open http://localhost:8000 → pick demo1_assistant → ask:
#   "What's the weather and time in Riyadh?"   (watch the trace: 2 tool calls)
# → pick demo2_concierge → type:
#   "Flight from Dubai to Riyadh and a hotel under 700 SAR"  (watch it delegate)
```

### Demo 2 (VOICE) — the wow

Voice needs the Live model in `us-central1`, so switch env before launching:

```bash
export GOOGLE_CLOUD_LOCATION=us-central1
export TEXT_MODEL=gemini-2.5-flash                        # sub-agents
export VOICE_MODEL=gemini-live-2.5-flash-native-audio     # root, drives the mic
adk web agents
# open http://localhost:8000 → demo2_concierge → click the 🎤 mic → say:
#   "I'm flying from Dubai to Riyadh, find me a flight and something to do."
# It delegates to the sub-agents and speaks the answer back.
```

macOS TLS gotcha: if the mic session fails to connect, run
`export SSL_CERT_FILE=$(python -m certifi)` before `adk web`.

---

## Deployed — two services, two modalities

A Live native-audio model is **audio-only** (rejects typed calls) and lives in a
region; the newest text model is **global-only**. So typed and voice are two
Cloud Run services. Pick the right URL for the modality:

| Service | Model / location | Use | Not |
|---------|------------------|-----|-----|
| `gdg-agent-demos` | gemini-3.5-flash · global | **Type** (demo1 + demo2 typed) | mic won't work |
| `gdg-voice-concierge` | gemini-live-2.5-flash-native-audio · us-central1 | **Mic 📞 only** (demo2 voice) | typing errors |

> Typing into the voice service returns
> *"gemini-live-2.5-flash-native-audio is not supported in the generateContent API"* —
> that's expected. Use the mic there.

Deploy both:

```bash
./deploy/deploy.sh                              # typed service (global / 3.5-flash)
./deploy/deploy.sh --voice                      # voice service (us-central1 / native-audio)
```

## Web app skin (`webapp/`) — "skin on top, then pop the hood"

A branded single-page chat over the same agent API — good for showing a product
UI, then opening the ADK dev view (Events / multi-agent topology / traces) as the
"under the hood". Self-contained HTML, no build.

```bash
python3 -m http.server 3000 --directory webapp
# open http://localhost:3000
#  1. paste your typed-service URL in "Agent API" → Connect
#  2. pick demo2_concierge → click a sample → watch the → flight_agent / → hotel_agent chips
#  3. click "Pop the hood → ADK view" to show the raw ADK UI (topology + traces)
```

The skin talks to the **typed** service (needs CORS — services deploy with
`--allow_origins '*'`). Voice stays the mic in the ADK UI on the voice service.

---

## Verify it works (smoke tests)

```bash
source .venv/bin/activate
python tests/smoke_text.py         # demo1 + demo2 typed fire tools (global/3.5-flash)

GOOGLE_CLOUD_LOCATION=us-central1 VOICE_MODEL=gemini-live-2.5-flash-native-audio \
  python tests/smoke_voice.py      # Live model streams audio back
GOOGLE_CLOUD_LOCATION=us-central1 VOICE_MODEL=gemini-live-2.5-flash-native-audio \
  TEXT_MODEL=gemini-2.5-flash \
  python tests/smoke_voice_agent.py  # full voice→sub-agent→audio pipeline
```

All three print `... PASS`.

---

## Layout

```
agents/
  demo1_assistant/     # single agent: get_weather + get_current_time tools
  demo2_concierge/     # root coordinator
    agent.py           #   root (Live model) with 3 sub-agents as AgentTools
    sub_agents/        #   flight_agent, hotel_agent, activities_agent
tests/                 # 3 real smoke tests (text, voice, voice+agent)
deploy/deploy.sh       # Cloud Run deploy
Dockerfile             # Cloud Run image (serves adk web UI)
docs/                  # run-order cheat-sheet, region/sovereignty notes
setup.sh   .env.example
```

## Architecture note (Demo 2)

Only the **root** needs a Live (voice) model. Sub-agents are plain text agents
wrapped as `AgentTool`s, so delegation is reliable under bidi audio streaming and
sub-agents don't each need a Live model. The `adk web` trace shows
`concierge → flight_agent → search_flights` as you speak.

## Cleanup

```bash
gcloud run services delete gdg-agent-demos --region us-central1 --project YOUR_PROJECT_ID
```

See [`docs/run-order.md`](docs/run-order.md) for the on-stage cheat-sheet.
