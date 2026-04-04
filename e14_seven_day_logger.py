"""
E14 SEVEN-DAY OPERATIONAL LOG
Continuous data collection for mathematical mapping and validation.
Runs 24/7 for 7 days, records every cycle.
"""

import psutil
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
import threading

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

# Log directory
LOG_DIR = Path("C:/Users/Admin/OneDrive/Desktop/~E14-/logs_7day")
LOG_DIR.mkdir(exist_ok=True)

class E14SevenDayLogger:
    """Continuous logging for 7 days of operational data."""
    
    def __init__(self):
        self.state = {eng: {
            "tick": float(i * 6228.57),
            "beat": float(i * 6228.57),
            "breath": float(i * 6228.57),
            "cycle": float(i * 6228.57),
            "heat": INSOLATION_EQUILIBRIUM + (i * 0.001 - 0.007),
            "weather": 0.5,
        } for i, eng in enumerate(ENGINES)}
        
        self.cycle_count = 0
        self.execution_count = 0
        self.queue_count = 0
        self.start_time = time.time()
        self.start_datetime = datetime.now()
        
        # Per-day files
        self.current_day = 0
        self.day_start_time = self.start_time
        
        print(f"[E14 SEVEN-DAY LOGGER INITIALIZED]")
        print(f"  Start time: {self.start_datetime.isoformat()}")
        print(f"  Log directory: {LOG_DIR}")
        print(f"  Expected end: {(self.start_datetime + timedelta(days=7)).isoformat()}")
        print()
    
    def phase_diff(self, a, b):
        d = abs(a - b)
        return min(d, 86400.0 - d)
    
    def compute_k_score(self):
        """Compute K-score."""
        ratios = []
        
        for axis, tol in [("tick", 25), ("beat", 50), ("breath", 100), ("cycle", 200)]:
            converged = sum(1 for s in self.state.values() 
                           if self.phase_diff(s[axis], ARIES_POINT) <= tol)
            ratios.append(converged / len(self.state))
        
        heat_converged = sum(1 for s in self.state.values() 
                            if abs(s["heat"] - INSOLATION_EQUILIBRIUM) <= HEAT_TOLERANCE)
        ratios.append(heat_converged / len(self.state))
        
        weather_converged = sum(1 for s in self.state.values() 
                               if s["weather"] <= WEATHER_MAX)
        ratios.append(weather_converged / len(self.state))
        
        k = 1.0
        for r in ratios:
            k *= r
        return k ** (1.0 / len(ratios))
    
    def get_resources(self):
        """Get system resources."""
        return {
            "cpu_headroom": 100.0 - psutil.cpu_percent(interval=0.01),
            "memory_headroom": 100.0 - psutil.virtual_memory().percent,
            "disk_headroom": 100.0 - psutil.disk_usage('/').percent,
        }
    
    def update_state(self):
        """Update all engines."""
        for eng in self.state:
            for axis in ["tick", "beat", "breath", "cycle"]:
                current = self.state[eng][axis]
                self.state[eng][axis] = current * (1.0 - PHASE_PULLBACK) + ARIES_POINT * PHASE_PULLBACK
            
            h = self.state[eng]["heat"]
            self.state[eng]["heat"] = h * (1.0 - HEAT_DAMPING) + INSOLATION_EQUILIBRIUM * HEAT_DAMPING
            
            elapsed = time.time() - self.start_time
            self.state[eng]["weather"] = 0.5 + 0.3 * ((elapsed % 60) / 60)
    
    def can_execute(self):
        """Check execution conditions."""
        k = self.compute_k_score()
        resources = self.get_resources()
        
        conditions = {
            "k_score": k >= K_THRESHOLD,
            "cpu": resources["cpu_headroom"] > CPU_MIN,
            "memory": resources["memory_headroom"] > MEMORY_MIN,
            "disk": resources["disk_headroom"] > DISK_MIN,
            "weather": self.state[ENGINES[0]]["weather"] <= WEATHER_MAX,
        }
        
        return all(conditions.values()), k, resources, conditions
    
    def run_cycle(self):
        """Run one cycle and log."""
        self.cycle_count += 1
        cycle_start = time.time()
        
        self.update_state()
        can_exec, k, resources, conditions = self.can_execute()
        
        if can_exec:
            self.execution_count += 1
            status = "EXECUTED"
        else:
            self.queue_count += 1
            status = "QUEUED"
        
        elapsed = time.time() - self.start_time
        cycle_time = time.time() - cycle_start
        
        cycle_data = {
            "cycle": self.cycle_count,
            "elapsed_seconds": elapsed,
            "timestamp": datetime.now().isoformat(),
            "k_score": round(k, 4),
            "resources": {
                "cpu_headroom": round(resources["cpu_headroom"], 1),
                "memory_headroom": round(resources["memory_headroom"], 1),
                "disk_headroom": round(resources["disk_headroom"], 1),
            },
            "conditions": {k: v for k, v in conditions.items()},
            "status": status,
            "cycle_time_ms": round(cycle_time * 1000, 2),
        }
        
        return cycle_data
    
    def write_cycle_log(self, cycle_data):
        """Write cycle to daily log file."""
        day_num = int((time.time() - self.start_time) / 86400) + 1
        
        if day_num != self.current_day:
            self.current_day = day_num
            self.day_start_time = time.time()
        
        log_file = LOG_DIR / f"day_{day_num:02d}.jsonl"
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(cycle_data) + '\n')
    
    def write_summary(self):
        """Write hourly summary."""
        elapsed = time.time() - self.start_time
        hours = elapsed / 3600
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "hours_elapsed": round(hours, 2),
            "days_elapsed": round(hours / 24, 2),
            "total_cycles": self.cycle_count,
            "executions": self.execution_count,
            "queued": self.queue_count,
            "execution_rate": round(self.execution_count / max(1, self.cycle_count) * 100, 2),
            "cycles_per_hour": round(self.cycle_count / max(1, hours), 0),
        }
        
        summary_file = LOG_DIR / "summary.jsonl"
        with open(summary_file, 'a') as f:
            f.write(json.dumps(summary) + '\n')
        
        return summary

def run_seven_day_test():
    """Run continuous test for 7 days."""
    logger = E14SevenDayLogger()
    
    print("[STARTING 7-DAY OPERATIONAL TEST]")
    print(f"  Logging to: {LOG_DIR}")
    print(f"  This will run for 7 days continuously")
    print(f"  Data collected per cycle: K-score, resources, conditions, execution status")
    print()
    
    summary_interval = 3600  # Write summary every hour
    last_summary = time.time()
    
    cycle = 0
    while True:
        try:
            cycle_data = logger.run_cycle()
            logger.write_cycle_log(cycle_data)
            
            # Write summary every hour
            if time.time() - last_summary > summary_interval:
                summary = logger.write_summary()
                last_summary = time.time()
                
                print(f"[HOUR {summary['hours_elapsed']:.1f}] "
                      f"Cycles: {summary['total_cycles']} | "
                      f"Executed: {summary['executions']} ({summary['execution_rate']:.2f}%) | "
                      f"Queued: {summary['queued']}")
            
            # Print every 100 cycles
            if cycle % 100 == 0:
                print(f"  Cycle {logger.cycle_count}: K={cycle_data['k_score']:.4f} | {cycle_data['status']}")
            
            cycle += 1
            
            # Check if 7 days complete
            elapsed = time.time() - logger.start_time
            if elapsed > 7 * 86400:
                print("\n[7-DAY TEST COMPLETE]")
                final_summary = logger.write_summary()
                print(f"  Total cycles: {final_summary['total_cycles']}")
                print(f"  Executions: {final_summary['executions']}")
                print(f"  Queued: {final_summary['queued']}")
                print(f"  Execution rate: {final_summary['execution_rate']:.2f}%")
                print(f"  Data files: {list(LOG_DIR.glob('day_*.jsonl'))}")
                break
            
            # Sleep to control cycle rate (~50 cycles/sec)
            time.sleep(0.02)
        
        except KeyboardInterrupt:
            print("\n[TEST INTERRUPTED]")
            summary = logger.write_summary()
            print(f"  Cycles completed: {summary['total_cycles']}")
            print(f"  Hours elapsed: {summary['hours_elapsed']:.2f}")
            print(f"  Data saved to: {LOG_DIR}")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(1)

if __name__ == "__main__":
    run_seven_day_test()
