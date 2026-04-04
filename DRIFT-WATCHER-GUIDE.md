# DRIFT WATCHER GUIDE
# こたひたんが・どりふと見守り

## Overview

**Drift Watcher** is a real-time K(t) coherence monitor that tracks system unity score over time, detects drift patterns, and alerts when thresholds are crossed.

### Rhythm Philosophy

Every observation is clocked to natural rhythm cycles:

```
TICK   = 50ms    (fast micro-feedback)
BEAT   = 200ms   (normal reading speed)
BREATH = 1500ms  (pause to absorb)
CYCLE  = 12s     (full micro-cycle)
```

The watcher samples at BEAT intervals (200ms) and organizes observations into 12-second cycles.

---

## Files

### `kotahitanga_driftwatcher.py`
**Main monitoring engine**

Features:
- Real-time K(t) sampling via SymPy engine
- Drift detection (degrading / stable / recovering)
- Phase tracking (TICK, BEAT, BREATH, CYCLE)
- Alert thresholds (WARN @ 80%, FAIL @ 50%)
- Command-line args: `--interval`, `--max-cycles`, `--verbose`

**Usage:**
```bash
python kotahitanga_driftwatcher.py --verbose --max-cycles 5
```

### `driftwatcher-bridge.ps1`
**PowerShell control interface**

Functions:
- `Start-DriftWatcher` — Launch background watcher
- `Get-DriftWatcherOutput` — Retrieve current output
- `Stop-DriftWatcher` — Terminate watcher
- `Watch-Coherence` — Real-time blocking monitor

---

## Usage Examples

### Example 1: Quick 30-second Watch
```powershell
cd C:\Users\Admin\OneDrive\Desktop\~E14-
. .\driftwatcher-bridge.ps1

Watch-Coherence -Seconds 30
```

Output:
```
[14:23:15.342] ℹ️ K=0.857 | BEAT | Drift: stable
[14:23:15.542] ℹ️ K=0.857 | BREATH | Drift: stable
[14:23:16.042] ✅ K=1.000 | TICK | Drift: recovering
...
```

### Example 2: Background Monitoring
```powershell
# Start watcher (infinite, verbose)
$watcher = Start-DriftWatcher -Interval 200 -Verbose

# Do other work...
Start-Sleep -Seconds 30

# Check output
Get-DriftWatcherOutput -JobId $watcher.Id

# Stop when done
Stop-DriftWatcher -JobId $watcher.Id
```

### Example 3: Detect Drift Patterns
```powershell
# Run for 60 seconds, check for degradation
Watch-Coherence -Seconds 60 -Verbose
```

Shows phase bars + drift direction:
```
[14:24:00.123] ℹ️ Phase: BEAT   ▂▄▆█ | Cycle:   1 | K(t) = 0.857 | Drift: stable (-0.0001)
[14:24:00.323] ℹ️ Phase: BREATH ▁▃▅▇ | Cycle:   1 | K(t) = 0.857 | Drift: stable (+0.0000)
[14:24:01.523] ⚠️ Phase: CYCLE ▃▅▇█ | Cycle:   2 | K(t) = 0.714 | Drift: degrading (-0.0143)
```

---

## Drift Detection Algorithm

### Calculation
```python
# Window = 10 samples (2 seconds at BEAT interval)
recent_K = [K₁, K₂, ..., K₁₀]
delta = K₁₀ - K₁
velocity = delta / window_size

# Classification
if velocity < -0.01:
    direction = "degrading"
elif velocity > +0.01:
    direction = "recovering"
else:
    direction = "stable"
```

### Alert Conditions
- **WARN**: K < 80% (0.8) AND degrading
- **FAIL**: K < 50% (0.5)

---

## Integration with E14 Console

Add to `E14-Console.ps1`:

```powershell
function E14-Drift-Watch {
    <#
    .SYNOPSIS
    Real-time coherence drift monitoring
    #>
    param(
        [int] $Seconds = 60,
        [switch] $Verbose = $false
    )
    
    . .\driftwatcher-bridge.ps1
    Watch-Coherence -Seconds $Seconds -Verbose:$Verbose
}

function E14-Drift-Background {
    <#
    .SYNOPSIS
    Start background drift watcher
    #>
    . .\driftwatcher-bridge.ps1
    $job = Start-DriftWatcher -Verbose
    Write-Host "Watcher Job ID: $($job.Id)"
    return $job.Id
}

function E14-Drift-Status {
    <#
    .SYNOPSIS
    Get status of running watcher
    #>
    param([int] $JobId)
    . .\driftwatcher-bridge.ps1
    Get-DriftWatcherOutput -JobId $JobId
}
```

Usage:
```powershell
. .\E14-Console.ps1

# Quick 30-second watch
E14-Drift-Watch -Seconds 30

# Background monitoring
$id = E14-Drift-Background
E14-Drift-Status -JobId $id
```

---

## Metrics Explained

### K(t) — Unity Score
- Range: [0, 1]
- 0 = All 7 dimensions FAIL
- 1 = All 7 dimensions PASS
- 0.857 = 6/7 dimensions PASS (typical safe threshold)

### Direction
- **stable**: |velocity| < 0.01 per sample
- **degrading**: velocity < -0.01 (K declining)
- **recovering**: velocity > +0.01 (K improving)

### Phase
- **TICK** (0-50ms): Micro-feedback phase
- **BEAT** (50-200ms): Normal observation phase
- **BREATH** (200-1500ms): Pause to absorb
- **CYCLE** (1500-12000ms): Long integration phase

---

## Configuration

Edit `kotahitanga_driftwatcher.py` to customize:

```python
# Thresholds
K_THRESHOLD_WARN = 0.8      # Alert when K < 80%
K_THRESHOLD_FAIL = 0.5      # Critical when K < 50%
K_STABLE_WINDOW  = 10       # Samples for stability (2s at BEAT)

# Rhythm
TICK_S   = 0.050
BEAT_S   = 0.200
BREATH_S = 1.500
CYCLE_S  = 12.000
```

---

## Real-World Scenarios

### Scenario 1: Stable System
```
K holds at 0.857 for multiple cycles
Direction: stable
Velocity: ~0.0
→ System is healthy, no action needed
```

### Scenario 2: Gradual Degradation
```
Cycle 1: K = 0.857
Cycle 2: K = 0.800
Cycle 3: K = 0.714
Direction: degrading
Velocity: -0.014 per sample
→ Alert! Investigate dimension failures
```

### Scenario 3: Recovery
```
(After fix applied)
Cycle 3: K = 0.714
Cycle 4: K = 0.800
Cycle 5: K = 0.857
Direction: recovering
→ Dimension remediation successful
```

---

## Implementation Notes

### SymPy Integration
Drift Watcher calls `kotahitanga_sympy.py` on every sample to get K(t).
- No caching: fresh calculation each BEAT
- Fallback: returns -1.0 if Python unavailable
- Timeout: 5 seconds per SymPy call

### Background Job Management
```powershell
# Start
$job = Start-DriftWatcher -Verbose
$job | Format-List  # See job details

# Monitor
Get-Job -Id $job.Id | Format-Table
Receive-Job -Job $job  # Get output

# Stop
Stop-Job -Id $job.Id
Remove-Job -Id $job.Id
```

### Thread Safety
Each watcher runs in isolated Python process → no threading conflicts.

---

## Next Steps

1. **Deploy watcher** → Add E14-Drift-Watch to console
2. **Set custom thresholds** → Tune K_THRESHOLD_WARN/FAIL
3. **Create dashboards** → Capture K(t) history over hours
4. **Automate response** → Trigger remediation on FAIL alert
5. **Historical analysis** → Store drift patterns for ML training

---

**Status: ✅ Drift Watcher Ready for Monitoring**
