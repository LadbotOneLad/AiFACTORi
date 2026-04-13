"""
E14 COSMOLOGICAL ORACLE — FINAL COMPLETE IMPLEMENTATION

THE REAL SKY:
13 actual constellations on the ecliptic plane:
  1. Aries
  2. Taurus
  3. Gemini
  4. Cancer
  5. Leo
  6. Virgo
  7. Libra
  8. Scorpius
  9. OPHIUCHUS (Serpent Bearer, Nov 29–Dec 17)
  10. Sagittarius
  11. Capricorn
  12. Aquarius
  13. Pisces

THE CYCLES:
  - Axial precession: 25,772 years
  - Great Alignment: 260,000 years (full tilt+wobble+eccentricity+apsidal+galactic convergence)
  - Gregorian correction: 400 years (calendar emulator of precession)
  - E14 simulation: 48 hours = compressed 26,000-year precession

THE INVARIANTS:
  - Aries Point = 0.0 (celestial zero, spring equinox)
  - Heat equilibrium = 0.075 (orbital eccentricity / insolation)
  - Weather gate = XYO witness (environmental permission)
  - 6-axis convergence = Great Invariant moment
"""

import math
import random
from datetime import datetime

GRID_SECONDS = 172800  # 48 hours = compressed 26,000-year precession

# THE REAL SKY: 13 constellations in astronomical order
CONSTELLATIONS = [
    ("E01", "Aries", 0, "30 Mar–19 Apr"),
    ("E02", "Taurus", 1, "20 Apr–20 May"),
    ("E03", "Gemini", 2, "21 May–21 Jun"),
    ("E04", "Cancer", 3, "22 Jun–22 Jul"),
    ("E05", "Leo", 4, "23 Jul–22 Aug"),
    ("E06", "Virgo", 5, "23 Aug–23 Sep"),
    ("E07", "Libra", 6, "24 Sep–23 Oct"),
    ("E08", "Scorpius", 7, "24 Oct–29 Nov"),
    ("E09", "Ophiuchus", 8, "29 Nov–17 Dec"),  # THE 13TH, BETWEEN SCORPIO & SAGITTARIUS
    ("E10", "Sagittarius", 9, "18 Dec–20 Jan"),
    ("E11", "Capricorn", 10, "21 Jan–19 Feb"),
    ("E12", "Aquarius", 11, "20 Feb–20 Mar"),
    ("E13", "Pisces", 12, "21 Mar–29 Mar"),
]

ENGINES = [c[0] for c in CONSTELLATIONS]
CONSTELLATION_MAP = {c[0]: (c[1], c[2], c[3]) for c in CONSTELLATIONS}

# 6-AXIS CELESTIAL MECHANICS
TICK_PERIOD = 24 * 3600           # Earth rotation (1 day)
BEAT_PERIOD = 29.5 * 24 * 3600    # Lunar cycle (29.5 days)
BREATH_PERIOD = 365.25 * 24 * 3600 # Solar year
CYCLE_PERIOD = 25772 * 24 * 3600   # Axial precession (25,772 years)

PERIODS = {
    "tick": TICK_PERIOD,
    "beat": BEAT_PERIOD,
    "breath": BREATH_PERIOD,
    "cycle": CYCLE_PERIOD,
}

# INVARIANTS
ARIES_POINT = 0.0                  # Celestial zero (spring equinox)
INSOLATION_EQUILIBRIUM = 0.075     # Heat target (orbital eccentricity)
HEAT_TOLERANCE = 0.005

# OPERATIONAL PARAMETERS (TUNED)
DRIFT_MAGNITUDE = 0.5              # Natural precession/clock skew
PHASE_PULLBACK = 0.95              # Precessional correction authority
HEAT_DAMPING = 0.02                # Gregorian 400-year cycle damping
WEATHER_SAFE_MAX = 0.6             # Environmental gate threshold

# OPHIUCHUS THRESHOLD: E09 rises only at Great Invariant alignment
OPHIUCHUS_K_THRESHOLD = 0.99       # Near-perfect alignment required

# ═══════════════════════════════════════════════════════════════
# COSMOLOGICAL FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def phase_diff(a, b):
    """Circular phase distance on 86400-second circle."""
    d = abs(a - b)
    return min(d, 86400.0 - d)

def compute_k_score(state):
    """
    K-Score: Unity/Coherence Score (0.0–1.0)
    
    K = 1.0: All 13 constellations aligned at Aries Point
    K = 0.99: Ophiuchus rises (Great Invariant moment)
    K = 0.9: Classical 12 converged
    K = 0.7: Partial alignment
    K < 0.5: Scattered across sky
    """
    if not state:
        return 0.0
    
    ratios = {}
    
    # Temporal axes
    tick_converged = sum(1 for s in state.values() if phase_diff(s["tick"], ARIES_POINT) <= 25.0)
    beat_converged = sum(1 for s in state.values() if phase_diff(s["beat"], ARIES_POINT) <= 50.0)
    breath_converged = sum(1 for s in state.values() if phase_diff(s["breath"], ARIES_POINT) <= 100.0)
    cycle_converged = sum(1 for s in state.values() if phase_diff(s["cycle"], ARIES_POINT) <= 200.0)
    
    # Equilibrium axes
    heat_converged = sum(1 for s in state.values() if abs(s["heat"] - INSOLATION_EQUILIBRIUM) <= HEAT_TOLERANCE)
    weather_converged = sum(1 for s in state.values() if s["weather"] is not None and s["weather"] <= WEATHER_SAFE_MAX)
    
    ratios_list = [
        tick_converged / len(state),
        beat_converged / len(state),
        breath_converged / len(state),
        cycle_converged / len(state),
        heat_converged / len(state),
        weather_converged / len(state),
    ]
    
    # Geometric mean (multiplicative penalty)
    k = 1.0
    for r in ratios_list:
        k *= r
    k = k ** (1.0 / len(ratios_list))
    
    return k

def ophiuchus_rises(k_score, weather_safe, xyo_valid):
    """
    Ophiuchus (E09, Serpent Bearer) rises when:
    - K >= 0.99 (near-perfect alignment, Great Invariant moment)
    - Weather permits (environmental gate open)
    - XYO witness validates (cryptographic proof)
    
    This is the rarest event: full 13-constellation alignment.
    """
    return k_score >= OPHIUCHUS_K_THRESHOLD and weather_safe and xyo_valid

def get_active_constellations(state):
    """Return which constellations are active at this moment."""
    active = {}
    for eng, axes in state.items():
        const_name = CONSTELLATION_MAP[eng][0]
        if const_name not in active:
            active[const_name] = 0
        active[const_name] += 1
    return active

# ═══════════════════════════════════════════════════════════════
# ENVIRONMENT SIMULATION
# ═══════════════════════════════════════════════════════════════

def simulate_weather_truth(t):
    """Simulate Earth's environmental window."""
    day_phase = (t % 86400.0) / 86400.0
    base = 0.2 + 0.6 * math.sin(day_phase * math.pi) ** 2
    noise = random.uniform(-0.05, 0.05)
    return max(0.0, min(1.0, base + noise))

def simulate_xyo_witness(t, weather_truth):
    """XYO cryptographic proof availability."""
    if weather_truth > 0.9:
        return False
    return random.random() < 0.95

# ═══════════════════════════════════════════════════════════════
# STATE DYNAMICS (DRIFT + PULLBACK + PRECESSION)
# ═══════════════════════════════════════════════════════════════

def init_state():
    """Initialize 13 constellations in randomized positions."""
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
    Update all 13 engines with precession dynamics.
    
    1. Natural drift (celestial mechanics)
    2. Precessional pullback (toward Aries Point)
    3. Heat damping (Gregorian cycle emulation)
    4. Environmental gating (weather + XYO)
    """
    for eng in ENGINES:
        axes = state[eng]
        
        # DRIFT: Natural precession/entropy
        for axis in ["tick", "beat", "breath", "cycle"]:
            drift = random.uniform(-DRIFT_MAGNITUDE, DRIFT_MAGNITUDE)
            axes[axis] = (axes[axis] + drift) % 86400.0
        
        # PULLBACK: Precessional correction toward Aries Point
        for axis in ["tick", "beat", "breath", "cycle"]:
            axes[axis] = axes[axis] * (1.0 - PHASE_PULLBACK) + ARIES_POINT * PHASE_PULLBACK
        
        # HEAT DAMPING: Gregorian calendar cycle (400-year correction)
        axes["heat"] = axes["heat"] * (1.0 - HEAT_DAMPING) + INSOLATION_EQUILIBRIUM * HEAT_DAMPING
    
    # ENVIRONMENTAL GATING: Weather + XYO witness
    weather_truth = simulate_weather_truth(t)
    xyo_valid = simulate_xyo_witness(t, weather_truth)
    weather_scalar = weather_truth if xyo_valid else 1.0
    
    for eng in ENGINES:
        state[eng]["weather"] = weather_scalar if xyo_valid else None
    
    return state, weather_truth, xyo_valid, weather_scalar

# ═══════════════════════════════════════════════════════════════
# SIMULATION
# ═══════════════════════════════════════════════════════════════

def run_cosmological_simulation():
    """48-hour compressed precession cycle with 13 constellations."""
    state = init_state()
    
    k_scores = []
    ophiuchus_windows = []
    phase_errors = []
    
    print(f"E14 COSMOLOGICAL ORACLE: 13-Constellation Alignment")
    print(f"  Simulation: {GRID_SECONDS}s (48 hours)")
    print(f"  Represents: 1 Precession Cycle (25,772 years, compressed)")
    print(f"  Timescale: 1 second = 4.7 million seconds real time")
    print()
    
    ophiuchus_start = None
    
    for t in range(GRID_SECONDS):
        if (t + 1) % 43200 == 0:
            print(f"  t={t}s ({t/3600:.1f}h): {(t+1)/GRID_SECONDS*100:.0f}% complete")
        
        state, w_truth, xyo_valid, w_scalar = update_state(state, t)
        
        k = compute_k_score(state)
        k_scores.append(k)
        
        # Track phase error
        total_error = sum(phase_diff(s[ax], ARIES_POINT) 
                         for s in state.values() for ax in ["tick","beat","breath","cycle"])
        avg_error = total_error / (len(state) * 4)
        phase_errors.append(avg_error)
        
        # Check for Ophiuchus rising
        weather_safe = w_scalar <= WEATHER_SAFE_MAX
        if ophiuchus_rises(k, weather_safe, xyo_valid):
            if ophiuchus_start is None:
                ophiuchus_start = t
        else:
            if ophiuchus_start is not None:
                ophiuchus_windows.append((ophiuchus_start, t - 1))
                ophiuchus_start = None
    
    if ophiuchus_start is not None:
        ophiuchus_windows.append((ophiuchus_start, GRID_SECONDS - 1))
    
    return k_scores, ophiuchus_windows, phase_errors

# ═══════════════════════════════════════════════════════════════
# REPORTING
# ═══════════════════════════════════════════════════════════════

def print_cosmological_report(k_scores, ophiuchus_windows, phase_errors):
    """Final cosmological oracle report."""
    print()
    print("=" * 110)
    print(" E14 COSMOLOGICAL ORACLE — 13-CONSTELLATION ALIGNMENT REPORT ")
    print("=" * 110)
    print()
    
    print("[THE SKY: 13 CONSTELLATIONS]")
    print("  1. Aries      (Mar 30–Apr 19)")
    print("  2. Taurus     (Apr 20–May 20)")
    print("  3. Gemini     (May 21–Jun 21)")
    print("  4. Cancer     (Jun 22–Jul 22)")
    print("  5. Leo        (Jul 23–Aug 22)")
    print("  6. Virgo      (Aug 23–Sep 23)")
    print("  7. Libra      (Sep 24–Oct 23)")
    print("  8. Scorpius   (Oct 24–Nov 29)")
    print("  9. OPHIUCHUS  (Nov 29–Dec 17)  ← THE SERPENT BEARER")
    print("  10. Sagittarius (Dec 18–Jan 20)")
    print("  11. Capricorn  (Jan 21–Feb 19)")
    print("  12. Aquarius   (Feb 20–Mar 20)")
    print("  13. Pisces     (Mar 21–Mar 29)")
    print()
    
    print("[K-SCORE (CELESTIAL ALIGNMENT)]")
    k_perfect = sum(1 for k in k_scores if k >= 0.99)
    k_near = sum(1 for k in k_scores if 0.90 <= k < 0.99)
    k_partial = sum(1 for k in k_scores if 0.70 <= k < 0.90)
    k_scattered = sum(1 for k in k_scores if k < 0.70)
    
    print(f"  K >= 0.99 (Great Invariant moment):   {k_perfect:6d}s ({k_perfect/len(k_scores)*100:5.2f}%)")
    print(f"  K >= 0.90 (Classical 12 converged):   {k_near:6d}s ({k_near/len(k_scores)*100:5.2f}%)")
    print(f"  K >= 0.70 (Partial alignment):        {k_partial:6d}s ({k_partial/len(k_scores)*100:5.2f}%)")
    print(f"  K < 0.70 (Scattered):                 {k_scattered:6d}s ({k_scattered/len(k_scores)*100:5.2f}%)")
    
    avg_k = sum(k_scores) / len(k_scores)
    max_k = max(k_scores)
    print(f"  Average K: {avg_k:.4f}, Peak K: {max_k:.4f}")
    print()
    
    print("[OPHIUCHUS RISING (13th Constellation Activation)]")
    print(f"  Serpent Bearer manifestations: {len(ophiuchus_windows)}")
    if ophiuchus_windows:
        total_time = sum(end - start + 1 for start, end in ophiuchus_windows)
        print(f"  Total activation time: {total_time}s ({total_time/GRID_SECONDS*100:.4f}%)")
        print()
        print(f"  First 3 manifestations:")
        for i, (start, end) in enumerate(ophiuchus_windows[:3], 1):
            duration = end - start + 1
            print(f"    [{i}] {start:6d}–{end:6d}s ({duration}s) @ {start/3600:.2f}h")
    else:
        print(f"  No Ophiuchus activation (Great Invariant not reached)")
    print()
    
    print("[PRECESSION BREATHING (Drift vs Pullback)]")
    avg_error = sum(phase_errors) / len(phase_errors)
    max_error = max(phase_errors)
    min_error = min(phase_errors)
    print(f"  Average phase error: {avg_error:8.2f}s")
    print(f"  Range: {min_error:8.2f}s (order) to {max_error:8.2f}s (chaos)")
    print()
    
    print("[COSMOLOGICAL INTERPRETATION]")
    if max_k < 0.7:
        status = "DISPERSED"
        detail = "Constellations scattered, no alignment window"
    elif max_k < 0.9:
        status = "APPROACHING"
        detail = "Partial alignment, Great Invariant distant"
    elif max_k < 0.99:
        status = "NEARLY CONVERGED"
        detail = "Classical 12 converged, Ophiuchus forming"
    else:
        status = "ALIGNED"
        detail = "Great Invariant achieved, Ophiuchus risen"
    
    print(f"  Status: {status}")
    print(f"  Detail: {detail}")
    print(f"  Cycle interpretation: Precession is '{('advancing' if avg_k > 0.4 else 'retreating')}'")
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
    print("║" + " E14 COSMOLOGICAL ORACLE — 13 CONSTELLATIONS × 6-AXIS CELESTIAL MECHANICS ".center(108) + "║")
    print("║" + " Aries Point = 0.0 | Ophiuchus Between Scorpius & Sagittarius | Great Invariant = Alignment ".center(108) + "║")
    print("╚" + "═" * 108 + "╝\n")
    
    k_scores, ophiuchus_windows, phase_errors = run_cosmological_simulation()
    print_cosmological_report(k_scores, ophiuchus_windows, phase_errors)
