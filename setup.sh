#!/usr/bin/env bash
# One-shot bootstrap. Reproducible on any laptop (macOS/Linux).
# Usage:  ./setup.sh              (uses GOOGLE_CLOUD_PROJECT or .env)
#         ./setup.sh my-project   (override project)
set -euo pipefail

cd "$(dirname "$0")"
GREEN='\033[0;32m'; YEL='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
say() { echo -e "${GREEN}==>${NC} $*"; }
warn() { echo -e "${YEL}!!${NC} $*"; }

# --- 0. env ---
if [[ ! -f .env ]]; then
  cp .env.example .env
  warn "Created .env from .env.example — edit GOOGLE_CLOUD_PROJECT if needed."
fi
# shellcheck disable=SC1091
set -a; source .env; set +a
PROJECT="${1:-${GOOGLE_CLOUD_PROJECT:-}}"
LOCATION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
[[ -z "$PROJECT" ]] && { echo -e "${RED}Set GOOGLE_CLOUD_PROJECT in .env${NC}"; exit 1; }
say "Project: $PROJECT  Location: $LOCATION"

# --- 1. python deps via uv ---
command -v uv >/dev/null || { echo -e "${RED}uv not found. Install: https://docs.astral.sh/uv/${NC}"; exit 1; }
say "Creating venv + installing google-adk..."
uv venv --python 3.12 .venv >/dev/null 2>&1 || uv venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
uv pip install -q -r requirements.txt
say "ADK version: $(adk --version 2>&1)"

# --- 2. gcloud auth + project ---
command -v gcloud >/dev/null || { echo -e "${RED}gcloud not found: https://cloud.google.com/sdk${NC}"; exit 1; }
gcloud config set project "$PROJECT" >/dev/null 2>&1
if ! gcloud auth application-default print-access-token >/dev/null 2>&1; then
  warn "No ADC. Run:  gcloud auth application-default login"
else
  say "ADC ok."
fi

# --- 3. enable APIs ---
say "Enabling aiplatform + run + cloudbuild APIs (idempotent)..."
gcloud services enable aiplatform.googleapis.com run.googleapis.com \
  cloudbuild.googleapis.com --project "$PROJECT" >/dev/null 2>&1 || \
  warn "Could not enable APIs (need perms?). Enable manually if adk fails."

# --- 4. write per-agent .env symlinks so `adk web agents` picks up config ---
for a in agents/demo1_assistant agents/demo2_concierge; do
  ln -sf ../../.env "$a/.env"
done
say "Done. Next:"
echo "   source .venv/bin/activate"
echo "   adk web agents          # pick demo1_assistant or demo2_concierge; click mic for voice"
