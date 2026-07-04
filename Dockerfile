FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app \
    && apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app

USER app

EXPOSE 8201

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8201/live || exit 1

CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8201", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]
