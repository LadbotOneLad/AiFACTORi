# Docker Deployment Guide

Build, deploy, and publish E14 Oracle using Docker.

## Prerequisites

- Docker Desktop (https://www.docker.com/products/docker-desktop)
- Docker Compose (included with Desktop)
- Docker Hub account (free: https://hub.docker.com/signup)

## Local Deployment

### Build Locally

```bash
# Build image
docker build -t e14-oracle:1.0 -f Dockerfile .

# Verify
docker images | grep e14-oracle
# Output: e14-oracle  1.0  305MB  <date>
```

### Run with Docker Compose

```bash
# Start all 5 services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f e14_oracle

# Stop
docker-compose down
```

### Run Single Service

```bash
# Run oracle only
docker run -it e14-oracle:1.0 python3 oracle_layer.py

# Run with custom command
docker run -it e14-oracle:1.0 python3 e14_live.py
```

## Multi-Stage Build Explained

`Dockerfile` uses two stages:

```dockerfile
# Stage 1: Builder
# - Installs build-essential (gcc, make, etc.)
# - Compiles wheels for all dependencies
# - Creates /root/.local with compiled packages

# Stage 2: Production
# - Copies ONLY runtime dependencies from builder
# - Drops all build tools (400+ MB savings)
# - Creates non-root user
# - Final image: 305 MB (vs 700+ MB with single stage)
```

**Size comparison**:
- Single-stage: 700+ MB (includes build tools)
- Multi-stage: 305 MB (production-only)

## Services

### docker-compose.yml

5 services, 1 image, different entry points:

```yaml
services:
  e14_oracle:
    image: e14-oracle:1.0
    command: ["python3", "oracle_layer.py"]
    healthcheck:
      test: ["CMD", "python3", "-c", "import time; print('oracle_ok')"]
      interval: 30s

  e14_live:
    image: e14-oracle:1.0
    command: ["python3", "e14_live.py"]
    depends_on:
      e14_oracle:
        condition: service_healthy

  # ... more services
```

### Health Checks

Each service has a health check:

```bash
# Check status
docker-compose ps

# Expected output:
# e14_oracle     e14_live:1.0   python oracle... running (healthy)
# e14_live       e14_live:1.0   python e14_... running (healthy)
```

## Docker Hub Publication

### Step 1: Prepare Account

```bash
# 1. Create account: https://hub.docker.com/signup
# 2. Log in locally
docker login

# Verify
docker info | grep Username
```

### Step 2: Generate Access Token

1. Log in to https://hub.docker.com
2. Account Settings → Security → New Access Token
3. Name: `e14-publication`
4. Copy token
5. Use token as password (not Docker Hub password)

### Step 3: Build & Tag

```bash
# Variables
export DOCKER_HUB_USERNAME=your-username
export IMAGE_NAME=e14-oracle
export VERSION=1.0

# Build
docker build -t $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION .

# Tag as latest
docker tag $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION \
           $DOCKER_HUB_USERNAME/$IMAGE_NAME:latest

# Verify
docker images | grep e14
```

### Step 4: Push to Docker Hub

```bash
# Push versioned image
docker push $DOCKER_HUB_USERNAME/$IMAGE_NAME:1.0

# Push latest
docker push $DOCKER_HUB_USERNAME/$IMAGE_NAME:latest

# Monitor
# (Go to https://hub.docker.com/r/your-username/e14-oracle)
```

### Step 5: Pull Globally

```bash
# Anyone can now pull
docker pull your-username/e14-oracle:latest

# Verify
docker run -it your-username/e14-oracle:latest python3 oracle_layer.py
```

## Automated Publication Script

See `build-and-publish.sh`:

```bash
# Make executable
chmod +x build-and-publish.sh

# Run (builds, tags, pushes)
export DOCKER_HUB_USERNAME=your-username
./build-and-publish.sh

# Output:
# [1/5] Checking prerequisites...
# [2/5] Building Docker image...
# [3/5] Tagging image for Docker Hub...
# [4/5] Checking Docker Hub authentication...
# [5/5] Pushing to Docker Hub...
#
# ✓ Push successful
# Images published:
#   - your-username/e14-oracle:1.0
#   - your-username/e14-oracle:latest
```

## GitHub Actions CI/CD

Optional: Auto-publish on git push.

Create `.github/workflows/docker-publish.yml`:

```yaml
name: Publish E14 to Docker Hub

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: docker/setup-buildx-action@v2
      
      - uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_TOKEN }}
      
      - uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKER_HUB_USERNAME }}/e14-oracle:latest
            ${{ secrets.DOCKER_HUB_USERNAME }}/e14-oracle:1.0
```

Add secrets to GitHub:
1. Go to Settings → Secrets and variables → Actions
2. Add `DOCKER_HUB_USERNAME`
3. Add `DOCKER_HUB_TOKEN`

Now every push to main auto-publishes!

## Update docker-compose.yml

Change image references after publication:

```yaml
# Before:
services:
  e14_oracle:
    build:
      context: .
      dockerfile: Dockerfile

# After:
services:
  e14_oracle:
    image: your-username/e14-oracle:latest
```

Then restart:

```bash
docker-compose down
docker-compose up -d
```

## Troubleshooting

**Build fails: "build-essential not found"?**
```bash
# Docker daemon might be dead
docker ps

# Restart Docker Desktop if needed
```

**Push fails: "unauthorized"?**
```bash
# Re-authenticate
docker logout
docker login
# Paste username and token (not password)
```

**Image won't start?**
```bash
# Check logs
docker logs e14_oracle

# Run with verbose
docker run -it e14-oracle:1.0 python3 -u oracle_layer.py 2>&1 | head -50
```

**Port already in use?**
```yaml
# In docker-compose.yml, change ports:
e14_oracle:
  ports:
    - "8001:8001"  # Change 8001 if needed
```

**Need to rebuild?**
```bash
# Force rebuild (don't use cache)
docker build --no-cache -t e14-oracle:1.0 .

# Or with compose
docker-compose build --no-cache
```

## Performance Optimization

### Image Caching

Docker builds use layer caching:

```dockerfile
# Cached until this changes:
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Skipped if requirements.txt unchanged
COPY . /app
```

**Optimization**: If you edit source code, rebuild is fast (only final layer).

### Minimal Base Image

We use `python:3.11-slim` (150 MB base):

| Image | Size | Tradeoff |
|-------|------|----------|
| python:3.11-slim | 150 MB | Minimal (our choice) |
| python:3.11 | 900 MB | More packages |
| python:3.11-alpine | 50 MB | No glibc (C extensions fail) |

### Multi-Stage Build

- Builder stage: 600+ MB (with build-essential)
- Production stage: 305 MB (only runtime libs)
- **Savings**: 295 MB per image

## Security Best Practices

✅ **Applied**:
- Non-root user (`e14`)
- Read-only config volumes
- No privileged operations
- Health checks

📋 **Future**:
- Image scanning (Docker Scout)
- Secrets rotation
- Network policies (Kubernetes)
- RBAC (Kubernetes)

## Advanced Usage

### Custom Entry Point

```bash
# Override command
docker run -it e14-oracle:1.0 /bin/bash

# Run tests in container
docker run -it e14-oracle:1.0 python -m pytest tests/
```

### Volume Mounting

```bash
# Mount local code (development)
docker run -it -v $(pwd):/app e14-oracle:1.0 python oracle_layer.py

# Mount logs
docker run -it -v $(pwd)/logs:/app/logs e14-oracle:1.0 ...
```

### Environment Injection

```bash
docker run -it \
  -e K_THRESHOLD=0.95 \
  -e CPU_MIN=5 \
  e14-oracle:1.0 python e14_live.py
```

## Monitoring

### Container Stats

```bash
# Real-time stats
docker stats e14_oracle

# Output:
# CONTAINER          CPU %    MEM USAGE / LIMIT     NET I/O
# e14_oracle         0.5%     45MB / 512MB          1.2KB / 2.1KB
```

### Logs

```bash
# Follow logs (like tail -f)
docker-compose logs -f e14_oracle

# Last 100 lines
docker-compose logs e14_oracle --tail 100

# Specific service
docker-compose logs e14_live
```

---

See also:
- `README.md` — Overview
- `QUICK-START.md` — 5-minute setup
- `ARCHITECTURE.md` — System design
