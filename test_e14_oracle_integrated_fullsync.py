# test_e14_oracle_integrated_fullsync.py
# E14 Complete Synchronization Test Suite
# 周期調整 + 位相引き戻し + heat damping + weather gating
# 完全同期型シミュレーション

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

# 完全同期型用：周期を「12 の倍数」に寄せる
TOL = {
    "tick":   5.0,
    "beat":   10.0,
    "breath": 20.0,
    "cycle":  40.0,
}

# 周期（秒）を揃える：LCM が小さくなるように設計
PERIODS = {
    "tick":   12.0,   # 12秒で一周
    "beat":   24.0,   # 24秒で一周
    "breath": 48.0,   # 48秒で一周
    "cycle":  96.0,   # 96秒で一周
}

PHASE_PULLBACK = 0.4    # 位相を invariant に引き戻す強さ [A: Strengthened]
HEAT_DAMPING   = 0.02   # heat をコアに戻す割合
WEATHER_SAFE_MAX = 0.6  # これを超えると収束禁止 [D: Relaxed]

# ═══════════════════════════════════════════════════════════════
# ORACLE CORE
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

# ═══════════════════════════════════════════════════════════════
# WEATHER TRUTH + XYO WITNESS
# ═══════════════════════════════════════════════════════════════

def simulate_weather_truth(t):
    """Simulate BOM/satellite weather with daily cycle."""
    day_phase = (t % 86400) / 86400.0
    base = 0.2 + 0.6 * math.sin(day_phase * math.pi) ** 2  # 0.2~0.8
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
        return 1.0  # Danger: unverified
    return weather_truth

# ═══════════════════════════════════════════════════════════════
# STATE GENERATION (COMPLETE SYNC TYPE)
# ═══════════════════════════════════════════════════════════════

def init_state():
    """Initialize state for all 14 engines with randomized conditions [C: Chaotic start]."""
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
    Update temporal axes with phase pullback control policy.
    
    Each axis has a target period. Current phase is pulled toward
    ideal position at rate PHASE_PULLBACK.
    """
    for eng, axes in state.items():
        for axis in ["tick","beat","breath","cycle"]:
            period = PERIODS[axis]
            # Ideal phase: where we want to be
            ideal_phase = (t % period) / period * 86400.0
            # Current phase
            current = axes[axis]
            # Pullback: weighted blend toward ideal
            axes[axis] = current * (1.0 - PHASE_PULLBACK) + ideal_phase * PHASE_PULLBACK
    return state

def update_heat_axis(state, t):
    """
    Update heat axis with damping.
    
    Heat is constantly pulled toward HEAT_TARGET at rate HEAT_DAMPING.
    """
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
# INTEGRATED SIMULATION (COMPLETE SYNC TYPE)
# ═══════════════════════════════════════════════════════════════

def run_full_simulation():
    """Run complete 172,800-second simulation with full synchronization."""
    history = {}
    xyo_valid_count = 0
    safe_weather_count = 0
    weather_sum = 0.0

    state = init_state()

    print(f"Running {GRID_SECONDS}s simulation ({GRID_SECONDS/3600:.0f}h) with complete sync...")
    
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

        # Deep copy state for history
        history[t] = {
            "axes": {eng: dict(axes) for eng, axes in state.items()},
            "weather_truth": w_truth,
            "xyo_valid": xyo_valid,
            "weather_scalar": w_scalar,
        }

    verdict_5 = oracle_verdict(history, use_weather=False)
    verdict_6 = oracle_verdict(history, use_weather=True)

    stats = {
        "xyo_valid_ratio": xyo_valid_count / GRID_SECONDS,
        "safe_weather_ratio": safe_weather_count / GRID_SECONDS,
        "avg_weather_scalar": weather_sum / GRID_SECONDS,
    }

    return verdict_5, verdict_6, history, stats

# ═══════════════════════════════════════════════════════════════
# REPORTING
# ═══════════════════════════════════════════════════════════════

def print_report(verdict_5, verdict_6, stats):
    """Generate human-readable report."""
    print()
    print("=" * 110)
    print("E14 COMPLETE SYNCHRONIZATION TEST SUITE — FINAL REPORT")
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
        for i, (start, end) in enumerate(windows_5[:10], 1):
            duration = end - start + 1
            print(f"    Window {i}: [{start}s, {end}s] ({duration}s, {start/3600:.1f}h–{end/3600:.1f}h)")
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
        for i, (start, end) in enumerate(windows_6[:10], 1):
            duration = end - start + 1
            print(f"    Window {i}: [{start}s, {end}s] ({duration}s, {start/3600:.1f}h–{end/3600:.1f}h)")
    print()
    
    # Impact analysis
    print("[CONVERGENCE IMPACT ANALYSIS]")
    if verdict_5["converged"] and verdict_6["converged"]:
        ratio_reduction = (ratio_5 - ratio_6) / ratio_5 * 100 if ratio_5 > 0 else 0
        print(f"  5-axis convergence ratio: {ratio_5:.4%}")
        print(f"  6-axis convergence ratio: {ratio_6:.4%}")
        print(f"  Weather reduction impact: {ratio_reduction:.2f}%")
        print(f"  → Weather axis reduces convergence window by ~{ratio_reduction:.1f}%")
    print()
    
    # Weather & XYO stats
    print("[WEATHER & XYO STATISTICS]")
    print(f"  XYO witness valid: {stats['xyo_valid_ratio']:.2%}")
    print(f"  Safe weather periods: {stats['safe_weather_ratio']:.2%}")
    print(f"  Average weather scalar: {stats['avg_weather_scalar']:.4f}")
    print(f"  Weather safety threshold: {WEATHER_SAFE_MAX}")
    print()
    
    # System parameters
    print("[COMPLETE SYNC PARAMETERS]")
    print(f"  Phase pullback strength: {PHASE_PULLBACK}")
    print(f"  Heat damping rate: {HEAT_DAMPING}")
    print(f"  Temporal axis periods:")
    for axis, period in PERIODS.items():
        print(f"    {axis}: {period}s")
    print(f"  Tolerances:")
    for axis, tol in TOL.items():
        print(f"    {axis}: ±{tol}")
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
    print("║" + " E14 COMPLETE SYNCHRONIZATION TEST SUITE ".center(108) + "║")
    print("║" + " 周期調整 × 位相引き戻し × 熱ダンピング × 天気ゲート ".center(108) + "║")
    print("╚" + "═" * 108 + "╝")
    print()
    
    verdict_5, verdict_6, history, stats = run_full_simulation()
    print_report(verdict_5, verdict_6, stats)
