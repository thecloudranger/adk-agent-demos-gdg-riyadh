# Region & sovereignty notes (for the Dammam / KSA slides)

Verified against project `YOUR_PROJECT_ID` on 2026-07-17. Re-check the live console
the morning of the talk — availability moves.

## What we actually use

| Demo | Vertex location | Model | Why |
|------|-----------------|-------|-----|
| 1 (basic) + 2 typed | `global` | `gemini-3.5-flash` | Newest model is **global-only** (404 in us-central1). |
| 2 voice | `us-central1` | `gemini-live-2.5-flash-native-audio` | Live API is **region-only**; us-central1 verified. |

## me-central2 (Dammam) reality

Confirmed by the deck's own "Dammam — what runs in me-central2" slide and our tests:

- **In-region:** NVIDIA L4 / g2 machines, Model Garden self-deploy (vLLM),
  Vertex Prediction endpoints, Cloud Run / GKE.
- **NOT in-region:** frontier Gemini, Chirp 3 HD TTS, Vertex AI Search / Agent
  Search, Agent Engine / Agent Runtime, **and the Live API**.

So a *fully in-region* voice agent isn't possible today. Honest framing for the
talk: **data residency + customer-controlled keys + a local operating partner
(CNTXT / Assured Workloads)** — not "sovereign frontier AI."

## Sovereign option (if asked)

Capable Arabic open models on in-region L4 GPUs (from the deck):
`Gemma 3`, `Fanar-1-9B (QCRI)`, `Jais-2-8B (Inception)`, `ALLaM-2-7B (SDAIA)` —
self-deployed via Model Garden / vLLM in me-central2. Different demo, same ADK
`Agent(model=...)` shape (point ADK at a self-deployed endpoint).

## If you want the demos closer to region

- Voice: no in-region option today — keep us-central1, or use a self-deployed
  open model for a text-only in-region agent.
- Text: `gemini-2.5-flash` **is** served in us-central1 (works there); only
  `gemini-3.5-flash` forced us to `global`. Swap the model to stay regional if the
  sovereignty story matters more than "newest".
