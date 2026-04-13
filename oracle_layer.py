# oracle_layer.py
# E14 Dr Strange Oracle Layer
# Phase space convergence detection + branching futures evaluation
#
# Watches 14 engines × 4 axes in phase space,
# detects convergence to 1/7200 invariant,
# evaluates alternate futures for stability & coherence.
#
# K = 1.000 semantics: ring coherence = 1.0 when all axes converged to invariant

from dataclasses import dataclass, field
from typing import Dict, List, Callable, Optional, Tuple
import math
from enum import Enum

# ═══════════════════════════════════════════════════════════════
# CONSTANTS & CONFIGURATION
# ═══════════════════════════════════════════════════════════════

INVARIANT = 1.0 / 7200.0  # ていんが — base phase unit (12 seconds)
PHASE_CYCLE = 86400       # Full cycle in phase units

ENGINES = [f"E{str(i).zfill(2)}" for i in range(1, 15)]
AXES = ["tick", "beat", "breath", "cycle"]

# Circular phase tolerance per axis (phase units)
# Defines "close enough to invariant" for convergence
TOLERANCE = {
    "tick":   360,     # 1/240 of cycle — tight binding
    "beat":   1440,    # 1/60 of cycle
    "breath": 10800,   # 1/8 of cycle
    "cycle":  86400,   # full cycle (essentially 0 or 86400)
}

# Alternative: stricter tolerances for "hard" convergence
TOLERANCE_STRICT = {
    "tick":   10,      # very tight
    "beat":   40,
    "breath": 300,
    "cycle":  1000,
}

# ═══════════════════════════════════════════════════════════════
# PHASE STATE MODEL
# ═══════════════════════════════════════════════════════════════

PhaseState = Dict[str, Dict[str, float]]  # {engine: {axis: phase_value}}

def phase_distance(phi1: float, phi2: float, modulo: float = PHASE_CYCLE) -> float:
    """
    Compute shortest circular distance between two phase values.
    Both assumed to be in [0, modulo).
    """
    phi1 = phi1 % modulo
    phi2 = phi2 % modulo
    diff = abs(phi1 - phi2)
    return min(diff, modulo - diff)

def normalize_phase(phi: float, modulo: float = PHASE_CYCLE) -> float:
    """Normalize phase to [0, modulo)."""
    return phi % modulo

# ═══════════════════════════════════════════════════════════════
# CONVERGENCE DETECTION
# ═══════════════════════════════════════════════════════════════

def is_axis_converged(
    phase_state: PhaseState,
    axis: str,
    target: float = 0.0,
    tolerance: float = 100.0
) -> bool:
    """
    Check if all 14 engines are converged on given axis.
    
    Convergence: all engines within 'tolerance' phase units of 'target'.
    """
    for engine in ENGINES:
        if engine not in phase_state:
            return False
        phi = normalize_phase(phase_state[engine][axis])
        dist = phase_distance(phi, target)
        if dist > tolerance:
            return False
    return True

def is_ring_converged(
    phase_state: PhaseState,
    target: float = 0.0,
    tolerances: Optional[Dict[str, float]] = None
) -> bool:
    """
    Check if ALL 4 axes are converged across all 14 engines.
    
    Returns True only if ring is fully synchronized.
    """
    if tolerances is None:
        tolerances = TOLERANCE
    
    return all(
        is_axis_converged(phase_state, axis, target, tolerances[axis])
        for axis in AXES
    )

def compute_axis_coherence(
    phase_state: PhaseState,
    axis: str,
    target: float = 0.0
) -> float:
    """
    Compute coherence score for one axis (0.0 to 1.0).
    
    0.0 = all engines scattered
    1.0 = all engines at invariant
    
    Uses normalized average distance from target.
    """
    distances = []
    for engine in ENGINES:
        if engine in phase_state:
            phi = normalize_phase(phase_state[engine][axis])
            dist = phase_distance(phi, target)
            # Normalize distance to [0, 1] where PHASE_CYCLE/2 is 0.5
            normalized = 1.0 - (dist / (PHASE_CYCLE / 2.0))
            distances.append(max(0.0, normalized))
    
    return sum(distances) / len(distances) if distances else 0.0

def compute_ring_coherence(
    phase_state: PhaseState,
    target: float = 0.0
) -> float:
    """
    Compute ring coherence (Kotahitanja / K-value).
    
    K = average of coherences across all 4 axes.
    K = 1.0 <=> all engines converged to invariant on all axes.
    """
    coherences = [
        compute_axis_coherence(phase_state, axis, target)
        for axis in AXES
    ]
    return sum(coherences) / len(coherences) if coherences else 0.0

def detect_convergence_details(
    phase_state: PhaseState,
    target: float = 0.0,
    tolerances: Optional[Dict[str, float]] = None
) -> Dict:
    """
    Detailed convergence analysis.
    
    Returns:
        {
            "converged": bool,
            "ring_coherence": float,
            "per_axis_coherence": {axis: float},
            "per_axis_converged": {axis: bool},
            "converged_engines": [list of engine IDs at target],
            "failing_axes": [list of axes that failed],
        }
    """
    if tolerances is None:
        tolerances = TOLERANCE
    
    per_axis_coh = {axis: compute_axis_coherence(phase_state, axis, target) for axis in AXES}
    per_axis_conv = {axis: is_axis_converged(phase_state, axis, target, tolerances[axis]) for axis in AXES}
    
    converged_engines = []
    for engine in ENGINES:
        if engine in phase_state:
            if all(
                phase_distance(normalize_phase(phase_state[engine][axis]), target) <= tolerances[axis]
                for axis in AXES
            ):
                converged_engines.append(engine)
    
    failing_axes = [axis for axis, conv in per_axis_conv.items() if not conv]
    
    return {
        "converged": is_ring_converged(phase_state, target, tolerances),
        "ring_coherence": compute_ring_coherence(phase_state, target),
        "per_axis_coherence": per_axis_coh,
        "per_axis_converged": per_axis_conv,
        "converged_engines": converged_engines,
        "failing_axes": failing_axes,
    }

# ═══════════════════════════════════════════════════════════════
# BRANCHING & FUTURES
# ═══════════════════════════════════════════════════════════════

@dataclass
class BranchOutcome:
    """Result of simulating one branch (future)."""
    branch_id: str
    converged: bool
    time_to_converge: float  # seconds (or inf if never converged)
    coherence_score: float   # 0..1, best score during simulation
    failure_axes: List[str] = field(default_factory=list)
    final_state: Optional[PhaseState] = None
    
    def __repr__(self):
        status = "CONVERGED" if self.converged else "DIVERGED"
        return (f"Branch({self.branch_id}, {status}, K={self.coherence_score:.3f}, "
                f"t_conv={self.time_to_converge:.1f}s, failures={self.failure_axes})")

def simulate_branch(
    initial_state: PhaseState,
    control_policy: Callable[[PhaseState, float, float], PhaseState],
    duration: float = 86400.0,
    dt: float = 0.05,
    target: float = 0.0,
    tolerances: Optional[Dict[str, float]] = None
) -> BranchOutcome:
    """
    Simulate evolution of phase_state under control policy.
    
    Args:
        initial_state: Starting phase configuration
        control_policy: function(state, t, dt) -> new_state
        duration: simulation time (seconds)
        dt: time step (seconds)
        target: invariant target phase value
        tolerances: per-axis convergence tolerances
    
    Returns:
        BranchOutcome with convergence status, timing, coherence
    """
    if tolerances is None:
        tolerances = TOLERANCE
    
    t = 0.0
    state = {e: dict(initial_state[e]) for e in ENGINES}  # deep copy
    
    best_coherence = 0.0
    converged_at = None
    
    while t <= duration:
        # Evaluate coherence at current timestep
        coherence = compute_ring_coherence(state, target)
        best_coherence = max(best_coherence, coherence)
        
        # Check convergence
        if is_ring_converged(state, target, tolerances) and converged_at is None:
            converged_at = t
        
        # Advance simulation
        state = control_policy(state, t, dt)
        t += dt
    
    # Determine failure axes
    failure_axes = []
    if converged_at is None:
        details = detect_convergence_details(state, target, tolerances)
        failure_axes = details["failing_axes"]
    
    return BranchOutcome(
        branch_id="branch-unknown",
        converged=(converged_at is not None),
        time_to_converge=converged_at if converged_at is not None else float("inf"),
        coherence_score=best_coherence,
        failure_axes=failure_axes,
        final_state=state,
    )

# ═══════════════════════════════════════════════════════════════
# ORACLE LAYER (E14 Dr Strange)
# ═══════════════════════════════════════════════════════════════

class E14Oracle:
    """
    E14 Dr Strange Oracle.
    
    Watches 14 engines × 4 axes in phase space.
    Detects convergence to 1/7200 invariant.
    Evaluates branching futures for stability.
    """
    
    def __init__(
        self,
        target: float = 0.0,
        tolerances: Optional[Dict[str, float]] = None
    ):
        self.target = target
        self.tolerances = tolerances or TOLERANCE
        self.observation_history = []
        self.is_sealed = False
        self.seal_time = None
    
    def convergence_now(self, phase_state: PhaseState) -> bool:
        """Check if ring is currently converged."""
        return is_ring_converged(phase_state, self.target, self.tolerances)
    
    def score_now(self, phase_state: PhaseState) -> float:
        """Get current ring coherence (K-value)."""
        return compute_ring_coherence(phase_state, self.target)
    
    def observe(self, phase_state: PhaseState) -> Dict:
        """
        Observe current state and record it.
        
        Returns: convergence details dict
        """
        details = detect_convergence_details(phase_state, self.target, self.tolerances)
        
        # Record observation
        obs = {
            "timestamp": len(self.observation_history),
            "coherence": details["ring_coherence"],
            "converged": details["converged"],
            "details": details,
        }
        self.observation_history.append(obs)
        
        # Seal future if converged
        if details["converged"] and not self.is_sealed:
            self.is_sealed = True
            self.seal_time = len(self.observation_history) - 1
        
        return obs
    
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
            initial_state: starting phase configuration
            branches: dict of {branch_id: control_policy_function}
            duration: simulation horizon (seconds)
            dt: time step (seconds)
        
        Returns:
            Sorted list of outcomes (best coherence first, then earliest convergence)
        """
        outcomes = []
        
        for branch_id, policy in branches.items():
            outcome = simulate_branch(
                initial_state=initial_state,
                control_policy=policy,
                duration=duration,
                dt=dt,
                target=self.target,
                tolerances=self.tolerances
            )
            outcome.branch_id = branch_id
            outcomes.append(outcome)
        
        # Sort by: convergence (yes/no), then coherence (high/low), then time (early/late)
        outcomes.sort(key=lambda o: (not o.converged, -o.coherence_score, o.time_to_converge))
        
        return outcomes
    
    def status_report(self, phase_state: PhaseState) -> str:
        """Generate detailed status report."""
        details = detect_convergence_details(phase_state, self.target, self.tolerances)
        
        lines = []
        lines.append("=" * 90)
        lines.append("E14 ORACLE STATUS")
        lines.append("=" * 90)
        lines.append(f"Sealed: {'YES' if self.is_sealed else 'NO'}")
        lines.append(f"K-value (Ring Coherence): {details['ring_coherence']:.6f}")
        lines.append(f"Converged: {details['converged']}")
        lines.append("")
        
        lines.append("Per-Axis Status:")
        for axis in AXES:
            coh = details["per_axis_coherence"][axis]
            conv = "✓" if details["per_axis_converged"][axis] else "✗"
            bar = "█" * int(coh * 30) + "░" * (30 - int(coh * 30))
            lines.append(f"  {axis.upper():6s} {conv} [{bar}] {coh:.6f}")
        
        lines.append("")
        lines.append(f"Converged engines: {len(details['converged_engines'])} / {len(ENGINES)}")
        if details['failing_axes']:
            lines.append(f"Failing axes: {', '.join(details['failing_axes'])}")
        
        lines.append("=" * 90)
        return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════
# EXAMPLE CONTROL POLICIES
# ═══════════════════════════════════════════════════════════════

def policy_ideal_sync(state: PhaseState, t: float, dt: float) -> PhaseState:
    """
    Ideal policy: all engines sync perfectly to target (0).
    Advances each axis at its natural rate toward convergence.
    """
    new_state = {}
    for engine in ENGINES:
        new_state[engine] = {}
        for axis in AXES:
            current = state[engine][axis]
            # Advance toward 0 (target)
            rate = 360.0  # phase units per second (varies by axis in reality)
            new_val = (current + rate * dt) % PHASE_CYCLE
            new_state[engine][axis] = new_val
    return new_state

def policy_random_walk(state: PhaseState, t: float, dt: float) -> PhaseState:
    """
    Random walk policy: each engine drifts randomly.
    Demonstrates branch that fails to converge.
    """
    import random
    new_state = {}
    for engine in ENGINES:
        new_state[engine] = {}
        for axis in AXES:
            current = state[engine][axis]
            drift = (random.random() - 0.5) * 100 * dt
            new_val = (current + drift) % PHASE_CYCLE
            new_state[engine][axis] = new_val
    return new_state

def policy_sovereign_driven(state: PhaseState, t: float, dt: float) -> PhaseState:
    """
    Sovereign-driven policy: E02 (Sovereign/Neo) drives others to convergence.
    E02 leads; others follow with phase-locked loop.
    """
    new_state = {}
    
    # E02 (Sovereign) advances toward target
    e02_new = {}
    for axis in AXES:
        rate = 360.0
        new_val = (state["E02"][axis] + rate * dt) % PHASE_CYCLE
        e02_new[axis] = new_val
    
    new_state["E02"] = e02_new
    
    # Others lock to E02 with small phase offset
    for engine in ENGINES:
        if engine != "E02":
            new_state[engine] = {}
            for axis in AXES:
                target_phase = e02_new[axis]
                current = state[engine][axis]
                # PLL gain: 0.5 (half the error per step)
                error = phase_distance(current, target_phase)
                direction = 1.0 if (target_phase - current) % PHASE_CYCLE < PHASE_CYCLE / 2 else -1.0
                correction = min(error, 100.0 * dt) * direction
                new_val = (current + correction) % PHASE_CYCLE
                new_state[engine][axis] = new_val
    
    return new_state

# ═══════════════════════════════════════════════════════════════
# MAIN DEMO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print()
    print("╔" + "═" * 88 + "╗")
    print("║" + " E14 ORACLE LAYER — CONVERGENCE & BRANCHING ".center(88) + "║")
    print("╚" + "═" * 88 + "╝")
    print()
    
    # Initialize Oracle
    oracle = E14Oracle(target=0.0, tolerances=TOLERANCE)
    
    # Create initial state: all engines at phase 0 (perfect sync)
    initial_state_perfect = {
        engine: {axis: 0.0 for axis in AXES}
        for engine in ENGINES
    }
    
    # Create initial state: all engines scattered
    initial_state_scattered = {
        engine: {axis: float((i * 12345) % 86400) for axis in AXES}
        for i, engine in enumerate(ENGINES)
    }
    
    # Observe both
    print("[1] Perfect synchronization (all at phase 0)")
    obs1 = oracle.observe(initial_state_perfect)
    print(oracle.status_report(initial_state_perfect))
    print()
    
    print("[2] Scattered initial state")
    obs2 = oracle.observe(initial_state_scattered)
    print(oracle.status_report(initial_state_scattered))
    print()
    
    # Evaluate branches from scattered state
    print("[3] Evaluating 3 branching futures from scattered state")
    branches = {
        "ideal-sync": policy_ideal_sync,
        "sovereign-driven": policy_sovereign_driven,
        "random-walk": policy_random_walk,
    }
    
    outcomes = oracle.evaluate_branches(initial_state_scattered, branches, duration=10.0, dt=0.1)
    
    print()
    for i, outcome in enumerate(outcomes, 1):
        print(f"  [{i}] {outcome}")
    
    print()
    print("=" * 90)
    print("ORACLE CONCLUSION")
    print("=" * 90)
    print(f"Best outcome: {outcomes[0].branch_id}")
    print(f"  Converged: {outcomes[0].converged}")
    print(f"  K (coherence): {outcomes[0].coherence_score:.6f}")
    print(f"  Time to convergence: {outcomes[0].time_to_converge:.1f}s")
    print()
