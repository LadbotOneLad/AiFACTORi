# E14 QUICK REFERENCE — Session Checklist

## Current Status (End of Session)

**System**: Fully functional offset-decay oracle
**Test**: test_e14_offset_decay.py (WORKING)
**Success Rate**: 99.96% 5-axis, 57.76% 6-axis

---

## Quick Commands

### Run Full Simulation
```bash
cd "C:\Users\Admin\OneDrive\Desktop\~E14-"
python test_e14_offset_decay.py
```

### Edit Key Parameters
File: `test_e14_offset_decay.py` (around line 40)
```python
DECAY_FACTOR = 0.88          # Change this to tune convergence speed
WEATHER_SAFE_MAX = 0.6       # Change for weather gating threshold
TOL = {"tick": 5, ...}       # Change tolerances if needed
```

### Interpretation of Results

**5-AXIS Convergence Ratio**
- Target: 50–100% (higher = more convergence)
- Current: 99.96%
- Action: If too low, decrease DECAY_FACTOR

**6-AXIS vs 5-AXIS Ratio**
- Formula: (6-axis / 5-axis) * 100
- Current: 57.76% / 99.96% = 57.8%
- Meaning: Weather gates reduce by 42.2%

**K-Score Distribution**
- Bimodal (all 0.0 or 1.0): Current behavior ✓
- Gradual gradient (0.0→1.0): Adjust DECAY_FACTOR ↑

**Window Count**
- More windows = faster oscillation
- Current: 7,913 windows in 48h = 1 window per 22s
- Increase DECAY_FACTOR to reduce window count

---

## Decision Tree for Next Session

```
"Is bimodal K-score correct?"
├─ YES
│  ├─ Implement layer activation (Layer 1→2→3)
│  ├─ Add sealing logic (E12/E14)
│  └─ Move to Docker deployment
│
└─ NO (want smoother transitions)
   ├─ Try DECAY_FACTOR = 0.92
   └─ Rerun test and reassess
```

---

## Critical Parameters (Don't Change Without Reason)

```python
INVARIANT_PHASE = 0.0           # All engines sync to this phase
PERIODS = {12, 24, 48, 96}     # 4-axis rhythm periods (seconds)
HEAT_TARGET = 0.075             # Human-core thermal anchor
GRID_SECONDS = 172800           # 48-hour simulation window
```

---

## Engine Registry Reference

See `engines.yaml` for complete role mapping:
- **E01** (365): Validator — temporal sync
- **E02** (777): Sovereign — ultimate authority
- **E03** (101): Horizon — boundary observer
- **E04-E05**: Synchronizer/Integrator — phase locking
- **E06**: Witness — weather verification
- **E07**: Sentinel — environmental monitoring
- **E08-E09**: Pulse/Breath — human-scale rhythms
- **E10**: Watcher — long-term stability
- **E11**: Oracle — meta-oracle synthesizer
- **E12**: Closer — convergence lock
- **E13**: Harmonizer — rhythm coherence
- **E14**: Keeper — state archive & backup

**Layer Mapping** (for future implementation):
- Layer 1: E01, E03, E10 (validators)
- Layer 2: E04, E05, E13 (synchronizers)
- Layer 3: E02, E06-E09, E11-E12, E14 (full ensemble)

---

## File Locations

```
Main Simulation:  test_e14_offset_decay.py
Role Registry:    engines.yaml
Technical Docs:   CONVERGENCE-DIAGNOSIS.md
Status:           SESSION-COMPLETION.md
Changes:          CHANGES-SUMMARY.md
This File:        QUICK-REFERENCE.md
```

---

## Common Issues & Fixes

| Problem | Cause | Solution |
|---------|-------|----------|
| No convergence | DECAY_FACTOR too low | Increase to 0.85+ |
| Too many windows | DECAY_FACTOR too high | Decrease to 0.80–0.88 |
| 6-axis ratio too low | WEATHER_SAFE_MAX too strict | Increase from 0.6 to 0.7 |
| Convergence too fast | DECAY_FACTOR too close to 1.0 | Decrease to 0.80–0.85 |
| Tolerance violations | TOL values too tight | Increase (e.g., ±6, ±12, ±25, ±50) |

---

## Next Milestones

### Phase 1: Verification (Current)
- ✓ Offset-decay working
- ✓ Convergence detection working
- ⚠ Bimodal K-score (needs confirmation)

### Phase 2: Enhancement
- Layer-based activation (E01→E04→E02 cascading)
- Sealing logic (E12/E14 lock state)
- K-threshold gating (convergence only if K >= target)

### Phase 3: Deployment
- Docker containerization
- Kubernetes manifests
- Prometheus/Grafana monitoring
- Real-time K-score dashboard

---

## Emergency Rollback

If offset-decay fails unexpectedly:

**Revert to Last Known Good:**
```bash
git checkout test_e14_oracle_integrated.py
# (If not using git, manually restore from backup)
```

**Report Issue:**
Create new diagnostic with:
```bash
python analyze_convergence_failure.py
python root_cause_analysis.py
```

---

## Session Handoff Summary

**What was broken**: Time-dependent phase targets prevented convergence
**What was fixed**: Switched to fixed-target offset-decay model
**New test file**: test_e14_offset_decay.py (99.96% working)
**Current focus**: Confirm if bimodal K-score is desired behavior
**Next steps**: Layer activation + sealing logic

---

**Last Updated**: End of current session
**Test Status**: PASSING (172,730 convergence points on 5-axis)
**Ready for**: Next iteration or deployment planning
