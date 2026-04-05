# API Reference

Python API documentation for E14 Oracle.

## Core Classes

### E14Oracle

Main convergence detection and futures evaluation engine.

```python
from oracle_layer import E14Oracle, PhaseState, ENGINES, AXES

class E14Oracle:
    """
    E14 Dr. Strange Oracle.
    
    Watches 14 engines × 4 axes in phase space.
    Detects convergence to 1/7200 invariant.
    Evaluates branching futures for stability.
    """
    
    def __init__(self, target: float = 0.0, tolerances: Optional[Dict] = None):
        """
        Initialize oracle.
        
        Args:
            target: Invariant target phase (default: 0.0 = Aries Point)
            tolerances: Per-axis convergence tolerances (default: TOLERANCE)
        """
        
    def convergence_now(self, phase_state: PhaseState) -> bool:
        """
        Check if ring is currently converged.
        
        Args:
            phase_state: Dict of {engine: {axis: phase_value}}
        
        Returns:
            True if all 14 engines converged on all 4 axes
        """
        
    def score_now(self, phase_state: PhaseState) -> float:
        """
        Get current ring coherence (K-value).
        
        Args:
            phase_state: Current 14×4 phase configuration
        
        Returns:
            K-value (0.0 to 1.0), where 1.0 = perfect convergence
        """
        
    def observe(self, phase_state: PhaseState) -> Dict:
        """
        Observe current state and record it.
        
        Args:
            phase_state: Current state snapshot
        
        Returns:
            {
                "timestamp": int,
                "coherence": float,
                "converged": bool,
                "details": {...}
            }
        """
        
    def evaluate_branches(
        self,
        initial_state: PhaseState,
        branches: Dict[str, Callable],
        duration: float = 86400.0,
        dt: float = 0.05
    ) -> List[BranchOutcome]:
        """
        Evaluate multiple candidate branches (futures).
        
        Args:
            initial_state: Starting phase configuration
            branches: {branch_id: control_policy_function}
            duration: Simulation horizon (seconds)
            dt: Time step (seconds)
        
        Returns:
            Sorted list of BranchOutcome (best first)
        """
        
    def status_report(self, phase_state: PhaseState) -> str:
        """
        Generate detailed status report.
        
        Args:
            phase_state: Current configuration
        
        Returns:
            Formatted ASCII status report
        """
```

### E14LiveOracle

Real-time decision execution with resource gating.

```python
from e14_live import E14LiveOracle

class E14LiveOracle:
    """Production E14 Oracle — Real-time decision system."""
    
    def __init__(self):
        """Initialize live oracle."""
        
    def compute_k_score(self) -> float:
        """
        Get live K-score from current state.
        
        Returns:
            K-value (coherence 0.0-1.0)
        """
        
    def get_system_resources(self) -> Dict:
        """
        Get live system resources.
        
        Returns:
            {
                "cpu_headroom": float,    # % available
                "memory_headroom": float,
                "disk_headroom": float
            }
        """
        
    def can_execute(self) -> Tuple[bool, Dict]:
        """
        Check if safe to execute decision.
        
        Requires:
        - K >= 0.99
        - CPU headroom > 10%
        - Memory headroom > 15%
        - Disk headroom > 20%
        - Weather safe
        
        Returns:
            (can_execute: bool, details: Dict)
        """
        
    def execute(self, operation_id: str, operation_func: Callable) -> Dict:
        """
        Execute operation if safe, else queue.
        
        Args:
            operation_id: Unique operation identifier
            operation_func: Callable to execute
        
        Returns:
            {
                "operation_id": str,
                "executed": bool,
                "status": "EXECUTED" | "QUEUED" | "EXECUTION_FAILED",
                "k_score": float,
                "resources": {...},
                "conditions": {...}
            }
        """
        
    def get_status(self) -> Dict:
        """Get current system status."""
        
    def print_status(self) -> None:
        """Print formatted status to console."""
```

### BranchOutcome

Result of simulating one branching future.

```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class BranchOutcome:
    """Result of simulating one branch (future)."""
    
    branch_id: str                    # Unique identifier
    converged: bool                   # Achieved convergence?
    time_to_converge: float           # Seconds (or inf)
    coherence_score: float            # Best K during simulation (0..1)
    failure_axes: List[str] = []      # Axes that failed to converge
    final_state: Optional[PhaseState] = None  # Final state snapshot
```

## Type Definitions

### PhaseState

```python
PhaseState = Dict[str, Dict[str, float]]

# Example:
state = {
    "E01": {"tick": 0.0, "beat": 0.0, "breath": 0.0, "cycle": 0.0},
    "E02": {"tick": 100.5, "beat": 200.0, "breath": 500.0, "cycle": 1000.0},
    # ... 12 more engines
}
```

### Axes

```python
AXES = ["tick", "beat", "breath", "cycle"]  # 4 temporal axes

# Plus 2 more:
# - "heat" (thermal regulation)
# - "weather" (environmental XYO verification)

# Total: 6 axes × 14 engines = 84 phase values
```

### Engines

```python
ENGINES = [f"E{i:02d}" for i in range(1, 15)]

# E01, E02, E03, E04, E05, E06, E07, E08, E09, E10, E11, E12, E13, E14
# All 14 engines in consensus ring
```

## Constants

```python
# Phase space
PHASE_CYCLE = 86400           # Full cycle in phase units (seconds)
INVARIANT = 1.0 / 7200.0      # ていんが base phase unit (12 seconds)

# Convergence tolerances (phase units)
TOLERANCE = {
    "tick":   360,     # 1/240 of cycle
    "beat":   1440,    # 1/60 of cycle
    "breath": 10800,   # 1/8 of cycle
    "cycle":  86400,   # full cycle
}

# Strict tolerances (production)
TOLERANCE_STRICT = {
    "tick":   10,
    "beat":   40,
    "breath": 300,
    "cycle":  1000,
}

# Thermal
INSOLATION_EQUILIBRIUM = 0.075
HEAT_TOLERANCE = 0.005
HEAT_DAMPING = 0.02

# Decision thresholds
K_THRESHOLD = 0.99
CPU_MIN = 10
MEMORY_MIN = 15
DISK_MIN = 20
WEATHER_MAX = 0.6
```

## Functions

### Phase Utilities

```python
def phase_distance(phi1: float, phi2: float, modulo: float = PHASE_CYCLE) -> float:
    """
    Shortest circular distance between two phases.
    
    Args:
        phi1, phi2: Phase values
        modulo: Cycle modulo (default: PHASE_CYCLE)
    
    Returns:
        Distance (0 to modulo/2)
    """

def normalize_phase(phi: float, modulo: float = PHASE_CYCLE) -> float:
    """
    Normalize phase to [0, modulo).
    
    Args:
        phi: Phase value
        modulo: Cycle modulo
    
    Returns:
        Normalized phase
    """
```

### Convergence Utilities

```python
def is_axis_converged(
    phase_state: PhaseState,
    axis: str,
    target: float = 0.0,
    tolerance: float = 100.0
) -> bool:
    """Check if all 14 engines converged on one axis."""

def is_ring_converged(
    phase_state: PhaseState,
    target: float = 0.0,
    tolerances: Optional[Dict] = None
) -> bool:
    """Check if ALL 4 axes converged across all 14 engines."""

def compute_axis_coherence(
    phase_state: PhaseState,
    axis: str,
    target: float = 0.0
) -> float:
    """Compute coherence score for one axis (0.0 to 1.0)."""

def compute_ring_coherence(
    phase_state: PhaseState,
    target: float = 0.0
) -> float:
    """Compute ring coherence (K-value)."""

def detect_convergence_details(
    phase_state: PhaseState,
    target: float = 0.0,
    tolerances: Optional[Dict] = None
) -> Dict:
    """
    Detailed convergence analysis.
    
    Returns:
        {
            "converged": bool,
            "ring_coherence": float,
            "per_axis_coherence": {axis: float},
            "per_axis_converged": {axis: bool},
            "converged_engines": [list],
            "failing_axes": [list],
        }
    """
```

## Control Policies

Policy functions for branching futures simulation.

```python
def policy_ideal_sync(state: PhaseState, t: float, dt: float) -> PhaseState:
    """
    Ideal policy: all engines sync perfectly to target.
    
    Args:
        state: Current phase state
        t: Current time (seconds)
        dt: Time step (seconds)
    
    Returns:
        Updated state (all engines advanced toward target)
    """

def policy_sovereign_driven(state: PhaseState, t: float, dt: float) -> PhaseState:
    """
    Sovereign-driven policy: E02 leads, others follow with phase-locked loop.
    
    Args:
        state: Current state
        t: Current time
        dt: Time step
    
    Returns:
        Updated state (others lock to E02 with small offset)
    """

def policy_random_walk(state: PhaseState, t: float, dt: float) -> PhaseState:
    """
    Random walk policy: engines drift independently (divergence).
    
    Args:
        state: Current state
        t: Current time
        dt: Time step
    
    Returns:
        Updated state (random drift, no convergence)
    """
```

## Usage Examples

### Detect Convergence

```python
from oracle_layer import E14Oracle, ENGINES, AXES

oracle = E14Oracle(target=0.0)

# Perfect sync (all engines at phase 0)
state = {
    engine: {axis: 0.0 for axis in AXES}
    for engine in ENGINES
}

if oracle.convergence_now(state):
    print(f"Converged! K={oracle.score_now(state):.4f}")
```

### Evaluate Branches

```python
from oracle_layer import (
    E14Oracle, policy_ideal_sync, policy_sovereign_driven
)

oracle = E14Oracle()

# Scattered initial state
state = {
    f"E{i:02d}": {axis: float((i * 12345) % 86400) for axis in AXES}
    for i in range(1, 15)
}

# Evaluate 2 futures
branches = {
    "ideal": policy_ideal_sync,
    "sovereign": policy_sovereign_driven,
}

outcomes = oracle.evaluate_branches(state, branches, duration=10.0)

best = outcomes[0]
print(f"Best branch: {best.branch_id}")
print(f"Converged: {best.converged}")
print(f"K-score: {best.coherence_score:.4f}")
print(f"Time to convergence: {best.time_to_converge:.1f}s")
```

### Real-Time Decision Execution

```python
from e14_live import E14LiveOracle

oracle = E14LiveOracle()

# Define operation
def my_operation():
    print("Executing critical operation...")
    return {"status": "success"}

# Try to execute (or queue if gates blocked)
result = oracle.execute("OP_001", my_operation)

print(f"Status: {result['status']}")  # EXECUTED, QUEUED, or EXECUTION_FAILED
print(f"K-score: {result['k_score']:.4f}")
print(f"Blocked by: {[k for k,v in result['conditions'].items() if not v]}")
```

### Monitor System Status

```python
from e14_live import E14LiveOracle

oracle = E14LiveOracle()

# Get status
status = oracle.get_status()

print(f"K-score: {status['k_score']:.4f}")
print(f"CPU: {status['resources']['cpu_headroom']:.1f}%")
print(f"Memory: {status['resources']['memory_headroom']:.1f}%")
print(f"Executable: {status['executable']}")

# Print formatted output
oracle.print_status()
```

## Testing

```python
import pytest
from oracle_layer import E14Oracle, ENGINES, AXES

def test_perfect_convergence():
    """Test oracle detects perfect synchronization."""
    oracle = E14Oracle()
    state = {
        engine: {axis: 0.0 for axis in AXES}
        for engine in ENGINES
    }
    assert oracle.convergence_now(state) == True
    assert oracle.score_now(state) > 0.99

def test_scattered_divergence():
    """Test oracle detects scattered phases."""
    oracle = E14Oracle()
    state = {
        f"E{i:02d}": {axis: float((i * 12345) % 86400) for axis in AXES}
        for i in range(1, 15)
    }
    assert oracle.convergence_now(state) == False
    assert oracle.score_now(state) < 0.5
```

## Error Handling

```python
from oracle_layer import E14Oracle

oracle = E14Oracle()

# Malformed state
bad_state = {"E01": {"tick": 0.0}}  # Missing engines/axes

try:
    oracle.convergence_now(bad_state)
except (KeyError, ValueError) as e:
    print(f"Invalid state: {e}")

# Convergence check
state = {...}  # valid state
details = oracle.observe(state)

if details["converged"]:
    print("All engines synchronized!")
else:
    print(f"Failing axes: {details['details']['failing_axes']}")
```

## Performance Notes

- Phase distance: <1μs per engine
- Convergence check: <10ms (14 engines)
- K-value computation: <5ms
- Branch simulation: ~1s (3 futures, 10s horizon)
- Decision gate check: <50ms (system resource queries)

## See Also

- `ARCHITECTURE.md` — System design
- `CONFIGURATION.md` — Environment variables
- `QUICK-START.md` — 5-minute setup
- `test_*.py` — Example tests

---

**Last Updated**: 2025-01-14 | **Version**: 1.0.0
