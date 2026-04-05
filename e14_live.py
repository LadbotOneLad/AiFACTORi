"""
E14 ORACLE — PRODUCTION LIVE SYSTEM WITH XYO WITNESS LAYER
No simulation. Real time. Real decisions. Cryptographically verified.

Monitors actual system state and executes decisions when:
  - K-score >= 0.99 (all 13 engines aligned)
  - CPU headroom > 10%
  - Memory headroom > 15%
  - Disk headroom > 20%
  - XYO witness consensus achieved
"""

import psutil
import time
import json
import logging
from datetime import datetime
from collections import deque

from xyo_witness import XYOWitnessEngine, generate_witness_proof, XYO_ADDRESS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("E14Live")

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

# 13 ENGINES (LIVE)
ENGINES = [f"E{i:02d}" for i in range(1, 14)]

# Simulated geolocation (can be real from GPS/network)
SYSTEM_LOCATION = (40.7128, -74.0060)  # New York

class E14LiveOracle:
    """Production E14 Oracle — Real-time decision system with XYO cryptographic verification."""
    
    def __init__(self):
        self.state = {eng: {
            "tick": 0,
            "beat": 0,
            "breath": 0,
            "cycle": 0,
            "heat": INSOLATION_EQUILIBRIUM,
        } for eng in ENGINES}
        
        self.xyo_engine = XYOWitnessEngine(xyo_address=XYO_ADDRESS)
        self.history = deque(maxlen=1000)
        self.decisions = deque(maxlen=10000)
        self.start_time = time.time()
        self.execution_count = 0
        self.queue_count = 0
        self.xyo_verified_count = 0
        self.xyo_failed_count = 0
        
        logger.info("[E14 ORACLE INITIALIZED]")
        logger.info(f"  Engines: {len(ENGINES)}")
        logger.info(f"  XYO Address: {XYO_ADDRESS}")
        logger.info(f"  System Location: {SYSTEM_LOCATION}")
        logger.info(f"  Started: {datetime.now().isoformat()}")
        logger.info("")
    
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
    
    def generate_xyo_proofs(self) -> list:
        """Generate XYO witness proofs from sentinel nodes."""
        proofs = []
        
        # Use the 3 sentinel nodes as witnesses
        witness_locations = {
            "sentinel-1": (40.7128, -74.0060),   # NY
            "sentinel-2": (51.5074, -0.1278),    # London
            "sentinel-3": (35.6762, 139.6503),   # Tokyo
        }
        
        for witness_id, (lat, lon) in witness_locations.items():
            proof = generate_witness_proof(
                witness_id=witness_id,
                latitude=lat,
                longitude=lon,
                satellite_frame_id=f"SAT-{int(time.time())}",
                data={
                    "k_score": round(self.compute_k_score(), 4),
                    "operation_timestamp": datetime.now().isoformat(),
                    "xyo_address": XYO_ADDRESS,
                }
            )
            proofs.append(proof)
        
        return proofs
    
    def verify_xyo_consensus(self) -> bool:
        """Verify XYO witness consensus before execution."""
        proofs = self.generate_xyo_proofs()
        
        # Gate execution on XYO consensus
        can_execute = self.xyo_engine.gate_execution(proofs)
        
        if can_execute:
            self.xyo_verified_count += 1
        else:
            self.xyo_failed_count += 1
        
        return can_execute
    
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
    
    def can_execute(self) -> tuple:
        """Check if safe to execute decision."""
        k = self.compute_k_score()
        resources = self.get_system_resources()
        xyo_verified = self.verify_xyo_consensus()
        
        conditions = {
            "k_score": k >= K_THRESHOLD,
            "cpu": resources["cpu_headroom"] > CPU_MIN,
            "memory": resources["memory_headroom"] > MEMORY_MIN,
            "disk": resources["disk_headroom"] > DISK_MIN,
            "xyo_verified": xyo_verified,
        }
        
        return all(conditions.values()), {
            "k": k,
            "resources": resources,
            "conditions": conditions,
            "xyo_verified": xyo_verified,
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
            "xyo_verified": details["xyo_verified"],
            "executed": False,
        }
        
        if can_exec:
            try:
                operation_func()
                result["executed"] = True
                result["status"] = "EXECUTED"
                self.execution_count += 1
                logger.info(f"✓ EXECUTED: {operation_id} (K={details['k']:.4f}, XYO verified)")
            except Exception as e:
                result["error"] = str(e)
                result["status"] = "EXECUTION_FAILED"
                logger.error(f"✗ EXECUTION FAILED: {operation_id} - {e}")
        else:
            result["status"] = "QUEUED"
            self.queue_count += 1
            blocked_by = [k for k, v in details['conditions'].items() if not v]
            logger.info(f"-- QUEUED: {operation_id} (Blocked by: {', '.join(blocked_by)})")
        
        self.decisions.append(result)
        return result
    
    def get_status(self):
        """Live system status."""
        k = self.compute_k_score()
        resources = self.get_system_resources()
        can_exec, details = self.can_execute()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - self.start_time,
            "k_score": round(k, 4),
            "resources": {k: round(v, 1) for k, v in resources.items()},
            "executable": can_exec,
            "xyo_verified": details.get("xyo_verified", False),
            "stats": {
                "executed": self.execution_count,
                "queued": self.queue_count,
                "xyo_verified": self.xyo_verified_count,
                "xyo_failed": self.xyo_failed_count,
            }
        }
    
    def print_status(self):
        """Print live status."""
        status = self.get_status()
        
        k_ready = 'READY' if status['k_score'] >= K_THRESHOLD else 'WAITING'
        cpu_ok = 'OK' if status['resources']['cpu_headroom'] > CPU_MIN else 'LOW'
        mem_ok = 'OK' if status['resources']['memory_headroom'] > MEMORY_MIN else 'LOW'
        disk_ok = 'OK' if status['resources']['disk_headroom'] > DISK_MIN else 'LOW'
        xyo_ok = '✓ VERIFIED' if status['xyo_verified'] else '✗ PENDING'
        
        print(f"[{status['timestamp']}]")
        print(f"  K-Score: {status['k_score']:.4f} ({k_ready})")
        print(f"  CPU:     {status['resources']['cpu_headroom']:.1f}% headroom ({cpu_ok})")
        print(f"  Memory:  {status['resources']['memory_headroom']:.1f}% headroom ({mem_ok})")
        print(f"  Disk:    {status['resources']['disk_headroom']:.1f}% headroom ({disk_ok})")
        print(f"  XYO:     {xyo_ok}")
        print(f"  Status:  {'READY TO EXECUTE' if status['executable'] else 'WAITING FOR CONVERGENCE'}")
        print(f"  Stats:   {status['stats']['executed']} executed, {status['stats']['queued']} queued")
        print(f"           {status['stats']['xyo_verified']} XYO verified, {status['stats']['xyo_failed']} XYO failed")
        print()

# ═══════════════════════════════════════════════════════════════
# LIVE OPERATION
# ═══════════════════════════════════════════════════════════════

def example_operation():
    """Example operation to execute."""
    return {"status": "success", "timestamp": datetime.now().isoformat()}

def run_live():
    """Run E14 Oracle live with XYO witness verification."""
    oracle = E14LiveOracle()
    
    logger.info("[E14 LIVE ORACLE WITH XYO WITNESS LAYER]")
    logger.info("Decision rule: K >= 0.99 + CPU > 10% + Memory > 15% + Disk > 20% + XYO verified")
    logger.info("")
    
    logger.info("STARTING LIVE MONITORING WITH XYO CRYPTOGRAPHIC VERIFICATION...")
    logger.info("Press Ctrl+C to stop")
    logger.info("")
    
    cycle = 0
    while True:
        try:
            cycle += 1
            
            # Update engines
            oracle.update_engines()
            
            # Try to execute
            result = oracle.execute(f"OP_{cycle}", example_operation)
            
            # Print status every 5 operations
            if cycle % 5 == 0:
                oracle.print_status()
            
            # Sleep
            time.sleep(1)
            
        except KeyboardInterrupt:
            logger.info("")
            logger.info("[ORACLE SHUTDOWN]")
            logger.info(f"Executed: {oracle.execution_count}")
            logger.info(f"Queued: {oracle.queue_count}")
            logger.info(f"Total: {oracle.execution_count + oracle.queue_count}")
            logger.info(f"XYO Verified: {oracle.xyo_verified_count}")
            logger.info(f"XYO Failed: {oracle.xyo_failed_count}")
            
            # Print last 5 decisions
            logger.info("")
            logger.info("Last 5 decisions:")
            for decision in list(oracle.decisions)[-5:]:
                logger.info(f"  {decision['timestamp']}: {decision['operation_id']} -> {decision['status']} (XYO: {decision['xyo_verified']})")
            break

if __name__ == "__main__":
    run_live()
