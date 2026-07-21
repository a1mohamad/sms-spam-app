FROM python:3.13-slim

# Keep Python output visible in container logs and avoid storing pip's
# download cache in the final image.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# Create an unprivileged runtime user.
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser

# Install dependencies in a cache-friendly layer.
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

# Copy only runtime application and migration files.
COPY --chown=appuser:appgroup app ./app
COPY --chown=appuser:appgroup migrations ./migrations
COPY --chown=appuser:appgroup alembic.ini ./

# TensorFlow/Keras is not needed by the runtime image.
COPY --chown=appuser:appgroup \
    artifacts/sms-spam-model.onnx \
    artifacts/vocabs_config.json \
    artifacts/label_mapping.json \
    ./artifacts/

USER appuser

# Document the default application port; deployment platforms can override
# PORT at runtime.
EXPOSE 8000

# Check API readiness, including its PostgreSQL connection through /health.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/health', timeout=3).close()"

# Start only the API process; Compose or the deployment platform runs Alembic
# as a separate one-off migration job.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
