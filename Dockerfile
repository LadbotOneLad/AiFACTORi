# Multi-stage E14 Oracle production image
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies (minimal set)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements with wheel caching
COPY requirements.txt .
RUN pip install --no-cache-dir --compile \
    -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory early
WORKDIR /app

# Create non-root user with minimal shell
RUN groupadd -r e14 && useradd -r -g e14 -s /sbin/nologin e14

# Copy only runtime site-packages from builder (more efficient)
COPY --from=builder --chown=e14:e14 /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder --chown=e14:e14 /usr/local/bin /usr/local/bin

# Copy application code (exclude dev files via .dockerignore)
COPY --chown=e14:e14 . .

# Environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=2

# Switch to non-root user before health check
USER e14

# Health check with better error handling
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import psutil, sys; sys.exit(0 if psutil.virtual_memory() else 1);" || exit 1

# Explicit entrypoint for clarity
CMD ["python3", "e14_live.py"]
