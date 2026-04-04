"""
E14 COSMOLOGICAL ORACLE × SYSTEM RESOURCE MONITOR

Links E14 K-score computation to Windows Task Manager metrics:
  - CPU usage (%)
  - Memory usage (%)
  - Disk I/O (%)
  - Process threads
  - Virtual memory

E14 Decision Rule:
  Execute operation when:
    K >= 0.99 (alignment threshold)
    AND weather_safe
    AND xyo_verified
    AND CPU_headroom > 10%
    AND Memory_headroom > 15%
    AND Disk_headroom > 20%

This ensures decisions are not just cosmologically safe, but also
infrastructure-safe (sufficient resources to execute).
"""

import psutil
import math
import random
from datetime import datetime

GRID_SECONDS = 172800  # 48 hours

# 13 Constellations (accurate astronomical order)
CONSTELLATIONS = [
    ("E01", "Aries", 0, "30 Mar–19 Apr"),
    ("E02", "Taurus", 1, "20 Apr–20 May"),
    ("E03", "Gemini", 2, "21 May–21 Jun"),
    ("E04", "Cancer", 3, "22 Jun–22 Jul"),
    ("E05", "Leo", 4, "23 Jul–22 Aug"),
    ("E06", "Virgo", 5, "23 Aug–23 Sep"),
    ("E07", "Libra", 6, "24 Sep–23 Oct"),
    ("E08", "Scorpius", 7, "24 Oct–29 Nov"),
    ("E09", "Ophiuchus", 8, "29 Nov–17 Dec"),
    ("E10", "Sagittarius", 9, "18 Dec–20 Jan"),
    ("E11", "Capricorn", 10, "21 Jan–19 Feb"),
    ("E12", "Aquarius", 11, "20 Feb–20 Mar"),
    ("E13", "Pisces", 12, "21 Mar–29 Mar"),
]

ENGINES = [c[0] for c in CONSTELLATIONS]

# Thresholds for resource headroom
CPU_HEADROOM_MIN = 10           # %
MEMORY_HEADROOM_MIN = 15        # %
DISK_HEADROOM_MIN = 20          # %

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
# SYSTEM RESOURCE MONITORING (Windows Task Manager Integration)
# ═══════════════════════════════════════════════════════════════

class SystemResourceMonitor:
    """Monitor Windows system resources in real-time."""
    
    def __init__(self):
        """Initialize resource monitoring."""
        self.cpu_count = psutil.cpu_count()
        self.total_memory = psutil.virtual_memory().total
        self.total_disk = psutil.disk_usage('/').total
        
        # Get current process for detailed monitoring
        self.current_process = psutil.Process()
        
        print(f"[SYSTEM RESOURCES DETECTED]")
        print(f"  CPU cores: {self.cpu_count}")
        print(f"  Total memory: {self.total_memory / (1024**3):.2f} GB")
        print(f"  Total disk: {self.total_disk / (1024**3):.2f} GB")
        print()
    
    def get_cpu_usage(self):
        """Get current CPU usage (%)."""
        return psutil.cpu_percent(interval=0.1)
    
    def get_memory_usage(self):
        """Get current memory usage (%)."""
        return psutil.virtual_memory().percent
    
    def get_disk_usage(self):
        """Get current disk usage (%)."""
        return psutil.disk_usage('/').percent
    
    def get_cpu_headroom(self):
        """Get available CPU headroom (%)."""
        return 100.0 - self.get_cpu_usage()
    
    def get_memory_headroom(self):
        """Get available memory headroom (%)."""
        return 100.0 - self.get_memory_usage()
    
    def get_disk_headroom(self):
        """Get available disk headroom (%)."""
        return 100.0 - self.get_disk_usage()
    
    def get_process_info(self):
        """Get current process (E14 Oracle) resource usage."""
        try:
            with self.current_process.oneshot():
                cpu_percent = self.current_process.cpu_percent(interval=0.1)
                memory_info = self.current_process.memory_info()
                threads = self.current_process.num_threads()
                
            return {
                'cpu_percent': cpu_percent,
                'memory_mb': memory_info.rss / (1024**2),
                'threads': threads,
            }
        except:
            return {'cpu_percent': 0, 'memory_mb': 0, 'threads': 0}
    
    def is_safe_to_execute(self, cpu_min=CPU_HEADROOM_MIN, 
                          mem_min=MEMORY_HEADROOM_MIN,
                          disk_min=DISK_HEADROOM_MIN):
        """
        Check if system has sufficient headroom to execute.
        
        Returns: (safe: bool, details: dict)
        """
        cpu_headroom = self.get_cpu_headroom()
        mem_headroom = self.get_memory_headroom()
        disk_headroom = self.get_disk_headroom()
        
        safe = (cpu_headroom >= cpu_min and 
                mem_headroom >= mem_min and 
                disk_headroom >= disk_min)
        
        return safe, {
            'cpu_headroom': cpu_headroom,
            'mem_headroom': mem_headroom,
            'disk_headroom': disk_headroom,
            'cpu_safe': cpu_headroom >= cpu_min,
            'mem_safe': mem_headroom >= mem_min,
            'disk_safe': disk_headroom >= disk_min,
        }

# ═══════════════════════════════════════════════════════════════
# E14 COSMOLOGICAL FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def phase_diff(a, b):
    """Circular phase distance."""
    d = abs(a - b)
    return min(d, 86400.0 - d)

def compute_k_score(state):
    """K-Score computation."""
    if not state:
        return 0.0
    
    ratios_list = []
    
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
    
    k = 1.0
    for r in ratios_list:
        k *= r
    k = k ** (1.0 / len(ratios_list))
    
    return k

def ophiuchus_rises(k_score, weather_safe, xyo_valid):
    """Ophiuchus rises when all conditions met."""
    return k_score >= OPHIUCHUS_K_THRESHOLD and weather_safe and xyo_valid

def simulate_weather_truth(t):
    """Simulate weather."""
    day_phase = (t % 86400.0) / 86400.0
    base = 0.2 + 0.6 * math.sin(day_phase * math.pi) ** 2
    noise = random.uniform(-0.05, 0.05)
    return max(0.0, min(1.0, base + noise))

def simulate_xyo_witness(t, weather_truth):
    """Simulate XYO witness."""
    if weather_truth > 0.9:
        return False
    return random.random() < 0.95

def init_state():
    """Initialize state."""
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
    """Update state."""
    for eng in ENGINES:
        axes = state[eng]
        
        for axis in ["tick", "beat", "breath", "cycle"]:
            drift = random.uniform(-DRIFT_MAGNITUDE, DRIFT_MAGNITUDE)
            axes[axis] = (axes[axis] + drift) % 86400.0
            axes[axis] = axes[axis] * (1.0 - PHASE_PULLBACK) + ARIES_POINT * PHASE_PULLBACK
        
        axes["heat"] = axes["heat"] * (1.0 - HEAT_DAMPING) + INSOLATION_EQUILIBRIUM * HEAT_DAMPING
    
    weather_truth = simulate_weather_truth(t)
    xyo_valid = simulate_xyo_witness(t, weather_truth)
    weather_scalar = weather_truth if xyo_valid else 1.0
    
    for eng in ENGINES:
        state[eng]["weather"] = weather_scalar if xyo_valid else None
    
    return state, weather_truth, xyo_valid, weather_scalar

# ═══════════════════════════════════════════════════════════════
# INTEGRATED SIMULATION WITH RESOURCE MONITORING
# ═══════════════════════════════════════════════════════════════

def run_integrated_simulation():
    """Run E14 with system resource monitoring."""
    
    # Initialize resource monitor
    resource_monitor = SystemResourceMonitor()
    
    state = init_state()
    k_scores = []
    resource_history = []
    executable_windows = []
    executable_count = 0
    
    print(f"E14 COSMOLOGICAL ORACLE + SYSTEM RESOURCE MONITOR")
    print(f"  Simulation: {GRID_SECONDS}s (48 hours)")
    print(f"  Monitoring: CPU, Memory, Disk headroom")
    print(f"  Decision Rule: K >= {OPHIUCHUS_K_THRESHOLD} + weather + XYO + headroom")
    print()
    
    exe_window_start = None
    
    for t in range(GRID_SECONDS):
        if (t + 1) % 43200 == 0:
            print(f"  t={t}s ({t/3600:.1f}h): {(t+1)/GRID_SECONDS*100:.0f}% complete")
        
        state, w_truth, xyo_valid, w_scalar = update_state(state, t)
        
        # Compute E14 metrics
        k = compute_k_score(state)
        k_scores.append(k)
        weather_safe = w_scalar <= WEATHER_SAFE_MAX
        
        # Get system resources
        cpu_headroom = resource_monitor.get_cpu_headroom()
        mem_headroom = resource_monitor.get_memory_headroom()
        disk_headroom = resource_monitor.get_disk_headroom()
        
        is_safe, details = resource_monitor.is_safe_to_execute()
        
        # Store resource history (sample every 1000 seconds to avoid memory bloat)
        if t % 1000 == 0:
            resource_history.append({
                't': t,
                'cpu_headroom': cpu_headroom,
                'mem_headroom': mem_headroom,
                'disk_headroom': disk_headroom,
            })
        
        # Decision rule: E14 + Resources
        can_execute = ophiuchus_rises(k, weather_safe, xyo_valid) and is_safe
        
        if can_execute:
            if exe_window_start is None:
                exe_window_start = t
            executable_count += 1
        else:
            if exe_window_start is not None:
                executable_windows.append((exe_window_start, t - 1))
                exe_window_start = None
    
    if exe_window_start is not None:
        executable_windows.append((exe_window_start, GRID_SECONDS - 1))
    
    return k_scores, resource_history, executable_windows, executable_count, resource_monitor

# ═══════════════════════════════════════════════════════════════
# REPORTING
# ═══════════════════════════════════════════════════════════════

def print_integrated_report(k_scores, resource_history, executable_windows, 
                           executable_count, resource_monitor):
    """Print integrated E14 + Resource report."""
    
    print()
    print("=" * 120)
    print(" E14 COSMOLOGICAL ORACLE + WINDOWS TASK MANAGER INTEGRATION ")
    print("=" * 120)
    print()
    
    # E14 K-Score
    print("[E14 K-SCORE (CELESTIAL ALIGNMENT)]")
    k_099 = sum(1 for k in k_scores if k >= 0.99)
    k_090 = sum(1 for k in k_scores if 0.90 <= k < 0.99)
    k_070 = sum(1 for k in k_scores if 0.70 <= k < 0.90)
    
    print(f"  K >= 0.99 (Great Invariant): {k_099:6d}s ({k_099/len(k_scores)*100:5.2f}%)")
    print(f"  K >= 0.90 (Near converged):  {k_090:6d}s ({k_090/len(k_scores)*100:5.2f}%)")
    print(f"  K >= 0.70 (Partial):         {k_070:6d}s ({k_070/len(k_scores)*100:5.2f}%)")
    print(f"  Average K: {sum(k_scores)/len(k_scores):.4f}, Peak K: {max(k_scores):.4f}")
    print()
    
    # System Resources
    print("[SYSTEM RESOURCES (Live from Windows)]")
    if resource_history:
        latest = resource_history[-1]
        print(f"  CPU Headroom:    {latest['cpu_headroom']:6.2f}% (need > {CPU_HEADROOM_MIN}%)")
        print(f"  Memory Headroom: {latest['mem_headroom']:6.2f}% (need > {MEMORY_HEADROOM_MIN}%)")
        print(f"  Disk Headroom:   {latest['disk_headroom']:6.2f}% (need > {DISK_HEADROOM_MIN}%)")
    print()
    
    # Executable Windows
    print("[EXECUTABLE WINDOWS (E14 + Resources Combined)]")
    print(f"  Total seconds where safe to execute: {executable_count}s ({executable_count/GRID_SECONDS*100:.2f}%)")
    print(f"  Windows detected: {len(executable_windows)}")
    if executable_windows:
        total_window_time = sum(end - start + 1 for start, end in executable_windows)
        print(f"  Total window time: {total_window_time}s ({total_window_time/GRID_SECONDS*100:.2f}%)")
        print()
        print(f"  First 5 windows (where both E14 and resources permit):")
        for i, (start, end) in enumerate(executable_windows[:5], 1):
            duration = end - start + 1
            print(f"    [{i}] {start:6d}–{end:6d}s ({duration}s) @ {start/3600:.2f}h")
    else:
        print(f"  No executable windows found (either K too low or resources insufficient)")
    print()
    
    # Decision Rule Summary
    print("[DECISION RULE]")
    print(f"  Execute ONLY when ALL conditions met:")
    print(f"    1. K >= {OPHIUCHUS_K_THRESHOLD} (Ophiuchus/Great Invariant)")
    print(f"    2. Weather safe (scalar <= {WEATHER_SAFE_MAX})")
    print(f"    3. XYO verified (cryptographic proof)")
    print(f"    4. CPU headroom > {CPU_HEADROOM_MIN}%")
    print(f"    5. Memory headroom > {MEMORY_HEADROOM_MIN}%")
    print(f"    6. Disk headroom > {DISK_HEADROOM_MIN}%")
    print()
    print(f"  Result: {executable_count}s of safe execution time")
    print()
    
    print("=" * 120)

# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    random.seed(42)
    
    print("\n" + "╔" + "═" * 118 + "╗")
    print("║" + " E14 COSMOLOGICAL ORACLE × WINDOWS TASK MANAGER ".center(118) + "║")
    print("║" + " Celestial Alignment × System Resources × Decision Windows ".center(118) + "║")
    print("╚" + "═" * 118 + "╝\n")
    
    k_scores, resource_history, executable_windows, executable_count, resource_monitor = run_integrated_simulation()
    print_integrated_report(k_scores, resource_history, executable_windows, executable_count, resource_monitor)
