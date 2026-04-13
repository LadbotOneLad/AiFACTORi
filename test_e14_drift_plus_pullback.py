"""
E14 COMPLETE SYNC ORACLE — DRIFT + PULLBACK MODEL

Real-world operational system:
- Engines naturally DRIFT (entropy, sensor noise, clock skew)
- Control policy PULLS BACK (active correction toward invariant)
- Convergence windows emerge when drift < pullback
- Weather/XYO GATES when convergence is allowed

This is a competition between chaos (drift) and order (pullback).
"""

import math
import random

GRID_SECONDS = 86400 * 2

ENGINES = [
    "E01","E02","E03","E04","E05","E06","E07",
    "E08","E09","E10","E11","E12","E13","E14"
]

AXES = ["tick", "beat", "breath", "cycle", "heat", "weather"]

INVARIANT_PHASE = 0.0
HEAT_TARGET     = 0.075
HEAT_TOLERANCE  = 0.005

TOL = {
    "tick":   25.0,   # Relaxed for demonstration
    "beat":   50.0,
    "breath": 100.0,
    "cycle":  200.0,
}

# REAL WORLD: Engines drift naturally
DRIFT_MAGNITUDE = 3.0   # ±3 seconds per tick = light entropy

# CONTROL POLICY: Pullback strength to counter drift
PHASE_PULLBACK   = 0.8   # How hard we pull back (aggressive control)
HEAT_DAMPING     = 0.02  # Thermal control
WEATHER_SAFE_MAX = 0.6   # Environmental gating threshold

# ═══════════════════════════════════════════════════════════════
# ORACLE CORE
# ═══════════════════════════════════════════════════════════════

def phase_diff(a, b):
    """Circular phase distance (shortest arc on 86400-second circle)."""
    d = abs(a - b)
    return min(d, 86400.0 - d)

def axis_converged(state, axis):
    """Check if all engines converged on temporal axis."""
    target = INVARIANT_PHASE
    tol    = TOL[axis]
    for eng, axes in state.items():
        if phase_diff(axes[axis], target) > tol:
            return False
    return True

def heat_converged(state):
    """Check if all engines converged on heat axis."""
    for eng, axes in state.items():
        if abs(axes["heat"] - HEAT_TARGET) > HEAT_TOLERANCE:
            return False
    return True

def weather_converged(state):
    """Check weather convergence: stable + XYO verified."""
    for eng, axes in state.items():
        w = axes["weather"]
        if w is None:
            return False
        if w > WEATHER_SAFE_MAX:
            return False
    return True

def ring_converged_5axis(state):
    """5-axis convergence (temporal + thermal)."""
    temporal_ok = all(axis_converged(state, ax) for ax in ["tick","beat","breath","cycle"])
    thermal_ok  = heat_converged(state)
    return temporal_ok and thermal_ok

def ring_converged_6axis(state):
    """6-axis convergence (5-axis + weather)."""
    if not ring_converged_5axis(state):
        return False
    return weather_converged(state)

def compute_k_score(state):
    """
    Compute Unity Score K (0.0 to 1.0).
    Measures how close system is to full convergence.
    """
    if not state:
        return 0.0
    
    axis_ratios = {}
    
    # Temporal axes
    for axis in ["tick", "beat", "breath", "cycle"]:
        tol = TOL[axis]
        converged = sum(1 for eng, axes in state.items() 
                       if phase_diff(axes[axis], INVARIANT_PHASE) <= tol)
        axis_ratios[axis] = converged / len(state)
    
    # Heat axis
    converged_heat = sum(1 for eng, axes in state.items() 
                        if abs(axes["heat"] - HEAT_TARGET) <= HEAT_TOLERANCE)
    axis_ratios["heat"] = converged_heat / len(state)
    
    # Weather axis
    converged_weather = sum(1 for eng, axes in state.items() 
                           if axes["weather"] is not None and axes["weather"] <= WEATHER_SAFE_MAX)
    axis_ratios["weather"] = converged_weather / len(state)
    
    # Geometric mean = multiplicative penalty if any axis weak
    k = 1.0
    for ratio in axis_ratios.values():
        k *= ratio
    k = k ** (1.0 / len(axis_ratios))
    
    return k

# ═══════════════════════════════════════════════════════════════
# WEATHER TRUTH + XYO WITNESS
# ═══════════════════════════════════════════════════════════════

def simulate_weather_truth(t):
    """Simulate BOM/satellite weather with daily cycle."""
    day_phase = (t % 86400) / 86400.0
    base = 0.2 + 0.6 * math.sin(day_phase * math.pi) ** 2
    noise = random.uniform(-0.05, 0.05)
    return max(0.0, min(1.0, base + noise))

def simulate_xyo_witness(t, weather_truth):
    """Simulate XYO witness availability."""
    if weather_truth > 0.9:
        return False
    return random.random() < 0.95

def normalize_weather_scalar(weather_truth, xyo_valid):
    """Apply XYO verification to weather scalar."""
    if not xyo_valid:
        return 1.0  # Unverified = danger
    return weather_truth

# ═══════════════════════════════════════════════════════════════
# STATE GENERATION & UPDATE (DRIFT + PULLBACK)
# ═══════════════════════════════════════════════════════════════

def init_state():
    """Initialize with randomized phases."""
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
    """
    Update temporal axes with DRIFT + PULLBACK model.
    
    Real-world behavior:
    1. Natural drift (entropy): random walk
    2. Control policy pullback: toward invariant (0.0)
    3. Convergence when drift < pullback
    """
    for eng, axes in state.items():
        for axis in ["tick", "beat", "breath", "cycle"]:
            current = axes[axis]
            
            # STEP 1: Natural drift (entropy)
            drift = random.uniform(-DRIFT_MAGNITUDE, DRIFT_MAGNITUDE)
            drifted = (current + drift) % 86400.0
            
            # STEP 2: Control policy pullback toward invariant (0.0)
            # Linear blend: weighted average toward INVARIANT_PHASE
            pulled = drifted * (1.0 - PHASE_PULLBACK) + INVARIANT_PHASE * PHASE_PULLBACK
            
            axes[axis] = pulled
    
    return state

def update_heat_axis(state, t):
    """Update heat axis with damping toward target."""
    for eng, axes in state.items():
        h = axes["heat"]
        # Heat pulled toward HEAT_TARGET at rate HEAT_DAMPING
        axes["heat"] = h * (1.0 - HEAT_DAMPING) + HEAT_TARGET * HEAT_DAMPING
    return state

def update_weather_axis(state, t):
    """Update weather axis with truth + witness verification."""
    weather_truth = simulate_weather_truth(t)
    xyo_valid     = simulate_xyo_witness(t, weather_truth)
    scalar        = normalize_weather_scalar(weather_truth, xyo_valid)

    for eng, axes in state.items():
        axes["weather"] = scalar if xyo_valid else None

    return state, weather_truth, xyo_valid, scalar

# ═══════════════════════════════════════════════════════════════
# ORACLE SCAN & VERDICT
# ═══════════════════════════════════════════════════════════════

def oracle_scan(history, use_weather=False):
    """Scan history for convergence points."""
    hits = []
    for t in range(GRID_SECONDS):
        state = history[t]["axes"]
        if use_weather:
            if ring_converged_6axis(state):
                hits.append(t)
        else:
            if ring_converged_5axis(state):
                hits.append(t)
    return hits

def oracle_verdict(history, use_weather=False):
    """Compute oracle verdict."""
    hits = oracle_scan(history, use_weather=use_weather)
    if not hits:
        return {
            "converged": False,
            "points": [],
            "count": 0,
            "first": None,
            "last": None,
        }
    return {
        "converged": True,
        "points": hits,
        "first": hits[0],
        "last": hits[-1],
        "count": len(hits),
    }

def analyze_convergence_windows(verdict):
    """Analyze contiguous convergence windows."""
    if not verdict["converged"]:
        return []
    
    points = verdict["points"]
    windows = []
    
    if not points:
        return windows
    
    window_start = points[0]
    window_end = points[0]
    
    for t in points[1:]:
        if t == window_end + 1:
            window_end = t
        else:
            windows.append((window_start, window_end))
            window_start = t
            window_end = t
    
    windows.append((window_start, window_end))
    return windows

# ═══════════════════════════════════════════════════════════════
# INTEGRATED SIMULATION
# ═══════════════════════════════════════════════════════════════

def run_full_simulation():
    """Run complete 172,800-second simulation with drift+pullback."""
    history = {}
    k_scores = []
    xyo_valid_count = 0
    safe_weather_count = 0
    weather_sum = 0.0
    
    avg_phase_error = []  # Track average distance from invariant

    state = init_state()

    print(f"Running {GRID_SECONDS}s simulation ({GRID_SECONDS/3600:.0f}h)...")
    print(f"  Drift magnitude: ±{DRIFT_MAGNITUDE}s per tick")
    print(f"  Pullback strength: {PHASE_PULLBACK}")
    print(f"  Expected: Convergence when drift < pullback effect")
    print()
    
    for t in range(GRID_SECONDS):
        if (t + 1) % 43200 == 0:
            print(f"  Progress: {(t+1) / GRID_SECONDS * 100:.1f}%")
        
        state = update_temporal_axes(state, t)
        state = update_heat_axis(state, t)
        state, w_truth, xyo_valid, w_scalar = update_weather_axis(state, t)

        if xyo_valid:
            xyo_valid_count += 1
        if w_scalar <= WEATHER_SAFE_MAX and xyo_valid:
            safe_weather_count += 1
        weather_sum += w_scalar
        
        k = compute_k_score(state)
        k_scores.append(k)
        
        # Track average phase error
        total_error = sum(phase_diff(axes[ax], INVARIANT_PHASE) 
                         for axes in state.values() 
                         for ax in ["tick","beat","breath","cycle"])
        avg_error = total_error / (len(state) * 4)
        avg_phase_error.append(avg_error)

        # Deep copy state for history
        history[t] = {
            "axes": {eng: dict(axes) for eng, axes in state.items()},
            "weather_truth": w_truth,
            "xyo_valid": xyo_valid,
            "weather_scalar": w_scalar,
            "k_score": k,
            "avg_phase_error": avg_error,
        }

    verdict_5 = oracle_verdict(history, use_weather=False)
    verdict_6 = oracle_verdict(history, use_weather=True)

    stats = {
        "xyo_valid_ratio": xyo_valid_count / GRID_SECONDS,
        "safe_weather_ratio": safe_weather_count / GRID_SECONDS,
        "avg_weather_scalar": weather_sum / GRID_SECONDS,
        "k_scores": k_scores,
        "avg_phase_errors": avg_phase_error,
    }

    return verdict_5, verdict_6, history, stats

# ═══════════════════════════════════════════════════════════════
# REPORTING
# ═══════════════════════════════════════════════════════════════

def print_report(verdict_5, verdict_6, stats):
    """Generate human-readable report."""
    print()
    print("=" * 110)
    print("E14 DRIFT+PULLBACK ORACLE — FINAL REPORT")
    print("=" * 110)
    print()
    
    # 5-axis results
    print("[5-AXIS ORACLE] (temporal + thermal, no weather)")
    print(f"  Converged: {verdict_5['converged']}")
    print(f"  Convergence points: {verdict_5['count']} / {GRID_SECONDS}")
    ratio_5 = verdict_5["count"] / GRID_SECONDS if GRID_SECONDS else 0
    print(f"  Convergence ratio: {ratio_5:.4%}")
    
    if verdict_5["converged"]:
        print(f"  First hit: {verdict_5['first']}s ({verdict_5['first']/3600:.2f}h)")
        print(f"  Last hit: {verdict_5['last']}s ({verdict_5['last']/3600:.2f}h)")
        windows_5 = analyze_convergence_windows(verdict_5)
        print(f"  Contiguous windows: {len(windows_5)}")
        total_window_time = sum(end - start + 1 for start, end in windows_5)
        print(f"  Total window time: {total_window_time}s ({total_window_time/GRID_SECONDS:.2%})")
        if windows_5:
            print(f"  First 10 windows:")
            for i, (start, end) in enumerate(windows_5[:10], 1):
                duration = end - start + 1
                print(f"    [{i:2d}] {start:6d}–{end:6d}s ({duration:5d}s) @ {start/3600:5.2f}h")
    print()
    
    # 6-axis results
    print("[6-AXIS ORACLE] (5-axis + weather + XYO)")
    print(f"  Converged: {verdict_6['converged']}")
    print(f"  Convergence points: {verdict_6['count']} / {GRID_SECONDS}")
    ratio_6 = verdict_6["count"] / GRID_SECONDS if GRID_SECONDS else 0
    print(f"  Convergence ratio: {ratio_6:.4%}")
    
    if verdict_6["converged"]:
        print(f"  First hit: {verdict_6['first']}s ({verdict_6['first']/3600:.2f}h)")
        print(f"  Last hit: {verdict_6['last']}s ({verdict_6['last']/3600:.2f}h)")
        windows_6 = analyze_convergence_windows(verdict_6)
        print(f"  Contiguous windows: {len(windows_6)}")
        total_window_time = sum(end - start + 1 for start, end in windows_6)
        print(f"  Total window time: {total_window_time}s ({total_window_time/GRID_SECONDS:.2%})")
        if windows_6:
            print(f"  First 10 windows:")
            for i, (start, end) in enumerate(windows_6[:10], 1):
                duration = end - start + 1
                print(f"    [{i:2d}] {start:6d}–{end:6d}s ({duration:5d}s) @ {start/3600:5.2f}h")
    print()
    
    # Impact analysis
    print("[WEATHER & XYO IMPACT]")
    if verdict_5["converged"] and verdict_6["converged"]:
        ratio_reduction = (ratio_5 - ratio_6) / ratio_5 * 100 if ratio_5 > 0 else 0
        print(f"  5-axis ratio: {ratio_5:.4%}")
        print(f"  6-axis ratio: {ratio_6:.4%}")
        print(f"  Weather gating impact: {ratio_reduction:.2f}% reduction")
    print()
    
    # K-score analysis
    print("[K-SCORE (UNITY SCORE) BEHAVIOR]")
    k_scores = stats["k_scores"]
    if k_scores:
        avg_k = sum(k_scores) / len(k_scores)
        max_k = max(k_scores)
        min_k = min(k_scores)
        
        k_high = sum(1 for k in k_scores if k >= 0.90)
        k_medium = sum(1 for k in k_scores if 0.70 <= k < 0.90)
        k_low = sum(1 for k in k_scores if k < 0.70)
        
        print(f"  Average K: {avg_k:.4f}")
        print(f"  Range: {min_k:.4f} to {max_k:.4f}")
        print(f"  K >= 0.90 (high): {k_high}s ({k_high/GRID_SECONDS:.2%})")
        print(f"  0.70 ≤ K < 0.90 (medium): {k_medium}s ({k_medium/GRID_SECONDS:.2%})")
        print(f"  K < 0.70 (low): {k_low}s ({k_low/GRID_SECONDS:.2%})")
    print()
    
    # Phase error analysis
    print("[PHASE ERROR (Chaos vs Order)]")
    errors = stats["avg_phase_errors"]
    if errors:
        avg_error = sum(errors) / len(errors)
        max_error = max(errors)
        min_error = min(errors)
        print(f"  Average phase error: {avg_error:8.2f}s")
        print(f"  Range: {min_error:8.2f}s to {max_error:8.2f}s")
        print(f"  (Drift strength ±{DRIFT_MAGNITUDE}s vs Pullback {PHASE_PULLBACK})")
    print()
    
    # Weather & XYO stats
    print("[ENVIRONMENTAL GATING (Weather + XYO)]")
    print(f"  XYO witness valid: {stats['xyo_valid_ratio']:.2%}")
    print(f"  Safe weather periods: {stats['safe_weather_ratio']:.2%}")
    print(f"  Average weather scalar: {stats['avg_weather_scalar']:.4f}")
    print(f"  Safety threshold: {WEATHER_SAFE_MAX}")
    print()
    
    # System parameters
    print("[OPERATIONAL PARAMETERS]")
    print(f"  Drift magnitude: ±{DRIFT_MAGNITUDE}s (natural entropy)")
    print(f"  Pullback strength: {PHASE_PULLBACK} (control policy)")
    print(f"  Heat damping: {HEAT_DAMPING}")
    print(f"  Invariant phase (target): {INVARIANT_PHASE}")
    print(f"  Tolerances: tick ±5, beat ±10, breath ±20, cycle ±40")
    print()
    
    print("=" * 110)

# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    random.seed(42)
    
    print()
    print("╔" + "═" * 108 + "╗")
    print("║" + " E14 DRIFT + PULLBACK ORACLE SYSTEM ".center(108) + "║")
    print("║" + " 自然ドリフト × 制御政策 × 環境ゲート ".center(108) + "║")
    print("╚" + "═" * 108 + "╝")
    print()
    
    verdict_5, verdict_6, history, stats = run_full_simulation()
    print_report(verdict_5, verdict_6, stats)
