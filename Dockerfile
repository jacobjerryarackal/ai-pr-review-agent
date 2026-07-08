FROM python:3.11-slim

# Prevents Python from writing .pyc files (saves disk I/O in containers)
ENV PYTHONDONTWRITEBYTECODE=1

# Prevents Python output from being buffered — ensures logs appear in
# real time in docker-compose logs and Kubernetes pod logs.
ENV PYTHONUNBUFFERED=1

# Install system-level dependencies needed at runtime:
#   libpq-dev   — asyncpg (async Postgres driver) needs libpq
#   curl        — used in healthcheck probes
# We run apt-get in a single RUN layer and clean up apt lists to keep
# the image small. Each RUN creates a new image layer.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

WORKDIR /app

COPY pyproject.toml /app/
RUN pip install --no-cache-dir -e . || true

COPY . /app/
RUN pip install --no-cache-dir -e .

ENV PORT=8000
EXPOSE 8000

# WHY ["sh", "-c", "..."] form:
#   Railway parses the Dockerfile CMD to extract the start command.
#   Shell form (CMD uvicorn ... ${PORT:-8000}) confuses Railway's parser -> crash.
#   Plain JSON array (["uvicorn", "--port", "8000"]) doesn't expand $PORT env var.
#   ["sh", "-c", "..."] gives us BOTH: Railway parses it as valid JSON array,
#   and sh -c runs it through a shell which expands ${PORT:-8000} at runtime.
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]