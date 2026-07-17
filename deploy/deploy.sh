#!/usr/bin/env bash
# Deploy the agents to Cloud Run (serves the adk web UI at a public URL).
# Reproducible: run from repo root.
#   ./deploy/deploy.sh            typed service  (global / gemini-3.5-flash)
#   ./deploy/deploy.sh --voice    voice service  (us-central1 / native-audio Live)
#
# A Live native-audio model is audio-only and region-bound; the newest text model
# is global-only. So typed and voice are two separate services (two URLs).
set -euo pipefail
cd "$(dirname "$0")/.."

PROJECT="${GOOGLE_CLOUD_PROJECT:-YOUR_PROJECT_ID}"
REGION="${CLOUD_RUN_REGION:-us-central1}"   # Cloud Run service region (both cases)

if [[ "${1:-}" == "--voice" ]]; then
  SERVICE="${SERVICE_NAME:-gdg-voice-concierge}"
  ENVVARS="GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_LOCATION=us-central1,TEXT_MODEL=gemini-2.5-flash,VOICE_MODEL=gemini-live-2.5-flash-native-audio"
  TIMEOUT=3600   # long-lived voice WebSocket
else
  SERVICE="${SERVICE_NAME:-gdg-agent-demos}"
  ENVVARS="GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_LOCATION=global,TEXT_MODEL=gemini-3.5-flash"
  TIMEOUT=300
fi

echo "Deploying $SERVICE to Cloud Run ($REGION) in $PROJECT ..."
gcloud run deploy "$SERVICE" \
  --source . \
  --project "$PROJECT" \
  --region "$REGION" \
  --allow-unauthenticated \
  --memory 1Gi \
  --timeout "$TIMEOUT" \
  --set-env-vars "$ENVVARS"

URL=$(gcloud run services describe "$SERVICE" --project "$PROJECT" --region "$REGION" --format='value(status.url)')
echo "Live URL: $URL"
