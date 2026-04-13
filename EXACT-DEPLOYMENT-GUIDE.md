# 🎯 **EXACT E14 ORACLE DEPLOYMENT GUIDE**

## ✅ **WHAT TO DEPLOY**

**Deploy ONLY the docker-compose.yml — it handles everything.**

```powershell
cd "C:\Users\Admin\OneDrive\Desktop\~E14-"
docker-compose up -d
```

**That's it. All 5 services deploy automatically.**

---

## 📊 **WHAT DEPLOYS (5 SERVICES)**

| Service | Command | Purpose | Connects To |
|---------|---------|---------|-------------|
| **e14_oracle** | oracle_layer.py | Convergence detection | TaskManager (logs) |
| **e14_live** | e14_live.py | Real-time decisions | TaskManager (logs) |
| **e14_driftwatcher** | kotahitanga_driftwatcher.py | State monitoring | TaskManager (logs) |
| **e14_sympy** | kotahitanga_sympy.py | Math validation | TaskManager (logs) |
| **e14_taskmanager** | e14_seven_day_logger.py | **Aggregates all logs** | All services |

---

## 🔐 **LOCK CONFIGURATION (What's Active)**

```
Lock ID:           550e8400-e29b-41d4-a716-446655440000
Inception:         2025-01-14 10:00:00 UTC
Expiry:            2025-04-14 10:00:00 UTC
Duration:          90 days
Remaining:         89 days (ACTIVE NOW)
Root Hash:         a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
Phrase:            UNIT-LOCKED:14engines:90days:2025-01-14
```

**All services locked under single mechanism. One lock controls all 5 services.**

---

## 🌀 **WOBBLE CONFIGURATION (3-Strata Validation)**

```
WOBBLE_SUU:        0.05    (Stratum 1: Foundation)
WOBBLE_AHA:        0.075   (Stratum 2: Harmonic)
WOBBLE_RERE:       0.15    (Stratum 3: Resonance)

Formula:           H = (1/3)*SUU + (1/3)*AHA + (1/3)*RERE
Kotahitanja:       0.0917 (9.17% convergence baseline)
Status:            SYNCHRONIZED
```

**These wobble values are baked into lock-metadata.json. Don't change them.**

---

## 📋 **14-ENGINE RING (What's Connected)**

All 14 engines have metadata in `config/lock-metadata.json`:

```
E365   (Validator)   → TaskManager receives logs
E777   (Sovereign)   → TaskManager receives logs
E101   (Horizon)     → TaskManager receives logs
E1001  (Peer)        → TaskManager receives logs
E1002  (Peer)        → TaskManager receives logs
E1003  (Peer)        → TaskManager receives logs
E1004  (Peer)        → TaskManager receives logs
E1005  (Peer)        → TaskManager receives logs
E1006  (Peer)        → TaskManager receives logs
E1007  (Peer)        → TaskManager receives logs
E1008  (Peer)        → TaskManager receives logs
E1009  (Peer)        → TaskManager receives logs
E1010  (Peer)        → TaskManager receives logs
E1011  (Peer)        → TaskManager receives logs
E1012  (Keeper)      → TaskManager receives logs
```

**All 14 report to TaskManager. TaskManager aggregates everything.**

---

## 🔗 **TASKMANAGER CONNECTION DETAILS**

### **What TaskManager Does**
1. **Receives logs** from all 4 other services
2. **Aggregates** into unified 7-day rotating logs
3. **Validates** against lock-metadata.json (14 engines)
4. **Timestamps** with lock cycle information
5. **Archives** in `/logs` directory

### **TaskManager Configuration (in docker-compose.yml)**
```yaml
e14_taskmanager:
  command: ["python3", "e14_seven_day_logger.py"]
  env_file: ./config/.env.lock           # Reads lock data
  volumes:
    - ./config:/app/config:ro             # Reads 14-engine metadata
    - ./logs:/app/logs                    # Writes aggregated logs
```

### **TaskManager Reads From**
- Lock ID: `LOCK_ID=550e8400-e29b-41d4-a716-446655440000`
- Engine metadata: `lock-metadata.json` (all 14 engines)
- Wobble values: `WOBBLE_SUU`, `WOBBLE_AHA`, `WOBBLE_RERE`
- All 4 other services via syslog/file streaming

### **TaskManager Output Location**
```
/logs/
├── oracle/
│   ├── 2025-01-14.log  (Day 1)
│   ├── 2025-01-15.log  (Day 2)
│   └── ... (7-day rolling window)
├── live/
├── driftwatcher/
├── sympy/
└── aggregated/
    └── unified-log.json (all services)
```

---

## ⚙️ **CYCLE & WOBBLE BREAKDOWN**

### **What Is A Cycle**
- 90-day enforcement window
- **Cycle 1**: 2025-01-14 to 2025-04-14 (ACTIVE NOW)
- **Cycle 2**: Starts 2025-04-14 (auto-renewal)
- All engines validate against current cycle

### **What Wobble Does**
- **SUU (0.05)**: Foundation stability (tightest)
- **AHA (0.075)**: Harmonic alignment (medium)
- **RERE (0.15)**: Resonance tolerance (loosest)
- All 3 combined = K-value (0.0917 = 9.17%)

### **How TaskManager Uses Cycles**
1. Reads `LOCK_INCEPTION` and `LOCK_EXPIRY`
2. Calculates days elapsed in cycle
3. Tags every log entry with cycle number
4. When cycle expires, triggers renewal event
5. All 5 services get new lock values

---

## ✅ **EXACT DEPLOY COMMAND**

### **Start Everything**
```powershell
cd "C:\Users\Admin\OneDrive\Desktop\~E14-"
docker-compose up -d
```

### **Check Status (Immediately)**
```powershell
docker-compose ps
```

Expected output:
```
NAME               STATUS
e14_oracle         Up (health: starting)
e14_live           Up (health: starting)
e14_driftwatcher   Up (health: starting)
e14_sympy          Up (health: starting)
e14_taskmanager    Up (health: starting)
```

### **Monitor TaskManager (Key Service)**
```powershell
docker-compose logs -f e14_taskmanager
```

Expected output:
```
e14_taskmanager | [TaskManager] Initialized with lock: 550e8400-e29b-41d4...
e14_taskmanager | [TaskManager] Cycle: 1 | Days Elapsed: 1 | Days Remaining: 89
e14_taskmanager | [TaskManager] 14 engines registered from lock-metadata.json
e14_taskmanager | [TaskManager] Wobble values loaded: SUU=0.05, AHA=0.075, RERE=0.15
e14_taskmanager | [TaskManager] Aggregating logs from oracle, live, driftwatcher, sympy...
e14_taskmanager | [TaskManager] 7-day rolling archive active
```

---

## 🚀 **DOES ORDER MATTER?**

**No. All 5 services start automatically in correct order.**

docker-compose handles:
- ✅ Building images (if needed)
- ✅ Starting services in dependency order
- ✅ Passing environment variables (lock data)
- ✅ Mounting volumes (config, logs)
- ✅ Creating network
- ✅ Health checks

**You don't need to deploy them separately.**

---

## 📊 **DEEP DIVE: TASKMANAGER DATA FLOW**

```
Lock-Metadata.json (14 engines)
      ↓
.env.lock (wobble, lock ID)
      ↓
docker-compose.yml (passes to all services)
      ↓
TaskManager reads ALL of it
      ↓
Receives logs from:
  - e14_oracle → logs all convergence events
  - e14_live → logs all decision gates
  - e14_driftwatcher → logs all state changes
  - e14_sympy → logs all math validations
      ↓
TaskManager aggregates into:
  /logs/oracle/2025-01-14.log
  /logs/live/2025-01-14.log
  /logs/driftwatcher/2025-01-14.log
  /logs/sympy/2025-01-14.log
  /logs/aggregated/unified-log.json
      ↓
Every log entry tagged with:
  - Lock ID
  - Cycle number
  - Wobble values
  - Timestamp
  - Engine ID (from metadata)
```

---

## 🔍 **VERIFY EVERYTHING IS CONNECTED**

### **Check TaskManager Sees Lock Data**
```powershell
docker exec e14_taskmanager cat /app/config/.env.lock
```

Expected:
```
LOCK_ID=550e8400-e29b-41d4-a716-446655440000
LOCK_INCEPTION=2025-01-14T10:00:00.000Z
LOCK_EXPIRY=2025-04-14T10:00:00.000Z
WOBBLE_SUU=0.05
WOBBLE_AHA=0.075
WOBBLE_RERE=0.15
```

### **Check TaskManager Sees Engine Metadata**
```powershell
docker exec e14_taskmanager cat /app/config/lock-metadata.json | findstr "engineCount"
```

Expected:
```
"engineCount": 14
```

### **Check Logs Are Being Created**
```powershell
ls "C:\Users\Admin\OneDrive\Desktop\~E14-\logs"
```

Expected:
```
oracle/
driftwatcher/
sympy/
live/
taskmanager/
```

---

## 🎯 **FINAL ANSWER: WHAT TO DEPLOY**

### **Command**
```powershell
cd "C:\Users\Admin\OneDrive\Desktop\~E14-"
docker-compose up -d
```

### **What Happens**
- ✅ All 5 services deploy
- ✅ Lock data injected into all services
- ✅ Wobble values active (SUU=0.05, AHA=0.075, RERE=0.15)
- ✅ All 14 engines registered with TaskManager
- ✅ 89-day cycle enforced
- ✅ Logs start aggregating to `/logs`

### **Does Other Services Matter?**
**No.** They all deploy together. TaskManager automatically aggregates all logs.

### **Can You Deploy Just One?**
**Technically yes**, but TaskManager needs the others to aggregate logs. Deploy all 5.

---

## ✨ **QUICK REFERENCE**

| What | How | Status |
|------|-----|--------|
| Deploy all | `docker-compose up -d` | ✅ Recommended |
| Check status | `docker-compose ps` | ✅ Verify |
| View TaskManager logs | `docker-compose logs -f e14_taskmanager` | ✅ Monitor |
| Stop all | `docker-compose down` | ✅ Clean |
| View aggregated logs | `ls /logs/aggregated/` | ✅ Archive |

---

**TL;DR**: 
```
docker-compose up -d
docker-compose ps
docker-compose logs -f e14_taskmanager
```

**Everything else is automatic.** 🚀
