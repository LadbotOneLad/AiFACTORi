"""
E14 DEEP CYCLE ANALYSIS
Inspect what's happening in each decision cycle in detail.
"""

import psutil
import time
import json
from datetime import datetime
from collections import deque

ARIES_POINT = 0.0
INSOLATION_EQUILIBRIUM = 0.075
HEAT_TOLERANCE = 0.005
PHASE_PULLBACK = 0.95
HEAT_DAMPING = 0.02

K_THRESHOLD = 0.99
CPU_MIN = 10
MEMORY_MIN = 15
DISK_MIN = 20
WEATHER_MAX = 0.6

ENGINES = [f"E{i:02d}" for i in range(1, 14)]

class E14CycleAnalyzer:
    """Deep inspection of E14 cycles."""
    
    def __init__(self):
        self.state = {eng: {
            "tick": float(i * 6228.57),  # Start each engine at different phase
            "beat": float(i * 6228.57),
            "breath": float(i * 6228.57),
            "cycle": float(i * 6228.57),
            "heat": INSOLATION_EQUILIBRIUM + (i * 0.001 - 0.007),
            "weather": 0.5,
        } for i, eng in enumerate(ENGINES)}
        
        self.cycle_log = deque(maxlen=1000)
        self.cycle_count = 0
        self.start_time = time.time()
    
    def phase_diff(self, a, b):
        """Circular distance."""
        d = abs(a - b)
        return min(d, 86400.0 - d)
    
    def analyze_single_engine(self, eng):
        """Analyze one engine's state."""
        s = self.state[eng]
        
        analysis = {
            "engine": eng,
            "phases": {
                "tick": round(s["tick"], 2),
                "beat": round(s["beat"], 2),
                "breath": round(s["breath"], 2),
                "cycle": round(s["cycle"], 2),
            },
            "distances": {
                "tick_to_aries": round(self.phase_diff(s["tick"], ARIES_POINT), 2),
                "beat_to_aries": round(self.phase_diff(s["beat"], ARIES_POINT), 2),
                "breath_to_aries": round(self.phase_diff(s["breath"], ARIES_POINT), 2),
                "cycle_to_aries": round(self.phase_diff(s["cycle"], ARIES_POINT), 2),
            },
            "heat": {
                "value": round(s["heat"], 6),
                "distance_to_target": round(abs(s["heat"] - INSOLATION_EQUILIBRIUM), 6),
                "converged": abs(s["heat"] - INSOLATION_EQUILIBRIUM) <= HEAT_TOLERANCE,
            },
            "weather": round(s["weather"], 4),
        }
        
        return analysis
    
    def compute_k_score_detailed(self):
        """Compute K-score with detailed breakdown."""
        ratios = {}
        
        # Temporal axes
        for axis, tol in [("tick", 25), ("beat", 50), ("breath", 100), ("cycle", 200)]:
            converged = sum(1 for s in self.state.values() 
                           if self.phase_diff(s[axis], ARIES_POINT) <= tol)
            ratios[axis] = {
                "converged_count": converged,
                "total": len(self.state),
                "ratio": round(converged / len(self.state), 4),
                "tolerance": tol,
            }
        
        # Heat
        heat_converged = sum(1 for s in self.state.values() 
                            if abs(s["heat"] - INSOLATION_EQUILIBRIUM) <= HEAT_TOLERANCE)
        ratios["heat"] = {
            "converged_count": heat_converged,
            "total": len(self.state),
            "ratio": round(heat_converged / len(self.state), 4),
            "tolerance": HEAT_TOLERANCE,
        }
        
        # Weather
        weather_converged = sum(1 for s in self.state.values() 
                               if s["weather"] <= WEATHER_MAX)
        ratios["weather"] = {
            "converged_count": weather_converged,
            "total": len(self.state),
            "ratio": round(weather_converged / len(self.state), 4),
            "threshold": WEATHER_MAX,
        }
        
        # Compute K
        k_values = [r["ratio"] for r in ratios.values()]
        k = 1.0
        for v in k_values:
            k *= v
        k = k ** (1.0 / len(k_values))
        
        return {
            "axis_convergence": ratios,
            "k_score": round(k, 4),
            "k_threshold": K_THRESHOLD,
            "k_ready": k >= K_THRESHOLD,
        }
    
    def get_resources_detailed(self):
        """Get detailed resource analysis."""
        cpu_percent = psutil.cpu_percent(interval=0.01)
        cpu_headroom = 100.0 - cpu_percent
        
        mem = psutil.virtual_memory()
        mem_headroom = 100.0 - mem.percent
        
        disk = psutil.disk_usage('/')
        disk_headroom = 100.0 - disk.percent
        
        return {
            "cpu": {
                "percent_used": round(cpu_percent, 1),
                "headroom": round(cpu_headroom, 1),
                "threshold": CPU_MIN,
                "ok": cpu_headroom > CPU_MIN,
            },
            "memory": {
                "percent_used": round(mem.percent, 1),
                "used_gb": round(mem.used / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "total_gb": round(mem.total / (1024**3), 2),
                "headroom": round(mem_headroom, 1),
                "threshold": MEMORY_MIN,
                "ok": mem_headroom > MEMORY_MIN,
            },
            "disk": {
                "percent_used": round(disk.percent, 1),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "total_gb": round(disk.total / (1024**3), 2),
                "headroom": round(disk_headroom, 1),
                "threshold": DISK_MIN,
                "ok": disk_headroom > DISK_MIN,
            },
        }
    
    def update_state(self):
        """Update all engines one cycle."""
        for eng in self.state:
            # Pullback toward Aries Point
            for axis in ["tick", "beat", "breath", "cycle"]:
                current = self.state[eng][axis]
                self.state[eng][axis] = current * (1.0 - PHASE_PULLBACK) + ARIES_POINT * PHASE_PULLBACK
            
            # Heat damping
            h = self.state[eng]["heat"]
            self.state[eng]["heat"] = h * (1.0 - HEAT_DAMPING) + INSOLATION_EQUILIBRIUM * HEAT_DAMPING
            
            # Weather (sine wave)
            elapsed = time.time() - self.start_time
            self.state[eng]["weather"] = 0.5 + 0.3 * (elapsed % 60) / 60
    
    def can_execute(self):
        """Check all conditions."""
        k_detail = self.compute_k_score_detailed()
        resources = self.get_resources_detailed()
        
        conditions = {
            "k_score": {
                "value": k_detail["k_score"],
                "threshold": K_THRESHOLD,
                "pass": k_detail["k_ready"],
            },
            "cpu_headroom": {
                "value": resources["cpu"]["headroom"],
                "threshold": CPU_MIN,
                "pass": resources["cpu"]["ok"],
            },
            "memory_headroom": {
                "value": resources["memory"]["headroom"],
                "threshold": MEMORY_MIN,
                "pass": resources["memory"]["ok"],
            },
            "disk_headroom": {
                "value": resources["disk"]["headroom"],
                "threshold": DISK_MIN,
                "pass": resources["disk"]["ok"],
            },
            "weather": {
                "value": self.state[ENGINES[0]]["weather"],
                "threshold": WEATHER_MAX,
                "pass": self.state[ENGINES[0]]["weather"] <= WEATHER_MAX,
            },
        }
        
        all_pass = all(c["pass"] for c in conditions.values())
        
        return {
            "executable": all_pass,
            "conditions": conditions,
            "k_detail": k_detail,
            "resources": resources,
        }
    
    def run_cycle_with_analysis(self):
        """Run one cycle with deep analysis."""
        self.cycle_count += 1
        cycle_start = time.time()
        
        # Phase 1: Update state
        self.update_state()
        
        # Phase 2: Analyze
        execution_check = self.can_execute()
        
        # Phase 3: Log
        cycle_duration = time.time() - cycle_start
        
        cycle_data = {
            "cycle_number": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "duration_ms": round(cycle_duration * 1000, 2),
            "k_detail": execution_check["k_detail"],
            "resources": execution_check["resources"],
            "conditions": execution_check["conditions"],
            "executable": execution_check["executable"],
        }
        
        self.cycle_log.append(cycle_data)
        return cycle_data
    
    def print_cycle_analysis(self, cycle_data):
        """Pretty print cycle analysis."""
        print()
        print("-" * 120)
        print(f"CYCLE {cycle_data['cycle_number']} | {cycle_data['timestamp']} | {cycle_data['duration_ms']}ms")
        print("-" * 120)
        
        # K-Score breakdown
        k = cycle_data["k_detail"]
        print()
        print("[K-SCORE BREAKDOWN]")
        print(f"  Current K: {k['k_score']} (threshold: {k['k_threshold']}) {'READY' if k['k_ready'] else 'WAITING'}")
        print()
        print("  Per-axis convergence:")
        for axis, conv in k["axis_convergence"].items():
            print(f"    {axis:8s}: {conv['converged_count']:2d}/{conv['total']} engines | ratio: {conv['ratio']:.4f}")
        
        # Resource breakdown
        print()
        print("[SYSTEM RESOURCES]")
        res = cycle_data["resources"]
        
        print(f"  CPU:    {res['cpu']['percent_used']:5.1f}% used | {res['cpu']['headroom']:5.1f}% headroom | need > {res['cpu']['threshold']}% {'OK' if res['cpu']['ok'] else 'LOW'}")
        print(f"  Memory: {res['memory']['percent_used']:5.1f}% used | {res['memory']['headroom']:5.1f}% headroom | need > {res['memory']['threshold']}%")
        print(f"           {res['memory']['used_gb']:.1f}GB used / {res['memory']['available_gb']:.1f}GB available {'OK' if res['memory']['ok'] else 'LOW'}")
        print(f"  Disk:   {res['disk']['percent_used']:5.1f}% used | {res['disk']['headroom']:5.1f}% headroom | need > {res['disk']['threshold']}% {'OK' if res['disk']['ok'] else 'LOW'}")
        print(f"           {res['disk']['used_gb']:.1f}GB used / {res['disk']['free_gb']:.1f}GB free")
        
        # Decision conditions
        print()
        print("[DECISION CONDITIONS]")
        cond = cycle_data["conditions"]
        for key, val in cond.items():
            status = "PASS" if val["pass"] else "FAIL"
            print(f"  {key:20s}: {val['value']:8.2f} (need {'>=' if key == 'k_score' else '>'} {val['threshold']:6.2f}) [{status}]")
        
        # Final verdict
        print()
        print("[EXECUTION VERDICT]")
        if cycle_data["executable"]:
            print("  STATUS: READY TO EXECUTE [ALL CONDITIONS MET]")
        else:
            failed = [k for k, v in cond.items() if not v["pass"]]
            print(f"  STATUS: CANNOT EXECUTE [BLOCKED BY: {', '.join(failed)}]")
        
        print()

def main():
    """Run cycle analysis."""
    analyzer = E14CycleAnalyzer()
    
    print("\n" + "=" * 120)
    print(f"E14 DEEP CYCLE ANALYSIS")
    print("=" * 120)
    
    print("\nStarting cycle analysis...")
    print("Press Ctrl+C to stop\n")
    
    try:
        cycle = 0
        while True:
            cycle += 1
            
            cycle_data = analyzer.run_cycle_with_analysis()
            analyzer.print_cycle_analysis(cycle_data)
            
            # Show some engine details every 10 cycles
            if cycle % 10 == 0:
                print("[ENGINE STATE SAMPLE]")
                for eng_idx in [0, 6, 12]:
                    eng = ENGINES[eng_idx]
                    eng_analysis = analyzer.analyze_single_engine(eng)
                    print(f"\n  {eng}:")
                    print(f"    Phases: tick={eng_analysis['phases']['tick']:.1f}, beat={eng_analysis['phases']['beat']:.1f}, breath={eng_analysis['phases']['breath']:.1f}, cycle={eng_analysis['phases']['cycle']:.1f}")
                    print(f"    Distances: tick={eng_analysis['distances']['tick_to_aries']:.1f}, beat={eng_analysis['distances']['beat_to_aries']:.1f}, heat={eng_analysis['heat']['distance_to_target']:.6f}")
                print()
            
            time.sleep(0.5)  # Slow down for readability
    
    except KeyboardInterrupt:
        print("\n[ANALYSIS SHUTDOWN]")
        print(f"Total cycles: {analyzer.cycle_count}")
        print("\nLast 5 cycles summary:")
        for i, cycle_data in enumerate(list(analyzer.cycle_log)[-5:], 1):
            print(f"  Cycle {cycle_data['cycle_number']}: K={cycle_data['k_detail']['k_score']:.4f} | Executable: {cycle_data['executable']}")

if __name__ == "__main__":
    main()
