# Architecture Guide

Complete system design and component documentation.

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [6-Axis State Model](#6-axis-state-model)
4. [14-Engine Ring](#14-engine-ring)
5. [Convergence Algorithm](#convergence-algorithm)
6. [Decision Pipeline](#decision-pipeline)
7. [Lock Mechanism](#lock-mechanism)
8. [Security Model](#security-model)

## System Overview

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     E14 ORACLE SYSTEM                    │
└──────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
        ┌─────────────┐ ┌────────────┐ ┌──────────┐
        │   Oracle    │ │ DriftWatch │ │ Live     │
        │   Layer     │ │ (Observer) │ │ (Exec)   │
        └─────────────┘ └────────────┘ └──────────┘
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                ┌──────────────────────────────┐
                │  14-Engine Consensus Ring    │
                │  (Peer-to-Peer, Zero-Trust)  │
                └──────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
        ┌───────▼────┐ ┌────────────────┐ │
        │ Temporal   │ │ Thermal        │ │
        │ Axes       │ │ Regulation     │ │
        │ (4 axes)   │ │ (heat axis)    │ │
        └────────────┘ └────────────────┘ │
                                          │
                                  ┌───────▼────┐
                                  │ Environmental
                                  │ (weather)
                                  └────────────┘
```

### Data Flow

```
STATE → OBSERVE → CONVERGENCE CHECK → GATE → EXECUTE
  ↑                       ↓
  └───────── FEEDBACK ────┘
```

1. **STATE**: Current 6-axis configuration across 14 engines
2. **OBSERVE**: DriftWatcher monitors state continuously
3. **CONVERGENCE**: Oracle checks if K ≥ 0.99
4. **GATE**: Live oracle verifies resources (CPU, memory, disk, weather)
5. **EXECUTE**: If all gates open, execute decision
6. **FEEDBACK**: Adjust state based on execution result

## Core Components

### 1. E14 Oracle (oracle_layer.py)

**Responsibility**: Convergence detection and branching futures evaluation

```python
class E14Oracle:
    def __init__(self, target=0.0, tolerances=TOLERANCE):
        # Initialize oracle with target invariant (Aries Point = 0.0)
        pass
    
    def convergence_now(self, phase_state: PhaseState) -> bool:
        # Check if all 14 engines converged on all 4 axes
        pass
    
    def score_now(self, phase_state: PhaseState) -> float:
        # Get current K-value (coherence 0.0-1.0)
        pass
    
    def evaluate_branches(self, state, branches, duration):
        # Simulate multiple decision paths, rank by coherence
        pass
```

**Key Metrics**:
- **K-Value (Kotahitanja)**: Ring coherence (0.0 → 1.0)
- **Convergence Threshold**: K ≥ 0.99
- **Axes**: tick (50ms), beat (200ms), breath (1.5s), cycle (12s)

### 2. E14 DriftWatcher (kotahitanga_driftwatcher.py)

**Responsibility**: Continuous state monitoring and anomaly detection

```python
class KotahitangaDriftWatcher:
    def __init__(self):
        # Monitor 14 engines in real-time
        pass
    
    def observe_state(self) -> PhaseState:
        # Read current state from all engines
        pass
    
    def detect_drift(self) -> Dict:
        # Identify phase divergence or anomalies
        pass
    
    def report(self) -> Dict:
        # Summary of state coherence
        pass
```

**Watches**:
- Phase drift on all 6 axes
- Engine health (connectivity, responsiveness)
- Resource usage (CPU, memory, disk)
- Weather conditions (XYO oracle)

### 3. E14 Live (e14_live.py)

**Responsibility**: Real-time decision execution with resource gating

```python
class E14LiveOracle:
    def __init__(self):
        # Initialize decision executor
        pass
    
    def compute_k_score(self) -> float:
        # Get current coherence from 6 axes
        pass
    
    def get_system_resources(self) -> Dict:
        # CPU headroom, memory headroom, disk headroom
        pass
    
    def can_execute(self) -> Tuple[bool, Dict]:
        # Check: K ≥ 0.99 + CPU > 10% + Memory > 15% + Disk > 20% + weather safe
        pass
    
    def execute(self, operation_id, operation_func):
        # Execute if safe, else queue for later
        pass
```

**Decision Gates**:
- `K ≥ 0.99`: Coherence threshold
- `CPU > 10%`: Ensure headroom
- `Memory > 15%`: Ensure headroom
- `Disk > 20%`: Ensure headroom
- `Weather ≤ 0.6`: Environmental permission (XYO verified)

### 4. E14 SymPy (kotahitanga_sympy.py)

**Responsibility**: Mathematical computation and symbolic solving

Supports:
- Symbolic phase calculations
- Convergence differential equations
- Lock metadata validation
- Cryptographic hash verification

### 5. E14 TaskManager (e14_seven_day_logger.py)

**Responsibility**: Task queue orchestration and 7-day rotating logs

Features:
- Queue pending operations
- 7-day log rotation per engine
- Cycle-based task scheduling
- Audit trail of all decisions

## 6-Axis State Model

### Temporal Axes (4)

```
TICK (50ms)
├─ Fastest feedback loop
├─ Cardiac rhythm analogue
└─ Coupled to thermal stability (heat axis)

BEAT (200ms)
├─ Normal operational pace
├─ Cross-axis integration window
└─ Phase-lock bridge between tick and breath

BREATH (1.5s)
├─ Human-relevant timescale
├─ Respiratory analogue
└─ Thermal regulation checkpoint

CYCLE (12s)
├─ Macro-scale observation window
├─ Long-term stability monitor
└─ Precession analogue (26,000 years → 12s)
```

### Thermal Axis (1)

```
HEAT (Insolation Equilibrium)
├─ Target: 0.075 (Earth's orbital eccentricity analogue)
├─ Tolerance: ±0.005
├─ Damping: 0.02 (Gregorian correction cycle analogue)
└─ Coupled to: Human-core thermal stability
```

### Environmental Axis (1)

```
WEATHER (XYO-Verified)
├─ Geolocation + Timestamp + Cryptographic Proof
├─ Target: ≤ 0.6 (safe conditions)
├─ Permission gate for execution
└─ Weather-gated decision execution
```

**Total State Size**: 14 engines × 6 axes = 84 phase values

## 14-Engine Ring

### Engine Roles

| ID | Name | Role | Primary Axes |
|----|----|------|------|
| E01 | 365 | Validator | tick, beat, breath, cycle |
| E02 | 777 | Sovereign | All 6 (ultimate authority) |
| E03 | 101 | Horizon | cycle, heat (boundary observer) |
| E04-E14 | 1001-1012 | Peers | Subsets (consensus participants) |

### Consensus Model

- **Type**: Byzantine Fault Tolerant (BFT) variant
- **Quorum**: 14/14 engines must converge
- **Merkle Root**: All engines synchronized to identical cryptographic hash
- **Validation**: 4GR-FSE state machine (GROUND → READ → GATE → GROW)

### Peer Discovery

Engines discover each other via:
- `config/topology.yaml` (static registry)
- `config/lock-metadata.json` (shared lock state)
- Network broadcast (future: mDNS)

## Convergence Algorithm

### Phase Distance Calculation

```python
def phase_distance(phi1, phi2, modulo=PHASE_CYCLE):
    """Shortest circular distance between two phases."""
    diff = abs(phi1 - phi2)
    return min(diff, modulo - diff)
```

### Per-Axis Convergence

```python
def is_axis_converged(state, axis, target=0.0, tolerance=100.0):
    """Check if all 14 engines converged on one axis."""
    for engine in ENGINES:
        distance = phase_distance(state[engine][axis], target)
        if distance > tolerance:
            return False
    return True
```

### Ring Coherence (K-Value)

```python
def compute_ring_coherence(state, target=0.0):
    """
    K = geometric mean of 4 axes coherences
    
    Per-axis coherence = 1.0 - (avg_distance / PHASE_CYCLE/2)
    """
    coherences = [
        compute_axis_coherence(state, axis, target)
        for axis in AXES
    ]
    return geometric_mean(coherences)
```

### Branching Futures

Oracle simulates multiple control policies:

1. **Ideal Sync**: All engines advance toward target (best case)
2. **Sovereign Driven**: E02 leads, others follow with phase-locked loop
3. **Random Walk**: Engines drift independently (worst case)

**Selection Criteria**:
1. Convergence achieved (yes/no)
2. Coherence score (high/low)
3. Time to convergence (early/late)

## Decision Pipeline

```
STATE          OBSERVE        CONVERGENCE     GATE CHECK      EXECUTE
────────────→  ──────────→   ────────────→   ────────────→  ────────→
  (6 axes)     (monitor)     (K ≥ 0.99?)     (resources +    (if all
  across 14                                    weather)        gates
  engines                                                      open)
```

### Gating Conditions

All must be true to execute:

```python
conditions = {
    "k_score": K >= 0.99,
    "cpu_headroom": CPU_available > 10%,
    "memory_headroom": Memory_available > 15%,
    "disk_headroom": Disk_available > 20%,
    "weather_gate": Weather_safety <= 0.6,
}

can_execute = all(conditions.values())
```

### Execution Modes

1. **EXECUTED**: All gates open, decision executes immediately
2. **QUEUED**: Some gate blocked, decision queues for later
3. **EXECUTION_FAILED**: Execution attempted but failed (retry queued)

## Lock Mechanism

### 90-Day Lock

```json
{
  "lock_id": "550e8400-e29b-41d4-a716-446655440000",
  "lock_inception": "2025-01-14T10:00:00.000Z",
  "lock_expiry": "2025-04-14T10:00:00.000Z",
  "lock_duration_days": 90,
  "lock_root_hash": "a1b2c3d4...",
  "lock_phrase": "UNIT-LOCKED:14engines:90days:2025-01-14"
}
```

### Renewal Process

- **Every 90 days**: Automatic renewal via `lock-initialize.ts`
- **No downtime**: Services continue running during renewal
- **New hash**: Fresh cryptographic root generated
- **Cycle tracking**: Increments cycle counter (Cycle 1, Cycle 2, ...)

### Enforcement

- All 19 services locked under single mechanism
- Shared `.env.lock` environment file
- Temporal validation on every operation

## Security Model

### Zero-Trust Architecture

**Principle**: All signals validated through consensus before execution

```
DECISION REQUESTER
        ↓
    VALIDATE (E01 checks syntax)
        ↓
    VALIDATE (E02 checks authority)
        ↓
    VALIDATE (E03 checks boundary conditions)
        ↓
    VALIDATE (E04-E14 check consensus)
        ↓
    EXECUTE ONLY IF 14/14 AGREE
```

### Cryptographic Validation

- **Merkle Root**: Tree hash of all engine states
- **SHA-256**: Cryptographic hash function
- **Synchronization**: All engines verify identical root before execution
- **Proof**: Requires ≥99.9% signature uniqueness

### Network Isolation

- **Docker network**: `e14_net` (bridge, internal only)
- **No exposed ports**: Services communicate only via internal network
- **Config volumes**: Read-only access to shared state
- **Future**: NetworkPolicy for Kubernetes

### Access Control

(Future: RBAC in Kubernetes deployment)
- **Admin**: Create/delete operations
- **Operator**: Scale, execute pre-approved operations
- **Viewer**: Read-only access

## Data Flows

### Observation Flow

```
DriftWatcher reads all engines
         ↓
Computes phase state (14 × 6)
         ↓
Calculates coherence per axis
         ↓
Aggregates K-value
         ↓
Logs to history
```

### Execution Flow

```
Operation submitted
         ↓
Live oracle checks gates
         ↓
If all gates open:
  - Call operation function
  - Return result
  ↓
If some gates blocked:
  - Queue operation
  - Return queued status
  ↓
Log decision + outcome
```

### Convergence Flow

```
Phase drift detected
         ↓
DriftWatcher reports
         ↓
Oracle evaluates branches
         ↓
Simulates 3 futures
         ↓
Ranks by coherence
         ↓
Selects best path
         ↓
Advises TaskManager
```

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Convergence check | <10ms | Parallel, O(14) |
| K-value computation | <5ms | Aggregate operation |
| Phase distance | <1μs per engine | Circular modulo |
| Decision gate check | <50ms | System resource queries |
| Branching simulation | ~1s | 3 futures × 10s horizon |

## Future Extensions

- **Kubernetes HPA**: Auto-scaling 3-10 replicas
- **Observability**: Prometheus metrics, Grafana dashboards
- **Distributed Tracing**: Jaeger traces across services
- **API Gateway**: HTTP API on top of decision engine
- **Web Dashboard**: Real-time visualization of convergence
- **Multi-region**: Geo-distributed consensus

---

See also:
- `CONFIGURATION.md` — Environment variables
- `DOCKER-GUIDE.md` — Container deployment
- `API.md` — Python API reference
