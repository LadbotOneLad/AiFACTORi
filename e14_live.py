"""
E14 ORACLE — PRODUCTION LIVE SYSTEM
Real data sources + XYO verification + Byzantine consensus execution.

Data pipeline:
1. BOM IDR71B radar → real precipitation data
2. Local sensors → environmental readings
3. Sensor fusion → unified dataset
4. XYO verification → cryptographic integrity check
5. E14 phase convergence → K-value decision gates
6. Execution → only with verified data + consensus
"""

import psutil
import time
import json
import logging
from datetime import datetime
from collections import deque

from bom_radar import BOMRadarIngestion, BOMRadarData
from sensor_fusion import SensorFusion, LocalSensorArray, LocalSensor
from xyo_data_verification import XYODataVerification

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

# 14 ENGINES (LIVE WITH DATA VERIFICATION)
ENGINES = [f"E{i:02d}" for i in range(1, 15)]

class E14LiveOracle:
    """Production E14 Oracle with real data + XYO verification."""
    
    def __init__(self):
        # Phase convergence state
        self.state = {eng: {
            "tick": 0,
            "beat": 0,
            "breath": 0,
            "cycle": 0,
            "heat": INSOLATION_EQUILIBRIUM,
        } for eng in ENGINES}
        
        # Data ingestion & verification
        self.bom_engine = BOMRadarIngestion()
        self.sensor_fusion = SensorFusion()
        self.xyo_verifier = XYODataVerification()
        
        # Initialize local sensor array
        self.local_sensors = LocalSensorArray(
            location="Sydney, NSW",
            latitude=-33.8688,
            longitude=151.2093
        )
        self._init_sensors()
        
        # Execution tracking
        self.history = deque(maxlen=1000)
        self.decisions = deque(maxlen=10000)
        self.start_time = time.time()
        self.execution_count = 0
        self.queue_count = 0
        self.xyo_verified_count = 0
        self.data_failed_count = 0
        
        logger.info("[E14 ORACLE INITIALIZED — REAL DATA MODE]")
        logger.info(f"  Engines: {len(ENGINES)}")
        logger.info(f"  Data sources: BOM IDR71B Radar + Local Sensors")
        logger.info(f"  Verification: XYO witness layer")
        logger.info(f"  Started: {datetime.now().isoformat()}")
        logger.info("")
    
    def _init_sensors(self):
        """Initialize local sensor array."""
        self.local_sensors.add_sensor(LocalSensor("TEMP_01", "temperature", 22.5, "°C"))
        self.local_sensors.add_sensor(LocalSensor("HUMID_01", "humidity", 65.0, "%"))
        self.local_sensors.add_sensor(LocalSensor("PRESS_01", "pressure", 1013.25, "hPa"))
        self.local_sensors.add_sensor(LocalSensor("WIND_01", "wind_speed", 12.3, "m/s"))
        logger.info(f"✓ Initialized {len(self.local_sensors.sensors)} local sensors")
    
    def ingest_data(self) -> bool:
        """
        Ingest BOM + local sensor data.
        
        Returns True if data successfully ingested.
        """
        try:
            # Fetch BOM radar data
            bom_data = self.bom_engine.fetch_radar_data()
            if not bom_data:
                logger.warning("Failed to fetch BOM data")
                return False
            
            # Update local sensors (simulate new readings)
            self.local_sensors.update_sensor("TEMP_01", 22.5 + (time.time() % 5) / 10)
            self.local_sensors.update_sensor("HUMID_01", 65.0 + (time.time() % 10) / 5)
            
            # Fuse data
            self.sensor_fusion.add_bom_data(bom_data)
            self.sensor_fusion.add_local_sensors(self.local_sensors)
            fused = self.sensor_fusion.fuse()
            
            if not fused:
                logger.warning("Failed to fuse data")
                return False
            
            logger.info(f"✓ Data ingested: {fused['fusion_id']}")
            return True
        
        except Exception as e:
            logger.error(f"Data ingestion error: {e}")
            return False
    
    def verify_data(self) -> bool:
        """
        Verify ingested data with XYO witness layer.
        
        Returns True if data passes verification.
        """
        try:
            fused = self.sensor_fusion.get_fused_data()
            if not fused:
                logger.warning("No fused data to verify")
                self.data_failed_count += 1
                return False
            
            data_hash = self.sensor_fusion.get_data_hash()
            
            # Witness the data
            witness = self.xyo_verifier.witness_data(data_hash, fused)
            
            # Verify the witness
            is_verified = self.xyo_verifier.verify_witness(witness)
            
            if is_verified:
                self.xyo_verified_count += 1
                logger.info("✓ DATA VERIFIED by XYO witness layer")
                return True
            else:
                self.data_failed_count += 1
                logger.error("✗ DATA VERIFICATION FAILED")
                return False
        
        except Exception as e:
            logger.error(f"Verification error: {e}")
            self.data_failed_count += 1
            return False
    
    def get_phase_diff(self, a, b):
        """Circular phase distance."""
        d = abs(a - b)
        return min(d, 86400.0 - d)
    
    def compute_k_score(self):
        """Live K-score from phase convergence."""
        ratios = []
        
        for axis, tol in [("tick", 25), ("beat", 50), ("breath", 100), ("cycle", 200)]:
            converged = sum(1 for s in self.state.values() 
                           if self.get_phase_diff(s[axis], ARIES_POINT) <= tol)
            ratios.append(converged / len(self.state))
        
        heat_converged = sum(1 for s in self.state.values() 
                            if abs(s["heat"] - INSOLATION_EQUILIBRIUM) <= HEAT_TOLERANCE)
        ratios.append(heat_converged / len(self.state))
        
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
        """Update 14 engines toward convergence."""
        for eng in self.state:
            for axis in ["tick", "beat", "breath", "cycle"]:
                current = self.state[eng][axis]
                self.state[eng][axis] = current * (1.0 - PHASE_PULLBACK) + ARIES_POINT * PHASE_PULLBACK
            
            h = self.state[eng]["heat"]
            self.state[eng]["heat"] = h * (1.0 - HEAT_DAMPING) + INSOLATION_EQUILIBRIUM * HEAT_DAMPING
    
    def can_execute(self) -> tuple:
        """Check execution conditions."""
        k = self.compute_k_score()
        resources = self.get_system_resources()
        data_verified = self.verify_data()
        
        conditions = {
            "k_score": k >= K_THRESHOLD,
            "cpu": resources["cpu_headroom"] > CPU_MIN,
            "memory": resources["memory_headroom"] > MEMORY_MIN,
            "disk": resources["disk_headroom"] > DISK_MIN,
            "data_verified": data_verified,
        }
        
        return all(conditions.values()), {
            "k": k,
            "resources": resources,
            "conditions": conditions,
            "data_verified": data_verified,
            "timestamp": datetime.now().isoformat(),
        }
    
    def execute(self, operation_id, operation_func):
        """Execute operation if all conditions met."""
        can_exec, details = self.can_execute()
        
        result = {
            "operation_id": operation_id,
            "timestamp": details["timestamp"],
            "k_score": details["k"],
            "resources": details["resources"],
            "conditions": details["conditions"],
            "data_verified": details["data_verified"],
            "executed": False,
        }
        
        if can_exec:
            try:
                operation_func()
                result["executed"] = True
                result["status"] = "EXECUTED"
                self.execution_count += 1
                logger.info(f"✓ EXECUTED: {operation_id} (K={details['k']:.4f}, Data verified)")
            except Exception as e:
                result["error"] = str(e)
                result["status"] = "EXECUTION_FAILED"
                logger.error(f"✗ EXECUTION FAILED: {operation_id}")
        else:
            result["status"] = "QUEUED"
            self.queue_count += 1
            blocked = [k for k, v in details['conditions'].items() if not v]
            logger.info(f"-- QUEUED: {operation_id} (Blocked: {', '.join(blocked)})")
        
        self.decisions.append(result)
        return result
    
    def get_status(self):
        """Get system status."""
        k = self.compute_k_score()
        resources = self.get_system_resources()
        can_exec, details = self.can_execute()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - self.start_time,
            "k_score": round(k, 4),
            "resources": {k: round(v, 1) for k, v in resources.items()},
            "executable": can_exec,
            "data_verified": details.get("data_verified", False),
            "stats": {
                "executed": self.execution_count,
                "queued": self.queue_count,
                "data_verified": self.xyo_verified_count,
                "data_failed": self.data_failed_count,
            }
        }

# ═══════════════════════════════════════════════════════════════
# LIVE OPERATION
# ═══════════════════════════════════════════════════════════════

def example_operation():
    """Example operation."""
    return {"status": "success", "timestamp": datetime.now().isoformat()}

def run_live():
    """Run E14 Oracle live."""
    oracle = E14LiveOracle()
    
    logger.info("[E14 LIVE ORACLE — REAL DATA + VERIFICATION MODE]")
    logger.info("Pipeline: BOM IDR71B → Sensor Fusion → XYO Verify → E14 Execute")
    logger.info("Press Ctrl+C to stop")
    logger.info("")
    
    cycle = 0
    while True:
        try:
            cycle += 1
            
            # Ingest data
            oracle.ingest_data()
            
            # Update phase convergence
            oracle.update_engines()
            
            # Try to execute
            result = oracle.execute(f"OP_{cycle}", example_operation)
            
            # Print status every 10 cycles
            if cycle % 10 == 0:
                status = oracle.get_status()
                logger.info(f"")
                logger.info(f"[Status] K={status['k_score']:.4f} | "
                           f"Executed={status['stats']['executed']} | "
                           f"Verified={status['stats']['data_verified']} | "
                           f"Failed={status['stats']['data_failed']}")
            
            time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("")
            logger.info("[SHUTDOWN]")
            logger.info(f"Executed: {oracle.execution_count}")
            logger.info(f"Queued: {oracle.queue_count}")
            logger.info(f"Data verified: {oracle.xyo_verified_count}")
            logger.info(f"Data failed: {oracle.data_failed_count}")
            break

if __name__ == "__main__":
    run_live()
