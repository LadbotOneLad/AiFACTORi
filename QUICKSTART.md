# E14 MASTER CONTROL — QUICK START

## Initialize PowerShell Console

```powershell
# 1. Load the E14 console
. "C:\Users\Admin\OneDrive\Desktop\~E14-\E14-Console.ps1"

# 2. You'll see:
#    ✓ manifests/
#    ✓ cli/
#    ✓ docs/
#    ✓ config/
#    Ready. Type E14-Help for commands.
```

## Common Commands

### Check Everything
```powershell
E14-Check-All   # Full system check (Docker + K8s + Coherence)
```

### Docker (14-engine local cluster)
```powershell
E14-Docker-Start        # Start 14 engines
E14-Docker-Status       # Check running containers
E14-Docker-Logs 365     # Tail engine-365 logs
E14-Docker-Stop         # Stop cluster
```

### Kubernetes (Production deployment)
```powershell
E14-K8S-Deploy          # Deploy to K8s cluster
E14-K8S-Status          # Check K8s pods
E14-K8S-Scale 5         # Scale to 5 replicas
E14-K8S-Coherence       # 7-dimension validation
```

### Monitoring
```powershell
E14-Gtop-Status         # Docker engine health
E14-Gtop-Map            # Docker topology
E14-Gtop-K8-Status      # K8s health
E14-Gtop-K8-Map         # K8s topology
```

### Help
```powershell
E14-Help                # Show all commands
```

---

## Directory Structure

```
~E14-/
├── E14-Console.ps1           ← Load this first
├── cli/
│   ├── gtop.ps1              Docker topology CLI
│   ├── gtop-k8.ps1           K8s CLI
│   ├── k8-mu-orch-coherence.ps1   7-dimension validator
│   └── treplay.ps1           Session logger
├── manifests/
│   ├── docker-compose-14engines.yml   Local deployment
│   ├── k8s-mu-orch-manifest.yaml      K8s deployment
│   └── k8s-lock-*.yaml                K8s config
├── config/
│   ├── .env.lock              Environment variables
│   ├── lock-metadata.json     Lock state
│   └── topology.yaml          Engine registry
└── docs/
    ├── README.md              System overview
    ├── K8S-MU-ORCH-GUIDE.md   Kubernetes guide
    ├── 4D-TERMINAL-SETUP.md   Terminal setup
    ├── RHYTHM-GUIDE.md        Timing & rhythm
    └── [30+ more docs]
```

---

## Step 1: Initialize Console

Open PowerShell and run:

```powershell
cd C:\Users\Admin\OneDrive\Desktop\~E14-
. .\E14-Console.ps1
```

You'll see:
```
╔════════════════════════════════════════════════════════════╗
║       .15% SOLAR WAGYU — DIGITAL CUT                       ║
║       E14 Master Control Console                           ║
╚════════════════════════════════════════════════════════════╝

Home: C:\Users\Admin\OneDrive\Desktop\~E14-

✓ manifests/
✓ cli/
✓ docs/
✓ config/

Ready. Type E14-Help for commands.
```

---

## Step 2: Run System Check

```powershell
E14-Check-All
```

This runs:
1. Docker status
2. K8s status
3. Engine health check
4. 7-dimension coherence validation

---

## Step 3: Start Cluster (Choose One)

### Option A: Docker (Local, 14 engines)
```powershell
E14-Docker-Start
E14-Docker-Status
```

### Option B: Kubernetes (Production, 3-10 replicas)
```powershell
E14-K8S-Deploy
E14-K8S-Status
```

---

## Monitoring in Real-Time

```powershell
# Watch Docker engines
E14-Gtop-Status   # Shows all 14 engines + health

# Watch K8s pods
E14-Gtop-K8-Status   # Shows pod replicas + scaling

# See topology
E14-Gtop-Map      # Visual ASCII map

# Validate coherence
E14-K8S-Coherence # 7-dimension check (✓ or ⚠ or ✗)
```

---

## Help & References

```powershell
# Show all commands
E14-Help

# View specific documentation
notepad C:\Users\Admin\OneDrive\Desktop\~E14-\docs\README.md
notepad C:\Users\Admin\OneDrive\Desktop\~E14-\docs\K8S-MU-ORCH-GUIDE.md
notepad C:\Users\Admin\OneDrive\Desktop\~E14-\docs\RHYTHM-GUIDE.md
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Initialize | `. .\E14-Console.ps1` |
| Full check | `E14-Check-All` |
| Start Docker | `E14-Docker-Start` |
| Start K8s | `E14-K8S-Deploy` |
| Check health | `E14-Gtop-Status` |
| Check K8s | `E14-K8S-Status` |
| Scale K8s | `E14-K8S-Scale 5` |
| Validate | `E14-K8S-Coherence` |
| Help | `E14-Help` |

---

## Troubleshooting

**Console won't load:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
. .\E14-Console.ps1
```

**Can't find Docker:**
```powershell
# Make sure Docker Desktop is running
docker ps
```

**Can't connect to K8s:**
```powershell
# Check kubectl is configured
kubectl config current-context
kubectl get nodes
```

**Coherence check fails:**
```powershell
# Check all 7 dimensions
E14-K8S-Coherence -Verbose
```

---

## What's in Each File

### E14-Console.ps1
Master control script. Load this first with `. .\E14-Console.ps1`

### cli/gtop.ps1
Docker topology CLI. Shows 14 engines + health.

### cli/gtop-k8.ps1
Kubernetes CLI. Status, map, rollout, scaling.

### cli/k8-mu-orch-coherence.ps1
7-dimension validator. Checks all systems aligned.

### manifests/docker-compose-14engines.yml
Deploy all 14 engines locally via Docker Compose.

### manifests/k8s-mu-orch-manifest.yaml
Deploy to Kubernetes (3-10 pods, auto-scaling).

### config/.env.lock
Lock parameters + wobble constants.

### docs/README.md
System overview.

### docs/K8S-MU-ORCH-GUIDE.md
Full Kubernetes deployment guide.

### docs/RHYTHM-GUIDE.md
Timing, pacing, and rhythm philosophy.

---

## Status Summary

✅ 14-engine system (Docker or K8s)
✅ Multi-user identity (JWT + RBAC)
✅ 90-day lock synchronization
✅ Rhythm-aware orchestration
✅ 7-dimension coherence validation
✅ Zero-trust networking
✅ Auto-scaling (K8s HPA)
✅ Full monitoring + health checks

**Ready for production.**

---

**Created:** 2026-04-04
**System:** .15% SOLAR WAGYU — DIGITAL CUT
**Console:** E14 Master Control
**Status:** ✅ OPERATIONAL
