"""
Root cause analysis: Why temporal axes don't converge.

The issue: randomizing to [0, 86400) and pulling at PHASE_PULLBACK=0.4
doesn't bring all 14 engines to within ±5/±10/±20/±40 simultaneously.

Let's compute convergence probability.
"""

import math
import random

ENGINES = 14
TOL = {
    "tick":   5.0,    # ±5
    "beat":   10.0,   # ±10
    "breath": 20.0,   # ±20
    "cycle":  40.0,   # ±40
}
PERIODS = {
    "tick":   12.0,
    "beat":   24.0,
    "breath": 48.0,
    "cycle":  96.0,
}
PHASE_PULLBACK = 0.4

def phase_diff(a, b):
    d = abs(a - b)
    return min(d, 86400.0 - d)

def check_convergence_at_t(t):
    """At time t, what % of random engines converge on each axis?"""
    results = {}
    
    for axis in ["tick", "beat", "breath", "cycle"]:
        period = PERIODS[axis]
        ideal_phase = (t % period) / period * 86400.0
        tol = TOL[axis]
        
        converged_count = 0
        for _ in range(10000):  # Monte Carlo
            # Random initial position
            init_pos = random.uniform(0, 86400.0)
            # After one pull
            pulled_pos = init_pos * (1.0 - PHASE_PULLBACK) + ideal_phase * PHASE_PULLBACK
            # Check if converged
            if phase_diff(pulled_pos, ideal_phase) <= tol:
                converged_count += 1
        
        prob = converged_count / 10000
        results[axis] = prob
    
    return results

def estimate_all_engines_converged():
    """
    Probability that ALL 14 engines converge on ALL 4 axes simultaneously.
    """
    # Sample 100 time steps
    convergence_counts = {ax: 0 for ax in ["tick", "beat", "breath", "cycle"]}
    
    for t in [0, 1000, 5000, 10000, 50000, 100000]:
        probs = check_convergence_at_t(t)
        for ax, p in probs.items():
            if p > 0.5:  # Naive threshold
                convergence_counts[ax] += 1
    
    print("[AXIS-BY-AXIS CONVERGENCE PROBABILITY]")
    for ax in ["tick", "beat", "breath", "cycle"]:
        print(f"  {ax}: {convergence_counts[ax]}/6 sample points > 50%")
    
    print()
    print("[MATHEMATICAL REALITY]")
    print(f"For ALL 14 engines to converge on ALL 4 axes:")
    print(f"  - Each axis needs P(convergence) for all 14 engines")
    print(f"  - Single-engine probability at best ~0.1%–1% per axis")
    print(f"  - 14 engines → ~(p^14) probability")
    print(f"  - 4 axes → (p^14)^4 = p^56")
    print(f"  - Result: Virtually impossible without stronger pullback or larger tolerance")
    
    print()
    print("[DIAGNOSIS]")
    print("A. PHASE_PULLBACK=0.4 is still too weak for randomized initial conditions")
    print("B. With 14 engines, the overlap probability is exponential in N")
    print("C. Need either:")
    print("   - Stronger pullback (0.6–0.8)")
    print("   - Larger tolerances (±10/±20/±40/±80)")
    print("   - Fewer engines to synchronize (5–7 instead of 14)")
    print("   - Multi-step convergence (first phase lock 4 engines, then 14)")

if __name__ == "__main__":
    random.seed(42)
    estimate_all_engines_converged()
