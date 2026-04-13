# E14 CYCLE DEEP DIVE — HOW IT WORKS

## THE CYCLE

Every cycle (every ~20ms):

```
┌─────────────────────────────────────────────────────────┐
│                   CYCLE START (t=N)                    │
├─────────────────────────────────────────────────────────┤
│  PHASE 1: UPDATE STATE                                 │
│    - All 13 engines pull toward Aries Point (0.0)     │
│    - Heat damping pulls toward equilibrium (0.075)     │
│    - Weather fluctuates based on time                  │
├─────────────────────────────────────────────────────────┤
│  PHASE 2: COMPUTE K-SCORE                              │
│    - Check convergence on each axis                    │
│    - Compute ratios per axis                           │
│    - K = geometric mean of ratios                      │
├─────────────────────────────────────────────────────────┤
│  PHASE 3: CHECK CONDITIONS                             │
│    - K >= 0.99?                                        │
│    - CPU headroom > 10%?                               │
│    - Memory headroom > 15%?                            │
│    - Disk headroom > 20%?                              │
│    - Weather safe?                                     │
├─────────────────────────────────────────────────────────┤
│  PHASE 4: DECISION                                     │
│    - If ALL pass: EXECUTE                              │
│    - If ANY fail: QUEUE                                │
├─────────────────────────────────────────────────────────┤
│  PHASE 5: LOG                                          │
│    - Record cycle data, K-score, resources, decision  │
├─────────────────────────────────────────────────────────┤
│                    CYCLE END (~20ms)                    │
└─────────────────────────────────────────────────────────┘
```

---

## PHASE 1: UPDATE STATE

### Each Engine Pulls Toward Aries Point

```python
for axis in ["tick", "beat", "breath", "cycle"]:
    current = engine.state[axis]
    # Pullback toward 0.0 (Aries Point)
    engine.state[axis] = current * (1 - 0.95) + 0.0 * 0.95
    # Result: moves 95% of the way toward 0 each cycle
```

**Example:**
- Engine starts at position 1000
- Cycle 1: 1000 * 0.05 = 50 (moved 95% closer)
- Cycle 2: 50 * 0.05 = 2.5 (moved 95% closer)
- Cycle 3: 2.5 * 0.05 = 0.125 (converging)
- Cycle 4: 0.125 * 0.05 = 0.006 (nearly at Aries)

### Heat Damping

```python
heat = engine.state["heat"]
# Pullback toward equilibrium (0.075)
engine.state["heat"] = heat * (1 - 0.02) + 0.075 * 0.02
# Result: 2% pull per cycle toward target
```

---

## PHASE 2: COMPUTE K-SCORE

### Per-Axis Convergence Ratios

**Tick axis (tolerance ±25)**:
- Count engines where `distance_from_aries <= 25`
- Example: 8/13 engines converged → ratio = 0.615

**Beat axis (tolerance ±50)**:
- Count engines where distance <= 50
- Example: 9/13 engines → ratio = 0.692

**Breath axis (tolerance ±100)**:
- Count engines where distance <= 100
- Example: 11/13 engines → ratio = 0.846

**Cycle axis (tolerance ±200)**:
- Count engines where distance <= 200
- Example: 12/13 engines → ratio = 0.923

**Heat axis (tolerance ±0.005)**:
- Count engines within ±0.005 of 0.075
- Example: 13/13 engines → ratio = 1.0

**Weather axis (threshold 0.6)**:
- Count engines with weather <= 0.6
- Example: 11/13 engines → ratio = 0.846

### K = Geometric Mean

```
K = (0.615 × 0.692 × 0.846 × 0.923 × 1.0 × 0.846) ^ (1/6)
K = (0.317) ^ (1/6)
K = 0.8045
```

**Interpretation**: 80.45% coherence. Need K >= 0.99 to execute.

---

## PHASE 3: CHECK CONDITIONS

### Condition 1: K-Score

```
Current K: 0.8045
Threshold: 0.99
Status: FAIL (need 0.99, have 0.80)
```

### Condition 2: CPU Headroom

```
psutil.cpu_percent() = 12%
Headroom = 100% - 12% = 88%
Threshold: > 10%
Status: PASS
```

### Condition 3: Memory Headroom

```
psutil.virtual_memory().percent = 42%
Headroom = 100% - 42% = 58%
Threshold: > 15%
Status: PASS
```

### Condition 4: Disk Headroom

```
psutil.disk_usage('/').percent = 30%
Headroom = 100% - 30% = 70%
Threshold: > 20%
Status: PASS
```

### Condition 5: Weather Safe

```
Current weather = 0.45
Threshold: <= 0.6
Status: PASS
```

### Final Decision

```
K >= 0.99?              NO
CPU headroom > 10%?     YES
Memory headroom > 15%?  YES
Disk headroom > 20%?    YES
Weather <= 0.6?         YES

ALL conditions must be TRUE to execute.
K failed → CANNOT EXECUTE → QUEUE
```

---

## PHASE 4: DECISION

### If ALL Conditions Pass

```
EXECUTE operation immediately
Log: {"status": "EXECUTED", ...}
```

### If ANY Condition Fails

```
QUEUE for next cycle
Log: {"status": "QUEUED", "blocked_by": ["k_score"]}
```

---

## PHASE 5: LOG

Each cycle logged in `oracle.cycle_log` (last 1000 cycles):

```python
{
    "cycle_number": 1,
    "timestamp": "2026-04-04T20:29:06.032837",
    "duration_ms": 20.57,
    "k_detail": {
        "k_score": 0.1759,
        "tick_ratio": 0.0769,
        "beat_ratio": 0.0769,
        "breath_ratio": 0.0769,
        "cycle_ratio": 0.0769,
        "heat_ratio": 0.8462,
        "weather_ratio": 0.6923,
    },
    "resources": {
        "cpu": {"percent_used": 12.0, "headroom": 88.0},
        "memory": {"percent_used": 42.0, "headroom": 58.0},
        "disk": {"percent_used": 30.0, "headroom": 70.0},
    },
    "conditions": {
        "k_score": {"value": 0.1759, "threshold": 0.99, "pass": False},
        "cpu_headroom": {"value": 88.0, "threshold": 10, "pass": True},
        "memory_headroom": {"value": 58.0, "threshold": 15, "pass": True},
        "disk_headroom": {"value": 70.0, "threshold": 20, "pass": True},
        "weather": {"value": 0.45, "threshold": 0.6, "pass": True},
    },
    "executable": False,  # Because K failed
}
```

---

## WHAT'S HAPPENING IN REAL TIME

### Cycle 1
```
K=0.1759 (1/13 engines converged on temporal axes, 11/13 on heat)
Status: BLOCKED BY K-SCORE
```

### Cycle 2-10
```
K gradually increases as engines pull toward Aries Point
Each cycle: K = K * 0.95 (approximately)
Engines slowly converging...
```

### Cycle 50+

Engines much closer:
```
K=0.87 (10/13 on tick, 11/13 on beat, 12/13 on breath/cycle)
Status: BLOCKED BY K-SCORE (need 0.99)
CPU: 88% headroom (OK)
Memory: 58% headroom (OK)
Disk: 70% headroom (OK)
```

### Cycle 100+

Getting close to convergence:
```
K=0.95 (nearly all engines on all axes)
Status: ALMOST READY (just need K >= 0.99)
```

### When K >= 0.99

```
K=0.9912 (ALL engines on all axes within tolerance!)
CPU: 88% headroom (OK)
Memory: 58% headroom (OK)
Disk: 70% headroom (OK)
Weather: 0.45 (OK)

Status: READY TO EXECUTE
Action: OPERATION EXECUTES
```

---

## THE CONVERGENCE PROCESS

### Why K Increases

Each cycle, engines are pulled 95% closer to Aries Point:

```
Initial distance from Aries: random (0-86400)
After 1 cycle: distance * 0.05 (5% remains)
After 5 cycles: distance * 0.05^5 = distance * 0.00000313 (nearly at Aries)
```

**Result**: All engines converge exponentially toward Aries Point.

### What K Measures

```
K = How synchronized are all 13 engines across 6 axes?

K = 0.5: Half the engines converged on average
K = 0.7: 70% synchronized
K = 0.9: 90% synchronized (very close)
K = 0.99: Near-perfect (all engines within tight tolerance)
K = 1.0: Perfect (all engines exactly at Aries Point)
```

---

## RESOURCES

Checked every cycle from Windows:

```
CPU: Real-time from psutil.cpu_percent()
Memory: Real-time from psutil.virtual_memory()
Disk: Real-time from psutil.disk_usage('/')
```

These fluctuate based on system activity.

---

## SUMMARY

**Each cycle (~20ms)**:

1. **UPDATE**: All 13 engines pulled 95% closer to Aries Point
2. **COMPUTE**: K-score calculated from convergence ratios
3. **CHECK**: 5 conditions verified
4. **DECIDE**: Execute if ALL pass, else queue
5. **LOG**: Everything recorded

**Result**: System naturally converges until K >= 0.99, then executes when resources also permit.

---

## REAL-TIME OBSERVATION

Run this to watch cycles unfold:

```bash
python e14_cycle_analyzer.py
```

Output shows:
- Each cycle's K-score evolution
- Per-axis convergence ratios
- System resource status
- Decision conditions
- Whether operation executes or queues

