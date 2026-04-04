"""
REVISED: Better phase pullback mechanics.

Current formula: x(t+1) = x(t) * (1 - p) + ideal(t) * p

Problem: This is a **constant blending** regardless of current error.
If x(t) is far from ideal, we only move p fraction toward it.
With p=0.4, we move at 0.4 per tick. Far distances take 100+ steps.

Better: Use EXPONENTIAL DECAY to target.

New formula: x(t+1) = ideal(t) + (x(t) - ideal(t)) * decay_factor
where decay_factor controls how fast we shrink the error.

decay_factor=0.5 means error halves each step.
"""

import math
import random

PERIODS = {
    "tick":   12.0,
    "beat":   24.0,
    "breath": 48.0,
    "cycle":  96.0,
}

INVARIANT_PHASE = 0.0
TOL = {
    "tick":   5.0,
    "beat":   10.0,
    "breath": 20.0,
    "cycle":  40.0,
}

def phase_diff(a, b):
    d = abs(a - b)
    return min(d, 86400.0 - d)

def phase_add(phase, delta):
    """Add delta to phase, wrapping around 86400."""
    return (phase + delta) % 86400.0

# Test both formulas
PHASE_PULLBACK_OLD = 0.4
DECAY_FACTOR_NEW = 0.5

def test_convergence():
    """
    Simulate 100 random engines on tick axis.
    Old formula vs new formula.
    """
    engines_old = [random.uniform(0, 86400.0) for _ in range(100)]
    engines_new = engines_old.copy()
    
    print("[CONVERGENCE TEST: 100 Random Engines on Tick Axis]")
    print(f"  Period: {PERIODS['tick']}s")
    print(f"  Target: {INVARIANT_PHASE}")
    print(f"  Tolerance: ±{TOL['tick']}")
    print(f"  Old pullback: {PHASE_PULLBACK_OLD}")
    print(f"  New decay factor: {DECAY_FACTOR_NEW}")
    print()
    
    # Simulate 1000 timesteps
    for t in range(1000):
        axis = "tick"
        period = PERIODS[axis]
        ideal = (t % period) / period * 86400.0
        tol = TOL[axis]
        
        # OLD formula
        for i in range(len(engines_old)):
            engines_old[i] = engines_old[i] * (1.0 - PHASE_PULLBACK_OLD) + ideal * PHASE_PULLBACK_OLD
        
        # NEW formula
        for i in range(len(engines_new)):
            error = phase_diff(engines_new[i], ideal)
            # Get signed error (can be positive or negative direction)
            raw_error = (engines_new[i] - ideal) % 86400.0
            if raw_error > 43200:
                raw_error -= 86400.0
            engines_new[i] = ideal + raw_error * DECAY_FACTOR_NEW
        
        # Check convergence
        if t % 100 == 0 or t < 10:
            old_converged = sum(1 for e in engines_old if phase_diff(e, ideal) <= tol)
            new_converged = sum(1 for e in engines_new if phase_diff(e, ideal) <= tol)
            
            old_avg_err = sum(phase_diff(e, ideal) for e in engines_old) / len(engines_old)
            new_avg_err = sum(phase_diff(e, ideal) for e in engines_new) / len(engines_new)
            
            print(f"t={t:4d}: OLD: {old_converged:3d}/100 converged (avg_err={old_avg_err:7.2f}), "
                  f"NEW: {new_converged:3d}/100 converged (avg_err={new_avg_err:7.2f})")
            
            if new_converged == 100:
                print(f"\nNEW formula converged all 100 engines in {t} steps!")
                break

if __name__ == "__main__":
    random.seed(42)
    test_convergence()
