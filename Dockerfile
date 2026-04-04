# Multi-stage E14 Oracle production image
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and build wheels
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r e14 && useradd -r -g e14 e14

# Copy only runtime dependencies from builder
COPY --from=builder /root/.local /home/e14/.local

# Copy application code
COPY --chown=e14:e14 . .

# Set Python path
ENV PATH=/home/e14/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER e14

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import psutil; print('ok')" || exit 1

# Default command
CMD ["python3", "e14_live.py"]
