# E14 ORACLE — FILES & WHAT TO USE

## 🚀 PRODUCTION-READY (Use These)

### Core System
- **test_e14_real_world_operational.py** 
  - Main monitoring simulation
  - Measures K-score, decision windows, phase error
  - Run this to test your system
  - OUTPUT: Decision window metrics + operational readiness status

### Configuration & Registry
- **engines.yaml**
  - 14-engine role registry
  - Don't modify unless adding engines
  - Reference for understanding roles

### Supporting Library
- **kotahitanga_sympy.py**
  - K-score mathematics (if you need to understand the math)
  - Optional, read-only reference

---

## 📖 DOCUMENTATION (Read These)

### Quick Start (10 min)
1. **FINAL-SUMMARY.md** ← Start here
2. **OPERATIONAL-GAIN-SUMMARY.md** ← Why this matters

### Implementation (1–2 hours)
3. **TUNING-GUIDE.md** ← How to calibrate parameters
4. **DEPLOYMENT-CHECKLIST.md** ← Step-by-step to production

### Reference (As needed)
- **QUICK-REFERENCE.md** ← Cheat sheet & commands

---

## 📦 LEGACY / EXPERIMENTAL (Don't Use)

### Broken/Superseded
- ❌ test_e14_oracle_integrated_fullsync.py (zero convergence)
- ❌ test_e14_offset_decay.py (theoretical only)
- ❌ test_e14_layered_convergence.py (layer concept not needed)
- ❌ test_e14_drift_plus_pullback.py (prototype, use real_world_operational instead)

### Diagnostic Only
- ❌ analyze_convergence_failure.py (debug artifact)
- ❌ root_cause_analysis.py (analysis only)
- ❌ test_convergence_mechanics.py (exploration)
- ❌ sweep_decay_factor.py (tuning experiment)

### Deprecated Documentation
- ❌ SESSION-CONTINUATION-SUMMARY.md (old approach)
- ❌ SESSION-COMPLETION.md (old approach)
- ❌ CHANGES-SUMMARY.md (old approach)
- ❌ CONVERGENCE-DIAGNOSIS.md (old approach)

---

## ✅ WHAT TO DO NOW

### Option 1: Quick Understanding (15 min)
```
1. Read: FINAL-SUMMARY.md
2. Run: python test_e14_real_world_operational.py
3. Look at: K-Score output
```

### Option 2: Full Implementation (2–3 hours)
```
1. Read: OPERATIONAL-GAIN-SUMMARY.md
2. Read: TUNING-GUIDE.md
3. Measure: Your actual drift (NTP precision, clock sync, etc.)
4. Run: test_e14_real_world_operational.py with your drift value
5. Tune: DRIFT_MAGNITUDE and PHASE_PULLBACK
6. Test: Until decision windows appear
```

### Option 3: Production Deployment (1 week)
```
Follow: DEPLOYMENT-CHECKLIST.md
  Phase 1: Calibration (1–2 hours)
  Phase 2: Monitoring setup (2–4 hours)
  Phase 3: Decision automation (4–8 hours)
  Phase 4: Docker + Kubernetes (1 day)
  Phase 5: Operational monitoring (ongoing)
```

---

## 🎯 YOUR WORKFLOW

### 1. Understand
```bash
cd ~/E14-
cat FINAL-SUMMARY.md
```

### 2. Test
```bash
python test_e14_real_world_operational.py
```

### 3. Calibrate
```python
# Edit test_e14_real_world_operational.py line 38-42
DRIFT_MAGNITUDE = 1.0    # Your measured drift
PHASE_PULLBACK = 0.90    # Try 0.85–0.95
K_THRESHOLD_HIGH = 0.80  # Try 0.70–0.90

# Run again
python test_e14_real_world_operational.py
```

### 4. Monitor
```
Follow DEPLOYMENT-CHECKLIST.md Phase 2
  → Prometheus integration
  → Grafana dashboard
  → Alerting
```

### 5. Deploy
```
Follow DEPLOYMENT-CHECKLIST.md Phase 3–5
  → Decision automation
  → Docker containerization
  → Kubernetes deployment
  → Operations handoff
```

---

## 📋 FILE CLASSIFICATION

| File | Type | Status | Use |
|------|------|--------|-----|
| test_e14_real_world_operational.py | Code | ✅ LIVE | Deploy this |
| engines.yaml | Config | ✅ LIVE | Reference |
| kotahitanga_sympy.py | Library | ✅ LIVE | Optional |
| FINAL-SUMMARY.md | Doc | ✅ LIVE | Read first |
| OPERATIONAL-GAIN-SUMMARY.md | Doc | ✅ LIVE | Understand why |
| TUNING-GUIDE.md | Doc | ✅ LIVE | Calibrate |
| DEPLOYMENT-CHECKLIST.md | Doc | ✅ LIVE | Implement |
| QUICK-REFERENCE.md | Doc | ✅ LIVE | Cheat sheet |
| test_e14_offset_decay.py | Code | ❌ OLD | Archive only |
| test_e14_oracle_integrated_fullsync.py | Code | ❌ OLD | Archive only |
| CONVERGENCE-DIAGNOSIS.md | Doc | ❌ OLD | Archive only |
| SESSION-*.md | Doc | ❌ OLD | Archive only |

---

## 🚨 CRITICAL FILES TO KEEP

**These must exist for deployment**:
- ✓ test_e14_real_world_operational.py
- ✓ engines.yaml
- ✓ TUNING-GUIDE.md
- ✓ DEPLOYMENT-CHECKLIST.md

**These can be archived**:
- ✓ Everything else with ❌ status

---

## 🔧 HOW TO ADAPT FOR YOUR USE CASE

### Blockchain Consensus
```python
# In test_e14_real_world_operational.py
DRIFT_MAGNITUDE = 0.5    # NTP-synced nodes
PHASE_PULLBACK = 0.92    # Strong consensus
K_THRESHOLD_HIGH = 0.95  # Ultra-safe (block finalization)
```

### Autonomous Fleet
```python
DRIFT_MAGNITUDE = 2.0    # GPS sync + wireless latency
PHASE_PULLBACK = 0.88    # Medium-strong control
K_THRESHOLD_HIGH = 0.80  # Medium confidence (maneuver safety)
```

### Distributed Payment
```python
DRIFT_MAGNITUDE = 0.5    # Atomic clocks
PHASE_PULLBACK = 0.95    # Maximum control
K_THRESHOLD_HIGH = 0.90  # High confidence (money at stake)
```

### Multi-Agent Trading
```python
DRIFT_MAGNITUDE = 1.0    # Low-latency network
PHASE_PULLBACK = 0.85    # Medium control
K_THRESHOLD_HIGH = 0.70  # Accept medium confidence (speed matters)
```

---

## 📞 SUPPORT

- **"What does K-score mean?"** → Read OPERATIONAL-GAIN-SUMMARY.md
- **"How do I tune parameters?"** → Read TUNING-GUIDE.md
- **"How do I deploy?"** → Follow DEPLOYMENT-CHECKLIST.md
- **"How do I understand the math?"** → Check FINAL-SUMMARY.md "The Math Behind It"
- **"What if decision windows disappear?"** → See QUICK-REFERENCE.md "Common Issues"

---

## ✨ SUMMARY

**Keep:**
- test_e14_real_world_operational.py (core system)
- engines.yaml (registry)
- FINAL-SUMMARY.md, OPERATIONAL-GAIN-SUMMARY.md, TUNING-GUIDE.md, DEPLOYMENT-CHECKLIST.md (docs)

**Ignore/Archive:**
- Everything else marked ❌

**Action:**
1. Read FINAL-SUMMARY.md (10 min)
2. Run test_e14_real_world_operational.py (5 min)
3. Tune parameters (30 min)
4. Deploy (follow checklist)

**Timeline to Production**: 1 week with this guide.
