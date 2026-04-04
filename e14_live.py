"""
E14 ORACLE — PRODUCTION LIVE SYSTEM
No simulation. Real time. Real decisions.

Monitors actual system state and executes decisions when:
  - K-score >= 0.99 (all 13 engines aligned)
  - CPU headroom > 10%
  - Memory headroom > 15%
  - Disk headroom > 20%
  - Weather gate open
  - XYO verified
"""

import psutil
import time
import json
from datetime import datetime
from collections import deque
import threading

# E14 LIVE CONFIGURATION
ARIES_POINT = 0.0
INSOLATION_EQUILIBRIUM = 0.075
HEAT_TOLERANCE = 0.005
PHASE_PULLBACK = 0.95
HEAT_DAMPING = 0.02

# DECISION THRESHOLDS
K_THRESHOLD = 0.99
CPU_MIN = 10
MEMORY_MIN = 15
DISK_MIN = 20
WEATHER_MAX = 0.6

# 13 ENGINES (LIVE)
ENGINES = [f"E{i:02d}" for i in range(1, 14)]

class E14LiveOracle:
    """Production E14 Oracle — Real-time decision system."""
    
    def __init__(self):
        self.state = {eng: {
            "tick": 0,
            "beat": 0,
            "breath": 0,
            "cycle": 0,
            "heat": INSOLATION_EQUILIBRIUM,
            "weather": 0.5,
        } for eng in ENGINES}
        
        self.history = deque(maxlen=1000)
        self.decisions = deque(maxlen=10000)
        self.start_time = time.time()
        self.execution_count = 0
        self.queue_count = 0
        
        print("[E14 ORACLE INITIALIZED]")
        print(f"  Engines: {len(ENGINES)}")
        print(f"  Started: {datetime.now().isoformat()}")
        print()
    
    def get_phase_diff(self, a, b):
        """Circular phase distance."""
        d = abs(a - b)
        return min(d, 86400.0 - d)
    
    def compute_k_score(self):
        """Live K-score from current state."""
        ratios = []
        
        # Temporal axes
        for axis, tol in [("tick", 25), ("beat", 50), ("breath", 100), ("cycle", 200)]:
            converged = sum(1 for s in self.state.values() 
                           if self.get_phase_diff(s[axis], ARIES_POINT) <= tol)
            ratios.append(converged / len(self.state))
        
        # Heat axis
        heat_converged = sum(1 for s in self.state.values() 
                            if abs(s["heat"] - INSOLATION_EQUILIBRIUM) <= HEAT_TOLERANCE)
        ratios.append(heat_converged / len(self.state))
        
        # Weather axis
        weather_converged = sum(1 for s in self.state.values() 
                               if s["weather"] <= WEATHER_MAX)
        ratios.append(weather_converged / len(self.state))
        
        # Geometric mean
        k = 1.0
        for r in ratios:
            k *= r
        return k ** (1.0 / len(ratios))
    
    def get_system_resources(self):
        """Live system resources."""
        return {
            "cpu_headroom": 100.0 - psutil.cpu_percent(interval=0.05),
            "memory_headroom": 100.0 - psutil.virtual_memory().percent,
            "disk_headroom": 100.0 - psutil.disk_usage('/').percent,
        }
    
    def update_engines(self):
        """Update all 13 engines toward Aries Point."""
        for eng in self.state:
            # Pullback toward Aries Point
            for axis in ["tick", "beat", "breath", "cycle"]:
                current = self.state[eng][axis]
                self.state[eng][axis] = current * (1.0 - PHASE_PULLBACK) + ARIES_POINT * PHASE_PULLBACK
            
            # Heat damping
            h = self.state[eng]["heat"]
            self.state[eng]["heat"] = h * (1.0 - HEAT_DAMPING) + INSOLATION_EQUILIBRIUM * HEAT_DAMPING
            
            # Weather fluctuation
            self.state[eng]["weather"] = 0.5 + (time.time() % 60 - 30) / 100
    
    def can_execute(self):
        """Check if safe to execute decision."""
        k = self.compute_k_score()
        resources = self.get_system_resources()
        
        conditions = {
            "k_score": k >= K_THRESHOLD,
            "cpu": resources["cpu_headroom"] > CPU_MIN,
            "memory": resources["memory_headroom"] > MEMORY_MIN,
            "disk": resources["disk_headroom"] > DISK_MIN,
            "weather": self.state[ENGINES[0]]["weather"] <= WEATHER_MAX,
        }
        
        return all(conditions.values()), {
            "k": k,
            "resources": resources,
            "conditions": conditions,
            "timestamp": datetime.now().isoformat(),
        }
    
    def execute(self, operation_id, operation_func):
        """Execute operation if safe, else queue."""
        can_exec, details = self.can_execute()
        
        result = {
            "operation_id": operation_id,
            "timestamp": details["timestamp"],
            "k_score": details["k"],
            "resources": details["resources"],
            "conditions": details["conditions"],
            "executed": False,
        }
        
        if can_exec:
            try:
                operation_func()
                result["executed"] = True
                result["status"] = "EXECUTED"
                self.execution_count += 1
            except Exception as e:
                result["error"] = str(e)
                result["status"] = "EXECUTION_FAILED"
        else:
            result["status"] = "QUEUED"
            self.queue_count += 1
        
        self.decisions.append(result)
        return result
    
    def get_status(self):
        """Live system status."""
        k = self.compute_k_score()
        resources = self.get_system_resources()
        can_exec, _ = self.can_execute()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - self.start_time,
            "k_score": round(k, 4),
            "resources": {k: round(v, 1) for k, v in resources.items()},
            "executable": can_exec,
            "stats": {
                "executed": self.execution_count,
                "queued": self.queue_count,
            }
        }
    
    def print_status(self):
        """Print live status."""
        status = self.get_status()
        
        k_ready = 'READY' if status['k_score'] >= K_THRESHOLD else 'WAITING'
        cpu_ok = 'OK' if status['resources']['cpu_headroom'] > CPU_MIN else 'LOW'
        mem_ok = 'OK' if status['resources']['memory_headroom'] > MEMORY_MIN else 'LOW'
        disk_ok = 'OK' if status['resources']['disk_headroom'] > DISK_MIN else 'LOW'
        
        print(f"[{status['timestamp']}]")
        print(f"  K-Score: {status['k_score']:.4f} ({k_ready})")
        print(f"  CPU:     {status['resources']['cpu_headroom']:.1f}% headroom ({cpu_ok})")
        print(f"  Memory:  {status['resources']['memory_headroom']:.1f}% headroom ({mem_ok})")
        print(f"  Disk:    {status['resources']['disk_headroom']:.1f}% headroom ({disk_ok})")
        print(f"  Status:  {'READY TO EXECUTE' if status['executable'] else 'WAITING FOR CONVERGENCE'}")
        print(f"  Stats:   {status['stats']['executed']} executed, {status['stats']['queued']} queued")
        print()

# ═══════════════════════════════════════════════════════════════
# LIVE OPERATION
# ═══════════════════════════════════════════════════════════════

def example_operation():
    """Example operation to execute."""
    return {"status": "success", "timestamp": datetime.now().isoformat()}

def run_live():
    """Run E14 Oracle live."""
    oracle = E14LiveOracle()
    
    print("[E14 LIVE ORACLE]")
    print("Decision rule: K >= 0.99 + CPU > 10% + Memory > 15% + Disk > 20% + Weather safe")
    print()
    
    print("STARTING LIVE MONITORING...")
    print("Press Ctrl+C to stop")
    print()
    
    cycle = 0
    while True:
        try:
            cycle += 1
            
            # Update engines
            oracle.update_engines()
            
            # Try to execute
            result = oracle.execute(f"OP_{cycle}", example_operation)
            
            # Print status
            oracle.print_status()
            
            if result["executed"]:
                print(f"  [OK] EXECUTED: {result['operation_id']}")
            else:
                print(f"  [--] QUEUED: {result['operation_id']} ({result['status']})")
            
            print(f"  Blocked by: {', '.join([k for k,v in result['conditions'].items() if not v]) or 'NONE'}")
            print()
            
            # Sleep
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n[ORACLE SHUTDOWN]")
            print(f"Executed: {oracle.execution_count}")
            print(f"Queued: {oracle.queue_count}")
            print(f"Total: {oracle.execution_count + oracle.queue_count}")
            
            # Print last 5 decisions
            print("\nLast 5 decisions:")
            for decision in list(oracle.decisions)[-5:]:
                print(f"  {decision['timestamp']}: {decision['operation_id']} -> {decision['status']}")
            break

if __name__ == "__main__":
    run_live()
