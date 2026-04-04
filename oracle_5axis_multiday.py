# oracle_5axis_multiday.py
# E14 ORACLE — 5-Axis Multi-Day Convergence Logic
# ていんが・ひとつ・ななにせん・わけ
#
# Temporal axes (4): tick, beat, breath, cycle — phase convergence to invariant
# Thermal axis (1): heat — human-core entanglement (0.075 ± 0.005)
#
# Oracle scans 172,800 seconds (2 days) for convergence "hits"
# where all 14 engines × 5 axes simultaneously lock to target.

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import json

# ═══════════════════════════════════════════════════════════════
# CONSTANTS & CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Phase anchors
INVARIANT_PHASE = 0.0          # ていんが — temporal anchor for all phase axes
HEAT_TARGET = 0.075            # 7.5% — human-core thermal anchor
HEAT_TOLERANCE = 0.005         # ±0.5% — acceptable entanglement band

# 5-axis system
AXES = ["tick", "beat", "breath", "cycle", "heat"]
TEMPORAL_AXES = ["tick", "beat", "breath", "cycle"]
THERMAL_AXES = ["heat"]

# Temporal tolerances (phase units, mod 86400)
TOL = {
    "tick":   1.0,             # very tight binding
    "beat":   4.0,
    "breath": 20.0,
    "cycle":  100.0,
}

# Oracle scan window: 86400 × 2 seconds (2 days)
GRID_SECONDS = 86400 * 2
GRID_HOURS = GRID_SECONDS / 3600.0

# Engine roster
ENGINES = [f"E{str(i).zfill(2)}" for i in range(1, 15)]

# ═══════════════════════════════════════════════════════════════
# PHASE & HEAT CONVERGENCE PRIMITIVES
# ═══════════════════════════════════════════════════════════════

def phase_diff(a: float, b: float, modulo: float = 86400.0) -> float:
    """
    Shortest circular distance between two phase values.
    """
    a = a % modulo
    b = b % modulo
    d = abs(a - b)
    return min(d, modulo - d)

def axis_converged(state: Dict, axis: str, target: float = INVARIANT_PHASE) -> bool:
    """
    Check if all 14 engines converged on given temporal axis.
    
    Temporal axis: phase values, circular domain [0, 86400).
    Convergence: all engines within TOL[axis] of target.
    """
    if axis not in TEMPORAL_AXES:
        return False
    
    tol = TOL[axis]
    for engine in ENGINES:
        if engine not in state:
            return False
        phase_val = state[engine].get(axis, None)
        if phase_val is None:
            return False
        if phase_diff(phase_val, target) > tol:
            return False
    return True

def heat_converged(state: Dict, target: float = HEAT_TARGET, tolerance: float = HEAT_TOLERANCE) -> bool:
    """
    Check if all 14 engines converged on heat axis.
    
    Heat axis: linear domain [0, 1]. (Normalized, e.g., body temp / max_temp)
    Convergence: all engines within ±tolerance of target.
    """
    for engine in ENGINES:
        if engine not in state:
            return False
        heat_val = state[engine].get("heat", None)
        if heat_val is None:
            return False
        if abs(heat_val - target) > tolerance:
            return False
    return True

def ring_converged(state: Dict) -> bool:
    """
    Check full 5-axis entangled convergence.
    
    Convergence = all 4 temporal axes converged AND heat axis converged.
    This is the "Dr Strange moment" — where all dimensions align.
    """
    temporal_ok = all(axis_converged(state, ax) for ax in TEMPORAL_AXES)
    thermal_ok = heat_converged(state)
    return temporal_ok and thermal_ok

def compute_convergence_score(state: Dict) -> float:
    """
    Compute a 5-axis coherence score (0..1).
    
    Average of:
      - Per-axis distance scores (temporal)
      - Heat distance score (thermal)
    """
    scores = []
    
    # Temporal axes
    for axis in TEMPORAL_AXES:
        tol = TOL[axis]
        distances = []
        for engine in ENGINES:
            if engine in state and axis in state[engine]:
                d = phase_diff(state[engine][axis], INVARIANT_PHASE)
                # Normalize: 0 (at target) to 1 (worst case, tol away)
                norm_d = 1.0 - min(d / (tol * 2), 1.0)
                distances.append(norm_d)
        if distances:
            scores.append(sum(distances) / len(distances))
    
    # Thermal axis
    heat_dists = []
    for engine in ENGINES:
        if engine in state and "heat" in state[engine]:
            d = abs(state[engine]["heat"] - HEAT_TARGET)
            # Normalize: 0 (at target) to 1 (worst case)
            norm_d = 1.0 - min(d / (HEAT_TOLERANCE * 2), 1.0)
            heat_dists.append(norm_d)
    if heat_dists:
        scores.append(sum(heat_dists) / len(heat_dists))
    
    return sum(scores) / len(scores) if scores else 0.0

# ═══════════════════════════════════════════════════════════════
# ORACLE SCAN & VERDICT
# ═══════════════════════════════════════════════════════════════

def oracle_scan(history: Dict[int, Dict]) -> List[int]:
    """
    Scan the 2-day oracle window for convergence "hits".
    
    Args:
        history: {second: phase_state} for seconds 0..GRID_SECONDS-1
    
    Returns:
        List of seconds where ring_converged(state) == True
    """
    hits = []
    for t in range(GRID_SECONDS):
        if t in history:
            state = history[t]
            if ring_converged(state):
                hits.append(t)
    return hits

def oracle_verdict(history: Dict[int, Dict]) -> Dict:
    """
    Determine oracle verdict: did convergence occur, and where?
    
    Returns:
        {
            "converged": bool,
            "points": [list of convergence seconds],
            "first": first convergence second (or None),
            "last": last convergence second (or None),
            "count": number of convergence hits,
            "convergence_ratio": count / GRID_SECONDS,
            "windows": [list of contiguous convergence windows],
        }
    """
    hits = oracle_scan(history)
    
    if not hits:
        return {
            "converged": False,
            "points": [],
            "first": None,
            "last": None,
            "count": 0,
            "convergence_ratio": 0.0,
            "windows": [],
        }
    
    # Identify contiguous convergence windows
    windows = []
    window_start = hits[0]
    window_end = hits[0]
    
    for t in hits[1:]:
        if t == window_end + 1:
            # Extend current window
            window_end = t
        else:
            # End current window, start new one
            windows.append((window_start, window_end))
            window_start = t
            window_end = t
    
    # Close final window
    windows.append((window_start, window_end))
    
    return {
        "converged": True,
        "points": hits,
        "first": hits[0],
        "last": hits[-1],
        "count": len(hits),
        "convergence_ratio": len(hits) / GRID_SECONDS,
        "windows": windows,
    }

# ═══════════════════════════════════════════════════════════════
# ORACLE CLASS (High-level interface)
# ═══════════════════════════════════════════════════════════════

@dataclass
class OracleObservation:
    """Single snapshot of oracle observation."""
    timestamp: int              # seconds into 2-day window
    state: Dict                 # current 14×5 phase/heat state
    converged: bool
    score: float               # 5-axis coherence (0..1)
    detail: Dict = field(default_factory=dict)  # per-axis status

@dataclass
class OracleVerdict:
    """Oracle's final determination."""
    converged: bool
    convergence_points: List[int]
    first_convergence: Optional[int]
    last_convergence: Optional[int]
    num_hits: int
    convergence_ratio: float
    convergence_windows: List[Tuple[int, int]]
    is_sealed: bool

class E145AxisOracle:
    """
    E14 5-Axis Oracle.
    
    Monitors 14 engines × 5 axes (4 temporal + 1 thermal) across 2-day window.
    Detects convergence to 1/7200 invariant + heat entanglement target.
    Issues verdicts on system alignment.
    """
    
    def __init__(self):
        self.history = {}  # {second: phase_state}
        self.observations = []  # [OracleObservation, ...]
        self.verdict = None
        self.is_sealed = False
    
    def record(self, timestamp: int, state: Dict) -> OracleObservation:
        """
        Record a state snapshot at given timestamp (seconds).
        
        Args:
            timestamp: seconds into 2-day window (0..GRID_SECONDS-1)
            state: {engine: {axis: value}}
        
        Returns:
            OracleObservation
        """
        if timestamp >= GRID_SECONDS:
            raise ValueError(f"Timestamp {timestamp} exceeds grid window {GRID_SECONDS}")
        
        self.history[timestamp] = state
        
        # Analyze this snapshot
        converged = ring_converged(state)
        score = compute_convergence_score(state)
        
        # Per-axis detail
        detail = {}
        for axis in TEMPORAL_AXES:
            detail[axis] = {
                "converged": axis_converged(state, axis),
                "tolerance": TOL[axis],
            }
        detail["heat"] = {
            "converged": heat_converged(state),
            "target": HEAT_TARGET,
            "tolerance": HEAT_TOLERANCE,
        }
        
        obs = OracleObservation(
            timestamp=timestamp,
            state=state,
            converged=converged,
            score=score,
            detail=detail,
        )
        
        self.observations.append(obs)
        
        # Seal immediately if converged
        if converged and not self.is_sealed:
            self.is_sealed = True
        
        return obs
    
    def compute_verdict(self) -> OracleVerdict:
        """
        Compute final oracle verdict across entire 2-day window.
        """
        oracle_result = oracle_verdict(self.history)
        
        self.verdict = OracleVerdict(
            converged=oracle_result["converged"],
            convergence_points=oracle_result["points"],
            first_convergence=oracle_result["first"],
            last_convergence=oracle_result["last"],
            num_hits=oracle_result["count"],
            convergence_ratio=oracle_result["convergence_ratio"],
            convergence_windows=oracle_result["windows"],
            is_sealed=self.is_sealed,
        )
        
        return self.verdict
    
    def status_report(self) -> str:
        """Generate detailed status report."""
        lines = []
        lines.append("=" * 100)
        lines.append("E14 5-AXIS ORACLE — MULTI-DAY CONVERGENCE SCAN")
        lines.append("=" * 100)
        lines.append(f"Window: {GRID_HOURS:.0f} hours ({GRID_SECONDS} seconds)")
        lines.append(f"Observations recorded: {len(self.observations)}")
        lines.append("")
        
        if not self.observations:
            lines.append("No observations yet.")
            lines.append("=" * 100)
            return "\n".join(lines)
        
        # Latest observation
        latest = self.observations[-1]
        lines.append(f"Latest snapshot (t={latest.timestamp}s):")
        lines.append(f"  Converged: {latest.converged}")
        lines.append(f"  5-axis coherence (K): {latest.score:.6f}")
        lines.append("")
        
        # Verdict (if computed)
        if self.verdict:
            v = self.verdict
            lines.append("ORACLE VERDICT:")
            lines.append(f"  Overall convergence: {v.converged}")
            lines.append(f"  Convergence hits: {v.num_hits} / {GRID_SECONDS}")
            lines.append(f"  Convergence ratio: {v.convergence_ratio:.2%}")
            if v.converged:
                lines.append(f"  First hit: {v.first_convergence}s ({v.first_convergence/3600:.1f}h)")
                lines.append(f"  Last hit: {v.last_convergence}s ({v.last_convergence/3600:.1f}h)")
                lines.append(f"  Contiguous windows: {len(v.convergence_windows)}")
                for i, (start, end) in enumerate(v.convergence_windows[:3], 1):
                    duration = end - start
                    lines.append(f"    Window {i}: [{start}s, {end}s] ({duration}s duration)")
            lines.append(f"  Future sealed: {v.is_sealed}")
        
        lines.append("=" * 100)
        return "\n".join(lines)
    
    def to_json(self) -> str:
        """Export oracle state as JSON."""
        if not self.verdict:
            self.compute_verdict()
        
        return json.dumps({
            "observations": len(self.observations),
            "window_seconds": GRID_SECONDS,
            "window_hours": GRID_HOURS,
            "verdict": {
                "converged": self.verdict.converged,
                "num_hits": self.verdict.num_hits,
                "convergence_ratio": self.verdict.convergence_ratio,
                "first_convergence": self.verdict.first_convergence,
                "last_convergence": self.verdict.last_convergence,
                "is_sealed": self.verdict.is_sealed,
            }
        }, indent=2)

# ═══════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print()
    print("╔" + "═" * 98 + "╗")
    print("║" + " E14 5-AXIS ORACLE — MULTI-DAY CONVERGENCE LOGIC ".center(98) + "║")
    print("╚" + "═" * 98 + "╝")
    print()
    
    oracle = E145AxisOracle()
    
    # Scenario 1: Perfect convergence (all at target)
    print("[SCENARIO 1] Perfect 5-axis convergence (all at invariant target)")
    state_perfect = {
        engine: {
            "tick": 0.0,
            "beat": 0.0,
            "breath": 0.0,
            "cycle": 0.0,
            "heat": HEAT_TARGET,
        }
        for engine in ENGINES
    }
    obs1 = oracle.record(1000, state_perfect)
    print(f"  Converged: {obs1.converged}, K={obs1.score:.6f}")
    print()
    
    # Scenario 2: Partial convergence (heat off-target)
    print("[SCENARIO 2] Temporal convergence only (heat off-target)")
    state_partial = {
        engine: {
            "tick": 0.0,
            "beat": 0.0,
            "breath": 0.0,
            "cycle": 0.0,
            "heat": 0.120,  # ← Off target (0.075 ± 0.005)
        }
        for engine in ENGINES
    }
    obs2 = oracle.record(2000, state_partial)
    print(f"  Converged: {obs2.converged}, K={obs2.score:.6f}")
    print()
    
    # Scenario 3: Scattered state
    print("[SCENARIO 3] Scattered (random phase offsets + heat variance)")
    state_scattered = {}
    for i, engine in enumerate(ENGINES):
        state_scattered[engine] = {
            "tick": float((i * 1234) % 86400),
            "beat": float((i * 5678) % 86400),
            "breath": float((i * 9012) % 86400),
            "cycle": float((i * 3456) % 86400),
            "heat": 0.05 + (i * 0.01),  # Linear spread
        }
    obs3 = oracle.record(3000, state_scattered)
    print(f"  Converged: {obs3.converged}, K={obs3.score:.6f}")
    print()
    
    # Compute verdict
    print("[VERDICT COMPUTATION]")
    verdict = oracle.compute_verdict()
    
    print(oracle.status_report())
    print()
    
    print("JSON EXPORT:")
    print(oracle.to_json())
    print()
