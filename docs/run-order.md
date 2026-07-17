# On-stage cheat-sheet

Two terminals ready, venv active in both. Browser at `http://localhost:8000`.

## Before you walk on
```bash
cd adk-agent-demos-gdg-riyadh && source .venv/bin/activate
# sanity (optional, ~20s):
python tests/smoke_text.py
```
Have the deployed URL open in a tab too:
`https://gdg-agent-demos-YOUR_PROJECT_NUMBER.us-central1.run.app`

---

## Demo 1 — basic agent (2–3 min)
**Terminal A** (default .env = global + gemini-3.5-flash):
```bash
adk web agents
```
1. Pick **demo1_assistant**.
2. Ask: *"What's the weather and current time in Riyadh?"*
3. **Point at the trace panel** → two tool calls (`get_weather`, `get_current_time`).
   Line: *"The model didn't know the weather — it called a tool. That tool
   boundary is the whole game."*
4. Flip to the **Cloud Run URL** tab, ask the same thing.
   Line: *"Same agent, deployed on Google Cloud, running the newest Gemini 3.5 Flash."*

## Demo 2 — voice + multi-agent (4–5 min)  ← the wow
Stop Terminal A (Ctrl-C). **Terminal B**:
```bash
export GOOGLE_CLOUD_LOCATION=us-central1
export TEXT_MODEL=gemini-2.5-flash
export VOICE_MODEL=gemini-live-2.5-flash-native-audio
adk web agents
```
1. Pick **demo2_concierge**. Click the **🎤 mic**.
2. Say: *"I'm flying from Dubai to Riyadh — find me a flight and something to do."*
3. **Point at the trace** → `concierge → flight_agent → search_flights`, then
   `→ activities_agent`. It **speaks** the plan back.
   Line: *"One agent, or a team? This is a coordinator delegating to specialists —
   and you're talking to it. Native audio in, native audio out."*
4. Follow-up by voice: *"Add a hotel under 700 riyal."* → `hotel_agent` fires.

---

## If something breaks (fallbacks)
- **Mic won't connect** → `export SSL_CERT_FILE=$(python -m certifi)` then relaunch.
- **Live/us-central1 hiccups** → drop voice, run demo2 **typed** (still shows
  multi-agent delegation). Unset `VOICE_MODEL`, set `GOOGLE_CLOUD_LOCATION=global`.
- **Wifi dies** → tools return canned data; local `adk web` still runs. Only the
  model call needs network. Worst case, talk over the deployed-URL screenshot.
- **Whole laptop sad** → the Cloud Run URL is independent; demo from there (typed).

## Cleanup after
```bash
gcloud run services delete gdg-agent-demos --region us-central1 --project YOUR_PROJECT_ID
```
