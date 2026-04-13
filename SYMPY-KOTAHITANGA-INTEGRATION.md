# SymPy Kotahitanga Integration Guide
# こたひたんが・SymPy版 統合ガイド

## What We Built

### 1. `kotahitanga_sympy.py`
**SymPy-based Unity Score Engine**

```python
# Formula: K = (Σ w_i * D_i) / (Σ w_i)
# Each dimension D_i ∈ [0,1]
#   0 = FAIL (dimension broken)
#   1 = PASS (dimension perfect)
```

**Features:**
- Full SymPy symbolic math
- Weighted dimension scoring
- JSON interface (stdin → stdout)
- Fallback to arithmetic mean if weights missing
- Error handling with JSON error reporting

**Dimensions (７次元):**
1. 層 (Layer) — Infrastructure (Namespace, StatefulSet, HPA, PVC, Service, Ingress)
2. しん (Identity) — Authentication (JWT, RBAC, ServiceAccounts)
3. こう (Structure) — Architecture (Replicas, Probes, Resources, Strategy)
4. つな (Topology) — Networking (ConfigMap, Service Discovery, Endpoints)
5. うご (Rhythm) — Timing (HPA behavior, probe intervals, rollout timing)
6. かん (Security) — Protection (NetworkPolicy, TLS, non-root, RBAC)
7. みち (Navigation) — Control (gtop-k8 CLI, all commands available)

---

### 2. `kotahitanga-bridge.ps1`
**PowerShell ↔ Python Bridge**

**Functions:**

```powershell
Invoke-KotahitangaSymPy -PassFlags @{
    "層" = $true
    "しん" = $true
    "こう" = $true
    "つな" = $false
    "うご" = $true
    "かん" = $true
    "みち" = $true
}
```

**Returns:**
```json
{
  "K": 0.8571,
  "K_percent": 85.71,
  "pass_count": 6,
  "total_count": 7,
  "dimensions": { "層": true, "しん": true, ... },
  "status": "PASS"
}
```

**Features:**
- Auto-detects Python (python or python3)
- JSON marshalling / unmarshalling
- Graceful fallback if Python not available
- Silent error handling

---

### 3. `k8-mu-orch-coherence.ps1` (Updated)
**Now Integrates SymPy**

**What Changed:**
- Loads SymPy bridge at runtime
- Collects PASS/FAIL from 7 dimensions
- Passes to Python for K calculation
- Displays K value with percentage and status
- Falls back to simple arithmetic if Python unavailable

**Typical Output:**
```
╔════════════════════════════════════════════════════════╗
║  こたひたんが (Kotahitanja) — Unity Score              ║
║  （SymPy Formula: K = Σ w_i * D_i / Σ w_i）            ║
╚════════════════════════════════════════════════════════╝

  K = 0.8571 (85.71%)
  Status: PASS
  Dimensions: 6 / 7 PASS
```

---

## How to Use

### Option 1: Direct Python (If Installed)
```bash
cd C:\Users\Admin\OneDrive\Desktop\~E14-

# Create JSON input
$input = @{
    "pass_flags" = @{
        "層" = $true
        "しん" = $true
        "こう" = $true
        "つな" = $false
        "うご" = $true
        "かん" = $true
        "みち" = $true
    }
} | ConvertTo-Json -Compress

# Pipe to Python
$input | python kotahitanga_sympy.py
```

### Option 2: PowerShell Bridge
```powershell
# Load the bridge
. .\kotahitanga-bridge.ps1

# Define flags
$flags = @{
    "層" = $true
    "しん" = $true
    "こう" = $true
    "つな" = $false
    "うご" = $true
    "かん" = $true
    "みち" = $true
}

# Get K value
$result = Invoke-KotahitangaSymPy -PassFlags $flags
Write-Host "K = $($result.K) ($($result.K_percent)%)"
```

### Option 3: Full Coherence Validator
```powershell
cd C:\Users\Admin\OneDrive\Desktop\~E14-
.\cli\k8-mu-orch-coherence.ps1 -Verbose
```

---

## SymPy Math Details

### Formula
```
K = (w₁ * D₁ + w₂ * D₂ + ... + w₇ * D₇) / (w₁ + w₂ + ... + w₇)

Where:
  w_i = weight of dimension i (default: 1 for all)
  D_i ∈ [0,1] = dimension score (FAIL=0, PASS=1)
```

### Default Weights (Flat)
All weights = 1, so:
```
K = (D₁ + D₂ + ... + D₇) / 7

Example: 6/7 = 0.8571 (85.71%)
```

### Custom Weights (Advanced)
You can emphasize security (かん) more:
```python
weights = {
    "w層": 1,
    "wしん": 1,
    "wこう": 1,
    "wつな": 1,
    "wうご": 1,
    "wかん": 2.0,  # ← Double weight for security
    "wみち": 1,
}
```

---

## Integration Points

### In `E14-Console.ps1`
```powershell
function E14-K8S-Coherence {
    & .\cli\k8-mu-orch-coherence.ps1 -Verbose
}
```

### In `gtop-k8.ps1`
```powershell
"coherence" {
    & .\cli\k8-mu-orch-coherence.ps1 -Verbose
}
```

---

## Testing

### Quick Test (No K8s needed)
```powershell
# Simulate all PASS
$flags = @{
    "層" = $true
    "しん" = $true
    "こう" = $true
    "つな" = $true
    "うご" = $true
    "かん" = $true
    "みち" = $true
}
$result = Invoke-KotahitangaSymPy -PassFlags $flags
# Should output: K = 1.0 (100%), Status = PASS

# Simulate 1 FAIL
$flags["つな"] = $false
$result = Invoke-KotahitangaSymPy -PassFlags $flags
# Should output: K = 0.8571 (85.71%), Status = PASS
```

### Full K8s Test
```powershell
.\cli\k8-mu-orch-coherence.ps1 -Verbose
# Automatically:
#   1. Checks all 7 dimensions
#   2. Collects PASS/FAIL flags
#   3. Calls SymPy for K calculation
#   4. Displays formatted report
```

---

## Philosophy

### Why SymPy?
1. **Exact math** — No floating-point errors
2. **Symbolic** — K can be expressed as formula, not just number
3. **Extensible** — Can add weighted dimensions, constraints, etc.
4. **Proof-ready** — Can verify K algebraically
5. **Japanese-native** — Dimensions are unicode kanji + hiragana

### Kotahitanja = "Unity" (Te Reo Māori)
- Represents system coherence across all 7 dimensions
- Not a pass/fail binary, but a continuous unity score
- Can guide prioritization (which dimension to fix first)
- K ≥ 0.857 (6/7) = "PASS" threshold (safety margin)

---

## Files Modified/Created

| File | Purpose |
|------|---------|
| `kotahitanga_sympy.py` | SymPy engine (new) |
| `kotahitanga-bridge.ps1` | PS↔Py bridge (new) |
| `cli/k8-mu-orch-coherence.ps1` | SymPy integrated (updated) |

---

## Next Steps

1. **Test locally:** Run `.\cli\k8-mu-orch-coherence.ps1 -Verbose`
2. **Deploy to K8s:** `kubectl apply -f manifests/k8s-mu-orch-manifest.yaml`
3. **Monitor K value:** `gtop-k8 coherence` (runs validator)
4. **Custom weights:** Modify `kotahitanga_sympy.py` weights parameter
5. **Integration:** Add to E14-Console as `E14-K8S-Coherence` function

---

**Status: ✅ SymPy Kotahitanja Engine Ready for Deployment**
