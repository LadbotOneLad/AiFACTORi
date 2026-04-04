# kotahitanga_driftwatcher_docker.py
# Docker版 — SymPy依存なし（スタンドアロン）
# こたひたんが・どりふと見守り（Docker対応版）
#
# Monitors K(t) coherence with drift detection
# No external dependencies - pure Python implementation
# TICK=50ms, BEAT=200ms, BREATH=1500ms, CYCLE=12s

import json
import time
import sys
from datetime import datetime
from collections import deque
from enum import Enum

# ─────────────────────────────────────────────
# Rhythm Constants — りつどう
# ─────────────────────────────────────────────

class Rhythm(Enum):
    TICK   = 0.050      # 50ms — fast micro-feedback
    BEAT   = 0.200      # 200ms — normal reading speed
    BREATH = 1.500      # 1.5s — pause to absorb
    CYCLE  = 12.000     # 12s — full micro-cycle

TICK_S   = Rhythm.TICK.value
BEAT_S   = Rhythm.BEAT.value
BREATH_S = Rhythm.BREATH.value
CYCLE_S  = Rhythm.CYCLE.value

# Drift thresholds
K_THRESHOLD_WARN = 0.8      # K drops below 80% → WARN
K_THRESHOLD_FAIL = 0.5      # K drops below 50% → FAIL
K_STABLE_WINDOW  = 10       # samples for stability check

# ─────────────────────────────────────────────
# Utilities — ユーティリティ
# ─────────────────────────────────────────────

def log(msg: str, level: str = "INFO"):
    """Log with timestamp and level."""
    now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    level_emoji = {
        "INFO": "ℹ️",
        "WARN": "⚠️",
        "FAIL": "❌",
        "OK": "✅",
    }.get(level, "•")
    print(f"[{now}] {level_emoji} {msg}")

def get_rhythm_phase(elapsed: float) -> tuple:
    """Determine rhythm phase and time-in-phase."""
    phase = elapsed % CYCLE_S
    
    if phase < TICK_S:
        return ("TICK", phase / TICK_S)
    elif phase < BEAT_S:
        return ("BEAT", (phase - TICK_S) / (BEAT_S - TICK_S))
    elif phase < BREATH_S:
        return ("BREATH", (phase - BEAT_S) / (BREATH_S - BEAT_S))
    else:
        return ("CYCLE", (phase - BREATH_S) / (CYCLE_S - BREATH_S))

def calculate_K_simple(pass_flags: dict) -> float:
    """
    Simple K calculation (no SymPy needed).
    K = count(PASS) / total
    """
    if not pass_flags:
        return 0.0
    
    pass_count = sum(1 for v in pass_flags.values() if v)
    total = len(pass_flags)
    return pass_count / total

def detect_drift(K_history: deque, window: int = K_STABLE_WINDOW) -> dict:
    """
    Detect coherence drift — どりふと・けんしゅつ
    
    Returns:
        {
            "is_drifting": bool,
            "direction": "stable" | "degrading" | "recovering",
            "velocity": float (change per sample),
            "alert": bool (threshold crossed)
        }
    """
    if len(K_history) < window:
        return {
            "is_drifting": False,
            "direction": "stable",
            "velocity": 0.0,
            "alert": False
        }
    
    recent = list(K_history)[-window:]
    start = recent[0]
    end = recent[-1]
    delta = end - start
    velocity = delta / window
    
    is_drifting = abs(velocity) > 0.01  # More than 1% change per sample
    
    if velocity < -0.01:
        direction = "degrading"
    elif velocity > 0.01:
        direction = "recovering"
    else:
        direction = "stable"
    
    # Alert if below thresholds
    alert = end < K_THRESHOLD_FAIL or (direction == "degrading" and end < K_THRESHOLD_WARN)
    
    return {
        "is_drifting": is_drifting,
        "direction": direction,
        "velocity": velocity,
        "alert": alert
    }

# ─────────────────────────────────────────────
# Main Watcher Loop — メイン見守りループ
# ─────────────────────────────────────────────

def kotahitanga_driftwatcher(
    check_interval: float = BEAT_S,
    max_cycles: int = None,
    verbose: bool = False,
    pass_all: bool = True
):
    """
    Monitor K(t) coherence with drift detection.
    
    Args:
        check_interval: How often to sample (default: BEAT=200ms)
        max_cycles: Max cycles before exit (None = infinite)
        verbose: Print detailed phase info
        pass_all: All dimensions start as PASS (True) or FAIL (False)
    """
    log("こたひたんが・どりふと見守り — 開始（Te Kaitiaki o te Kotahitanga）")
    log(f"Check interval: {check_interval*1000:.0f}ms | Max cycles: {max_cycles or '∞'}")
    log("Mode: Docker standalone (no SymPy dependency)")
    
    t0 = time.time()
    cycle_count = 0
    K_history = deque(maxlen=100)  # Keep last 100 samples
    
    try:
        while True:
            elapsed = time.time() - t0
            phase_name, phase_progress = get_rhythm_phase(elapsed)
            
            # Increment cycle on CYCLE → TICK transition
            if phase_name == "TICK" and phase_progress < 0.1:
                cycle_count += 1
                if max_cycles and cycle_count > max_cycles:
                    log("Max cycles reached. Exiting.", "OK")
                    break
            
            # Example: check all dimensions (replace with real checks)
            pass_flags = {
                "層":   pass_all,   # Layer
                "しん": pass_all,   # Identity
                "こう": pass_all,   # Structure
                "つな": pass_all,   # Topology
                "うご": pass_all,   # Rhythm
                "かん": pass_all,   # Security
                "みち": pass_all,   # Navigation
            }
            
            # Calculate K (simple arithmetic mean)
            K = calculate_K_simple(pass_flags)
            K_history.append(K)
            
            # Detect drift
            drift = detect_drift(K_history)
            
            # Format output
            if verbose:
                # Detailed phase info
                phase_bar = "▁" * int(phase_progress * 8)
                phase_bar = phase_bar.ljust(8)
                log(
                    f"Phase: {phase_name:6s} {phase_bar} | "
                    f"Cycle: {cycle_count:3d} | "
                    f"K(t) = {K:.3f} ({K*100:.1f}%) | "
                    f"Drift: {drift['direction']:10s} ({drift['velocity']:+.4f})"
                )
            else:
                # Compact output
                status_emoji = "✅" if K >= 0.9 else "⚠️" if K >= 0.7 else "❌"
                log(
                    f"{status_emoji} K={K:.3f} | {phase_name} | "
                    f"Drift: {drift['direction']:10s}",
                    level="WARN" if drift['alert'] else "INFO"
                )
            
            # Alert on threshold crossing
            if drift['alert']:
                log(f"ALERT: Coherence drift detected! K={K:.3f}, Direction={drift['direction']}", "FAIL")
            
            # Sleep until next beat
            time.sleep(check_interval)
    
    except KeyboardInterrupt:
        log("Interrupted by user.", "OK")
    except Exception as e:
        log(f"Fatal error: {e}", "FAIL")
        sys.exit(1)
    
    finally:
        elapsed_total = time.time() - t0
        log(f"Watcher stopped. Total time: {elapsed_total:.1f}s, Cycles: {cycle_count}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Kotahitanja Drift Watcher (Docker)")
    parser.add_argument("--interval", type=float, default=BEAT_S, help=f"Check interval in seconds (default: {BEAT_S})")
    parser.add_argument("--max-cycles", type=int, default=None, help="Max cycles before exit")
    parser.add_argument("--verbose", action="store_true", help="Verbose phase output")
    parser.add_argument("--pass-all", type=bool, default=True, help="All dimensions PASS (True) or FAIL (False)")
    
    args = parser.parse_args()
    
    kotahitanga_driftwatcher(
        check_interval=args.interval,
        max_cycles=args.max_cycles,
        verbose=args.verbose,
        pass_all=args.pass_all
    )
