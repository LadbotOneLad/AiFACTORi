# kotahitanga_driftwatcher.py
# こたひたんが・どりふと見守り
# Te Kaitiaki o te Kotahitanga — Drift Watcher
#
# Monitors K(t) coherence drift across clocked rhythm cycles
# TICK=50ms, BEAT=200ms, BREATH=1500ms, CYCLE=12s
#
# Real-time monitoring with drift detection & alerting

import json
import time
import sys
from datetime import datetime
from subprocess import Popen, PIPE
from pathlib import Path
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

# Path to SymPy engine
ENGINE = Path(__file__).parent / "kotahitanga_sympy.py"

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

def get_rhythm_phase(elapsed: float) -> tuple[str, float]:
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

def run_sympy(pass_flags: dict) -> dict:
    """
    Call kotahitanga_sympy.py and return full result.
    
    Returns: {"K": float, "K_percent": float, "status": str}
    On error: {"K": -1.0, "K_percent": -1.0, "status": "ERROR"}
    """
    payload = json.dumps({"pass_flags": pass_flags}).encode()
    
    try:
        proc = Popen(
            ["python", str(ENGINE)],
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE
        )
        out, err = proc.communicate(payload, timeout=5)
        result = json.loads(out.decode())
        return {
            "K": float(result.get("K", -1.0)),
            "K_percent": float(result.get("K_percent", -1.0)),
            "status": result.get("status", "ERROR")
        }
    except Exception as e:
        log(f"SymPy Error: {e}", "FAIL")
        return {"K": -1.0, "K_percent": -1.0, "status": "ERROR"}

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
    verbose: bool = False
):
    """
    Monitor K(t) coherence with drift detection.
    
    Args:
        check_interval: How often to sample (default: BEAT=200ms)
        max_cycles: Max cycles before exit (None = infinite)
        verbose: Print detailed phase info
    """
    log("こたひたんが・どりふと見守り — 開始（Tea Kaitiaki o te Kotahitanga）")
    log(f"Check interval: {check_interval*1000:.0f}ms | Max cycles: {max_cycles or '∞'}")
    
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
                "層":   True,   # Layer OK
                "しん": True,   # Identity OK
                "こう": True,   # Structure OK
                "つな": True,   # Topology OK
                "うご": True,   # Rhythm OK
                "かん": True,   # Security OK
                "みち": True,   # Navigation OK
            }
            
            # Call SymPy engine
            result = run_sympy(pass_flags)
            K = result["K"]
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
                    f"K(t) = {K:.3f} ({result['K_percent']:.1f}%) | "
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
    
    parser = argparse.ArgumentParser(description="Kotahitanja Drift Watcher")
    parser.add_argument("--interval", type=float, default=BEAT_S, help=f"Check interval in seconds (default: {BEAT_S})")
    parser.add_argument("--max-cycles", type=int, default=None, help="Max cycles before exit")
    parser.add_argument("--verbose", action="store_true", help="Verbose phase output")
    
    args = parser.parse_args()
    
    kotahitanga_driftwatcher(
        check_interval=args.interval,
        max_cycles=args.max_cycles,
        verbose=args.verbose
    )
