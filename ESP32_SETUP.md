# ESP32 Integration with Docker MQTT Bridge

## System Architecture

```
ESP32 (WiFi)
    ↓ MQTT
[MQTT Broker] 1883/TCP (docker network)
    ↓
[ESP32 Bridge Service] (Python paho-mqtt)
    ↓
[XYO Oracle] (localhost:8004/seal)
```

## Setup Steps

### 1. Flash ESP32 Sketch

1. Open `esp32_sketch.ino` in Arduino IDE
2. Configure WiFi credentials:
   ```cpp
   const char* ssid = "YOUR_SSID";
   const char* password = "YOUR_PASSWORD";
   ```
3. Configure MQTT broker IP (your host machine):
   ```cpp
   const char* mqtt_server = "192.168.1.100";  // Get with: ipconfig (Windows) or ifconfig (Mac/Linux)
   ```
4. Install required Arduino libraries:
   - WiFi (built-in)
   - PubSubClient (Sketch → Include Library → Search "pubsublient")
   - ArduinoJson (Sketch → Include Library → Search "arduinojson")
5. Select Board: ESP32 Dev Module
6. Upload to ESP32

### 2. Verify MQTT Broker is Running

```bash
docker compose ps
# Should show mqtt_broker and esp32_bridge as "Up"
```

Check MQTT logs:
```bash
docker logs mqtt_broker
```

### 3. Verify ESP32 Bridge Connection

```bash
docker logs esp32_bridge
# Look for: "Connected to MQTT broker mqtt_broker:1883"
```

### 4. Test Message Flow

Option A: From container (automated test):
```bash
docker exec esp32_bridge python3 /app/test_mqtt.py
```

Option B: From ESP32 (physical device):
- ESP32 will connect to MQTT broker every 5 seconds (configured in sketch)
- Check logs: `docker logs esp32_bridge`
- Look for: `RX esp32/sensors/data: {...}`

Option C: Manual publish from host:
```bash
mosquitto_pub -h localhost -t esp32/sensors/data -m '{"temp":24.5,"humidity":50}'
```

### 5. Verify Data Sealing

Once ESP32 publishes, bridge logs should show:
```
RX esp32/sensors/data: {'temp': 23.5, 'humidity': 45.2, ...}
Sealed to XYO: esp32/sensors/data
```

## Configuration

### ESP32 Sensor Pins (esp32_sketch.ino)
- GPIO 34 (TEMP_PIN): Temperature sensor (ADC)
- GPIO 35 (HUM_PIN): Humidity sensor (ADC)
- GPIO 32 (MOTION_PIN): Motion/digital sensor

Adjust calibration in sketch:
```cpp
float temperature = (temp_raw / 4095.0) * 40.0;  // 0-40°C range
float humidity = (hum_raw / 4095.0) * 100.0;     // 0-100% range
```

### MQTT Topics

Publish from ESP32 to:
- `esp32/sensors/data` — Main sensor readings (temperature, humidity, motion, RSSI, uptime)
- `esp32/sensors/raw` — Optional: raw ADC values
- `esp32/status` — Optional: connection status

Subscribe in bridge to: `esp32/sensors/#` (all subtopics)

### Environment Variables (docker-compose.yml)

```yaml
environment:
  - MQTT_BROKER=mqtt_broker      # Container hostname
  - MQTT_PORT=1883               # MQTT standard port
  - MQTT_TOPIC=esp32/sensors/#   # Topic filter
  - XYO_ENDPOINT=http://localhost:8004/seal  # Witness endpoint
```

## Troubleshooting

### ESP32 won't connect to WiFi
- Check SSID and password in sketch
- Verify ESP32 is within WiFi range
- Check WiFi 2.4GHz (ESP32 doesn't support 5GHz)
- Serial monitor will show "WiFi connected!" when successful

### ESP32 connects but no MQTT messages
- Verify MQTT broker IP is correct (not container hostname)
- Check `docker logs mqtt_broker` for connection errors
- Verify port 1883 is open: `netstat -an | grep 1883`
- Test from container: `docker exec esp32_bridge python3 /app/test_mqtt.py`

### Bridge not receiving messages
- Check `docker logs esp32_bridge` for connection status
- Verify MQTT topic matches: should start with `esp32/sensors/`
- Confirm MQTT_TOPIC env var: `docker compose config | grep MQTT_TOPIC`

### Memory/Performance
- ESP32 RAM: ~320KB available (keep JSON payloads <512 bytes)
- MQTT publish interval: 5 seconds (adjust in sketch: `PUBLISH_INTERVAL`)
- If memory low, disable motion sensor or reduce sampling rate

## Docker Commands

Start services:
```bash
docker compose up -d
```

Stop services:
```bash
docker compose down
```

View real-time logs:
```bash
docker compose logs -f esp32_bridge
docker compose logs -f mqtt_broker
```

Test MQTT connectivity from container:
```bash
docker exec esp32_bridge python3 -c "import paho.mqtt.client as mqtt; print('MQTT OK')"
```

Rebuild after code changes:
```bash
docker compose up -d --build
```

## Advanced

### Add More Sensors
1. Add GPIO pin in `esp32_sketch.ino`
2. Read sensor data in `publishSensorData()`
3. Add to JSON payload
4. Adjust `DynamicJsonDocument` size if needed

### Authentication
1. Edit `config/mosquitto.conf`: remove `allow_anonymous true`
2. Add user/password authentication in mosquitto config
3. Update `esp32_sketch.ino`: 
   ```cpp
   client.setServer(mqtt_server, mqtt_port);
   client.connect("ESP32_SENSOR", mqtt_user, mqtt_password);
   ```
4. Update `esp32_bridge.py` MQTT credentials

### Network Bridge to Host
If ESP32 is on different network, expose MQTT outside Docker:
```yaml
ports:
  - "0.0.0.0:1883:1883"  # Listen on all interfaces
```

Then use host machine's external IP from ESP32.

## Files

- `esp32_sketch.ino` — Arduino sketch for ESP32 board
- `esp32_bridge.py` — Python MQTT listener (bridges to XYO)
- `config/mosquitto.conf` — MQTT broker config
- `docker-compose.yml` — Services orchestration
- `test_mqtt.py` — Manual MQTT test utility
