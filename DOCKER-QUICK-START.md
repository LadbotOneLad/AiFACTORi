# E14 Docker Quick Start

## Status

✅ **Docker-ready** — All services containerized and pushed to GitHub

## Local Deployment (30 seconds)

```bash
# 1. Navigate to project
cd C:\Users\Admin\OneDrive\Desktop\~E14-

# 2. Start all 5 services
docker-compose up -d

# 3. Check status
docker-compose ps

# 4. View logs
docker-compose logs -f e14_oracle
```

## What Runs

| Service | Container | Status |
|---------|-----------|--------|
| Oracle | e14_oracle | Phase convergence detector |
| DriftWatcher | e14_driftwatcher | State observer |
| TaskManager | e14_taskmanager | Task queue & logging |
| SymPy | e14_sympy | Mathematical validator |
| Live | e14_live | Real-time decisions |

All 5 services use the same image (`e14-oracle:1.0`) with different entry points.

## Docker Hub Publication

### Step 1: Create Docker Hub Account
1. Go to https://hub.docker.com/signup
2. Create free account

### Step 2: Generate Access Token
1. Log in to Docker Hub
2. Settings → Security → New Access Token
3. Name it (e.g., "e14-publication")
4. Copy the token

### Step 3: Publish
```bash
cd C:\Users\Admin\OneDrive\Desktop\~E14-

# Option A: Automated (recommended)
$env:DOCKER_HUB_USERNAME = "your-docker-hub-username"
bash build-and-publish.sh

# Option B: Manual
docker login
docker build -t your-username/e14-oracle:1.0 .
docker push your-username/e14-oracle:1.0
docker push your-username/e14-oracle:latest
```

### Step 4: Verify
```bash
# Anyone can now pull globally
docker pull your-username/e14-oracle:latest
```

## Development Workflow

```bash
# Make changes to source code
# (e.g., oracle_layer.py, e14_live.py, etc.)

# Rebuild image
docker build -t e14-oracle:1.0 .

# Test locally
docker-compose down
docker-compose up -d

# Verify services
docker-compose logs e14_oracle

# Push to Docker Hub
docker tag e14-oracle:1.0 your-username/e14-oracle:1.0
docker push your-username/e14-oracle:1.0
```

## File Structure

```
~E14-/
├── Dockerfile                    ← Multi-stage build definition
├── requirements.txt              ← Python dependencies
├── docker-compose.yml            ← 5-service orchestration
├── .dockerignore                 ← Build optimization
├── build-and-publish.sh          ← Publication script
│
├── oracle_layer.py               ← Convergence engine
├── e14_live.py                   ← Real-time decisions
├── kotahitanga_driftwatcher.py   ← State watcher
├── kotahitanga_sympy.py          ← Math validation
├── e14_seven_day_logger.py       ← Task manager
│
├── config/
│   ├── .env.lock                 ← Lock configuration
│   ├── lock-metadata.json        ← State metadata
│   └── topology.yaml             ← Engine registry
│
└── docs/
    └── DOCKER-PUBLICATION.md     ← Full publication guide
```

## Ports & Networking

All services communicate via Docker network `e14_net`:
- Internal only (no exposed ports for this version)
- Services resolve by container name
- Volumes mounted read-only for config

To expose ports, modify `docker-compose.yml`:

```yaml
services:
  e14_oracle:
    ports:
      - "8001:8001"  # If oracle exposes HTTP
```

## Logs & Debugging

```bash
# View all logs
docker-compose logs

# Follow oracle service
docker-compose logs -f e14_oracle

# Check container health
docker ps

# Inspect service
docker-compose exec e14_oracle python3 -c "import oracle_layer; print('OK')"
```

## Cleanup

```bash
# Stop services
docker-compose down

# Remove image
docker rmi e14-oracle:1.0

# Prune unused Docker resources
docker system prune
```

## Next Steps

1. ✅ **Local test** — `docker-compose up -d`
2. ⬜ **Create Docker Hub account** — https://hub.docker.com/signup
3. ⬜ **Generate access token** — Settings → Security
4. ⬜ **Publish** — `bash build-and-publish.sh`
5. ⬜ **Update compose** — Change image references to Docker Hub URLs
6. ⬜ **Commit & push** — Git push to GitHub

---

**Need details?** See DOCKER-PUBLICATION.md for comprehensive guide.

**Status:** Ready for Docker Hub. Execute publication script when credentials are ready.
