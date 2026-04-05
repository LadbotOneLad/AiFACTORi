# Configuration Guide

Environment variables, settings, and customization.

## .env File

Create `.env` in project root or use `config/.env.lock`:

```bash
# LOCK CONFIGURATION
LOCK_ID=550e8400-e29b-41d4-a716-446655440000
LOCK_INCEPTION=2025-01-14T10:00:00.000Z
LOCK_EXPIRY=2025-04-14T10:00:00.000Z
LOCK_ROOT_HASH=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
LOCK_PHRASE=UNIT-LOCKED:14engines:90days:2025-01-14

# ORACLE THRESHOLDS
K_THRESHOLD=0.99              # Convergence required (K-value)
CONVERGENCE_TOLERANCE=100.0   # Phase tolerance per axis

# LIVE ORACLE GATES
CPU_MIN=10                    # Minimum CPU headroom %
MEMORY_MIN=15                 # Minimum memory headroom %
DISK_MIN=20                   # Minimum disk headroom %
WEATHER_MAX=0.6               # Maximum weather safety threshold

# TEMPORAL SCALING
ARIES_POINT=0.0               # Convergence target phase
PHASE_PULLBACK=0.95           # Correction strength (0.0-1.0)
HEAT_DAMPING=0.02             # Thermal regulation damping
HEAT_EQUILIBRIUM=0.075        # Target insolation level
HEAT_TOLERANCE=0.005          # Heat tolerance band

# LOGGING
LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json               # json or text
LOG_ROTATION=daily            # daily, weekly, size-based

# DOCKER
DOCKER_REGISTRY=docker.io
DOCKER_IMAGE_TAG=latest
```

## Lock Metadata

`config/lock-metadata.json` contains:

```json
{
  "lock_id": "550e8400-e29b-41d4-a716-446655440000",
  "lock_inception": "2025-01-14T10:00:00.000Z",
  "lock_expiry": "2025-04-14T10:00:00.000Z",
  "lock_duration_days": 90,
  "lock_root_hash": "a1b2c3d4...",
  "cycle": 2,
  "engines": {
    "E01": { "role": "Validator", "port": 365 },
    "E02": { "role": "Sovereign", "port": 777 },
    ...
  },
  "created": "2025-01-14T10:00:00Z",
  "updated": "2025-01-14T10:00:00Z"
}
```

## Engine Topology

`config/topology.yaml`:

```yaml
engines:
  E01:
    name: "365"
    role: "Validator"
    primary_axes: [tick, beat, breath, cycle]
    
  E02:
    name: "777"
    role: "Sovereign"
    primary_axes: [tick, beat, breath, cycle, heat, weather]
```

## Runtime Configuration

### Via Environment Variables

```bash
export K_THRESHOLD=0.95
export CPU_MIN=5
python e14_live.py
```

### Via Docker Compose

`docker-compose.yml`:
```yaml
services:
  e14_oracle:
    environment:
      K_THRESHOLD: "0.99"
      CPU_MIN: "10"
```

### Via config/.env.lock

```bash
source config/.env.lock
python oracle_layer.py
```

## Phase Tolerances

Defines "convergence" per axis:

```python
TOLERANCE = {
    "tick":   360,      # 1/240 of cycle
    "beat":   1440,     # 1/60 of cycle
    "breath": 10800,    # 1/8 of cycle
    "cycle":  86400,    # full cycle
}

TOLERANCE_STRICT = {
    "tick":   10,       # very tight
    "beat":   40,
    "breath": 300,
    "cycle":  1000,
}
```

Use `TOLERANCE_STRICT` for production, `TOLERANCE` for testing.

## Tuning Parameters

### For Development

```bash
K_THRESHOLD=0.85            # Lower for faster testing
CPU_MIN=1                   # Don't block on resources
MEMORY_MIN=1
DISK_MIN=1
WEATHER_MAX=1.0             # Disable weather gating
```

### For Production

```bash
K_THRESHOLD=0.99            # Strict convergence requirement
CPU_MIN=20                  # Ensure headroom
MEMORY_MIN=25
DISK_MIN=30
WEATHER_MAX=0.6             # Strict weather requirement
```

### For High-Latency Environments

```bash
CONVERGENCE_TOLERANCE=500   # Loosen phase tolerance
PHASE_PULLBACK=0.80         # Slower correction
```

## Docker Compose Configuration

`docker-compose.yml` environment section:

```yaml
services:
  e14_oracle:
    env_file: config/.env.lock
    environment:
      K_THRESHOLD: "${K_THRESHOLD}"
      CPU_MIN: "${CPU_MIN}"
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs:rw
```

## Logging Configuration

### Python Logging

```python
import logging

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Oracle initialized")
```

### Log Locations

```
logs/
├── oracle/
│   ├── cycle_1.log
│   ├── cycle_2.log
│   └── current.log
├── driftwatcher/
├── taskmanager/
├── sympy/
└── live/
```

### Log Rotation

7-day cycle rotation in TaskManager:

```python
# Day 1-7: cycle_1.log
# Day 8-14: cycle_2.log
# After 7 days, old logs archived
```

## Performance Tuning

### Docker Resource Limits

```yaml
services:
  e14_oracle:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
        reservations:
          cpus: "0.5"
          memory: 256M
```

### Python Optimization

```python
# Cache compiled tolerances
TOLERANCE_COMPILED = {
    k: float(v) for k, v in TOLERANCE.items()
}

# Use numpy for phase calculations (future)
import numpy as np
```

## Validation

### Check Configuration

```bash
# Load and validate
python -c "from config import LOCK_ID; print(f'Lock: {LOCK_ID}')"

# Test convergence thresholds
python -c "from oracle_layer import K_THRESHOLD; print(f'K={K_THRESHOLD}')"

# Verify engine registry
python -c "from config.topology import engines; print(f'Engines: {len(engines)}')"
```

### Self-Test

```bash
python test_configuration.py
```

## Secrets Management

### Development

Store secrets in `.env.lock` (gitignored):

```bash
echo "LOCK_ROOT_HASH=secret_value" >> config/.env.lock
```

### Production (Kubernetes)

Use Kubernetes Secrets:

```bash
kubectl create secret generic e14-lock \
  --from-file=config/lock-metadata.json
```

### CI/CD

Use GitHub Secrets:

```yaml
env:
  LOCK_ID: ${{ secrets.LOCK_ID }}
  LOCK_ROOT_HASH: ${{ secrets.LOCK_ROOT_HASH }}
```

## Migration Guide

### Upgrading Lock Duration

```bash
# Generate new 90-day lock
node lock-initialize.ts

# Restart services
docker-compose restart
```

### Changing Convergence Thresholds

```bash
# Update .env
K_THRESHOLD=0.98

# Restart oracle
docker-compose restart e14_oracle

# Verify
docker-compose logs e14_oracle | grep "K_THRESHOLD"
```

## Common Configurations

### For CI/CD Testing

```bash
K_THRESHOLD=0.80
CPU_MIN=0
MEMORY_MIN=0
DISK_MIN=0
WEATHER_MAX=1.0
LOG_LEVEL=DEBUG
```

### For Production Kubernetes

```bash
K_THRESHOLD=0.99
CPU_MIN=30
MEMORY_MIN=40
DISK_MIN=50
WEATHER_MAX=0.4
LOG_LEVEL=WARNING
```

### For Local Development

```bash
K_THRESHOLD=0.85
CPU_MIN=5
MEMORY_MIN=5
DISK_MIN=5
WEATHER_MAX=0.9
LOG_LEVEL=DEBUG
```

## Troubleshooting

**Services won't start?**
- Check `.env.lock` exists: `test -f config/.env.lock`
- Verify syntax: `python -c "import os; os.environ"`
- Check Docker logs: `docker-compose logs e14_oracle`

**K-value too low?**
- Loosen `CONVERGENCE_TOLERANCE`
- Increase `PHASE_PULLBACK` (faster correction)
- Check if engines are actually running

**Gates always blocking?**
- Check system resources: `docker stats`
- Lower `CPU_MIN`, `MEMORY_MIN`, `DISK_MIN` for testing
- Verify weather data source

**Lock expired?**
```bash
node lock-initialize.ts
docker-compose restart
```

---

See also:
- `ARCHITECTURE.md` — System design
- `.env` — Example environment file
- `docker-compose.yml` — Service configuration
