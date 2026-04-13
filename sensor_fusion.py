"""
SENSOR FUSION LAYER
Combines BOM radar data with local sensors.
Creates unified environmental dataset for XYO witnessing.
"""

import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("SensorFusion")

# ═══════════════════════════════════════════════════════════════
# LOCAL SENSOR DATA
# ═══════════════════════════════════════════════════════════════

class LocalSensor:
    """Individual local sensor reading."""
    
    def __init__(self, sensor_id: str, sensor_type: str, value: float, unit: str, timestamp: str = None):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type  # temperature, humidity, pressure, wind_speed, etc.
        self.value = value
        self.unit = unit
        self.timestamp = timestamp or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp,
        }

class LocalSensorArray:
    """Array of local sensors."""
    
    def __init__(self, location: str, latitude: float, longitude: float):
        self.location = location
        self.latitude = latitude
        self.longitude = longitude
        self.sensors = {}
        self.last_update = None
    
    def add_sensor(self, sensor: LocalSensor):
        """Add sensor to array."""
        self.sensors[sensor.sensor_id] = sensor
        self.last_update = datetime.now()
    
    def update_sensor(self, sensor_id: str, value: float):
        """Update sensor value."""
        if sensor_id in self.sensors:
            self.sensors[sensor_id].value = value
            self.sensors[sensor_id].timestamp = datetime.now().isoformat()
            self.last_update = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "sensors": {k: v.to_dict() for k, v in self.sensors.items()},
            "last_update": self.last_update.isoformat() if self.last_update else None,
        }

# ═══════════════════════════════════════════════════════════════
# SENSOR FUSION ENGINE
# ═══════════════════════════════════════════════════════════════

class SensorFusion:
    """Fuse BOM radar + local sensors into unified dataset."""
    
    def __init__(self):
        self.bom_data = None
        self.local_sensors = None
        self.fused_dataset = None
        self.fusion_count = 0
        self.data_hash = None
        
        logger.info("Sensor Fusion Engine initialized")
    
    def add_bom_data(self, bom_data):
        """Ingest BOM radar data."""
        self.bom_data = bom_data
        logger.info(f"✓ BOM data added: {bom_data}")
    
    def add_local_sensors(self, sensor_array: LocalSensorArray):
        """Ingest local sensor array."""
        self.local_sensors = sensor_array
        logger.info(f"✓ Local sensors added: {sensor_array.location} ({len(sensor_array.sensors)} sensors)")
    
    def fuse(self) -> Optional[Dict]:
        """
        Fuse BOM + local sensor data into unified dataset.
        
        Returns:
            Fused dataset dict with integrated readings
        """
        if not self.bom_data or not self.local_sensors:
            logger.warning("Cannot fuse: missing BOM data or local sensors")
            return None
        
        self.fused_dataset = {
            "timestamp": datetime.now().isoformat(),
            "fusion_id": f"FUSION_{self.fusion_count}",
            
            # BOM radar composite
            "bom_radar": {
                "product": self.bom_data.product,
                "radar_id": self.bom_data.radar_id,
                "coverage": self.bom_data.coverage,
                "reflectivity_samples": len(self.bom_data.reflectivity),
                "precipitation_samples": len(self.bom_data.precipitation),
                "velocity_samples": len(self.bom_data.velocity),
                "quality": self.bom_data.quality,
                "validity": self.bom_data.validity,
                "bom_data_hash": self.bom_data.data_hash,
                "bom_timestamp": self.bom_data.timestamp,
            },
            
            # Local sensor readings
            "local_sensors": self.local_sensors.to_dict(),
            
            # Integrated metrics
            "integrated_metrics": self._compute_integrated_metrics(),
        }
        
        # Compute fused dataset hash for XYO witnessing
        self.data_hash = self._compute_fused_hash()
        self.fused_dataset["fused_data_hash"] = self.data_hash
        
        self.fusion_count += 1
        
        logger.info(f"✓ Fusion complete: {self.fused_dataset['fusion_id']}")
        logger.info(f"  Data hash: {self.data_hash[:32]}...")
        
        return self.fused_dataset
    
    def _compute_integrated_metrics(self) -> Dict:
        """Compute integrated environmental metrics."""
        metrics = {
            "avg_reflectivity": sum(self.bom_data.reflectivity) / len(self.bom_data.reflectivity) if self.bom_data.reflectivity else 0,
            "avg_precipitation": sum(self.bom_data.precipitation) / len(self.bom_data.precipitation) if self.bom_data.precipitation else 0,
            "max_reflectivity": max(self.bom_data.reflectivity) if self.bom_data.reflectivity else 0,
            "max_precipitation": max(self.bom_data.precipitation) if self.bom_data.precipitation else 0,
        }
        
        # Add local sensor metrics
        if self.local_sensors:
            for sensor_id, sensor in self.local_sensors.sensors.items():
                metrics[f"local_{sensor.sensor_type}"] = sensor.value
        
        return metrics
    
    def _compute_fused_hash(self) -> str:
        """Compute hash of entire fused dataset for integrity."""
        dataset_str = json.dumps(self.fused_dataset, sort_keys=True)
        return hashlib.sha256(dataset_str.encode()).hexdigest()
    
    def get_fused_data(self) -> Optional[Dict]:
        """Get latest fused dataset."""
        return self.fused_dataset
    
    def get_data_hash(self) -> str:
        """Get hash of fused data (for XYO witnessing)."""
        return self.data_hash or ""
    
    def get_status(self) -> Dict:
        """Get fusion engine status."""
        return {
            "engine": "Sensor Fusion",
            "bom_data_available": self.bom_data is not None,
            "local_sensors_available": self.local_sensors is not None,
            "fusion_count": self.fusion_count,
            "latest_fused_hash": self.data_hash or "none",
            "fused_data": self.fused_dataset,
            "status": "OPERATIONAL",
        }

# ═══════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    
    print()
    print("╔" + "═" * 88 + "╗")
    print("║" + " SENSOR FUSION LAYER ".center(88) + "║")
    print("╚" + "═" * 88 + "╝")
    print()
    
    # Create sensor array
    print("[1] Creating local sensor array...")
    sensors = LocalSensorArray(
        location="Sydney, NSW",
        latitude=-33.8688,
        longitude=151.2093
    )
    
    sensors.add_sensor(LocalSensor("TEMP_01", "temperature", 22.5, "°C"))
    sensors.add_sensor(LocalSensor("HUMID_01", "humidity", 65.0, "%"))
    sensors.add_sensor(LocalSensor("PRESS_01", "pressure", 1013.25, "hPa"))
    sensors.add_sensor(LocalSensor("WIND_01", "wind_speed", 12.3, "m/s"))
    
    print(f"✓ Created sensor array with {len(sensors.sensors)} sensors")
    print()
    
    # Mock BOM data
    print("[2] Creating mock BOM radar data...")
    class MockBOMData:
        def __init__(self):
            self.product = "National Composite Reflectivity"
            self.radar_id = "IDR71B"
            self.coverage = "Australia"
            self.reflectivity = list(range(0, 80, 10))
            self.precipitation = list(range(0, 200, 20))
            self.velocity = list(range(-50, 50, 10))
            self.quality = 0.95
            self.validity = True
            self.data_hash = "abc123def456"
            self.timestamp = datetime.now().isoformat()
    
    bom_data = MockBOMData()
    print(f"✓ Created BOM data: {bom_data.product}")
    print()
    
    # Fuse
    print("[3] Fusing BOM + local sensors...")
    fusion = SensorFusion()
    fusion.add_bom_data(bom_data)
    fusion.add_local_sensors(sensors)
    fused = fusion.fuse()
    
    if fused:
        print("✓ Fusion successful")
        print()
        print("[4] Fused dataset:")
        print(f"  Fusion ID: {fused['fusion_id']}")
        print(f"  Timestamp: {fused['timestamp']}")
        print(f"  Data hash: {fused['fused_data_hash'][:32]}...")
        print(f"  BOM sensors: {fused['bom_radar']['reflectivity_samples']}")
        print(f"  Local sensors: {len(fused['local_sensors']['sensors'])}")
        print(f"  Metrics: {len(fused['integrated_metrics'])} integrated")
    else:
        print("✗ Fusion failed")
    
    print()
