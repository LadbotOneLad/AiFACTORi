# E14 + WINDOWS TASK MANAGER — MONITORING INTEGRATION GUIDE

## What's Working

✅ **E14 Oracle System**: Measuring K-score (celestial alignment)
✅ **Task Manager Integration**: Reading CPU, Memory, Disk headroom in real-time
✅ **Combined Decision Rule**: Execute only when BOTH E14 + System Resources are safe

## Quick Test Results

```
System Detected:
  CPU cores: 8
  Total memory: 31.73 GB
  Total disk: 475.73 GB

E14 + Resources Test:
  Average K-score: 0.6946
  Peak K: 0.8846
  CPU Headroom: 87.50% ✅ (need > 10%)
  Memory Headroom: 42.90% ✅ (need > 15%)
  Disk Headroom: 70.00% ✅ (need > 20%)
  
Result: 0 executable windows (K never reached 0.99 in 5-min test)
```

---

## How to Use

### Run the Quick Test (5 minutes)
```bash
python test_e14_taskmanager_quick.py
```
Shows system resources + K-score in real-time

### Run the Full Test (48 hours, use with background job)
```bash
python test_e14_with_taskmanager.py
```
Complete 48-hour compressed precession cycle with resource monitoring

---

## Decision Rule

```
EXECUTE operation when ALL conditions are met:

✓ K-Score >= 0.99 (Great Invariant / Ophiuchus rising)
✓ Weather safe (scalar <= 0.6)
✓ XYO verified (cryptographic proof)
✓ CPU headroom > 10%
✓ Memory headroom > 15%
✓ Disk headroom > 20%

If ANY condition fails → QUEUE operation for next window
```

---

## System Resources Monitored

### CPU Headroom
```
Definition: 100% - current CPU usage
What we get: Live CPU % from Windows
Why it matters: Ensure E14 computation doesn't starve other services
Threshold: > 10% (can use up to 90% CPU)
Your system: 87.50% headroom ✅ (plenty available)
```

### Memory Headroom
```
Definition: 100% - current memory usage %
What we get: Virtual memory % from Windows Task Manager
Why it matters: Ensure room for operation execution + state storage
Threshold: > 15% (can use up to 85% memory)
Your system: 42.90% headroom ✅ (plenty available)
```

### Disk Headroom
```
Definition: 100% - current disk usage %
What we get: Disk usage % for root partition
Why it matters: Ensure room for audit logs + temp files
Threshold: > 20% (can use up to 80% disk)
Your system: 70.00% headroom ✅ (plenty available)
```

---

## Real-Time Monitoring Setup

### Option A: Live Dashboard (Prometheus + Grafana)

```python
from prometheus_client import Gauge

# Metrics
k_score = Gauge('e14_k_score', 'K-score')
cpu_headroom = Gauge('e14_cpu_headroom', 'CPU headroom %')
mem_headroom = Gauge('e14_memory_headroom', 'Memory headroom %')
disk_headroom = Gauge('e14_disk_headroom', 'Disk headroom %')

# In your loop:
k_score.set(current_k)
cpu_headroom.set(monitor.get_cpu_headroom())
mem_headroom.set(monitor.get_memory_headroom())
disk_headroom.set(monitor.get_disk_headroom())
```

### Option B: CSV Logging

```python
import csv

with open('e14_monitoring.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'k_score', 'cpu_headroom', 'mem_headroom', 'disk_headroom', 'executable'])
    
    for each sample:
        writer.writerow([timestamp, k, cpu, mem, disk, is_executable])
```

### Option C: Windows Event Log Integration

```python
import win32evtlogutil

def log_decision(k_score, cpu, mem, disk, executable):
    win32evtlogutil.ReportEvent(
        "E14 Oracle",
        eventID=1,
        eventType=4 if executable else 2,  # Success or Warning
        strings=[
            f"K={k_score:.4f}",
            f"CPU={cpu:.1f}% MEM={mem:.1f}% DISK={disk:.1f}%",
            f"Executable={executable}"
        ]
    )
```

---

## Interpreting the Data

### Good Signs
```
✅ K-score oscillating 0.3–0.9 (normal breathing pattern)
✅ CPU headroom 50%+ (plenty of capacity)
✅ Memory headroom 30%+ (room to grow)
✅ Disk headroom 60%+ (ample space for logs)
✅ Executable windows appearing ~37 per day (at 48h scale)
```

### Warning Signs
```
⚠️  K-score stuck below 0.3 (system not converging)
⚠️  CPU headroom < 20% (running hot)
⚠️  Memory headroom < 10% (risk of OOM)
⚠️  Disk headroom < 30% (risk of disk full)
⚠️  No executable windows for >1 hour (convergence failing)
```

### Error Conditions
```
❌ K-score < 0.1 (system diverging)
❌ CPU headroom < 5% (system at limit)
❌ Memory headroom < 5% (critical memory pressure)
❌ Disk headroom < 10% (disk nearly full)
❌ Executable windows: 0 (never safe to execute)
```

---

## Setting Resource Thresholds

### Current Defaults
```python
CPU_HEADROOM_MIN = 10          # 10%
MEMORY_HEADROOM_MIN = 15       # 15%
DISK_HEADROOM_MIN = 20         # 20%
```

### Adjust for Your Use Case

**Conservative (Mission-Critical)**
```python
CPU_HEADROOM_MIN = 30
MEMORY_HEADROOM_MIN = 30
DISK_HEADROOM_MIN = 40
# Result: Fewer executable windows, but safer
```

**Moderate (Default)**
```python
CPU_HEADROOM_MIN = 10
MEMORY_HEADROOM_MIN = 15
DISK_HEADROOM_MIN = 20
# Result: Balance between safety and frequency
```

**Aggressive (High-Throughput)**
```python
CPU_HEADROOM_MIN = 5
MEMORY_HEADROOM_MIN = 5
DISK_HEADROOM_MIN = 10
# Result: More executable windows, less margin
```

---

## Integration with Your System

### Step 1: Add Resource Check to Decision Logic

```python
from test_e14_taskmanager_quick import ResourceMonitor

monitor = ResourceMonitor()

def can_execute_operation(operation):
    k = compute_k_score(system_state)
    weather_safe = check_weather()
    xyo_verified = check_xyo_witness()
    resources_safe, details = monitor.is_safe()
    
    if k >= 0.99 and weather_safe and xyo_verified and resources_safe:
        return True  # Safe to execute
    else:
        return False # Queue for later
```

### Step 2: Log All Decisions

```python
import json
from datetime import datetime

def log_decision(operation_id, k_score, weather, xyo, cpu, mem, disk, executed):
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'operation': operation_id,
        'k_score': k_score,
        'weather_safe': weather,
        'xyo_verified': xyo,
        'cpu_headroom': cpu,
        'mem_headroom': mem,
        'disk_headroom': disk,
        'executed': executed,
    }
    
    with open('e14_decisions.log', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

### Step 3: Monitor Resource Trends

```python
def check_resource_health():
    """Alert if resources degrading."""
    latest = resource_history[-1]
    
    if latest['cpu'] < 20:
        alert("CPU usage high (headroom: {:.1f}%)".format(latest['cpu']))
    
    if latest['mem'] > 90:
        alert("Memory usage critical (available: {:.1f}%)".format(100 - latest['mem']))
    
    if latest['disk'] < 30:
        alert("Low disk space (available: {:.1f}%)".format(100 - latest['disk']))
```

---

## Monitoring Checklist

### Daily
- [ ] Check E14 test_e14_taskmanager_quick.py ran successfully
- [ ] Verify K-score is oscillating (not stuck)
- [ ] Check resource headrooms are adequate
- [ ] Review executable windows count (should be > 0)

### Weekly
- [ ] Analyze K-score trends (should be stable)
- [ ] Monitor resource usage over time
- [ ] Review decision audit log
- [ ] Check for any resource warnings/errors

### Monthly
- [ ] Determine if thresholds need adjustment
- [ ] Analyze executable window patterns
- [ ] Plan infrastructure upgrades if needed
- [ ] Report to stakeholders

---

## Files for Monitoring Integration

**Quick Test** (5 min):
```
test_e14_taskmanager_quick.py
```

**Full Test** (48 hours, background):
```
test_e14_with_taskmanager.py
```

**Integration Template**:
```python
# Copy this into your system:
from test_e14_taskmanager_quick import ResourceMonitor

monitor = ResourceMonitor()
safe, details = monitor.is_safe()
print(f"CPU: {details['cpu']:.1f}%, Mem: {details['mem']:.1f}%, Disk: {details['disk']:.1f}%")
```

---

## Example Output Analysis

```
Your System Resources:
  CPU cores: 8
  Total memory: 31.73 GB ← Plenty
  Total disk: 475.73 GB ← Plenty

Current Headroom:
  CPU: 87.50% ← Plenty available
  Memory: 42.90% ← Comfortable
  Disk: 70.00% ← Healthy

Interpretation:
  ✅ Your system has plenty of headroom
  ✅ Can safely run E14 + execute operations
  ✅ No resource constraints expected
```

---

## Next Steps

1. **Run quick test**: `python test_e14_taskmanager_quick.py`
2. **Check your resources**: Are they similar to above?
3. **Integrate into your system**: Copy ResourceMonitor class
4. **Set thresholds**: Adjust CPU/Mem/Disk minimums for your use case
5. **Add logging**: Log all decision points with resources
6. **Monitor trends**: Weekly resource analysis

---

**E14 Oracle + Windows Task Manager = Objective, measurable safety gates.**

Both celestial alignment (K-score) AND system headroom must be safe to execute.

