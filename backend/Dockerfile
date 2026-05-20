FROM python:3.11-slim

# System deps: curl (healthcheck), libpq5 (psycopg2 runtime), gcc + libpq-dev (build)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd -m -u 1001 appuser

WORKDIR /app

# Install deps first for layer cache efficiency
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
