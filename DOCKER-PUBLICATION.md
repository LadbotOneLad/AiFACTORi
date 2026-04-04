# Docker Publication Guide

## Quick Summary

The E14 Oracle system is now containerized and ready for Docker Hub publication.

**Status:**
- ✅ Dockerfile (multi-stage, production-grade)
- ✅ requirements.txt (psutil, sympy, flask, pyyaml, python-dateutil)
- ✅ docker-compose.yml (5 synchronized services)
- ✅ .dockerignore (optimized build)
- ✅ Build verified locally (305 MB image size)
- ✅ Pushed to GitHub

## Files Created

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage Python 3.11-slim image with non-root user, health checks |
| `requirements.txt` | Python dependencies (psutil, sympy, flask, pyyaml, python-dateutil) |
| `docker-compose.yml` | 5-service orchestration (oracle, driftwatcher, taskmanager, sympy, live) |
| `.dockerignore` | Build optimization (ignores docs, tests, PowerShell scripts) |
| `build-and-publish.sh` | Automated build, tag, and Docker Hub push script |

## Image Details

**Base:** python:3.11-slim (official Python image, ~150 MB base)

**Multi-stage build:**
1. **Builder stage**: Compiles wheels with build-essential, creates user dependencies
2. **Production stage**: Copies only runtime dependencies, drops build tools

**Security:**
- Non-root user: `e14` (group: `e14`)
- Read-only config volumes
- Health checks on all services
- No privileged operations

**Size:** 305 MB (includes all 5 service entry points)

## Deployment Scenarios

### Local Development

```bash
docker-compose up -d
docker-compose logs -f
```

### Single Container Run

```bash
docker run -it e14-oracle:1.0 python3 oracle_layer.py
```

### Production Multi-Service

```bash
docker-compose -f docker-compose.yml up -d
docker-compose ps
docker-compose logs e14_oracle
```

## Docker Hub Publication Steps

### Prerequisites

1. **Create Docker Hub account** (free): https://hub.docker.com/signup
2. **Generate access token**:
   - Log in to Hub
   - Settings → Security → New Access Token
   - Copy token
3. **Login locally**:
   ```bash
   docker login
   # Paste username and token when prompted
   ```

### Publish

```bash
# Option 1: Automated script
DOCKER_HUB_USERNAME=yourname ./build-and-publish.sh

# Option 2: Manual steps
docker build -t yourname/e14-oracle:1.0 .
docker tag yourname/e14-oracle:1.0 yourname/e14-oracle:latest
docker push yourname/e14-oracle:1.0
docker push yourname/e14-oracle:latest
```

### Verify

```bash
# Pull from any machine
docker pull yourname/e14-oracle:latest
docker run -it yourname/e14-oracle:latest python3 oracle_layer.py
```

## GitHub Actions Automation (Optional)

Add `.github/workflows/docker-publish.yml` to auto-publish on git push:

```yaml
name: Publish E14 to Docker Hub

on:
  push:
    branches: [main]

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

Then add secrets to GitHub:
- `DOCKER_HUB_USERNAME` = your Docker Hub username
- `DOCKER_HUB_TOKEN` = your access token

## Service Mappings

All 5 services run from the same image, different entry points:

| Service | Port | Command | Purpose |
|---------|------|---------|---------|
| e14_oracle | - | python3 oracle_layer.py | Convergence detection |
| e14_driftwatcher | - | python3 kotahitanga_driftwatcher.py | State observer |
| e14_taskmanager | - | python3 e14_seven_day_logger.py | Task queue |
| e14_sympy | - | python3 kotahitanga_sympy.py | Math computation |
| e14_live | - | python3 e14_live.py | Real-time decision engine |

## Next Steps

1. **Update docker-compose.yml** to use published images:
   ```yaml
   services:
     e14_oracle:
       image: yourname/e14-oracle:latest
       # ... rest of config
   ```

2. **Update README.md** with Docker Hub links

3. **Tag releases** in GitHub:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. **Monitor pulls** on Docker Hub dashboard

5. **Keep image updated**:
   - Update requirements.txt
   - Rebuild and push
   - GitHub Actions auto-handles if enabled

## Image Pull Examples

Once published, anyone can use the E14 system:

```bash
# Pull image
docker pull yourname/e14-oracle:latest

# Run oracle service
docker run -it yourname/e14-oracle:latest python3 oracle_layer.py

# Run in compose
cat > docker-compose.yml << 'EOF'
version: '3.9'
services:
  oracle:
    image: yourname/e14-oracle:latest
    command: python3 oracle_layer.py
    volumes:
      - ./config:/app/config:ro
EOF

docker-compose up
```

## Troubleshooting

**Docker not found?**
```bash
# Ensure Docker Desktop is running
docker ps
```

**Login failed?**
```bash
# Verify token has correct permissions
docker logout
docker login  # Re-authenticate
```

**Push rejected?**
```bash
# Verify image is tagged correctly
docker images | grep e14-oracle

# Re-tag if needed
docker tag e14-oracle:1.0 yourname/e14-oracle:1.0
```

**Image too large?**
- Reduce dependencies in requirements.txt
- Use alpine instead of slim
- Remove unused files from .dockerignore

## Support

- **Docker Docs**: https://docs.docker.com/
- **Docker Hub**: https://hub.docker.com/
- **GitHub Integration**: https://docs.docker.com/build/ci/github-actions/

---

**Status:** Ready for publication. Run build-and-publish.sh to complete.
