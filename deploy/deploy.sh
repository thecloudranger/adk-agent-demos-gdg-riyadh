#!/usr/bin/env bash
# Deploy the agents to Cloud Run (serves the adk web UI at a public URL).
# Reproducible: run from repo root ->  ./deploy/deploy.sh
#
# Note: uses gemini-3.5-flash on the GLOBAL Vertex endpoint (the only place it's
# served). The DEPLOYED URL is the typed demo surface (demo1 + demo2 typed).
# The VOICE demo runs locally in us-central1 — the Live API isn't on global.
set -euo pipefail
cd "$(dirname "$0")/.."

PROJECT="${GOOGLE_CLOUD_PROJECT:-YOUR_PROJECT_ID}"
REGION="${CLOUD_RUN_REGION:-us-central1}"   # Cloud Run service region
SERVICE="${SERVICE_NAME:-gdg-agent-demos}"

echo "Deploying $SERVICE to Cloud Run ($REGION) in $PROJECT ..."
gcloud run deploy "$SERVICE" \
  --source . \
  --project "$PROJECT" \
  --region "$REGION" \
  --allow-unauthenticated \
  --memory 1Gi \
  --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_LOCATION=global,TEXT_MODEL=gemini-3.5-flash"

URL=$(gcloud run services describe "$SERVICE" --project "$PROJECT" --region "$REGION" --format='value(status.url)')
echo "Live URL: $URL"
