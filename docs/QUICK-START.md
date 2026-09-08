# E14 Oracle — Quick Start

Get E14 Oracle running in 5 minutes.

## Prerequisites

- Docker & Docker Compose (easiest)
- OR: Python 3.11+, pip

## Option 1: Docker (Recommended)

```bash
# 1. Clone
git clone https://github.com/LadbotOneLad/AiFACTORi.git
cd AiFACTORi

# 2. Start services
docker-compose up -d

# 3. Monitor
docker-compose logs -f e14_oracle

# 4. Stop
docker-compose down
```

**Result**: 5 services running (oracle, driftwatcher, taskmanager, sympy, live)

## Option 2: Local Python

```bash
# 1. Clone
git clone https://github.com/LadbotOneLad/AiFACTORi.git
cd AiFACTORi

# 2. Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install
pip install -r requirements.txt

# 4. Run oracle
python oracle_layer.py

# Output will show:
# ╔══════════════════════════════════════════════════════════════════╗
# ║    E14 ORACLE LAYER — CONVERGENCE & BRANCHING                  ║
# ╚══════════════════════════════════════════════════════════════════╝
```

## What's Running

| Service | Command | Purpose |
|---------|---------|---------|
| E14 Oracle | `oracle_layer.py` | Convergence detection |
| E14 Live | `e14_live.py` | Real-time decisions |
| E14 DriftWatcher | `kotahitanga_driftwatcher.py` | State monitoring |
| E14 SymPy | `kotahitanga_sympy.py` | Math validation |
| E14 TaskManager | `e14_seven_day_logger.py` | Queue & logging |

## Verify Installation

```bash
# Check convergence detection
python oracle_layer.py

# Expected: Oracle tests 3 branching futures, reports K-value

# Check real-time oracle
python e14_live.py

# Expected: Monitors K-score, CPU, memory, disk, weather conditions
# Prints status every second
```

## Common Commands

```bash
# View all logs
docker-compose logs

# Follow specific service
docker-compose logs -f e14_live

# Check status
docker-compose ps

# Stop and remove
docker-compose down

# Rebuild images
docker-compose up --build

# Run single service
docker-compose up e14_oracle
```

## Next Steps

- **Docker Hub**: See `docs/DOCKER-GUIDE.md`
- **Configuration**: See `docs/CONFIGURATION.md`
- **Architecture**: See `docs/ARCHITECTURE.md`
- **Contributing**: See `CONTRIBUTING.md`

## Troubleshooting

**Docker not found?**
- Install Docker Desktop: https://www.docker.com/products/docker-desktop

**Port already in use?**
- Change port in `docker-compose.yml`

**Python import error?**
- Ensure virtual environment is activated: `source venv/bin/activate`

**Permission denied on build-and-publish.sh?**
```bash
chmod +x build-and-publish.sh
./build-and-publish.sh
```

## Support

- **Docs**: See `docs/` folder
- **Issues**: https://github.com/LadbotOneLad/AiFACTORi/issues
- **Discussions**: https://github.com/LadbotOneLad/AiFACTORi/discussions

---

**Next**: Read full README.md for complete documentation
