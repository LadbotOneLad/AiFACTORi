# E14 — MASTER FILE INDEX

## Console & Control

- **E14-Console.ps1** — Master control script. Load with `. .\E14-Console.ps1`
- **QUICKSTART.md** — Quick start guide (READ THIS FIRST)

## CLI Tools (./cli/)

- **gtop.ps1** — Docker topology CLI (docker engine health)
- **gtop-k8.ps1** — Kubernetes CLI (k8s status/map/scale/rollout)
- **k8-mu-orch-coherence.ps1** — 7-dimension coherence validator
- **treplay.ps1** — Session logger & time replay

## Kubernetes Manifests (./manifests/)

- **k8s-mu-orch-manifest.yaml** — Complete K8s deployment (14 engines, 3-10 replicas, HPA, RBAC, NetworkPolicy)
- **docker-compose-14engines.yml** — Docker Compose for local development
- **k8s-lock-configmap.yaml** — Lock metadata ConfigMap
- **k8s-lock-secret.yaml** — JWT + secrets

## Configuration (./config/)

- **.env.lock** — Environment variables (LOCK_ID, wobble constants, etc.)
- **lock-metadata.json** — Current lock state (Merkle root, engine hashes, Kotahitanja score)
- **topology.yaml** — Engine registry (all 14 engines with roles)

## Documentation (./docs/)

### Core System
- **README.md** — System overview & status
- **whitepaper.md** — Complete system philosophy

### Deployment
- **K8S-MU-ORCH-GUIDE.md** — Full Kubernetes deployment guide
- **4D-TERMINAL-SETUP.md** — 4D terminal architecture (Space/Time/Topology/Identity)
- **90-DAY-LOCK-GUIDE.md** — Lock mechanism & renewal process

### Technical
- **4GR_FSE_GUIDE.md** — 4GR-FSE engine (GROUND/READ/GATE/GROW phases)
- **DIGITAL_THYMUS_GUIDE.md** — Zero-trust security layer
- **RHYTHM-GUIDE.md** — Timing, pacing, rhythm philosophy (TICK/BEAT/BREATH)
- **COMPUTATIONAL-TESLA-COIL-TUNING.md** — Tuning targets

### Constitutional
- **IDENTITY-DOCTRINE-CONSTITUTION.md** — 6 binding articles
- **CONSTITUTION-DECLARATION.md** — Constitutional doctrine

### IP & Legal
- **IP-PROTECTION-PATENTS-TRADEMARKS.md** — Patents, trademarks, copyrights
- **LICENSE** — MIT License
- **OWNERSHIP.md** — Ownership declaration

### Campaigns
- **SOCIAL-MEDIA-CAMPAIGN.md** — Social media strategy
- **GLOBAL-AI-TEAMS-CAMPAIGN.md** — Global outreach (12 languages)
- **NVIDIA-CAMPAIGN.md** — GPU acceleration angle

### Miscellaneous
- **system-state.md** — Current system metrics
- **LOCK-DEPLOYMENT-CHECKLIST.md** — Deployment verification
- **LOCK-SYNCHRONIZED-SUMMARY.md** — Synchronization status
- **MCP_V2_DOCUMENTATION.md** — MCP audit suite
- **TESLA-COIL-ENFORCEMENT-CHECKLIST.md** — Enforcement verification

---

## Quick File Locations

```
~E14-/
├── E14-Console.ps1              ← START HERE
├── QUICKSTART.md                ← READ THIS
├── FILE-INDEX.md                ← THIS FILE
│
├── cli/
│   ├── gtop.ps1                 Docker CLI
│   ├── gtop-k8.ps1              K8s CLI
│   ├── k8-mu-orch-coherence.ps1 Coherence validator
│   └── treplay.ps1              Session logger
│
├── manifests/
│   ├── k8s-mu-orch-manifest.yaml        K8s deployment
│   ├── docker-compose-14engines.yml     Docker deployment
│   ├── k8s-lock-configmap.yaml          Lock ConfigMap
│   └── k8s-lock-secret.yaml             Secrets
│
├── config/
│   ├── .env.lock                Environment
│   ├── lock-metadata.json       Lock state
│   └── topology.yaml            Engine registry
│
└── docs/
    ├── README.md                Overview
    ├── K8S-MU-ORCH-GUIDE.md     K8s guide
    ├── QUICKSTART.md            Quick start
    ├── RHYTHM-GUIDE.md          Timing
    └── [30+ more docs]
```

---

## Console Commands Reference

```powershell
# Load console (REQUIRED FIRST)
. .\E14-Console.ps1

# System checks
E14-Check-All                  # Full check (Docker + K8s + Coherence)

# Docker (local 14-engine cluster)
E14-Docker-Start               # Start
E14-Docker-Status              # Status
E14-Docker-Logs <engine>       # Logs (e.g., 365)
E14-Docker-Stop                # Stop

# Kubernetes (production)
E14-K8S-Deploy                 # Deploy
E14-K8S-Status                 # Status
E14-K8S-Scale <n>              # Scale 1-10
E14-K8S-Coherence              # 7-dimension check

# Monitoring
E14-Gtop-Status                # Docker health
E14-Gtop-Map                   # Docker topology
E14-Gtop-K8-Status             # K8s health
E14-Gtop-K8-Map                # K8s topology

# Help
E14-Help                       # Show all commands
```

---

## Execution Flow

1. **Initialize**
   ```powershell
   . .\E14-Console.ps1
   ```
   (Loads all functions & checks directory structure)

2. **Check System**
   ```powershell
   E14-Check-All
   ```
   (Runs Docker status, K8s status, health check, coherence validation)

3. **Deploy (Choose One)**
   ```powershell
   # Option A: Docker (local, 14 engines)
   E14-Docker-Start
   
   # Option B: Kubernetes (production, 3-10 replicas)
   E14-K8S-Deploy
   ```

4. **Monitor**
   ```powershell
   E14-Gtop-Status              # Check engines
   E14-K8S-Status               # Check pods
   E14-K8S-Coherence            # Validate coherence
   ```

5. **Scale (K8s only)**
   ```powershell
   E14-K8S-Scale 5              # Scale to 5 pods
   ```

---

## System Status

✅ 14 synchronized engines (365, 777, 101, 1001-1012)
✅ Docker deployment (local development)
✅ Kubernetes deployment (production)
✅ 90-day lock enforcement
✅ Multi-user identity (JWT + RBAC)
✅ Rhythm-aware orchestration
✅ 7-dimension coherence validation
✅ Zero-trust networking
✅ Auto-scaling (HPA 3-10)

**Status: OPERATIONAL & READY FOR PRODUCTION**

---

## Key Metrics

- **Engines:** 14 total (3 core: 365/777/101, 12 peer: 1001-1012)
- **Lock:** 550e8400-e29b-41d4-a716-446655440000
- **Inception:** 2025-01-14T10:00:00.000Z
- **Expiry:** 2025-04-14T10:00:00.000Z
- **Kotahitanja (Unity Score):** 0.0917 (91.7%)
- **K8s Replicas:** 3-10 (HPA auto-scaling)
- **Coherence Status:** ✅ SYNCHRONIZED

---

## Support

For help:
1. Run `E14-Help` in PowerShell console
2. Check `QUICKSTART.md` for common tasks
3. Review `docs/K8S-MU-ORCH-GUIDE.md` for detailed deployment
4. Run `E14-K8S-Coherence -Verbose` to diagnose issues

---

**Created:** 2026-04-04
**System:** .15% SOLAR WAGYU — DIGITAL CUT
**Console:** E14 Master Control
**Ready:** ✅ YES
