# test_e14_offset_decay.py
# E14 Complete Synchronization Test Suite (REVISED)
# Offset-decay model: engines synchronize to global INVARIANT_PHASE = 0.0
# 周期調整 × オフセット減衰 × 熱ダンピング × 天気ゲート

import math
import random

GRID_SECONDS = 86400 * 2

ENGINES = [
    "E01","E02","E03","E04","E05","E06","E07",
    "E08","E09","E10","E11","E12","E13","E14"
]

AXES = ["tick", "beat", "breath", "cycle", "heat", "weather"]

INVARIANT_PHASE = 0.0  # Fixed global target (not time-dependent)
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

# NEW: Exponential decay instead of pullback blend
DECAY_FACTOR = 0.88     # How fast phase offsets shrink (0.60-0.80 range) [Tuned for breathing]
HEAT_DAMPING   = 0.02   # Heat toward target
WEATHER_SAFE_MAX = 0.6

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
    K = geometric mean of convergence ratios across all 6 axes.
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
    
    # Geometric mean
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
# STATE GENERATION & UPDATE (OFFSET-DECAY MODEL)
# ═══════════════════════════════════════════════════════════════

def init_state():
    """Initialize with randomized phase offsets."""
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
    Update temporal axes with exponential offset decay.
    
    Each engine's phase is pulled toward INVARIANT_PHASE via decay.
    Offset shrinks exponentially: offset(t+1) = offset(t) * decay_factor
    """
    for eng, axes in state.items():
        for axis in ["tick", "beat", "breath", "cycle"]:
            current = axes[axis]
            target = INVARIANT_PHASE
            
            # Compute signed offset
            offset = (current - target) % 86400.0
            if offset > 43200.0:  # Wrap to [-43200, 43200]
                offset -= 86400.0
            
            # Decay offset exponentially
            offset *= DECAY_FACTOR
            
            # New position
            axes[axis] = (target + offset) % 86400.0
    
    return state

def update_heat_axis(state, t):
    """Update heat axis with damping toward target."""
    for eng, axes in state.items():
        h = axes["heat"]
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
    """Run complete 172,800-second simulation with offset-decay model."""
    history = {}
    k_scores = []
    xyo_valid_count = 0
    safe_weather_count = 0
    weather_sum = 0.0

    state = init_state()

    print(f"Running {GRID_SECONDS}s simulation ({GRID_SECONDS/3600:.0f}h) with offset-decay model...")
    print(f"Decay factor: {DECAY_FACTOR} (higher = slower convergence)")
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

        # Deep copy state for history
        history[t] = {
            "axes": {eng: dict(axes) for eng, axes in state.items()},
            "weather_truth": w_truth,
            "xyo_valid": xyo_valid,
            "weather_scalar": w_scalar,
            "k_score": k,
        }

    verdict_5 = oracle_verdict(history, use_weather=False)
    verdict_6 = oracle_verdict(history, use_weather=True)

    stats = {
        "xyo_valid_ratio": xyo_valid_count / GRID_SECONDS,
        "safe_weather_ratio": safe_weather_count / GRID_SECONDS,
        "avg_weather_scalar": weather_sum / GRID_SECONDS,
        "k_scores": k_scores,
    }

    return verdict_5, verdict_6, history, stats

# ═══════════════════════════════════════════════════════════════
# REPORTING
# ═══════════════════════════════════════════════════════════════

def print_report(verdict_5, verdict_6, stats):
    """Generate human-readable report."""
    print()
    print("=" * 110)
    print("E14 OFFSET-DECAY CONVERGENCE TEST — FINAL REPORT")
    print("=" * 110)
    print()
    
    # 5-axis results
    print("[5-AXIS ORACLE] (temporal + thermal, no weather)")
    print(f"  Converged: {verdict_5['converged']}")
    print(f"  Convergence points: {verdict_5['count']} / {GRID_SECONDS}")
    ratio_5 = verdict_5["count"] / GRID_SECONDS if GRID_SECONDS else 0
    print(f"  Convergence ratio: {ratio_5:.4%}")
    
    if verdict_5["converged"]:
        print(f"  First hit: {verdict_5['first']}s ({verdict_5['first']/3600:.1f}h)")
        print(f"  Last hit: {verdict_5['last']}s ({verdict_5['last']/3600:.1f}h)")
        windows_5 = analyze_convergence_windows(verdict_5)
        print(f"  Contiguous windows: {len(windows_5)}")
        total_window_time = sum(end - start + 1 for start, end in windows_5)
        print(f"  Total window time: {total_window_time}s ({total_window_time/GRID_SECONDS:.2%})")
        for i, (start, end) in enumerate(windows_5[:15], 1):
            duration = end - start + 1
            print(f"    Window {i}: [{start}s, {end}s] ({duration}s, {start/3600:.2f}h–{end/3600:.2f}h)")
    print()
    
    # 6-axis results
    print("[6-AXIS ORACLE] (5-axis + weather + XYO)")
    print(f"  Converged: {verdict_6['converged']}")
    print(f"  Convergence points: {verdict_6['count']} / {GRID_SECONDS}")
    ratio_6 = verdict_6["count"] / GRID_SECONDS if GRID_SECONDS else 0
    print(f"  Convergence ratio: {ratio_6:.4%}")
    
    if verdict_6["converged"]:
        print(f"  First hit: {verdict_6['first']}s ({verdict_6['first']/3600:.1f}h)")
        print(f"  Last hit: {verdict_6['last']}s ({verdict_6['last']/3600:.1f}h)")
        windows_6 = analyze_convergence_windows(verdict_6)
        print(f"  Contiguous windows: {len(windows_6)}")
        total_window_time = sum(end - start + 1 for start, end in windows_6)
        print(f"  Total window time: {total_window_time}s ({total_window_time/GRID_SECONDS:.2%})")
        for i, (start, end) in enumerate(windows_6[:15], 1):
            duration = end - start + 1
            print(f"    Window {i}: [{start}s, {end}s] ({duration}s, {start/3600:.2f}h–{end/3600:.2f}h)")
    print()
    
    # Impact analysis
    print("[CONVERGENCE IMPACT ANALYSIS]")
    if verdict_5["converged"] and verdict_6["converged"]:
        ratio_reduction = (ratio_5 - ratio_6) / ratio_5 * 100 if ratio_5 > 0 else 0
        print(f"  5-axis convergence ratio: {ratio_5:.4%}")
        print(f"  6-axis convergence ratio: {ratio_6:.4%}")
        print(f"  Weather reduction impact: {ratio_reduction:.2f}%")
        print(f"  -> Weather + XYO gates reduce convergence by ~{ratio_reduction:.1f}%")
    print()
    
    # K-score analysis
    print("[K-SCORE (UNITY SCORE) ANALYSIS]")
    k_scores = stats["k_scores"]
    if k_scores:
        avg_k = sum(k_scores) / len(k_scores)
        max_k = max(k_scores)
        min_k = min(k_scores)
        
        k_high = sum(1 for k in k_scores if k >= 0.90)
        k_medium = sum(1 for k in k_scores if 0.70 <= k < 0.90)
        k_low = sum(1 for k in k_scores if k < 0.70)
        
        print(f"  Average K: {avg_k:.4f}")
        print(f"  Max K: {max_k:.4f}, Min K: {min_k:.4f}")
        print(f"  K >= 0.90: {k_high} seconds ({k_high/GRID_SECONDS:.2%})")
        print(f"  0.70 <= K < 0.90: {k_medium} seconds ({k_medium/GRID_SECONDS:.2%})")
        print(f"  K < 0.70: {k_low} seconds ({k_low/GRID_SECONDS:.2%})")
    print()
    
    # Weather & XYO stats
    print("[WEATHER & XYO STATISTICS]")
    print(f"  XYO witness valid: {stats['xyo_valid_ratio']:.2%}")
    print(f"  Safe weather periods: {stats['safe_weather_ratio']:.2%}")
    print(f"  Average weather scalar: {stats['avg_weather_scalar']:.4f}")
    print(f"  Weather safety threshold: {WEATHER_SAFE_MAX}")
    print()
    
    # System parameters
    print("[OFFSET-DECAY PARAMETERS]")
    print(f"  Decay factor: {DECAY_FACTOR} (exponential shrink rate)")
    print(f"  Heat damping rate: {HEAT_DAMPING}")
    print(f"  Invariant phase (global target): {INVARIANT_PHASE}")
    print(f"  Temporal axis tolerances:")
    for axis, tol in TOL.items():
        if axis in PERIODS:
            print(f"    {axis}: ±{tol} (period {PERIODS[axis]}s)")
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
    print("║" + " E14 OFFSET-DECAY SYNCHRONIZATION TEST SUITE ".center(108) + "║")
    print("║" + " オフセット減衰 × 熱ダンピング × 天気ゲート ".center(108) + "║")
    print("╚" + "═" * 108 + "╝")
    print()
    
    verdict_5, verdict_6, history, stats = run_full_simulation()
    print_report(verdict_5, verdict_6, stats)
