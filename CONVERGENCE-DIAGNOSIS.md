# E14 System — Convergence Analysis & Next Steps

## Root Cause Analysis

### What A+C+D Revealed
1. **A (Stronger pullback 0.10→0.4)**: Applied successfully
2. **C (Randomized initial conditions)**: Applied successfully  
3. **D (Relaxed weather gating 0.4→0.6)**: Applied successfully

**Result**: 0 convergence points across 172,800s (48h)

### Why Convergence Failed

**Mathematical Reality:**
- 14 engines must all converge within ±5/±10/±20/±40 on 4 axes **simultaneously**
- With randomized initial state [0, 86400) and pullback=0.4:
  - Single engine → ~0.1% chance to reach tolerance per tick per axis
  - 14 engines → p^14 ≈ 10^-28 (impossible)
  - 4 axes → (p^14)^4 (even more impossible)

**Hidden Problem in Convergence Formula:**
- Current: `x(t+1) = x(t) * (1-p) + ideal(t) * p`
- Issue: `ideal(t)` itself **changes every timestep** as t advances
- Target is a **moving phase** relative to the ticking clock
- Engines are chasing a constantly-moving ideal, never catching it

**Net Effect:** System oscillates around ideal rather than converging

---

## Session Summary vs. Current Reality

### Original Philosophy (Session Summary)
> "E14 is a **Complete Synchronization Type** system:
> - Naturally disperses (entropy)
> - Actively pulls back to invariant (control policy via phase pullback)
> - Responds to environment (weather gating + XYO witness)
> - Synchronizes completely when all conditions align (K=1.0)"

### Problem with Current Implementation
The original design expects:
- A **static invariant phase** (INVARIANT_PHASE = 0.0)
- All engines to **phase-lock** to this constant
- Weather/XYO acts as a **gating mechanism** for when lock is allowed

But the current code implements:
- A **time-dependent phase target** that varies with period
- Impossible simultaneous convergence across 14 engines
- No incremental locking mechanism

---

## Proposed Fix: Return to Design Intent

### Revised Understanding

**E14 operates in "breaths":**

1. **Dispersal Phase (0–60s)**: 
   - All 14 engines drift slightly (entropy)
   - Thermal damping holds heat near target
   - Weather/XYO accumulate witness data

2. **Convergence Phase (60–120s)**:
   - When K-score crosses threshold (0.7+)
   - Pullback strengthens temporarily
   - Engines spiral toward INVARIANT_PHASE = 0.0 globally
   - All temporal axes lock to 0.0 (perfect synchronization)

3. **Seal Phase (120–180s)**:
   - If K=1.0 achieved and weather safe
   - Keeper (E14) locks entire state
   - No further divergence until window closes

### Implementation Strategy

**Option A: Simpler Math (Recommended)**
- Store `phase_offset` per engine (deviation from ideal 0.0)
- Pullback **shrinks offset** exponentially: `offset → offset * decay_factor`
- When `|offset| < tol` for all engines on all axes: **full convergence**
- No moving targets; pure exponential decay to fixed point

**Option B: Staged Synchronization**
- Lock 3 engines (E01, E03, E10) first
- Once Layer 1 K ≥ 0.95, add Layer 2 (E04, E05, E13)
- Once Layer 2 K ≥ 0.85, add Layer 3 (remaining 8)
- Exponential cascade of lock events

**Option C: Reduce Ensemble**
- Start with 5–7 "core" engines instead of 14
- Verify breathing pattern at smaller scale
- Add remaining engines in production deployment

---

## Recommended Next Steps

### Immediate (Next Session)
1. **Choose Option A** (simplest, clearest)
2. Rewrite convergence mechanics:
   ```
   # Each engine has a phase OFFSET from global invariant
   engine.tick_offset = initial_random()
   # Each tick: exponentially decay offset
   engine.tick_offset *= decay_factor  # e.g., 0.6
   # Convergence: all offsets below tolerance
   ```
3. Test with 172,800s simulation
4. Expect to see **breathing windows** (periodic convergence bursts)

### Key Constants to Lock In
```
INVARIANT_PHASE = 0.0              # Fixed global target
DECAY_FACTOR = 0.60-0.80           # How fast offset shrinks
PERIODS = {12, 24, 48, 96}s        # Unchanged
TOLERANCES = {±5, ±10, ±20, ±40}   # Unchanged
```

### Success Criteria
- **50+ convergence windows** across 48h window
- **Periodic breathing pattern** (not random)
- **5-axis convergence**: ~30+ windows
- **6-axis convergence**: ~10–20 windows (weather gating reduces)
- K-scores showing cyclical rise/fall pattern

---

## Files to Modify
1. `test_e14_oracle_integrated_fullsync.py` — Rewrite phase pullback logic
2. Keep `engines.yaml` intact (role mapping still valid)
3. Create new `test_e14_offset_decay.py` for Option A testing

---

## Not Changing (Per Session Summary)
- **B (Tolerance adjustment)**: Deferred until breathing pattern confirmed
- 14 engines total
- 6-axis architecture
- Weather/XYO witness layer

