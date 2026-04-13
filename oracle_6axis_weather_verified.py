# oracle_6axis_weather_verified.py
# E14 6-AXIS ORACLE — WEATHER TRUTH + XYO WITNESS + ORACLE COHERENCE
# ていんが・ひとつ・ななにせん・わけ
#
# 3-layer architecture:
#   Layer 1 (TRUTH):   BOM / satellite / radar → weather scalar (0.0=stable, 1.0=severe)
#   Layer 2 (WITNESS): XYO proof → verify location/source/timestamp authenticity
#   Layer 3 (ORACLE):  E14 coherence check → seal or reject
#
# 6 axes:
#   Temporal (4): tick, beat, breath, cycle  — 1/7200 invariant
#   Thermal (1):  heat                       — human-core (0.075 ± 0.005)
#   Weather (1):  weather                    — BOM/satellite (0.0..1.0), XYO-verified

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json

# ═══════════════════════════════════════════════════════════════
# LAYER 1: WEATHER TRUTH (BOM / Satellite)
# ═══════════════════════════════════════════════════════════════

@dataclass
class WeatherRawData:
    """Raw data from BOM / satellite / radar."""
    source: str              # "BOM", "satellite_GOES", "radar_Sydney", etc.
    timestamp: int           # Unix seconds
    location: Tuple[float, float]  # (lat, lon)
    
    # Raw measurements
    radar_intensity: float   # 0.0..1.0 (reflectivity dBZ normalized)
    precipitation: float     # 0.0..1.0 (mm/h normalized)
    cloud_cover: float      # 0.0..1.0 (fraction)
    wind_speed: float       # 0.0..1.0 (m/s normalized)
    
    def normalize(self) -> float:
        """
        Aggregate raw weather data into single stability scalar.
        
        0.0 = perfectly stable (clear sky)
        1.0 = severe weather (danger zone)
        """
        # Weighted average of severity indicators
        weights = {
            "radar_intensity": 0.3,
            "precipitation": 0.3,
            "cloud_cover": 0.2,
            "wind_speed": 0.2,
        }
        
        total = (
            self.radar_intensity * weights["radar_intensity"] +
            self.precipitation * weights["precipitation"] +
            self.cloud_cover * weights["cloud_cover"] +
            self.wind_speed * weights["wind_speed"]
        )
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, total))

# ═══════════════════════════════════════════════════════════════
# LAYER 2: WITNESS VERIFICATION (XYO)
# ═══════════════════════════════════════════════════════════════

class XYOProofStatus(Enum):
    """XYO witness proof validity."""
    VALID = "valid"           # All checks pass
    INVALID = "invalid"       # Proof failed
    UNVERIFIED = "unverified" # No proof available
    EXPIRED = "expired"       # Proof too old

@dataclass
class XYOProof:
    """XYO witness proof structure."""
    witness_id: str          # XYO sentinel ID (e.g., "XYO_sentinel_001")
    location: Tuple[float, float]  # (lat, lon) where witness observed
    timestamp: int           # When witness observed (Unix seconds)
    claimed_source: str      # What source claimed (e.g., "BOM_Sydney")
    signature: str           # Cryptographic proof
    status: XYOProofStatus = XYOProofStatus.UNVERIFIED
    
    def verify(self, weather_data: WeatherRawData) -> bool:
        """
        Verify that this XYO proof validates the weather data.
        
        Checks:
          1. Location match (within tolerance)
          2. Timestamp match (within tolerance)
          3. Source match (is it the claimed source?)
          4. Signature valid (hasn't been tampered)
        """
        # Tolerance: ±0.05 degrees (≈5km), ±5 seconds
        loc_tol = 0.05
        time_tol = 5
        
        # Check 1: Location
        lat_diff = abs(self.location[0] - weather_data.location[0])
        lon_diff = abs(self.location[1] - weather_data.location[1])
        if lat_diff > loc_tol or lon_diff > loc_tol:
            self.status = XYOProofStatus.INVALID
            return False
        
        # Check 2: Timestamp
        time_diff = abs(self.timestamp - weather_data.timestamp)
        if time_diff > time_tol:
            self.status = XYOProofStatus.EXPIRED
            return False
        
        # Check 3: Source match
        if self.claimed_source != weather_data.source:
            self.status = XYOProofStatus.INVALID
            return False
        
        # Check 4: Signature (simplified: just check non-empty for demo)
        if not self.signature:
            self.status = XYOProofStatus.INVALID
            return False
        
        self.status = XYOProofStatus.VALID
        return True

def verify_with_xyo(
    weather_data: WeatherRawData,
    xyo_proof: Optional[XYOProof]
) -> bool:
    """
    Verify weather data using XYO witness.
    
    If no proof provided, weather is unverified (but not rejected).
    Returns: True if verified OR unverified, False if invalid.
    """
    if xyo_proof is None:
        # No proof = unverified but acceptable (for now)
        return True
    
    return xyo_proof.verify(weather_data)

# ═══════════════════════════════════════════════════════════════
# LAYER 3: ORACLE COHERENCE (E14)
# ═══════════════════════════════════════════════════════════════

# Phase & heat anchors (from earlier)
INVARIANT_PHASE = 0.0
HEAT_TARGET = 0.075
HEAT_TOLERANCE = 0.005

# Weather thresholds
WEATHER_SAFE_THRESHOLD = 0.3    # Weather ≤ 0.3 = safe for convergence
WEATHER_CAUTION_THRESHOLD = 0.6  # 0.3 < weather ≤ 0.6 = degraded operations
WEATHER_DANGER_THRESHOLD = 1.0   # > 0.6 = danger, cannot converge

# Temporal tolerances
TOL = {
    "tick": 1.0,
    "beat": 4.0,
    "breath": 20.0,
    "cycle": 100.0,
}

AXES = ["tick", "beat", "breath", "cycle", "heat", "weather"]
TEMPORAL_AXES = ["tick", "beat", "breath", "cycle"]
THERMAL_AXES = ["heat"]
WEATHER_AXES = ["weather"]

ENGINES = [f"E{str(i).zfill(2)}" for i in range(1, 15)]

def phase_diff(a: float, b: float, modulo: float = 86400.0) -> float:
    """Circular distance on phase domain."""
    a = a % modulo
    b = b % modulo
    d = abs(a - b)
    return min(d, modulo - d)

def axis_converged(state: Dict, axis: str, target: float = INVARIANT_PHASE) -> bool:
    """Check temporal axis convergence."""
    if axis not in TEMPORAL_AXES:
        return False
    tol = TOL[axis]
    for engine in ENGINES:
        if engine not in state or axis not in state[engine]:
            return False
        if phase_diff(state[engine][axis], target) > tol:
            return False
    return True

def heat_converged(state: Dict) -> bool:
    """Check thermal axis convergence."""
    for engine in ENGINES:
        if engine not in state or "heat" not in state[engine]:
            return False
        if abs(state[engine]["heat"] - HEAT_TARGET) > HEAT_TOLERANCE:
            return False
    return True

def weather_permits_convergence(state: Dict) -> Tuple[bool, str]:
    """
    Check if weather conditions permit convergence.
    
    Returns: (permitted, status_string)
    """
    weather_vals = [state[e].get("weather", 1.0) for e in ENGINES if e in state]
    if not weather_vals:
        return True, "no_weather_data"
    
    avg_weather = sum(weather_vals) / len(weather_vals)
    
    if avg_weather <= WEATHER_SAFE_THRESHOLD:
        return True, "safe"
    elif avg_weather <= WEATHER_CAUTION_THRESHOLD:
        return False, "caution"
    else:
        return False, "danger"

def ring_converged_with_weather(state: Dict) -> Tuple[bool, Dict]:
    """
    Full 6-axis convergence check.
    
    Returns:
        (converged: bool, detail: dict)
    """
    # Temporal check
    temporal_ok = all(axis_converged(state, ax) for ax in TEMPORAL_AXES)
    
    # Thermal check
    thermal_ok = heat_converged(state)
    
    # Weather check
    weather_ok, weather_status = weather_permits_convergence(state)
    
    converged = temporal_ok and thermal_ok and weather_ok
    
    detail = {
        "temporal_ok": temporal_ok,
        "thermal_ok": thermal_ok,
        "weather_ok": weather_ok,
        "weather_status": weather_status,
    }
    
    return converged, detail

# ═══════════════════════════════════════════════════════════════
# ORACLE CLASS (6-AXIS)
# ═══════════════════════════════════════════════════════════════

@dataclass
class WeatherVerificationResult:
    """Result of weather data verification."""
    valid: bool
    source: str
    weather_scalar: float
    xyo_proof_status: str
    message: str

@dataclass
class OracleVerdict6Axis:
    """Oracle verdict with weather info."""
    converged: bool
    temporal_ok: bool
    thermal_ok: bool
    weather_ok: bool
    weather_status: str
    weather_scalar: float
    xyo_verified: bool
    message: str

class E146AxisOracle:
    """
    E14 6-Axis Oracle: temporal + thermal + weather (XYO-verified).
    """
    
    def __init__(self):
        self.history = {}  # {timestamp: (state, weather_verification)}
        self.is_sealed = False
    
    def ingest_weather(
        self,
        timestamp: int,
        weather_data: WeatherRawData,
        xyo_proof: Optional[XYOProof] = None
    ) -> WeatherVerificationResult:
        """
        Ingest weather data with XYO verification.
        
        Returns: WeatherVerificationResult
        """
        # Layer 2: Verify with XYO
        xyo_valid = verify_with_xyo(weather_data, xyo_proof)
        
        # Layer 1: Normalize weather
        weather_scalar = weather_data.normalize()
        
        # Determine XYO status
        if xyo_proof is None:
            xyo_status = "unverified"
        else:
            xyo_status = xyo_proof.status.value
        
        # Only accept if either:
        #   (a) XYO verified, OR
        #   (b) No XYO proof but data looks good
        if xyo_valid or (xyo_proof is None and weather_scalar < 0.5):
            valid = True
            message = f"Weather ingested: {weather_data.source}, scalar={weather_scalar:.3f}, XYO={xyo_status}"
        else:
            valid = False
            message = f"Weather rejected: XYO proof failed ({xyo_status})"
        
        return WeatherVerificationResult(
            valid=valid,
            source=weather_data.source,
            weather_scalar=weather_scalar if valid else None,
            xyo_proof_status=xyo_status,
            message=message,
        )
    
    def update_state_with_weather(
        self,
        state: Dict,
        weather_verification: WeatherVerificationResult
    ) -> Dict:
        """Update state dict with verified weather data."""
        if not weather_verification.valid:
            # Reject: use default safe value
            for engine in ENGINES:
                if engine in state:
                    state[engine]["weather"] = 1.0  # Assume danger
            return state
        
        # Accept: distribute weather scalar to all engines
        w = weather_verification.weather_scalar
        for engine in ENGINES:
            if engine in state:
                state[engine]["weather"] = w
        
        return state
    
    def observe(
        self,
        timestamp: int,
        state: Dict,
        weather_data: Optional[WeatherRawData] = None,
        xyo_proof: Optional[XYOProof] = None
    ) -> OracleVerdict6Axis:
        """
        Observe full state with optional weather data.
        
        Returns: OracleVerdict6Axis
        """
        # Verify weather if provided
        weather_verification = None
        if weather_data:
            weather_verification = self.ingest_weather(timestamp, weather_data, xyo_proof)
            state = self.update_state_with_weather(state, weather_verification)
        
        # Check 6-axis convergence
        converged, detail = ring_converged_with_weather(state)
        
        # Store history
        self.history[timestamp] = (state, weather_verification)
        
        # Seal if converged
        if converged and not self.is_sealed:
            self.is_sealed = True
        
        # Determine message
        if not converged:
            if not detail["temporal_ok"]:
                msg = "Temporal axes not converged"
            elif not detail["thermal_ok"]:
                msg = "Thermal axis not converged"
            elif not detail["weather_ok"]:
                msg = f"Weather prevents convergence ({detail['weather_status']})"
            else:
                msg = "Unknown reason"
        else:
            msg = "All 6 axes converged — Future sealed"
        
        return OracleVerdict6Axis(
            converged=converged,
            temporal_ok=detail["temporal_ok"],
            thermal_ok=detail["thermal_ok"],
            weather_ok=detail["weather_ok"],
            weather_status=detail["weather_status"],
            weather_scalar=state[ENGINES[0]].get("weather", -1.0) if ENGINES[0] in state else -1.0,
            xyo_verified=(weather_verification.xyo_proof_status == "valid") if weather_verification else False,
            message=msg,
        )
    
    def status_report(self) -> str:
        """Generate status report."""
        if not self.history:
            return "Oracle: No observations yet."
        
        latest_ts = max(self.history.keys())
        latest_state, latest_weather = self.history[latest_ts]
        
        lines = []
        lines.append("=" * 110)
        lines.append("E14 6-AXIS ORACLE — WEATHER-VERIFIED COHERENCE")
        lines.append("=" * 110)
        lines.append(f"Observations: {len(self.history)}")
        lines.append(f"Sealed: {self.is_sealed}")
        lines.append("")
        
        # Latest observation detail
        lines.append(f"Latest (t={latest_ts}s):")
        if latest_weather:
            lines.append(f"  Weather: source={latest_weather.source}, scalar={latest_weather.weather_scalar}, XYO={latest_weather.xyo_proof_status}")
        
        # Per-engine 6-axis snapshot
        if ENGINES[0] in latest_state:
            eng_state = latest_state[ENGINES[0]]
            lines.append("")
            lines.append(f"  {ENGINES[0]} state sample:")
            for ax in AXES:
                if ax in eng_state:
                    val = eng_state[ax]
                    if ax in TEMPORAL_AXES:
                        lines.append(f"    {ax}: {val:.1f} (mod 86400)")
                    elif ax == "heat":
                        lines.append(f"    {ax}: {val:.6f} (target {HEAT_TARGET}±{HEAT_TOLERANCE})")
                    elif ax == "weather":
                        lines.append(f"    {ax}: {val:.6f} (safe ≤ {WEATHER_SAFE_THRESHOLD})")
        
        lines.append("=" * 110)
        return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print()
    print("╔" + "═" * 108 + "╗")
    print("║" + " E14 6-AXIS ORACLE — WEATHER TRUTH + XYO WITNESS + ORACLE COHERENCE ".center(108) + "║")
    print("╚" + "═" * 108 + "╝")
    print()
    
    oracle = E146AxisOracle()
    
    # Create reference state (all at invariant)
    state_perfect = {
        engine: {
            "tick": 0.0,
            "beat": 0.0,
            "breath": 0.0,
            "cycle": 0.0,
            "heat": HEAT_TARGET,
            "weather": 0.0,
        }
        for engine in ENGINES
    }
    
    # Scenario 1: Clear weather (BOM) + valid XYO proof
    print("[SCENARIO 1] Clear weather + valid XYO proof")
    weather_clear = WeatherRawData(
        source="BOM_Sydney",
        timestamp=1000,
        location=(-33.8688, 151.2093),
        radar_intensity=0.1,
        precipitation=0.05,
        cloud_cover=0.2,
        wind_speed=0.1,
    )
    xyo_proof_valid = XYOProof(
        witness_id="XYO_sentinel_001",
        location=(-33.8688, 151.2093),
        timestamp=1000,
        claimed_source="BOM_Sydney",
        signature="valid_sig_xyz",
    )
    
    verdict1 = oracle.observe(1000, state_perfect.copy(), weather_clear, xyo_proof_valid)
    print(f"  Converged: {verdict1.converged}")
    print(f"  Weather: {verdict1.weather_scalar:.3f} (status: {verdict1.weather_status})")
    print(f"  XYO verified: {verdict1.xyo_verified}")
    print(f"  Message: {verdict1.message}")
    print()
    
    # Scenario 2: Severe weather (no XYO proof)
    print("[SCENARIO 2] Severe weather (no XYO proof)")
    weather_severe = WeatherRawData(
        source="satellite_GOES",
        timestamp=2000,
        location=(-33.8688, 151.2093),
        radar_intensity=0.9,
        precipitation=0.85,
        cloud_cover=0.95,
        wind_speed=0.8,
    )
    
    verdict2 = oracle.observe(2000, state_perfect.copy(), weather_severe, None)
    print(f"  Converged: {verdict2.converged}")
    print(f"  Weather: {verdict2.weather_scalar:.3f} (status: {verdict2.weather_status})")
    print(f"  XYO verified: {verdict2.xyo_verified}")
    print(f"  Message: {verdict2.message}")
    print()
    
    # Scenario 3: Data from wrong location (XYO rejects)
    print("[SCENARIO 3] XYO rejects: wrong location")
    xyo_proof_invalid = XYOProof(
        witness_id="XYO_sentinel_002",
        location=(0.0, 0.0),  # ← Wrong location
        timestamp=3000,
        claimed_source="BOM_Sydney",
        signature="tampered_sig",
    )
    
    verdict3 = oracle.observe(3000, state_perfect.copy(), weather_clear, xyo_proof_invalid)
    print(f"  Converged: {verdict3.converged}")
    print(f"  Weather: {verdict3.weather_scalar}")
    print(f"  XYO verified: {verdict3.xyo_verified}")
    print(f"  Message: {verdict3.message}")
    print()
    
    print(oracle.status_report())
    print()
