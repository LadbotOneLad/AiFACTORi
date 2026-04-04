"""
Diagnostic: Why is convergence failing with A+C+D adjustments?
Test each axis separately to identify the bottleneck.
"""

import math
import random

ENGINES = [
    "E01","E02","E03","E04","E05","E06","E07",
    "E08","E09","E10","E11","E12","E13","E14"
]

INVARIANT_PHASE = 0.0
HEAT_TARGET     = 0.075
HEAT_TOLERANCE  = 0.005

TOL = {
    "tick":   5.0,
    "beat":   10.0,
    "breath": 20.0,
    "cycle":  40.0,
}

PERIODS = {
    "tick":   12.0,
    "beat":   24.0,
    "breath": 48.0,
    "cycle":  96.0,
}

PHASE_PULLBACK = 0.4
HEAT_DAMPING   = 0.02

def phase_diff(a, b):
    d = abs(a - b)
    return min(d, 86400.0 - d)

def init_state():
    state = {}
    for eng in ENGINES:
        state[eng] = {
            "tick":   random.uniform(0, 86400.0),
            "beat":   random.uniform(0, 86400.0),
            "breath": random.uniform(0, 86400.0),
            "cycle":  random.uniform(0, 86400.0),
            "heat":   HEAT_TARGET + random.uniform(-0.01, 0.01),
            "weather": None,
        }
    return state

def update_temporal_axes(state, t):
    for eng, axes in state.items():
        for axis in ["tick","beat","breath","cycle"]:
            period = PERIODS[axis]
            ideal_phase = (t % period) / period * 86400.0
            current = axes[axis]
            axes[axis] = current * (1.0 - PHASE_PULLBACK) + ideal_phase * PHASE_PULLBACK
    return state

def update_heat_axis(state, t):
    for eng, axes in state.items():
        h = axes["heat"]
        axes["heat"] = h * (1.0 - HEAT_DAMPING) + HEAT_TARGET * HEAT_DAMPING
    return state

def analyze_per_axis_convergence():
    """Test convergence on each axis independently."""
    state = init_state()
    GRID = 172800
    
    axis_converge_times = {ax: [] for ax in ["tick","beat","breath","cycle","heat"]}
    
    print("\n[DIAGNOSTIC: Per-Axis Convergence Analysis]")
    print()
    
    for t in range(GRID):
        state = update_temporal_axes(state, t)
        state = update_heat_axis(state, t)
        
        # Check each axis
        for axis in ["tick","beat","breath","cycle"]:
            if axis not in axis_converge_times:
                continue
            
            tol = TOL[axis]
            all_converged = True
            for eng, axes in state.items():
                if phase_diff(axes[axis], INVARIANT_PHASE) > tol:
                    all_converged = False
                    break
            
            if all_converged:
                axis_converge_times[axis].append(t)
        
        # Heat
        all_heat_converged = True
        for eng, axes in state.items():
            if abs(axes["heat"] - HEAT_TARGET) > HEAT_TOLERANCE:
                all_heat_converged = False
                break
        if all_heat_converged:
            axis_converge_times["heat"].append(t)
    
    # Report
    for axis in ["tick","beat","breath","cycle","heat"]:
        hits = axis_converge_times[axis]
        ratio = len(hits) / GRID * 100
        print(f"{axis:8s}: {len(hits):5d} converge points ({ratio:6.2f}%)", end="")
        if hits:
            print(f" | first={hits[0]}s, last={hits[-1]}s")
        else:
            print()
    
    # Combined analysis
    print()
    print("[5-AXIS COMBINATION CHECK]")
    
    # Count simultaneous convergence
    tick_set = set(axis_converge_times["tick"])
    beat_set = set(axis_converge_times["beat"])
    breath_set = set(axis_converge_times["breath"])
    cycle_set = set(axis_converge_times["cycle"])
    heat_set = set(axis_converge_times["heat"])
    
    all_5_set = tick_set & beat_set & breath_set & cycle_set & heat_set
    print(f"Simultaneous 5-axis convergence: {len(all_5_set)} points")
    
    if len(all_5_set) > 0:
        print(f"  First: {min(all_5_set)}s, Last: {max(all_5_set)}s")
    
    # Check pairwise overlaps
    print()
    print("[PAIRWISE OVERLAP ANALYSIS]")
    pairs = [
        ("tick", "beat"), ("tick", "breath"), ("tick", "cycle"), ("tick", "heat"),
        ("beat", "breath"), ("beat", "cycle"), ("beat", "heat"),
        ("breath", "cycle"), ("breath", "heat"),
        ("cycle", "heat"),
    ]
    
    for a, b in pairs:
        set_a = set(axis_converge_times[a])
        set_b = set(axis_converge_times[b])
        overlap = len(set_a & set_b)
        print(f"  {a} ∩ {b}: {overlap}")

if __name__ == "__main__":
    random.seed(42)
    analyze_per_axis_convergence()
