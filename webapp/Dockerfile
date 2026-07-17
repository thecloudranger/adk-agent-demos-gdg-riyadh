# Static host for the web app skin on Cloud Run.
FROM python:3.12-slim
WORKDIR /site
COPY index.html .
# Cloud Run provides $PORT (8080). Serve the single-page skin.
CMD ["sh", "-c", "python -m http.server ${PORT:-8080}"]
