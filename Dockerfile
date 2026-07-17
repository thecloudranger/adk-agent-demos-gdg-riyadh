# Reproducible Cloud Run image for the ADK agents (serves the adk web UI).
# Built by `gcloud run deploy --source .` (see deploy/deploy.sh).
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents ./agents

# Vertex backend; project/location/model come from --set-env-vars at deploy time.
ENV GOOGLE_GENAI_USE_VERTEXAI=TRUE

# Cloud Run provides $PORT (8080). adk web serves the chat UI + trace panel.
CMD ["sh", "-c", "adk web agents --host 0.0.0.0 --port ${PORT:-8080}"]
