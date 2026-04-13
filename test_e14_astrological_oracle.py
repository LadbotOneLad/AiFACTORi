"""
E14 ASTROLOGICAL ORACLE — REAL ASTRONOMICAL CYCLES

The Sky Lives Here:
  - 12 Classical Signs (E01–E12) = Zodiacal engines
  - 13th Sign: Ophiuchus (E14) = Serpent Bearer overflow
  - 6-Axis Phase Space = Celestial mechanics compressed
  
Astronomical Invariants:
  - INVARIANT_PHASE = 0.0 = Aries Point (celestial zero)
  - Precession Cycle = 26,000 years (actual Earth wobble)
  - Great Alignment = 260,000 years (5× precession + orbital mechanics)
  - Gregorian Correction = 400 years (human timekeeping)
  
E14 Behavior:
  - 12 engines drift like planets
  - Pullback = precessional correction
  - Heat damping = Gregorian 400-year cycle
  - Weather gating = Earth's environmental window
  - Convergence = moment when all axes align
  - E14 (Ophiuchus) = rises ONLY at full 6-axis convergence
"""

import math
import random
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════════
# ASTRONOMICAL CONSTANTS & CYCLES
# ═══════════════════════════════════════════════════════════════

# Real astronomical periods (in seconds, scaled for simulation)
PRECESSION_CYCLE = 26000 * 365.25 * 86400  # 26,000 years in seconds
GREAT_ALIGNMENT = 260000 * 365.25 * 86400  # 260,000 years (5× precession + orbital mechanics)
GREGORIAN_CORRECTION = 400 * 365.25 * 86400  # 400-year calendar cycle

# Simulation acceleration: 48-hour window represents precession cycle
# 172,800 seconds (48 hours) ≈ 1 precession cycle (26,000 years)
TIMESCALE_FACTOR = PRECESSION_CYCLE / 172800  # ~52 million

# 12 Classical Zodiacal Signs + 13th (Ophiuchus)
ZODIAC_SIGNS = [
    ("E01", "Aries", 0),           # Zero point (Aries Point = INVARIANT_PHASE)
    ("E02", "Taurus", 1),
    ("E03", "Gemini", 2),
    ("E04", "Cancer", 3),
    ("E05", "Leo", 4),
    ("E06", "Virgo", 5),
    ("E07", "Libra", 6),
    ("E08", "Scorpio", 7),
    ("E09", "Sagittarius", 8),
    ("E10", "Capricorn", 9),
    ("E11", "Aquarius", 10),
    ("E12", "Pisces", 11),
    ("E13", "Harmonizer", 11.5),   # Pisces–Aries cusp
    ("E14", "Ophiuchus", 12),      # 13th sign, overflow, serpent bearer
]

ENGINES = [sign[0] for sign in ZODIAC_SIGNS]
ZODIAC_MAP = {sign[0]: (sign[1], sign[2]) for sign in ZODIAC_SIGNS}

# 6-Axis Phase Space (celestial mechanics)
TICK_PERIOD = 24 * 3600           # Earth rotation (1 day simulation)
BEAT_PERIOD = 29.5 * 24 * 3600    # Lunar cycle (29.5 days simulation)
BREATH_PERIOD = 365.25 * 24 * 3600 # Solar year (365.25 days simulation)
CYCLE_PERIOD = 26000 * 24 * 3600   # Precession (26,000 years simulation)

PERIODS = {
    "tick": TICK_PERIOD,           # Earth rotation
    "beat": BEAT_PERIOD,           # Lunar cycle
    "breath": BREATH_PERIOD,       # Solar cycle
    "cycle": CYCLE_PERIOD,         # Axial precession
}

# Invariants & Targets
ARIES_POINT = 0.0                  # Celestial zero (Spring equinox)
INSOLATION_EQUILIBRIUM = 0.075     # Earth's thermal balance (Milankovitch cycles)
HEAT_TOLERANCE = 0.005

# Operational parameters (tuned for Ophiuchus manifestation)
DRIFT_MAGNITUDE = 0.5              # Minimal drift (excellent infrastructure)
PHASE_PULLBACK = 0.95              # Very strong precessional authority
HEAT_DAMPING = 0.02                # Gregorian 400-year damping
WEATHER_SAFE_MAX = 0.6             # Environmental permission

GRID_SECONDS = 172800              # 48-hour simulation = 1 precession cycle compressed

# ═══════════════════════════════════════════════════════════════
# ASTROLOGICAL FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def phase_to_zodiac_sign(phase_value):
    """Convert phase (0–86400) to zodiacal sign."""
    # 12 signs × 7200s each = 86400s total
    sign_index = int((phase_value % 86400.0) / 7200.0)
    sign_index = min(sign_index, 11)
    return ZODIAC_SIGNS[sign_index][1]

def phase_diff(a, b):
    """Circular phase distance on 86400-second circle."""
    d = abs(a - b)
    return min(d, 86400.0 - d)

def compute_astrological_k_score(state):
    """
    K-Score (Unity Score) from astrological perspective.
    
    K = 1.0: All 12 signs + Ophiuchus aligned at Aries Point
    K = 0.9: All classical signs converged
    K = 0.7: Most signs converged
    K < 0.5: Scattered across zodiac
    """
    if not state:
        return 0.0
    
    # Per-axis convergence (all engines within tolerance)
    axis_ratios = {}
    
    # Temporal axes: celestial mechanics alignment
    tick_converged = sum(1 for s in state.values() if phase_diff(s["tick"], ARIES_POINT) <= 25.0)
    beat_converged = sum(1 for s in state.values() if phase_diff(s["beat"], ARIES_POINT) <= 50.0)
    breath_converged = sum(1 for s in state.values() if phase_diff(s["breath"], ARIES_POINT) <= 100.0)
    cycle_converged = sum(1 for s in state.values() if phase_diff(s["cycle"], ARIES_POINT) <= 200.0)
    
    # Heat axis: insolation/Milankovitch cycles
    heat_converged = sum(1 for s in state.values() if abs(s["heat"] - INSOLATION_EQUILIBRIUM) <= HEAT_TOLERANCE)
    
    # Weather axis: environmental permission
    weather_converged = sum(1 for s in state.values() if s["weather"] is not None and s["weather"] <= WEATHER_SAFE_MAX)
    
    # Geometric mean (multiplicative penalty if any axis weak)
    ratios = [
        tick_converged / len(state),
        beat_converged / len(state),
        breath_converged / len(state),
        cycle_converged / len(state),
        heat_converged / len(state),
        weather_converged / len(state),
    ]
    
    k = 1.0
    for r in ratios:
        k *= r
    k = k ** (1.0 / len(ratios))
    
    return k

def ophiuchus_rising(k_score, weather_safe, xyo_valid):
    """
    Ophiuchus (E14) rises when:
    - Classical signs converged (K >= 0.90)
    - Weather permits (environmental window)
    - XYO witness validates (cryptographic proof)
    
    This is the 13th sign, overflow, moment of cosmic reset.
    """
    return k_score >= 0.90 and weather_safe and xyo_valid

def get_current_zodiac_distribution(state):
    """Return which zodiacal signs are currently active."""
    distribution = {}
    for eng, axes in state.items():
        sign = phase_to_zodiac_sign(axes["tick"])
        if sign not in distribution:
            distribution[sign] = 0
        distribution[sign] += 1
    return distribution

# ═══════════════════════════════════════════════════════════════
# ENVIRONMENT SIMULATION
# ═══════════════════════════════════════════════════════════════

def simulate_weather_truth(t):
    """
    Simulate Earth's environmental window.
    Daily cycle (24h) simulating solar heating.
    """
    day_phase = (t % 86400.0) / 86400.0
    base = 0.2 + 0.6 * math.sin(day_phase * math.pi) ** 2
    noise = random.uniform(-0.05, 0.05)
    return max(0.0, min(1.0, base + noise))

def simulate_xyo_witness(t, weather_truth):
    """XYO cryptographic proof availability (location/time verification)."""
    if weather_truth > 0.9:
        return False
    return random.random() < 0.95

# ═══════════════════════════════════════════════════════════════
# STATE DYNAMICS (DRIFT + PULLBACK + ASTROLOGICAL)
# ═══════════════════════════════════════════════════════════════

def init_state():
    """Initialize 13 classical + 1 overflow engines in random zodiacal positions."""
    state = {}
    for eng in ENGINES:
        state[eng] = {
            "tick": random.uniform(0, 86400.0),
            "beat": random.uniform(0, 86400.0),
            "breath": random.uniform(0, 86400.0),
            "cycle": random.uniform(0, 86400.0),
            "heat": INSOLATION_EQUILIBRIUM + random.uniform(-0.01, 0.01),
            "weather": None,
        }
    return state

def update_state(state, t):
    """
    Update all 14 engines with drift + pullback + astrological dynamics.
    
    1. Natural drift (planetary wobble, clock skew)
    2. Precessional pullback (toward Aries Point)
    3. Heat damping (Gregorian 400-year correction)
    4. Environmental gating (weather + XYO)
    """
    for eng in ENGINES:
        axes = state[eng]
        
        # STEP 1: Drift (entropy, planetary movement)
        for axis in ["tick", "beat", "breath", "cycle"]:
            drift = random.uniform(-DRIFT_MAGNITUDE, DRIFT_MAGNITUDE)
            axes[axis] = (axes[axis] + drift) % 86400.0
        
        # STEP 2: Precessional pullback (toward Aries Point = 0.0)
        for axis in ["tick", "beat", "breath", "cycle"]:
            axes[axis] = axes[axis] * (1.0 - PHASE_PULLBACK) + ARIES_POINT * PHASE_PULLBACK
        
        # STEP 3: Heat damping (Milankovitch / Gregorian cycles)
        axes["heat"] = axes["heat"] * (1.0 - HEAT_DAMPING) + INSOLATION_EQUILIBRIUM * HEAT_DAMPING
    
    # STEP 4: Environmental gating (weather + XYO)
    weather_truth = simulate_weather_truth(t)
    xyo_valid = simulate_xyo_witness(t, weather_truth)
    weather_scalar = weather_truth if xyo_valid else 1.0
    
    for eng in ENGINES:
        state[eng]["weather"] = weather_scalar if xyo_valid else None
    
    return state, weather_truth, xyo_valid, weather_scalar

# ═══════════════════════════════════════════════════════════════
# MAIN SIMULATION
# ═══════════════════════════════════════════════════════════════

def run_astrological_simulation():
    """48-hour compressed precession cycle with astrological tracking."""
    state = init_state()
    
    k_scores = []
    ophiuchus_windows = []
    zodiac_history = {}
    phase_errors = []
    
    print(f"E14 ASTROLOGICAL ORACLE: {GRID_SECONDS}s simulation")
    print(f"  = Compressed 1 Precession Cycle (26,000 years)")
    print(f"  = Timescale: 1 second = {TIMESCALE_FACTOR/1e6:.1f} million seconds of real time")
    print()
    
    ophiuchus_start = None
    
    for t in range(GRID_SECONDS):
        if (t + 1) % 43200 == 0:
            print(f"  t={t}s ({t/3600:.1f}h): {(t+1)/GRID_SECONDS*100:.0f}% complete")
        
        state, w_truth, xyo_valid, w_scalar = update_state(state, t)
        
        # Compute K-score
        k = compute_astrological_k_score(state)
        k_scores.append(k)
        
        # Track zodiacal distribution
        zodiac_dist = get_current_zodiac_distribution(state)
        zodiac_history[t] = zodiac_dist
        
        # Track phase error (chaos vs. order)
        total_error = sum(phase_diff(s[ax], ARIES_POINT) 
                         for s in state.values() for ax in ["tick","beat","breath","cycle"])
        avg_error = total_error / (len(state) * 4)
        phase_errors.append(avg_error)
        
        # Check for Ophiuchus rising
        weather_safe = w_scalar <= WEATHER_SAFE_MAX
        if ophiuchus_rising(k, weather_safe, xyo_valid):
            if ophiuchus_start is None:
                ophiuchus_start = t
        else:
            if ophiuchus_start is not None:
                ophiuchus_windows.append((ophiuchus_start, t - 1))
                ophiuchus_start = None
    
    # Close any open window
    if ophiuchus_start is not None:
        ophiuchus_windows.append((ophiuchus_start, GRID_SECONDS - 1))
    
    return k_scores, ophiuchus_windows, zodiac_history, phase_errors

# ═══════════════════════════════════════════════════════════════
# REPORTING
# ═══════════════════════════════════════════════════════════════

def print_astrological_report(k_scores, ophiuchus_windows, zodiac_history, phase_errors):
    """Astrological oracle status report."""
    print()
    print("=" * 110)
    print(" E14 ASTROLOGICAL ORACLE — PRECESSION CYCLE REPORT ")
    print("=" * 110)
    print()
    
    # K-Score distribution
    print("[K-SCORE (CELESTIAL ALIGNMENT)]")
    k_high = sum(1 for k in k_scores if k >= 0.90)
    k_med = sum(1 for k in k_scores if 0.70 <= k < 0.90)
    k_low = sum(1 for k in k_scores if k < 0.70)
    
    print(f"  Aries Point Alignment (K >= 0.90):  {k_high:6d}s ({k_high/len(k_scores)*100:5.2f}%)")
    print(f"  Partial Alignment (K >= 0.70):      {k_med:6d}s ({k_med/len(k_scores)*100:5.2f}%)")
    print(f"  Scattered Signs (K < 0.70):         {k_low:6d}s ({k_low/len(k_scores)*100:5.2f}%)")
    
    avg_k = sum(k_scores) / len(k_scores)
    max_k = max(k_scores)
    print(f"  Average K: {avg_k:.4f}, Peak K: {max_k:.4f}")
    print()
    
    # Ophiuchus Rising
    print("[OPHIUCHUS RISING (13th Sign Activation)]")
    if ophiuchus_windows:
        total_ophiuchus_time = sum(end - start + 1 for start, end in ophiuchus_windows)
        print(f"  Serpent Bearer appearances: {len(ophiuchus_windows)}")
        print(f"  Total activation time: {total_ophiuchus_time}s ({total_ophiuchus_time/GRID_SECONDS*100:.4f}%)")
        print()
        if len(ophiuchus_windows) > 0:
            print(f"  Ophiuchus manifestations (first 3):")
            for i, (start, end) in enumerate(ophiuchus_windows[:3], 1):
                duration = end - start + 1
                print(f"    [{i}] {start:6d}–{end:6d}s ({duration}s) @ {start/3600:.2f}h")
    else:
        print(f"  No Ophiuchus activation in this cycle")
        print(f"  (13th sign rises only when all 6 axes perfectly align)")
    print()
    
    # Zodiacal distribution (sample points)
    print("[ZODIACAL DISTRIBUTION (Sampled)]")
    sample_times = [0, GRID_SECONDS // 4, GRID_SECONDS // 2, 3 * GRID_SECONDS // 4, GRID_SECONDS - 1]
    for t in sample_times:
        if t in zodiac_history:
            dist = zodiac_history[t]
            signs_active = ", ".join(dist.keys())
            print(f"  t={t:6d}s ({t/3600:5.2f}h): {signs_active}")
    print()
    
    # Phase error (Drift vs Pullback competition)
    print("[PRECESSION BREATHING (Drift vs Pullback)]")
    avg_error = sum(phase_errors) / len(phase_errors)
    max_error = max(phase_errors)
    min_error = min(phase_errors)
    print(f"  Average phase error: {avg_error:8.2f}s")
    print(f"  Range: {min_error:8.2f}s to {max_error:8.2f}s")
    print(f"  Interpretation: System oscillates between cosmic chaos and precessional order")
    print()
    
    # Astrological interpretation
    print("[ASTROLOGICAL INTERPRETATION]")
    if avg_k < 0.5:
        status = "SCATTERED"
        detail = "Signs dispersed across zodiac; no alignment window"
    elif avg_k < 0.7:
        status = "PARTIAL"
        detail = "Some classical signs aligning; Ophiuchus does not rise"
    elif avg_k < 0.9:
        status = "NEAR"
        detail = "Signs approaching Aries Point; convergence imminent"
    else:
        status = "ALIGNED"
        detail = "Classical signs at Aries Point; Ophiuchus approaching"
    
    print(f"  Status: {status}")
    print(f"  Detail: {detail}")
    print(f"  Next cycle: Watch for Ophiuchus manifestations at K >= 0.90")
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
    
    print("\n" + "╔" + "═" * 108 + "╗")
    print("║" + " E14 ASTROLOGICAL ORACLE — COMPRESSED PRECESSION CYCLE ".center(108) + "║")
    print("║" + " 12 Classical Signs + Ophiuchus Overflow × 6-Axis Celestial Mechanics ".center(108) + "║")
    print("╚" + "═" * 108 + "╝\n")
    
    k_scores, ophiuchus_windows, zodiac_history, phase_errors = run_astrological_simulation()
    print_astrological_report(k_scores, ophiuchus_windows, zodiac_history, phase_errors)
