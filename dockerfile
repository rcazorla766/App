FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MODEL_PATH=/app/app/models/trained_model_v1.pkl \
    MODEL_METADATA_PATH=/app/app/models/model_metadata.json \
    HOST=0.0.0.0 \
    PORT=8000

WORKDIR /app

RUN groupadd --system --gid 999 appgroup \
    && useradd --system --uid 999 --gid 999 --home-dir /app appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN chown -R appuser:appgroup /app

USER 999:999

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["sh", "-c", "uvicorn app.main:app --host ${HOST} --port ${PORT}"]
