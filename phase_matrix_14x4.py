# phase_matrix_14x4.py
# E14 Four-Axis Phase Matrix (14 engines × 4 axes)
# ていんが・ひとつ・ななにせん・わけ
#
# Core coordinate system for E14 multi-axis resonance field
# This matrix is the foundation for:
#   - driftwatcher axis monitoring
#   - YAML role mapping column structure
#   - hiragana label binding
#   - coherence calculation across all 56 phase states

import json
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════

INVARIANT = 1.0 / 7200.0  # ていんが

# Phase units (1/7200 basis)
PHASE_UNITS = {
    "tick":   360,      # 0.050s
    "beat":   1440,     # 0.200s
    "breath": 10800,    # 1.500s
    "cycle":  86400,    # 12.000s (1 day)
}

# 14 Engines
ENGINES = [
    ("E01", "365"),     # Validator
    ("E02", "777"),     # Sovereign
    ("E03", "101"),     # Horizon
    ("E04", "1001"),    # Peer
    ("E05", "1002"),    # Peer
    ("E06", "1003"),    # Peer
    ("E07", "1004"),    # Peer
    ("E08", "1005"),    # Peer
    ("E09", "1006"),    # Peer
    ("E10", "1007"),    # Peer
    ("E11", "1008"),    # Peer
    ("E12", "1009"),    # Peer
    ("E13", "1010"),    # Peer
    ("E14", "1012"),    # Peer
]

# 4 Axes
AXES = ["tick", "beat", "breath", "cycle"]

# ═══════════════════════════════════════════════════════════════
# PHASE MATRIX DEFINITION
# ═══════════════════════════════════════════════════════════════

@dataclass
class EngineAxisState:
    """Single engine's state on one axis."""
    engine_id: str          # E01-E14
    engine_name: str        # 365, 777, etc.
    axis: str              # tick, beat, breath, cycle
    phase_value: float = 0.0     # 0.0 to 1.0 (normalized)
    phase_units: int = 0         # raw phase count
    coherence: float = 1.0       # 1.0 = perfect
    
    def __repr__(self):
        return f"{self.engine_id}[{self.axis}]={self.phase_value:.3f}"

class PhaseMatrix:
    """14 × 4 phase state matrix for E14 ring."""
    
    def __init__(self):
        """Initialize all 56 phase states to 0.0."""
        # Main matrix: {engine_id: {axis: phase_value}}
        self.matrix: Dict[str, Dict[str, float]] = {
            engine_id: {axis: 0.0 for axis in AXES}
            for engine_id, _ in ENGINES
        }
        
        # Metadata
        self.engine_names = {engine_id: name for engine_id, name in ENGINES}
        self.timestamp = 0.0  # seconds elapsed
    
    def update_from_elapsed(self, elapsed_seconds: float):
        """
        Update all 56 phase states based on elapsed time.
        Each axis advances independently at its own rate.
        """
        self.timestamp = elapsed_seconds
        
        for engine_id in self.matrix:
            for axis in AXES:
                period_seconds = PHASE_UNITS[axis] * INVARIANT
                # Normalize to 0.0-1.0
                self.matrix[engine_id][axis] = (
                    (elapsed_seconds % period_seconds) / period_seconds
                )
    
    def get(self, engine_id: str, axis: str) -> float:
        """Get single phase value."""
        return self.matrix.get(engine_id, {}).get(axis, 0.0)
    
    def set(self, engine_id: str, axis: str, phase_value: float):
        """Set single phase value (0.0-1.0)."""
        if engine_id in self.matrix:
            self.matrix[engine_id][axis] = max(0.0, min(1.0, phase_value))
    
    def get_engine_state(self, engine_id: str) -> Dict[str, float]:
        """Get all 4 axis phases for one engine."""
        return self.matrix.get(engine_id, {})
    
    def get_axis_state(self, axis: str) -> Dict[str, float]:
        """Get phase values for one axis across all 14 engines."""
        return {engine_id: self.matrix[engine_id][axis] for engine_id in self.matrix}
    
    def get_axis_coherence(self, axis: str) -> float:
        """
        Calculate coherence for one axis across all 14 engines.
        Coherence = 1.0 (all synchronized) to 0.0 (scattered).
        """
        phases = list(self.get_axis_state(axis).values())
        if not phases:
            return 0.0
        
        # Circular variance approach
        mean_phase = sum(phases) / len(phases)
        variance = sum((p - mean_phase) ** 2 for p in phases) / len(phases)
        coherence = max(0.0, 1.0 - variance)
        return coherence
    
    def get_ring_coherence(self) -> float:
        """
        Calculate overall ring coherence (Kotahitanja).
        Average of coherences across all 4 axes.
        """
        coherences = [self.get_axis_coherence(axis) for axis in AXES]
        return sum(coherences) / len(coherences) if coherences else 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON/YAML export."""
        return {
            "timestamp": self.timestamp,
            "invariant": INVARIANT,
            "phase_units": PHASE_UNITS,
            "matrix": self.matrix,
            "coherence": {
                "tick": self.get_axis_coherence("tick"),
                "beat": self.get_axis_coherence("beat"),
                "breath": self.get_axis_coherence("breath"),
                "cycle": self.get_axis_coherence("cycle"),
                "ring": self.get_ring_coherence(),
            }
        }
    
    def to_json(self) -> str:
        """Export as JSON."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def print_matrix(self):
        """Pretty-print the 14×4 matrix."""
        print("=" * 80)
        print("E14 PHASE MATRIX (14 engines × 4 axes)")
        print("=" * 80)
        print(f"Timestamp: {self.timestamp:.3f}s | Invariant: 1/7200 | Ring Coherence: {self.get_ring_coherence():.3f}")
        print()
        
        # Header
        print(f"{'Engine':10s}", end="")
        for axis in AXES:
            print(f"{axis.upper():>12s}", end="")
        print()
        print("-" * 80)
        
        # Rows
        for engine_id, engine_name in ENGINES:
            print(f"{engine_id}({engine_name:>4s})", end="")
            for axis in AXES:
                phase = self.get(engine_id, axis)
                bar = "█" * int(phase * 10) + "░" * (10 - int(phase * 10))
                print(f"  {bar} {phase:.3f}", end="")
            print()
        
        print()
        print("AXIS COHERENCE:")
        for axis in AXES:
            coh = self.get_axis_coherence(axis)
            bar = "█" * int(coh * 20) + "░" * (20 - int(coh * 20))
            print(f"  {axis.upper():6s} [{bar}] {coh:.3f}")
        
        ring_coh = self.get_ring_coherence()
        print(f"\n  RING   [{'█' * int(ring_coh * 20)}{'░' * (20 - int(ring_coh * 20))}] {ring_coh:.3f}")
        print("=" * 80)

# ═══════════════════════════════════════════════════════════════
# EXPORT FORMATS
# ═══════════════════════════════════════════════════════════════

def export_matrix_as_yaml(matrix: PhaseMatrix) -> str:
    """Export phase matrix as YAML."""
    lines = []
    lines.append("# E14 Phase Matrix (YAML)")
    lines.append(f"# Timestamp: {matrix.timestamp:.3f}s")
    lines.append(f"# Invariant: 1/7200")
    lines.append("")
    lines.append("phase_matrix:")
    
    for engine_id, engine_name in ENGINES:
        lines.append(f"  {engine_id}:")
        lines.append(f"    name: \"{engine_name}\"")
        for axis in AXES:
            phase = matrix.get(engine_id, axis)
            lines.append(f"    {axis}: {phase:.6f}")
    
    lines.append("")
    lines.append("coherence:")
    for axis in AXES:
        coh = matrix.get_axis_coherence(axis)
        lines.append(f"  {axis}: {coh:.6f}")
    
    lines.append(f"  ring: {matrix.get_ring_coherence():.6f}")
    
    return "\n".join(lines)

def export_matrix_as_csv(matrix: PhaseMatrix) -> str:
    """Export phase matrix as CSV."""
    lines = []
    
    # Header
    lines.append(",".join(["Engine", "Name"] + [a.upper() for a in AXES]))
    
    # Rows
    for engine_id, engine_name in ENGINES:
        row = [engine_id, engine_name]
        for axis in AXES:
            phase = matrix.get(engine_id, axis)
            row.append(f"{phase:.6f}")
        lines.append(",".join(row))
    
    return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Create matrix
    matrix = PhaseMatrix()
    
    # Test at various elapsed times
    test_times = [0.0, 0.050, 0.200, 1.500, 12.0, 24.0]
    
    for elapsed in test_times:
        matrix.update_from_elapsed(elapsed)
        matrix.print_matrix()
        print()
    
    # Export examples
    print()
    print("=" * 80)
    print("EXPORT FORMATS")
    print("=" * 80)
    
    matrix.update_from_elapsed(1.5)
    
    print("\n--- YAML Format ---\n")
    print(export_matrix_as_yaml(matrix))
    
    print("\n--- CSV Format ---\n")
    print(export_matrix_as_csv(matrix))
    
    print("\n--- JSON Format ---\n")
    print(matrix.to_json())
