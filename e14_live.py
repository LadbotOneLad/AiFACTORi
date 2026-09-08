"""
E14 ORACLE — WITNESSED ATMOSPHERIC GRID
Executes decisions based on cryptographically attested satellite tiles.

Pipeline:
1. Satellite frames (BOM, Himawari, GOES, Meteosat) → raw atmospheric data
2. Sub-frame decomposition → regional tiles with pixel hashes
3. XYO bound-witness mesh → distributed nodes anchor tiles to ledger
4. E14 phase convergence → K-value operates on verified tiles
5. Execution → only with witnessed atmospheric grid
"""

import psutil
import time
import json
import logging
from datetime import datetime
from collections import deque
from typing import List, Dict

from satellite_tiles import SatelliteTileDecomposer, SatelliteTile
from xyo_bound_witness import XYOBoundWitnessMesh

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("E14Oracle")

# E14 CONFIGURATION
ARIES_POINT = 0.0
INSOLATION_EQUILIBRIUM = 0.075
HEAT_TOLERANCE = 0.005
PHASE_PULLBACK = 0.95
HEAT_DAMPING = 0.02

K_THRESHOLD = 0.99
CPU_MIN = 10
MEMORY_MIN = 15
DISK_MIN = 20

ENGINES = [f"E{i:02d}" for i in range(1, 15)]

class E14OracleWitnessedGrid:
    """E14 Oracle operating on witnessed atmospheric grid."""
    
    def __init__(self):
        # Phase convergence state
        self.state = {eng: {
            "tick": 0,
            "beat": 0,
            "breath": 0,
            "cycle": 0,
            "heat": INSOLATION_EQUILIBRIUM,
        } for eng in ENGINES}
        
        # Witnessed grid infrastructure
        self.tile_decomposer = SatelliteTileDecomposer()
        self.witness_mesh = XYOBoundWitnessMesh()
        
        self.witnessed_tiles = []
        self.execution_grid = {}  # Grid indexed by (lat, lon, time)
        
        # Execution tracking
        self.decisions = deque(maxlen=10000)
        self.start_time = time.time()
        self.execution_count = 0
        self.queue_count = 0
        self.witnessed_count = 0
        
        logger.info("[E14 ORACLE — WITNESSED ATMOSPHERIC GRID MODE]")
        logger.info(f"  Engines: {len(ENGINES)}")
        logger.info(f"  Data sources: BOM, Himawari, GOES, Meteosat")
        logger.info(f"  Verification: XYO bound-witness mesh")
        logger.info(f"  Started: {datetime.now().isoformat()}")
        logger.info("")
    
    def ingest_satellite_frames(self) -> List[SatelliteTile]:
        """Ingest and decompose satellite frames."""
        logger.info("Ingesting satellite frames...")
        
        tiles = []
        for satellite in ["BOM", "Himawari"]:  # Demo: 2 satellites
            satellite_tiles = self.tile_decomposer.decompose_satellite_frame(satellite)
            tiles.extend(satellite_tiles)
        
        logger.info(f"✓ Decomposed {len(tiles)} tiles from multiple satellites")
        return tiles
    
    def witness_tiles(self, tiles: List[SatelliteTile]) -> int:
        """Anchor tiles into XYO bound-witness mesh."""
        logger.info("Anchoring tiles into witness mesh...")
        
        witnessed = 0
        for tile in tiles:
            witnesses = self.witness_mesh.witness_tile(tile)
            if witnesses:
                self.witnessed_tiles.append(tile)
                witnessed += len(witnesses)
        
        self.witnessed_count += witnessed
        logger.info(f"✓ Witnessed {witnessed} tiles anchored to ledger")
        return witnessed
    
    def build_execution_grid(self):
        """Build spatial-temporal grid from witnessed tiles."""
        logger.info("Building execution grid from witnessed tiles...")
        
        for tile in self.witnessed_tiles:
            grid_key = (
                tile.latitude_min,
                tile.longitude_min,
                tile.timestamp[:10]
            )
            self.execution_grid[grid_key] = {
                "tile_id": tile.tile_id,
                "satellite": tile.satellite,
                "band": tile.band,
                "region": tile.region,
                "integrity_hash": tile.integrity_hash,
                "witnessed": True,
            }
        
        logger.info(f"✓ Execution grid built: {len(self.execution_grid)} cells")
    
    def get_phase_diff(self, a, b):
        """Circular phase distance."""
        d = abs(a - b)
        return min(d, 86400.0 - d)
    
    def compute_k_score(self):
        """K-score from phase convergence."""
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
        """System resources."""
        return {
            "cpu_headroom": 100.0 - psutil.cpu_percent(interval=0.05),
            "memory_headroom": 100.0 - psutil.virtual_memory().percent,
            "disk_headroom": 100.0 - psutil.disk_usage('/').percent,
        }
    
    def update_engines(self):
        """Update engines toward convergence."""
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
        grid_ready = len(self.execution_grid) > 0
        
        conditions = {
            "k_score": k >= K_THRESHOLD,
            "cpu": resources["cpu_headroom"] > CPU_MIN,
            "memory": resources["memory_headroom"] > MEMORY_MIN,
            "disk": resources["disk_headroom"] > DISK_MIN,
            "witnessed_grid": grid_ready,
        }
        
        return all(conditions.values()), {
            "k": k,
            "resources": resources,
            "conditions": conditions,
            "grid_cells": len(self.execution_grid),
            "timestamp": datetime.now().isoformat(),
        }
    
    def execute(self, operation_id, operation_func):
        """Execute operation if conditions met."""
        can_exec, details = self.can_execute()
        
        result = {
            "operation_id": operation_id,
            "timestamp": details["timestamp"],
            "k_score": details["k"],
            "resources": details["resources"],
            "conditions": details["conditions"],
            "grid_cells": details["grid_cells"],
            "executed": False,
        }
        
        if can_exec:
            try:
                operation_func()
                result["executed"] = True
                result["status"] = "EXECUTED"
                self.execution_count += 1
                logger.info(f"✓ EXECUTED: {operation_id} (K={details['k']:.4f}, Grid={details['grid_cells']} cells)")
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
    
    def get_status(self) -> Dict:
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
            "grid_cells": len(self.execution_grid),
            "witnessed_tiles": len(self.witnessed_tiles),
            "stats": {
                "executed": self.execution_count,
                "queued": self.queue_count,
                "total_witnessed": self.witnessed_count,
            }
        }

# ═══════════════════════════════════════════════════════════════
# LIVE OPERATION
# ═══════════════════════════════════════════════════════════════

def example_operation():
    """Example operation."""
    return {"status": "success", "timestamp": datetime.now().isoformat()}

def run_oracle():
    """Run E14 Oracle on witnessed grid."""
    oracle = E14OracleWitnessedGrid()
    
    logger.info("[E14 ORACLE — WITNESSED ATMOSPHERIC GRID]")
    logger.info("Pipeline: Satellite frames → Tile decomposition → XYO witness mesh → E14 execution")
    logger.info("Press Ctrl+C to stop")
    logger.info("")
    
    # Initial grid setup
    logger.info("[SETUP] Building witnessed grid...")
    tiles = oracle.ingest_satellite_frames()
    oracle.witness_tiles(tiles)
    oracle.build_execution_grid()
    logger.info("")
    
    cycle = 0
    while True:
        try:
            cycle += 1
            
            # Update convergence
            oracle.update_engines()
            
            # Try to execute
            result = oracle.execute(f"OP_{cycle}", example_operation)
            
            # Print status every 10 cycles
            if cycle % 10 == 0:
                status = oracle.get_status()
                logger.info(f"")
                logger.info(f"[Status] K={status['k_score']:.4f} | "
                           f"Executed={status['stats']['executed']} | "
                           f"Grid cells={status['grid_cells']} | "
                           f"Witnessed tiles={status['witnessed_tiles']}")
            
            time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("")
            logger.info("[SHUTDOWN]")
            logger.info(f"Executed: {oracle.execution_count}")
            logger.info(f"Queued: {oracle.queue_count}")
            logger.info(f"Total witnessed: {oracle.witnessed_count}")
            logger.info(f"Grid cells: {len(oracle.execution_grid)}")
            break

if __name__ == "__main__":
    run_oracle()
