# test_e14_oracle_integrated.py
# E14 Integrated Test Suite
# 6-axis × 14-engine × 172,800-second simulation
# Weather truth + XYO witness + Oracle convergence

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
    "tick":   1.0,
    "beat":   4.0,
    "breath": 20.0,
    "cycle":  100.0,
}

# ═══════════════════════════════════════════════════════════════
# ORACLE CORE (5軸 + weather軸オプション)
# ═══════════════════════════════════════════════════════════════

def phase_diff(a, b):
    """Circular phase distance."""
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
    """Check if weather is stable + XYO-verified (weather ≤ 0.3)."""
    for eng, axes in state.items():
        w = axes["weather"]
        if w is None:
            return False
        # 0.0~0.3 = stable, >0.3 = danger
        if w > 0.3:
            return False
    return True

def ring_converged_5axis(state):
    """5-axis convergence (temporal + thermal, no weather)."""
    temporal_ok = all(axis_converged(state, ax) for ax in ["tick","beat","breath","cycle"])
    thermal_ok  = heat_converged(state)
    return temporal_ok and thermal_ok

def ring_converged_6axis(state):
    """6-axis convergence (5-axis + weather)."""
    if not ring_converged_5axis(state):
        return False
    return weather_converged(state)

# ═══════════════════════════════════════════════════════════════
# WEATHER TRUTH + XYO WITNESS MODEL
# ═══════════════════════════════════════════════════════════════

def simulate_weather_truth(t):
    """
    Simulate weather truth from BOM/satellite.
    Pattern: calm -> severe -> calm over 24h cycle.
    """
    day_phase = (t % 86400) / 86400.0
    # Sinusoidal pattern: 0.1 (calm) to 0.9 (severe)
    base = 0.1 + 0.8 * math.sin(day_phase * math.pi) ** 2
    noise = random.uniform(-0.05, 0.05)
    return max(0.0, min(1.0, base + noise))

def simulate_xyo_witness(t, weather_truth):
    """
    Simulate XYO witness availability.
    - 90% of the time: witness available
    - If weather > 0.95: witness rejects (too severe to verify)
    """
    if weather_truth > 0.95:
        return False
    return random.random() < 0.9

def normalize_weather_scalar(weather_truth, xyo_valid):
    """
    Apply XYO verification result to weather scalar.
    
    If XYO valid: use actual weather_truth
    If XYO invalid: assume danger (1.0)
    """
    if not xyo_valid:
        return 1.0  # Danger: cannot trust unverified data
    return weather_truth

# ═══════════════════════════════════════════════════════════════
# 6-AXIS STATE GENERATION
# ═══════════════════════════════════════════════════════════════

def init_state():
    """Initialize empty state for all 14 engines."""
    state = {}
    for eng in ENGINES:
        state[eng] = {
            "tick":   0.0,
            "beat":   0.0,
            "breath": 0.0,
            "cycle":  0.0,
            "heat":   HEAT_TARGET,
            "weather": None,
        }
    return state

def update_temporal_axes(state, t):
    """Update temporal axes (tick/beat/breath/cycle)."""
    for eng, axes in state.items():
        axes["tick"]   = (t * 20.0)   % 86400.0   # 20 Hz equivalent
        axes["beat"]   = (t * 5.0)    % 86400.0   # 5 Hz
        axes["breath"] = (t * 0.66)   % 86400.0   # 0.66 Hz
        axes["cycle"]  = (t * (1.0/12.0)) % 86400.0  # 1/12 Hz (12s period)
    return state

def update_heat_axis(state, t):
    """Update heat axis (oscillates around HEAT_TARGET)."""
    drift = 0.002 * math.sin(t / 3600.0)  # ±0.002 drift over 1h
    for eng, axes in state.items():
        axes["heat"] = HEAT_TARGET + drift
    return state

def update_weather_axis(state, t):
    """
    Update weather axis.
    Returns: (updated_state, weather_truth, xyo_valid, weather_scalar)
    """
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

# ═══════════════════════════════════════════════════════════════
# INTEGRATED SIMULATION
# ═══════════════════════════════════════════════════════════════

def run_full_simulation():
    """Run complete 172,800-second simulation."""
    history = {}
    
    print(f"Running {GRID_SECONDS}s simulation ({GRID_SECONDS/3600:.0f}h)...")
    
    for t in range(GRID_SECONDS):
        if (t + 1) % 43200 == 0:
            print(f"  Progress: {t / GRID_SECONDS * 100:.1f}%")
        
        state = init_state()
        state = update_temporal_axes(state, t)
        state = update_heat_axis(state, t)
        state, w_truth, xyo_valid, w_scalar = update_weather_axis(state, t)
        
        history[t] = {
            "axes": state,
            "weather_truth": w_truth,
            "xyo_valid": xyo_valid,
            "weather_scalar": w_scalar,
        }
    
    verdict_5 = oracle_verdict(history, use_weather=False)
    verdict_6 = oracle_verdict(history, use_weather=True)
    
    return verdict_5, verdict_6, history

# ═══════════════════════════════════════════════════════════════
# ANALYSIS & REPORTING
# ═══════════════════════════════════════════════════════════════

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

def print_report(verdict_5, verdict_6, history):
    """Generate human-readable report."""
    print()
    print("=" * 100)
    print("E14 INTEGRATED TEST SUITE — FINAL REPORT")
    print("=" * 100)
    print()
    
    # 5-axis results
    print("[5-AXIS ORACLE] (temporal + thermal, no weather)")
    print(f"  Converged: {verdict_5['converged']}")
    print(f"  Convergence points: {verdict_5['count']} / {GRID_SECONDS}")
    ratio_5 = verdict_5["count"] / GRID_SECONDS if GRID_SECONDS else 0
    print(f"  Convergence ratio: {ratio_5:.6%}")
    
    if verdict_5["converged"]:
        print(f"  First hit: {verdict_5['first']}s ({verdict_5['first']/3600:.1f}h)")
        print(f"  Last hit: {verdict_5['last']}s ({verdict_5['last']/3600:.1f}h)")
        windows_5 = analyze_convergence_windows(verdict_5)
        print(f"  Contiguous windows: {len(windows_5)}")
        for i, (start, end) in enumerate(windows_5[:5], 1):
            duration = end - start + 1
            print(f"    Window {i}: [{start}s, {end}s] ({duration}s)")
    print()
    
    # 6-axis results
    print("[6-AXIS ORACLE] (5-axis + weather + XYO)")
    print(f"  Converged: {verdict_6['converged']}")
    print(f"  Convergence points: {verdict_6['count']} / {GRID_SECONDS}")
    ratio_6 = verdict_6["count"] / GRID_SECONDS if GRID_SECONDS else 0
    print(f"  Convergence ratio: {ratio_6:.6%}")
    
    if verdict_6["converged"]:
        print(f"  First hit: {verdict_6['first']}s ({verdict_6['first']/3600:.1f}h)")
        print(f"  Last hit: {verdict_6['last']}s ({verdict_6['last']/3600:.1f}h)")
        windows_6 = analyze_convergence_windows(verdict_6)
        print(f"  Contiguous windows: {len(windows_6)}")
        for i, (start, end) in enumerate(windows_6[:5], 1):
            duration = end - start + 1
            print(f"    Window {i}: [{start}s, {end}s] ({duration}s)")
    print()
    
    # Weather & XYO analysis
    print("[WEATHER & XYO ANALYSIS]")
    xyo_valid_count = sum(1 for t in range(GRID_SECONDS) if history[t]["xyo_valid"])
    xyo_ratio = xyo_valid_count / GRID_SECONDS
    print(f"  XYO witness valid: {xyo_valid_count} / {GRID_SECONDS} ({xyo_ratio:.2%})")
    
    avg_weather = sum(history[t]["weather_scalar"] or 1.0 for t in range(GRID_SECONDS)) / GRID_SECONDS
    print(f"  Average weather scalar: {avg_weather:.4f}")
    
    safe_count = sum(1 for t in range(GRID_SECONDS) if (history[t]["weather_scalar"] or 1.0) <= 0.3)
    safe_ratio = safe_count / GRID_SECONDS
    print(f"  Safe weather periods: {safe_count} / {GRID_SECONDS} ({safe_ratio:.2%})")
    print()
    
    # Impact of weather on convergence
    print("[WEATHER IMPACT]")
    if verdict_5["converged"] and verdict_6["converged"]:
        ratio_reduction = (ratio_5 - ratio_6) / ratio_5 * 100 if ratio_5 > 0 else 0
        print(f"  5-axis ratio: {ratio_5:.6%}")
        print(f"  6-axis ratio: {ratio_6:.6%}")
        print(f"  Reduction due to weather: {ratio_reduction:.2f}%")
    print()
    
    print("=" * 100)
    print()

# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    random.seed(42)
    
    print()
    print("╔" + "═" * 98 + "╗")
    print("║" + " E14 INTEGRATED TEST SUITE — FULL SIMULATION ".center(98) + "║")
    print("╚" + "═" * 98 + "╝")
    print()
    
    verdict_5, verdict_6, history = run_full_simulation()
    print_report(verdict_5, verdict_6, history)
