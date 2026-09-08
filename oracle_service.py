"""
E14 ORACLE SERVICE
Wraps oracle_layer.py into a long-running service for production.

Monitors convergence continuously, logs results, watches for seal events.
"""

import time
import json
import sys
from datetime import datetime
from pathlib import Path
from collections import deque
import logging

from oracle_layer import E14Oracle, TOLERANCE, ENGINES, AXES

# ═══════════════════════════════════════════════════════════════
# LOGGING SETUP
# ═══════════════════════════════════════════════════════════════

LOG_DIR = Path("/app/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "oracle_service.log")
    ]
)

logger = logging.getLogger("E14OracleService")

# ═══════════════════════════════════════════════════════════════
# ORACLE SERVICE
# ═══════════════════════════════════════════════════════════════

class E14OracleService:
    """Production oracle service with continuous monitoring."""
    
    def __init__(self, check_interval: float = 1.0):
        """
        Initialize oracle service.
        
        Args:
            check_interval: How often to sample state (seconds)
        """
        self.oracle = E14Oracle(target=0.0, tolerances=TOLERANCE)
        self.check_interval = check_interval
        self.observation_count = 0
        self.convergence_count = 0
        self.start_time = time.time()
        self.state_history = deque(maxlen=1000)
        
        logger.info("═══════════════════════════════════════════════════════════════")
        logger.info("E14 ORACLE SERVICE INITIALIZED")
        logger.info("═══════════════════════════════════════════════════════════════")
        logger.info(f"Check interval: {check_interval}s")
        logger.info(f"Target: {self.oracle.target}")
        logger.info(f"Engines: {len(ENGINES)}")
        logger.info(f"Axes: {len(AXES)}")
    
    def generate_phase_state(self):
        """Generate synthetic phase state for demonstration."""
        import random
        
        state = {}
        for i, engine in enumerate(ENGINES):
            state[engine] = {}
            for axis in AXES:
                # Gradually converge toward 0
                elapsed = time.time() - self.start_time
                base = float((i * 12345 + int(elapsed * 100)) % 86400)
                # Add convergence pull (stronger over time)
                convergence_pull = 0.95 ** (elapsed / 60.0)  # exponential pullback
                phase = base * (1.0 - convergence_pull)
                state[engine][axis] = phase
        
        return state
    
    def run(self, max_observations: int = None):
        """
        Run oracle service continuously.
        
        Args:
            max_observations: Stop after N observations (None = infinite)
        """
        logger.info("Starting oracle service loop...")
        logger.info("")
        
        try:
            while True:
                # Generate phase state
                phase_state = self.generate_phase_state()
                
                # Observe current state
                obs = self.oracle.observe(phase_state)
                self.observation_count += 1
                
                # Track state history
                self.state_history.append({
                    "observation": self.observation_count,
                    "coherence": obs["coherence"],
                    "converged": obs["converged"],
                    "timestamp": datetime.now().isoformat(),
                })
                
                # Count convergences
                if obs["converged"]:
                    self.convergence_count += 1
                
                # Log observation every 10 observations
                if self.observation_count % 10 == 0:
                    elapsed = time.time() - self.start_time
                    rate = self.observation_count / elapsed if elapsed > 0 else 0
                    
                    logger.info(
                        f"[OBS {self.observation_count:6d}] "
                        f"K={obs['coherence']:.6f} | "
                        f"Converged={obs['converged']} | "
                        f"Rate={rate:.1f} obs/s"
                    )
                
                # Log convergence events immediately
                if obs["converged"] and self.convergence_count == 1:
                    logger.info("!!! FIRST CONVERGENCE DETECTED !!!")
                    logger.info(self.oracle.status_report(phase_state))
                
                # Check stop condition
                if max_observations and self.observation_count >= max_observations:
                    logger.info(f"Reached max observations ({max_observations}). Stopping.")
                    break
                
                # Sleep until next check
                time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            logger.info("Service interrupted by user.")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            sys.exit(1)
        
        finally:
            self.print_summary()
    
    def print_summary(self):
        """Print final summary."""
        elapsed = time.time() - self.start_time
        
        logger.info("")
        logger.info("═══════════════════════════════════════════════════════════════")
        logger.info("E14 ORACLE SERVICE SHUTDOWN")
        logger.info("═══════════════════════════════════════════════════════════════")
        logger.info(f"Total runtime: {elapsed:.1f}s")
        logger.info(f"Total observations: {self.observation_count}")
        logger.info(f"Convergence events: {self.convergence_count}")
        
        if self.observation_count > 0:
            convergence_rate = self.convergence_count / self.observation_count * 100
            logger.info(f"Convergence rate: {convergence_rate:.1f}%")
        
        if self.state_history:
            latest = self.state_history[-1]
            logger.info(f"Final K-value: {latest['coherence']:.6f}")
            logger.info(f"Final state: {'CONVERGED' if latest['converged'] else 'DIVERGED'}")
        
        logger.info("")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="E14 Oracle Service")
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Check interval in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--max-observations",
        type=int,
        default=None,
        help="Stop after N observations (default: infinite)"
    )
    
    args = parser.parse_args()
    
    service = E14OracleService(check_interval=args.interval)
    service.run(max_observations=args.max_observations)
