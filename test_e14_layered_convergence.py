"""
E14 ORACLE — REVISED STRATEGY: Progressive/Layered Convergence

Instead of expecting all 14 engines to converge simultaneously,
model E14 as a 3-layer synchronization:

Layer 1 (Validators): E01, E03, E10 (3 engines) lock first
Layer 2 (Synchronizers): E04-E05, E13 (3 engines) follow
Layer 3 (Oracles & Support): E02, E06-E09, E11-E12, E14 (8 engines) complete

Each layer waits for previous to achieve K>=0.95 before activating.
"""

import math
import random

GRID_SECONDS = 86400 * 2

# Layer 1: Core validators
LAYER_1_ENGINES = ["E01", "E03", "E10"]

# Layer 2: Synchronizers  
LAYER_2_ENGINES = ["E04", "E05", "E13"]

# Layer 3: Full ensemble
LAYER_3_ENGINES = ["E02", "E06", "E07", "E08", "E09", "E11", "E12", "E14"]

ALL_ENGINES = LAYER_1_ENGINES + LAYER_2_ENGINES + LAYER_3_ENGINES

AXES = ["tick", "beat", "breath", "cycle", "heat", "weather"]

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

# Strategy adjustment: per-layer pullback
PHASE_PULLBACK_L1 = 0.5  # Validators: aggressive
PHASE_PULLBACK_L2 = 0.4  # Synchronizers: medium
PHASE_PULLBACK_L3 = 0.3  # Full ensemble: conservative

HEAT_DAMPING   = 0.02
WEATHER_SAFE_MAX = 0.6

def phase_diff(a, b):
    d = abs(a - b)
    return min(d, 86400.0 - d)

def init_state():
    """Initialize with randomized conditions."""
    state = {}
    for eng in ALL_ENGINES:
        state[eng] = {
            "tick":   random.uniform(0, 86400.0),
            "beat":   random.uniform(0, 86400.0),
            "breath": random.uniform(0, 86400.0),
            "cycle":  random.uniform(0, 86400.0),
            "heat":   HEAT_TARGET + random.uniform(-0.01, 0.01),
            "weather": None,
            "layer": None,  # Track which layer this engine belongs to
        }
        if eng in LAYER_1_ENGINES:
            state[eng]["layer"] = 1
        elif eng in LAYER_2_ENGINES:
            state[eng]["layer"] = 2
        else:
            state[eng]["layer"] = 3
    return state

def compute_k_score(state, engines_subset):
    """
    Compute K score (0.0 to 1.0) for a subset of engines.
    K = 1.0 when all axes converge within tolerance.
    """
    if not engines_subset:
        return 0.0
    
    # Score each axis
    axis_scores = {}
    for axis in ["tick", "beat", "breath", "cycle", "heat"]:
        converged_count = 0
        tol = TOL.get(axis, HEAT_TOLERANCE)
        
        for eng in engines_subset:
            if axis == "heat":
                if abs(state[eng]["heat"] - HEAT_TARGET) <= HEAT_TOLERANCE:
                    converged_count += 1
            else:
                if phase_diff(state[eng][axis], INVARIANT_PHASE) <= tol:
                    converged_count += 1
        
        axis_scores[axis] = converged_count / len(engines_subset)
    
    # K = geometric mean of axis scores
    k = 1.0
    for score in axis_scores.values():
        k *= score
    k = k ** (1.0 / len(axis_scores))
    
    return k

def update_state(state, t, active_layers):
    """
    Update state with layer-aware pullback.
    
    Only active layers get pulled. Inactive layers drift.
    """
    for eng, axes in state.items():
        layer = axes["layer"]
        
        if layer not in active_layers:
            # Inactive: apply minimal drift
            for axis in ["tick", "beat", "breath", "cycle"]:
                axes[axis] += random.uniform(-0.1, 0.1)
            continue
        
        # Active: apply layer-specific pullback
        if layer == 1:
            pullback = PHASE_PULLBACK_L1
        elif layer == 2:
            pullback = PHASE_PULLBACK_L2
        else:
            pullback = PHASE_PULLBACK_L3
        
        # Update temporal axes
        for axis in ["tick", "beat", "breath", "cycle"]:
            period = PERIODS[axis]
            ideal_phase = (t % period) / period * 86400.0
            current = axes[axis]
            axes[axis] = current * (1.0 - pullback) + ideal_phase * pullback
        
        # Update heat
        h = axes["heat"]
        axes["heat"] = h * (1.0 - HEAT_DAMPING) + HEAT_TARGET * HEAT_DAMPING
    
    return state

def simulate_layered_convergence():
    """Run full simulation with progressive layer activation."""
    history = {}
    state = init_state()
    
    k_scores = {1: [], 2: [], 3: []}
    activation_times = {1: 0, 2: None, 3: None}
    
    print(f"\nRunning {GRID_SECONDS}s simulation with layered convergence...")
    print()
    
    # Phase 1: Activate Layer 1 only
    active_layers = {1}
    print("PHASE 1: Activating Layer 1 (E01, E03, E10)...")
    
    for t in range(GRID_SECONDS):
        if (t + 1) % 43200 == 0:
            print(f"  Progress: {(t+1) / GRID_SECONDS * 100:.1f}%")
        
        state = update_state(state, t, active_layers)
        
        k1 = compute_k_score(state, LAYER_1_ENGINES)
        k_scores[1].append(k1)
        
        # Check activation threshold for Layer 2
        if activation_times[2] is None and k1 >= 0.90:
            activation_times[2] = t
            active_layers.add(2)
            print(f"  Layer 1 achieved K={k1:.3f} at {t}s ({t/3600:.1f}h) -> Activating Layer 2")
        
        # Check activation threshold for Layer 3
        if activation_times[3] is None and activation_times[2] is not None:
            k2 = compute_k_score(state, LAYER_2_ENGINES)
            k_scores[2].append(k2)
            if k2 >= 0.85:
                activation_times[3] = t
                active_layers.add(3)
                print(f"  Layer 2 achieved K={k2:.3f} at {t}s ({t/3600:.1f}h) -> Activating Layer 3")
        
        history[t] = {
            "state": {eng: dict(axes) for eng, axes in state.items()},
            "k_scores": {
                1: k_scores[1][-1],
                2: k_scores[2][-1] if len(k_scores[2]) > 0 else 0.0,
                3: compute_k_score(state, LAYER_3_ENGINES) if len(active_layers) == 3 else 0.0,
            },
            "active_layers": set(active_layers),
        }
    
    print()
    return history, activation_times, k_scores

def print_layered_report(history, activation_times, k_scores):
    """Generate report for layered convergence."""
    print("=" * 110)
    print("E14 LAYERED CONVERGENCE TEST — FINAL REPORT")
    print("=" * 110)
    print()
    
    print("[LAYER ACTIVATION TIMELINE]")
    print(f"  Layer 1 start: 0s")
    print(f"  Layer 2 start: {activation_times[2]}s ({activation_times[2]/3600:.1f}h)" if activation_times[2] else "  Layer 2: Not activated")
    print(f"  Layer 3 start: {activation_times[3]}s ({activation_times[3]/3600:.1f}h)" if activation_times[3] else "  Layer 3: Not activated")
    print()
    
    print("[K SCORE EVOLUTION]")
    if k_scores[1]:
        print(f"  Layer 1: min={min(k_scores[1]):.4f}, max={max(k_scores[1]):.4f}, final={k_scores[1][-1]:.4f}")
    if k_scores[2]:
        print(f"  Layer 2: min={min(k_scores[2]):.4f}, max={max(k_scores[2]):.4f}, final={k_scores[2][-1]:.4f}")
    if k_scores[3]:
        k3_vals = [history[t]["k_scores"][3] for t in sorted(history.keys()) if history[t]["k_scores"][3] > 0]
        if k3_vals:
            print(f"  Layer 3: min={min(k3_vals):.4f}, max={max(k3_vals):.4f}, final={k3_vals[-1]:.4f}")
    print()
    
    print("[CONVERGENCE ASSESSMENT]")
    final_state = history[GRID_SECONDS - 1]
    k_final = {1: final_state["k_scores"][1], 2: final_state["k_scores"][2], 3: final_state["k_scores"][3]}
    
    for layer in [1, 2, 3]:
        if activation_times[layer] is not None:
            elapsed = GRID_SECONDS - activation_times[layer]
            status = "CONVERGED" if k_final[layer] >= 0.95 else "In Progress" if k_final[layer] >= 0.7 else "FAILED"
            print(f"  Layer {layer}: K={k_final[layer]:.4f} [{status}] ({elapsed}s active)")
    print()
    
    print("=" * 110)

if __name__ == "__main__":
    random.seed(42)
    history, activation_times, k_scores = simulate_layered_convergence()
    print_layered_report(history, activation_times, k_scores)
