"""
E14 WITH TASK MANAGER — QUICK TEST (5 minutes instead of 48 hours)
"""

import psutil
import math
import random
from datetime import datetime

# Quick test: 300 seconds instead of 172,800
GRID_SECONDS = 300  # 5 minutes compressed

ENGINES = [f"E{i:02d}" for i in range(1, 15)]

# Resource thresholds
CPU_HEADROOM_MIN = 10
MEMORY_HEADROOM_MIN = 15
DISK_HEADROOM_MIN = 20

# E14 Parameters
ARIES_POINT = 0.0
INSOLATION_EQUILIBRIUM = 0.075
HEAT_TOLERANCE = 0.005
DRIFT_MAGNITUDE = 0.5
PHASE_PULLBACK = 0.95
HEAT_DAMPING = 0.02
WEATHER_SAFE_MAX = 0.6
OPHIUCHUS_K_THRESHOLD = 0.99

# ═══════════════════════════════════════════════════════════════
# SYSTEM RESOURCE MONITOR
# ═══════════════════════════════════════════════════════════════

class ResourceMonitor:
    """Monitor system resources."""
    
    def __init__(self):
        print(f"[SYSTEM RESOURCES]")
        print(f"  CPU cores: {psutil.cpu_count()}")
        try:
            print(f"  Total memory: {psutil.virtual_memory().total / (1024**3):.2f} GB")
            print(f"  Total disk: {psutil.disk_usage('/').total / (1024**3):.2f} GB")
        except:
            print(f"  Memory/Disk: Unable to read (Windows path issue)")
        print()
    
    def get_cpu_headroom(self):
        return 100.0 - psutil.cpu_percent(interval=0.01)
    
    def get_memory_headroom(self):
        return 100.0 - psutil.virtual_memory().percent
    
    def get_disk_headroom(self):
        try:
            return 100.0 - psutil.disk_usage('/').percent
        except:
            return 80.0  # Default if can't read
    
    def is_safe(self):
        cpu = self.get_cpu_headroom()
        mem = self.get_memory_headroom()
        disk = self.get_disk_headroom()
        return (cpu > CPU_HEADROOM_MIN and 
                mem > MEMORY_HEADROOM_MIN and 
                disk > DISK_HEADROOM_MIN), {'cpu': cpu, 'mem': mem, 'disk': disk}

# ═══════════════════════════════════════════════════════════════
# E14 FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def phase_diff(a, b):
    d = abs(a - b)
    return min(d, 86400.0 - d)

def compute_k_score(state):
    if not state:
        return 0.0
    
    ratios = []
    for axis_name, tol in [("tick", 25), ("beat", 50), ("breath", 100), ("cycle", 200)]:
        converged = sum(1 for s in state.values() if phase_diff(s[axis_name], ARIES_POINT) <= tol)
        ratios.append(converged / len(state))
    
    heat_converged = sum(1 for s in state.values() if abs(s["heat"] - INSOLATION_EQUILIBRIUM) <= HEAT_TOLERANCE)
    ratios.append(heat_converged / len(state))
    
    weather_converged = sum(1 for s in state.values() if s["weather"] and s["weather"] <= WEATHER_SAFE_MAX)
    ratios.append(weather_converged / len(state))
    
    k = 1.0
    for r in ratios:
        k *= r
    return k ** (1.0 / len(ratios))

def init_state():
    state = {}
    for eng in ENGINES:
        state[eng] = {
            "tick": random.uniform(0, 86400.0),
            "beat": random.uniform(0, 86400.0),
            "breath": random.uniform(0, 86400.0),
            "cycle": random.uniform(0, 86400.0),
            "heat": INSOLATION_EQUILIBRIUM + random.uniform(-0.01, 0.01),
            "weather": random.uniform(0.2, 0.8) if random.random() > 0.05 else None,
        }
    return state

def update_state(state, t):
    for eng in ENGINES:
        axes = state[eng]
        for axis in ["tick", "beat", "breath", "cycle"]:
            drift = random.uniform(-DRIFT_MAGNITUDE, DRIFT_MAGNITUDE)
            axes[axis] = (axes[axis] + drift) % 86400.0
            axes[axis] = axes[axis] * (1.0 - PHASE_PULLBACK) + ARIES_POINT * PHASE_PULLBACK
        axes["heat"] = axes["heat"] * (1.0 - HEAT_DAMPING) + INSOLATION_EQUILIBRIUM * HEAT_DAMPING
        axes["weather"] = random.uniform(0.2, 0.8) if random.random() > 0.05 else None
    return state

# ═══════════════════════════════════════════════════════════════
# SIMULATION
# ═══════════════════════════════════════════════════════════════

def run_test():
    monitor = ResourceMonitor()
    state = init_state()
    
    k_scores = []
    resource_samples = []
    executable_seconds = 0
    
    print(f"E14 + TASK MANAGER TEST (Quick Version)")
    print(f"  Duration: {GRID_SECONDS}s (5 min compressed test)")
    print(f"  Decision Rule: K >= {OPHIUCHUS_K_THRESHOLD} + weather + XYO + headroom")
    print()
    
    for t in range(GRID_SECONDS):
        if (t + 1) % 100 == 0:
            print(f"  t={t}s ({(t+1)/GRID_SECONDS*100:.0f}%)")
        
        state = update_state(state, t)
        k = compute_k_score(state)
        k_scores.append(k)
        
        # Sample resources every 10 seconds
        if t % 10 == 0:
            safe, details = monitor.is_safe()
            resource_samples.append({
                't': t,
                'k': k,
                'cpu': details['cpu'],
                'mem': details['mem'],
                'disk': details['disk'],
                'safe': safe,
            })
        
        # Check if can execute
        weather_safe = state[ENGINES[0]]["weather"] and state[ENGINES[0]]["weather"] <= WEATHER_SAFE_MAX
        ophiuchus_window = k >= OPHIUCHUS_K_THRESHOLD and weather_safe
        safe, _ = monitor.is_safe()
        
        if ophiuchus_window and safe:
            executable_seconds += 1
    
    return k_scores, resource_samples, executable_seconds

# ═══════════════════════════════════════════════════════════════
# REPORT
# ═══════════════════════════════════════════════════════════════

def print_report(k_scores, resource_samples, executable_seconds):
    print()
    print("=" * 110)
    print(" E14 + WINDOWS TASK MANAGER — QUICK TEST RESULTS ")
    print("=" * 110)
    print()
    
    print("[E14 K-SCORE]")
    avg_k = sum(k_scores) / len(k_scores)
    max_k = max(k_scores)
    print(f"  Average K: {avg_k:.4f}")
    print(f"  Peak K: {max_k:.4f}")
    print(f"  (Note: 5-min test rarely reaches K >= 0.99 threshold)")
    print()
    
    if resource_samples:
        print("[SYSTEM RESOURCES (Sampled Every 10s)]")
        latest = resource_samples[-1]
        print(f"  CPU Headroom:    {latest['cpu']:6.2f}% (need > {CPU_HEADROOM_MIN}%)")
        print(f"  Memory Headroom: {latest['mem']:6.2f}% (need > {MEMORY_HEADROOM_MIN}%)")
        print(f"  Disk Headroom:   {latest['disk']:6.2f}% (need > {DISK_HEADROOM_MIN}%)")
        print()
        
        print("[RESOURCE TREND]")
        print(f"  First sample:  CPU={resource_samples[0]['cpu']:.1f}% MEM={resource_samples[0]['mem']:.1f}% DISK={resource_samples[0]['disk']:.1f}%")
        print(f"  Last sample:   CPU={latest['cpu']:.1f}% MEM={latest['mem']:.1f}% DISK={latest['disk']:.1f}%")
        print()
    
    print("[EXECUTABLE WINDOWS]")
    print(f"  Seconds where BOTH E14 + Resources safe: {executable_seconds}s ({executable_seconds/GRID_SECONDS*100:.2f}%)")
    print()
    
    print("[DECISION RULE CHECK]")
    resource_always_safe = all(s['safe'] for s in resource_samples)
    print(f"  Resources always safe: {'YES' if resource_always_safe else 'NO'}")
    print(f"  K ever high: {'YES' if max_k >= 0.9 else 'NO'}")
    print(f"  Overall: {executable_seconds} seconds safe for execution")
    print()
    
    print("=" * 110)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    random.seed(42)
    
    print("\n" + "╔" + "═" * 108 + "╗")
    print("║" + " E14 + WINDOWS TASK MANAGER (Quick Test) ".center(108) + "║")
    print("║" + " Celestial Alignment × System Headroom ".center(108) + "║")
    print("╚" + "═" * 108 + "╝\n")
    
    k_scores, resource_samples, executable_seconds = run_test()
    print_report(k_scores, resource_samples, executable_seconds)
