# phase_map_7200.py
# 1/7200 Invariant Ring — Relationship Phase Map
# ていんが・ひとつ・ななにせん・わけ
#
# Defines the 1/7200 phase constant and derives:
# - Rhythm relationships (TICK/BEAT/BREATH/CYCLE)
# - Engine role mappings (14 engines)
# - Position-phase pairs

import math
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple

# ─────────────────────────────────────────────
# Core Invariant — コア定数
# ─────────────────────────────────────────────

INVARIANT_PHASE = 1 / 7200  # ていんが = 定数 invariant
SECONDS_PER_DAY = 86400      # 1日
PHASE_DIVISIONS = 7200       # わけ = 分割数

# Verify: INVARIANT_PHASE * 7200 = 1 day
assert INVARIANT_PHASE * PHASE_DIVISIONS == 1.0, "Invariant validation failed"

# ─────────────────────────────────────────────
# Rhythm Constants — リズム定数
# ─────────────────────────────────────────────

class RhythmPhase(Enum):
    """Clocked rhythm phases mapped to 1/7200."""
    
    TICK   = 0.050      # 50ms — マイクロフィードバック
    BEAT   = 0.200      # 200ms — 標準観測
    BREATH = 1.500      # 1.5s — 吸収の間
    CYCLE  = 12.000     # 12s — マイクロサイクル

# Convert rhythm seconds to phase units (1/7200)
TICK_PHASES   = int(RhythmPhase.TICK.value / (SECONDS_PER_DAY / PHASE_DIVISIONS))
BEAT_PHASES   = int(RhythmPhase.BEAT.value / (SECONDS_PER_DAY / PHASE_DIVISIONS))
BREATH_PHASES = int(RhythmPhase.BREATH.value / (SECONDS_PER_DAY / PHASE_DIVISIONS))
CYCLE_PHASES  = int(RhythmPhase.CYCLE.value / (SECONDS_PER_DAY / PHASE_DIVISIONS))

print(f"Rhythm-to-Phase Conversion:")
print(f"  TICK   = {TICK_PHASES} phases ({RhythmPhase.TICK.value*1000:.0f}ms)")
print(f"  BEAT   = {BEAT_PHASES} phases ({RhythmPhase.BEAT.value*1000:.0f}ms)")
print(f"  BREATH = {BREATH_PHASES} phases ({RhythmPhase.BREATH.value*1000:.0f}ms)")
print(f"  CYCLE  = {CYCLE_PHASES} phases ({RhythmPhase.CYCLE.value*1000:.0f}ms)")
print()

# ─────────────────────────────────────────────
# Engine Definitions — エンジン定義
# ─────────────────────────────────────────────

@dataclass
class Engine:
    """Engine metadata."""
    id: int                  # 1-14
    name: str               # 365, 777, 101, 1001-1012
    role: str               # Validator, Sovereign, Horizon, Peer
    hiragana_label: str     # ひらがなラベル
    
    def __repr__(self):
        return f"E{self.id:02d}({self.name}:{self.role})"

ENGINES = [
    Engine(1, "365", "Validator", "さんろく"),   # 365-day cycle
    Engine(2, "777", "Sovereign", "なななな"),   # Ultimate authority
    Engine(3, "101", "Horizon", "ひゃくいち"),  # Boundary witness
    Engine(4, "1001", "Peer", "せんいち"),     # Peer consensus
    Engine(5, "1002", "Peer", "せんに"),
    Engine(6, "1003", "Peer", "せんさん"),
    Engine(7, "1004", "Peer", "せんし"),
    Engine(8, "1005", "Peer", "せんご"),
    Engine(9, "1006", "Peer", "せんろく"),
    Engine(10, "1007", "Peer", "せんしち"),
    Engine(11, "1008", "Peer", "せんはち"),
    Engine(12, "1009", "Peer", "せんきゅう"),
    Engine(13, "1010", "Peer", "せんじゅう"),
    Engine(14, "1012", "Peer", "せんじゅうに"),
]

# ─────────────────────────────────────────────
# Phase Role Labels — 位相役割ラベル
# ─────────────────────────────────────────────

class PhaseRole(Enum):
    """Phase relationship roles (ひらがな encoded)."""
    
    # Axes
    いねい = "identity-axis"        # しん (Identity)
    こあ = "coherence-axis"         # こう (Structure/Coherence)
    いお = "i-o-axis"              # つな (Topology/IO)
    とき = "timing-axis"            # うご (Rhythm/Timing)
    はね = "bounce-axis"            # かん (Security/Bounce)
    とい = "topology-inquiry"       # 位相問合
    わ = "wa-ring"                 # 環 (Ring)
    ひと = "hitotsunoki"           # 統一 (Unity)
    ね = "ne-root"                 # 根 (Root)
    
    # Relations
    まひ = "mark-hit"              # マーク衝突
    
    def __repr__(self):
        return self.name

# ─────────────────────────────────────────────
# Relationship Pairs — 関係ペア表
# ─────────────────────────────────────────────

@dataclass
class RelationshipPair:
    """Engine-Object relationship with phase labels."""
    engine_id: int          # て (Hand/Engine)
    object_role: str       # お (Object)
    phase_label: str       # [X] 位相
    target_label: str      # [Y] 関係先
    hiragana: str          # ひらがなコード
    
    def __repr__(self):
        eng = [e for e in ENGINES if e.id == self.engine_id][0]
        return f"E{self.engine_id}({eng.name}) -[{self.phase_label}]-> {self.target_label}"

# Parse the phase map block into relationship pairs
PHASE_MAP_PAIRS = [
    # Line: て　お　いねい　の　こあ
    RelationshipPair(1, "observer", "いねい", "こあ", "いねい・こあ"),
    # Line: て　ひと　はね　て　とき　の　わ
    RelationshipPair(2, "unity", "はね", "わ", "はね・わ"),
    # Line: て　ね　の　はね　て　いお
    RelationshipPair(3, "root", "はね", "いお", "はね・いお"),
    # Line: て　お　まひ　の　いお
    RelationshipPair(4, "observer", "まひ", "いお", "まひ・いお"),
    # Line: て　お　とい　の　はね
    RelationshipPair(5, "observer", "とい", "はね", "とい・はね"),
    # Line: て　お　わ　の　いお
    RelationshipPair(6, "observer", "わ", "いお", "わ・いお"),
    # Line: て　お　いお　の　はね
    RelationshipPair(7, "observer", "いお", "はね", "いお・はね"),
    # Line: て　お　とき　の　いお
    RelationshipPair(8, "observer", "とき", "いお", "とき・いお"),
    # Line: て　お　はね　の　いお
    RelationshipPair(9, "observer", "はね", "いお", "はね・いお"),
    # Line: て　お　いお　の　とき
    RelationshipPair(10, "observer", "いお", "とき", "いお・とき"),
    # Line: て　お　とき　の　わ
    RelationshipPair(11, "observer", "とき", "わ", "とき・わ"),
    # Line: て　お　わ　の　とき
    RelationshipPair(12, "observer", "わ", "とき", "わ・とき"),
    # Line: て　お　いお　の　わ
    RelationshipPair(13, "observer", "いお", "わ", "いお・わ"),
]

# ─────────────────────────────────────────────
# Mapping Functions — マッピング関数
# ─────────────────────────────────────────────

def engine_by_id(engine_id: int) -> Engine:
    """Get engine by ID."""
    for e in ENGINES:
        if e.id == engine_id:
            return e
    raise ValueError(f"Engine {engine_id} not found")

def phase_to_seconds(phases: int) -> float:
    """Convert phase units to seconds."""
    return phases * (SECONDS_PER_DAY / PHASE_DIVISIONS)

def seconds_to_phase(seconds: float) -> int:
    """Convert seconds to phase units."""
    return int(seconds * (PHASE_DIVISIONS / SECONDS_PER_DAY))

def get_relationship_for_engine(engine_id: int) -> RelationshipPair:
    """Get primary relationship for engine."""
    for pair in PHASE_MAP_PAIRS:
        if pair.engine_id == engine_id:
            return pair
    return None

# ─────────────────────────────────────────────
# Display Functions — 表示関数
# ─────────────────────────────────────────────

def print_engine_roster():
    """Print all engines with roles."""
    print("=" * 60)
    print("ENGINE ROSTER (14 Engines)")
    print("=" * 60)
    for engine in ENGINES:
        print(f"  {engine}")
    print()

def print_phase_map():
    """Print all relationship pairs."""
    print("=" * 60)
    print("PHASE MAP (1/7200 Invariant Ring)")
    print("=" * 60)
    for i, pair in enumerate(PHASE_MAP_PAIRS, 1):
        # Simplified output without Japanese characters in repr
        eng = engine_by_id(pair.engine_id)
        print(f"  {i:2d}. E{pair.engine_id}({eng.name}) [{pair.phase_label}] -> {pair.target_label}")
    print()

def print_rhythm_mapping():
    """Print rhythm-to-phase conversion."""
    print("=" * 60)
    print("RHYTHM-PHASE MAPPING")
    print("=" * 60)
    print(f"  Invariant: 1/{PHASE_DIVISIONS} = {INVARIANT_PHASE:.6f}")
    print(f"  Phase width: {SECONDS_PER_DAY / PHASE_DIVISIONS:.4f} seconds")
    print()
    print("  Rhythm -> Phase Conversion:")
    print(f"    TICK   {RhythmPhase.TICK.value*1000:>6.0f}ms -> {TICK_PHASES:>5d} phases")
    print(f"    BEAT   {RhythmPhase.BEAT.value*1000:>6.0f}ms -> {BEAT_PHASES:>5d} phases")
    print(f"    BREATH {RhythmPhase.BREATH.value*1000:>6.0f}ms -> {BREATH_PHASES:>5d} phases")
    print(f"    CYCLE  {RhythmPhase.CYCLE.value*1000:>6.0f}ms -> {CYCLE_PHASES:>5d} phases")
    print()

if __name__ == "__main__":
    import sys
    import io
    # Force UTF-8 output
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print_engine_roster()
    print_rhythm_mapping()
    print_phase_map()
    
    # Example: Get E1 (365) relationship
    rel = get_relationship_for_engine(1)
    print(f"E1 Relationship: {rel.hiragana}")
    print()
