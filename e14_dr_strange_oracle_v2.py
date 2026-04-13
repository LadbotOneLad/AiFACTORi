# e14_dr_strange_oracle_v2.py
# Dr Strange in the Matrix — E14 Oracle (Data-Driven Version)
# ていんが・ひとつ・ななにせん・わけ
#
# Driven directly by phase_state dict with per-engine, per-axis phase values (mod 86400).
# Computes convergence to 1/7200 invariant and ring coherence in real-time.

import json
import math
from typing import Dict, List, Tuple
from dataclasses import dataclass

# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════

INVARIANT = 1.0 / 7200.0  # ていんが
PHASE_CYCLE = 86400       # Full phase cycle (phase units)

ENGINES = [f"E{str(i).zfill(2)}" for i in range(1, 15)]
AXES = ["tick", "beat", "breath", "cycle"]

# Phase units (1/7200 basis) in absolute units
PHASE_UNITS = {
    "tick":   360,      # 1/240 of cycle
    "beat":   1440,     # 1/60 of cycle
    "breath": 10800,    # 1/8 of cycle
    "cycle":  86400,    # 1 full cycle
}

# Engine metadata
ENGINE_METADATA = {
    "E01": {"name": "365", "role": "Validator", "hiragana": "さんろく"},
    "E02": {"name": "777", "role": "Sovereign", "hiragana": "なななな"},
    "E03": {"name": "101", "role": "Horizon", "hiragana": "ひゃくいち"},
    "E04": {"name": "1001", "role": "Peer", "hiragana": "せんいち"},
    "E05": {"name": "1002", "role": "Peer", "hiragana": "せんに"},
    "E06": {"name": "1003", "role": "Peer", "hiragana": "せんさん"},
    "E07": {"name": "1004", "role": "Peer", "hiragana": "せんし"},
    "E08": {"name": "1005", "role": "Peer", "hiragana": "せんご"},
    "E09": {"name": "1006", "role": "Peer", "hiragana": "せんろく"},
    "E10": {"name": "1007", "role": "Peer", "hiragana": "せんしち"},
    "E11": {"name": "1008", "role": "Peer", "hiragana": "せんはち"},
    "E12": {"name": "1009", "role": "Peer", "hiragana": "せんきゅう"},
    "E13": {"name": "1010", "role": "Peer", "hiragana": "せんじゅう"},
    "E14": {"name": "1012", "role": "Peer", "hiragana": "せんじゅうに"},
}

# ═══════════════════════════════════════════════════════════════
# ORACLE CORE
# ═══════════════════════════════════════════════════════════════

def normalize_phase(phase_value: int, axis: str) -> float:
    """
    Normalize phase value (0..86400) to fractional (0..1.0) for given axis.
    
    Args:
        phase_value: Phase count (0 to 86400)
        axis: "tick", "beat", "breath", or "cycle"
    
    Returns:
        Normalized phase (0.0 to 1.0)
    """
    axis_period = PHASE_UNITS.get(axis, PHASE_CYCLE)
    return (phase_value % PHASE_CYCLE) / axis_period

def compute_axis_variance(phase_state: Dict, axis: str) -> Tuple[float, float]:
    """
    Compute phase variance across all 14 engines for one axis.
    
    Returns:
        (variance, standard_deviation)
    """
    # Normalize all phases for this axis
    phases = [normalize_phase(phase_state[engine][axis], axis) for engine in ENGINES]
    
    # Circular mean (handles wrap-around)
    sin_sum = sum(math.sin(2 * math.pi * p) for p in phases)
    cos_sum = sum(math.cos(2 * math.pi * p) for p in phases)
    circular_mean = math.atan2(sin_sum, cos_sum) / (2 * math.pi)
    if circular_mean < 0:
        circular_mean += 1.0
    
    # Circular variance
    R = math.sqrt(sin_sum ** 2 + cos_sum ** 2) / len(phases)
    circular_variance = 1.0 - R
    
    return circular_variance, math.sqrt(circular_variance)

def compute_axis_coherence(phase_state: Dict, axis: str) -> float:
    """
    Compute coherence for one axis (0.0 = scattered, 1.0 = perfectly synchronized).
    
    Coherence = 1.0 - variance
    """
    variance, _ = compute_axis_variance(phase_state, axis)
    return 1.0 - variance

def compute_ring_coherence(phase_state: Dict) -> float:
    """
    Compute overall ring coherence (Kotahitanja).
    Average coherence across all 4 axes.
    """
    coherences = [compute_axis_coherence(phase_state, axis) for axis in AXES]
    return sum(coherences) / len(coherences) if coherences else 0.0

def compute_engine_phase_distance(phase_state: Dict, engine: str) -> float:
    """
    Compute how far one engine's 4-axis state is from perfect synchronization.
    
    Distance = average deviation across all 4 axes
    """
    deviations = []
    for axis in AXES:
        phase_val = normalize_phase(phase_state[engine][axis], axis)
        # Distance from synchronized state (0.0 or 1.0)
        deviation = min(phase_val, 1.0 - phase_val)
        deviations.append(deviation)
    
    return sum(deviations) / len(deviations)

def detect_convergence_point(phase_state: Dict, tolerance: float = 0.05) -> Dict:
    """
    Dr Strange detects convergence: which engines are synchronized within tolerance?
    
    Returns:
        {
            "converged_engines": list of engine IDs,
            "convergence_count": count,
            "convergence_ratio": converged / total,
            "avg_ring_coherence": float,
            "can_seal": bool (True if convergence_ratio > 0.9),
        }
    """
    convergent = []
    
    for engine in ENGINES:
        distance = compute_engine_phase_distance(phase_state, engine)
        if distance < tolerance:
            convergent.append(engine)
    
    ring_coh = compute_ring_coherence(phase_state)
    can_seal = (len(convergent) / len(ENGINES)) > 0.9 and ring_coh > 0.85
    
    return {
        "converged_engines": convergent,
        "convergence_count": len(convergent),
        "convergence_ratio": len(convergent) / len(ENGINES),
        "avg_ring_coherence": ring_coh,
        "can_seal": can_seal,
    }

# ═══════════════════════════════════════════════════════════════
# ORACLE CLASS
# ═══════════════════════════════════════════════════════════════

class DrStrangeOracle:
    """
    Observes phase state and detects convergence to invariant.
    Once converged, seals the future.
    """
    
    def __init__(self):
        self.phase_state = None
        self.convergence_history = []
        self.is_sealed = False
        self.seal_timestamp = None
    
    def observe(self, phase_state: Dict) -> Dict:
        """
        Observe current phase state and detect convergence.
        
        Args:
            phase_state: {engine: {axis: phase_value}}
        
        Returns:
            Convergence report
        """
        self.phase_state = phase_state
        
        # Compute metrics
        report = {
            "timestamp": len(self.convergence_history),
            "phase_state": phase_state,
            "axis_coherence": {axis: compute_axis_coherence(phase_state, axis) for axis in AXES},
            "ring_coherence": compute_ring_coherence(phase_state),
            "convergence": detect_convergence_point(phase_state),
        }
        
        self.convergence_history.append(report)
        
        # Try to seal if converged
        if report["convergence"]["can_seal"] and not self.is_sealed:
            self.seal()
        
        return report
    
    def seal(self):
        """Seal the future — no more branching allowed."""
        self.is_sealed = True
        self.seal_timestamp = len(self.convergence_history) - 1
    
    def get_status(self) -> str:
        """Generate oracle status report."""
        if not self.phase_state:
            return "Oracle: No observations yet."
        
        lines = []
        lines.append("=" * 90)
        lines.append("DR STRANGE ORACLE — CONVERGENCE STATUS")
        lines.append("=" * 90)
        
        # Ring coherence
        ring_coh = compute_ring_coherence(self.phase_state)
        lines.append(f"Ring Coherence (Kotahitanja): {ring_coh:.6f}")
        lines.append(f"Future sealed: {'YES ✓' if self.is_sealed else 'NO'}")
        lines.append("")
        
        # Axis coherence
        lines.append("Axis Coherence:")
        for axis in AXES:
            coh = compute_axis_coherence(self.phase_state, axis)
            bar = "█" * int(coh * 30) + "░" * (30 - int(coh * 30))
            lines.append(f"  {axis.upper():6s} [{bar}] {coh:.6f}")
        
        lines.append("")
        
        # Convergence status
        conv = detect_convergence_point(self.phase_state)
        lines.append(f"Convergent engines: {conv['convergence_count']} / {len(ENGINES)}")
        lines.append(f"Convergence ratio: {conv['convergence_ratio']:.2%}")
        
        if conv['converged_engines']:
            lines.append(f"Converged: {', '.join(conv['converged_engines'][:5])}")
            if len(conv['converged_engines']) > 5:
                lines.append(f"           {', '.join(conv['converged_engines'][5:])}")
        
        lines.append("")
        
        # Per-engine status
        lines.append("Engine distances from synchronization:")
        for engine in ENGINES:
            distance = compute_engine_phase_distance(self.phase_state, engine)
            status = "CONV" if distance < 0.05 else "DRIFTING"
            bar = "█" * int((1.0 - distance) * 20) + "░" * int(distance * 20)
            meta = ENGINE_METADATA[engine]
            lines.append(f"  {engine}({meta['name']:>4s}) [{bar}] {distance:.4f} {status}")
        
        lines.append("=" * 90)
        return "\n".join(lines)
    
    def to_json(self) -> str:
        """Export oracle state as JSON."""
        if not self.phase_state:
            return "{}"
        
        return json.dumps({
            "is_sealed": self.is_sealed,
            "seal_timestamp": self.seal_timestamp,
            "observations": len(self.convergence_history),
            "current_state": {
                "ring_coherence": compute_ring_coherence(self.phase_state),
                "axis_coherence": {axis: compute_axis_coherence(self.phase_state, axis) for axis in AXES},
                "convergence": detect_convergence_point(self.phase_state),
            }
        }, indent=2, ensure_ascii=False)

# ═══════════════════════════════════════════════════════════════
# DEMO: SYNTHETIC PHASE STATE
# ═══════════════════════════════════════════════════════════════

def generate_synthetic_phase_state(coherence_level: float = 1.0) -> Dict:
    """
    Generate synthetic phase state where all engines are synchronized.
    
    coherence_level: 1.0 = perfect sync, 0.0 = random
    """
    import random
    
    phase_state = {}
    
    if coherence_level == 1.0:
        # Perfect synchronization: all engines at same phase
        base_phase = 43200  # Mid-cycle
        for engine in ENGINES:
            phase_state[engine] = {
                "tick":   base_phase % PHASE_UNITS["tick"],
                "beat":   base_phase % PHASE_UNITS["beat"],
                "breath": base_phase % PHASE_UNITS["breath"],
                "cycle":  base_phase % PHASE_CYCLE,
            }
    else:
        # Partial synchronization with coherence_level
        base_phase = 43200
        for engine in ENGINES:
            for axis in AXES:
                # Add random jitter scaled by coherence_level
                jitter = (1.0 - coherence_level) * random.randint(-1000, 1000)
                phase_state[engine] = {
                    axis: int((base_phase + jitter) % PHASE_CYCLE)
                    for axis in AXES
                }
    
    return phase_state

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print()
    print("╔" + "═" * 88 + "╗")
    print("║" + " DR STRANGE ORACLE v2 — DATA-DRIVEN CONVERGENCE DETECTION ".center(88) + "║")
    print("╚" + "═" * 88 + "╝")
    print()
    
    # Initialize oracle
    oracle = DrStrangeOracle()
    
    # Test scenarios
    scenarios = [
        ("Perfect Synchronization (K=1.0)", 1.0),
        ("High Coherence (K=0.9)", 0.9),
        ("Medium Coherence (K=0.7)", 0.7),
        ("Low Coherence (K=0.5)", 0.5),
    ]
    
    for scenario_name, coherence_level in scenarios:
        print(f"\n[SCENARIO] {scenario_name}")
        print()
        
        # Generate phase state
        phase_state = generate_synthetic_phase_state(coherence_level)
        
        # Observe
        report = oracle.observe(phase_state)
        
        # Display
        print(oracle.get_status())
        print()
    
    # Final oracle state
    print("\n" + "=" * 90)
    print("ORACLE CONCLUSION")
    print("=" * 90)
    
    final_coh = compute_ring_coherence(oracle.phase_state)
    
    if oracle.is_sealed:
        print(f"\n✓ FUTURE SEALED")
        print(f"  Ring Coherence: {final_coh:.6f}")
        print(f"  Seal timestamp: {oracle.seal_timestamp}")
        print(f"\n  All 14 Dr Strange observers have aligned their observations.")
        print(f"  The invariant is locked. No branching beyond this point.")
    else:
        print(f"\n× Future not sealed")
        print(f"  Ring Coherence: {final_coh:.6f}")
        print(f"  Coherence must exceed 0.85 for sealing.")
    
    print()
    print("=" * 90)
    print("JSON EXPORT")
    print("=" * 90)
    print(oracle.to_json())
    print()
