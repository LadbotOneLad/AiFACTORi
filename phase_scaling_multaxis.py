# phase_scaling_multaxis.py
# E14 Multi-Axis Phase Scaling Model
# 多軸リズム場の正式仕様 — 1/7200 Invariant
#
# Complete multi-axis resonance field definition
# 4軸独立 × 14エンジン × 1/7200 invariant

import math
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

# ═══════════════════════════════════════════════════════════════
# CORE INVARIANT
# ═══════════════════════════════════════════════════════════════

INVARIANT = 1.0 / 7200.0  # ていんが — 1/7200 の定数
SECONDS_PER_DAY = 86400    # 1日を秒で

# Verify
assert INVARIANT * 7200 == 1.0, "Invariant validation failed"

# ═══════════════════════════════════════════════════════════════
# AXIS DEFINITIONS — 4軸独立周期
# ═══════════════════════════════════════════════════════════════

@dataclass
class Axis:
    """Independent rhythm axis."""
    name: str           # TICK, BEAT, BREATH, CYCLE
    period_seconds: float  # Rhythm period in seconds
    hiragana: str       # ひらがなラベル
    description: str    # 役割説明
    
    @property
    def phase_units(self) -> float:
        """Convert period to phase units (1/7200 basis)."""
        return self.period_seconds / INVARIANT
    
    @property
    def fraction_of_cycle(self) -> float:
        """Express as fraction of CYCLE period."""
        cycle_period = 12.0
        return self.period_seconds / cycle_period
    
    def __repr__(self):
        return f"{self.name}({self.period_seconds}s)"

# Define all 4 axes
AXES = {
    "TICK": Axis(
        name="TICK",
        period_seconds=0.050,
        hiragana="てぃっく",
        description="Micro-response axis — fastest feedback loop"
    ),
    "BEAT": Axis(
        name="BEAT",
        period_seconds=0.200,
        hiragana="びーと",
        description="Observation axis — standard reading speed"
    ),
    "BREATH": Axis(
        name="BREATH",
        period_seconds=1.500,
        hiragana="ぶれす",
        description="Integration axis — pause to absorb"
    ),
    "CYCLE": Axis(
        name="CYCLE",
        period_seconds=12.000,
        hiragana="さいくる",
        description="Coherence axis — full synchronization window"
    ),
}

# ═══════════════════════════════════════════════════════════════
# PHASE MAPPING TABLE
# ═══════════════════════════════════════════════════════════════

class PhaseMetrics:
    """Computed phase metrics for all axes."""
    
    def __init__(self):
        self.metrics = {}
        for axis_name, axis in AXES.items():
            self.metrics[axis_name] = {
                "period_seconds": axis.period_seconds,
                "phase_units": axis.phase_units,
                "fraction_of_cycle": axis.fraction_of_cycle,
                "hiragana": axis.hiragana,
                "description": axis.description,
                "cycles_per_day": SECONDS_PER_DAY / axis.period_seconds,
            }
    
    def __repr__(self):
        lines = []
        lines.append("=" * 70)
        lines.append("E14 MULTI-AXIS PHASE METRICS (1/7200 Invariant)")
        lines.append("=" * 70)
        lines.append("")
        
        for axis_name in ["TICK", "BEAT", "BREATH", "CYCLE"]:
            m = self.metrics[axis_name]
            lines.append(f"{axis_name:8s} ({m['hiragana']})")
            lines.append(f"  Period:      {m['period_seconds']:>10.3f} seconds")
            lines.append(f"  Phase units: {m['phase_units']:>10.1f} (1/7200 basis)")
            lines.append(f"  As fraction: 1/{1/m['fraction_of_cycle']:.0f} of CYCLE")
            lines.append(f"  Per day:     {m['cycles_per_day']:>10.0f} cycles")
            lines.append("")
        
        lines.append("=" * 70)
        return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════
# ENGINE PHASE ASSIGNMENT
# ═══════════════════════════════════════════════════════════════

@dataclass
class EnginePhaseState:
    """Phase state for one engine across all 4 axes."""
    engine_id: int        # 1-14
    engine_name: str      # 365, 777, 101, 1001-1012
    
    # Current phase for each axis (0.0 to 1.0)
    tick_phase: float = 0.0
    beat_phase: float = 0.0
    breath_phase: float = 0.0
    cycle_phase: float = 0.0
    
    def update_from_elapsed(self, elapsed_seconds: float):
        """Update all 4 axes based on elapsed time."""
        tick_axis = AXES["TICK"]
        beat_axis = AXES["BEAT"]
        breath_axis = AXES["BREATH"]
        cycle_axis = AXES["CYCLE"]
        
        self.tick_phase = (elapsed_seconds % tick_axis.period_seconds) / tick_axis.period_seconds
        self.beat_phase = (elapsed_seconds % beat_axis.period_seconds) / beat_axis.period_seconds
        self.breath_phase = (elapsed_seconds % breath_axis.period_seconds) / breath_axis.period_seconds
        self.cycle_phase = (elapsed_seconds % cycle_axis.period_seconds) / cycle_axis.period_seconds
    
    def __repr__(self):
        return (f"E{self.engine_id:02d}({self.engine_name}) "
                f"TICK:{self.tick_phase:.3f} BEAT:{self.beat_phase:.3f} "
                f"BREATH:{self.breath_phase:.3f} CYCLE:{self.cycle_phase:.3f}")

# ═══════════════════════════════════════════════════════════════
# 14-ENGINE RING SYNCHRONIZATION
# ═══════════════════════════════════════════════════════════════

class EngineRing:
    """14-engine multi-axis resonance field."""
    
    ENGINE_NAMES = [
        "365",      # E1 - Validator
        "777",      # E2 - Sovereign
        "101",      # E3 - Horizon
        "1001", "1002", "1003", "1004", "1005",
        "1006", "1007", "1008", "1009", "1010", "1012"
    ]
    
    def __init__(self):
        self.engines = [
            EnginePhaseState(i+1, self.ENGINE_NAMES[i])
            for i in range(14)
        ]
        self.elapsed_seconds = 0.0
    
    def tick(self, delta_seconds: float):
        """Advance all engines by delta_seconds."""
        self.elapsed_seconds += delta_seconds
        for engine in self.engines:
            engine.update_from_elapsed(self.elapsed_seconds)
    
    def get_axis_coherence(self, axis_name: str) -> float:
        """
        Calculate coherence for one axis across all 14 engines.
        Returns 0.0 (scattered) to 1.0 (perfectly synchronized).
        """
        if not self.engines:
            return 0.0
        
        phases = [getattr(e, f"{axis_name.lower()}_phase") for e in self.engines]
        
        # Compute variance of phases (circular)
        mean_phase = sum(phases) / len(phases)
        variance = sum((p - mean_phase) ** 2 for p in phases) / len(phases)
        
        # Coherence: 1 - normalized_variance
        coherence = max(0.0, 1.0 - variance)
        return coherence
    
    def get_ring_coherence(self) -> float:
        """
        Calculate overall ring coherence (average across all 4 axes).
        This is the Kotahitanja for the multi-axis model.
        """
        axis_names = ["TICK", "BEAT", "BREATH", "CYCLE"]
        coherences = [self.get_axis_coherence(name) for name in axis_names]
        return sum(coherences) / len(coherences)
    
    def status_report(self) -> str:
        """Generate status report for all engines and axes."""
        lines = []
        lines.append("=" * 80)
        lines.append(f"E14 RING STATUS (elapsed: {self.elapsed_seconds:.3f}s)")
        lines.append("=" * 80)
        lines.append("")
        
        # Per-engine status
        for engine in self.engines:
            lines.append(f"  {engine}")
        
        lines.append("")
        lines.append("AXIS COHERENCE:")
        for axis_name in ["TICK", "BEAT", "BREATH", "CYCLE"]:
            coh = self.get_axis_coherence(axis_name)
            bar = "█" * int(coh * 20) + "░" * (20 - int(coh * 20))
            lines.append(f"  {axis_name:6s} [{bar}] {coh:.3f}")
        
        ring_coh = self.get_ring_coherence()
        lines.append("")
        lines.append(f"RING COHERENCE (Kotahitanja): {ring_coh:.3f}")
        lines.append("=" * 80)
        
        return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Print phase metrics
    metrics = PhaseMetrics()
    print(metrics)
    
    # Simulate ring over time
    print()
    ring = EngineRing()
    
    # Sample at different time points
    for elapsed in [0.0, 0.050, 0.200, 1.500, 12.0]:
        ring.elapsed_seconds = elapsed
        for engine in ring.engines:
            engine.update_from_elapsed(elapsed)
        print(ring.status_report())
        print()
