# Windows Setup Checklist for ESP32 + Docker

## Pre-Flight Checklist

- [ ] Windows 10 or 11
- [ ] Docker Desktop installed and running
- [ ] USB cable for ESP32 (data cable, not charge-only)
- [ ] ESP32 development board (ESP32-DevKit-C or similar)
- [ ] WiFi router accessible

## Step-by-Step Setup

### Phase 1: Tools Installation (30 minutes)

- [ ] **Arduino IDE 2.x**
  - Download: https://www.arduino.cc/en/software
  - Install and launch
  - Click through welcome screen

- [ ] **ESP32 Board Package**
  - Tools → Preferences
  - Paste: `https://dl.espressif.com/dl/package_esp32_index.json`
  - OK
  - Tools → Board Manager
  - Search "ESP32" → Install (Espressif Systems)
  - Wait 2-3 minutes

- [ ] **USB Driver**
  - Plug ESP32 into USB
  - Wait 3 seconds
  - Check Device Manager (Win+X → Device Manager)
  - Under "Ports (COM & LPT)" should show USB device
  - If shows "CH340" or error: Download driver
    - CH340: https://sparks.gogo.co.nz/ch340.html
    - CP2102: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
  - Extract .zip → Right-click .inf → Install
  - Restart Windows

### Phase 2: Network Configuration (5 minutes)

- [ ] **Get Host Machine IP**
  - Open PowerShell (Win+X → Windows PowerShell)
  - Type: `ipconfig`
  - Find "IPv4 Address" for your WiFi (e.g., 192.168.1.100)
  - **Write it down: ________________**

- [ ] **Open MQTT Firewall Port**
  - Windows Defender Firewall → Advanced Settings
  - Inbound Rules → New Rule
  - Port → TCP → 1883
  - Allow connection
  - All profiles checked
  - Name: "MQTT 1883"

### Phase 3: Docker Setup (5 minutes)

- [ ] **Docker Desktop Running**
  - Start Docker Desktop
  - Wait for "Docker is running"

- [ ] **Start Containers**
  - Open PowerShell
  - Navigate to project folder: `cd C:\path\to\project`
  - Type: `docker compose up -d`
  - Wait 10 seconds
  - Type: `docker ps` (verify mqtt_broker and esp32_bridge showing)

- [ ] **Test Setup**
  - PowerShell: `powershell -ExecutionPolicy Bypass -File test_setup.ps1`
  - All checks should show ✓

### Phase 4: Arduino Sketch Configuration (10 minutes)

- [ ] **Create Sketch**
  - Arduino IDE → File → New
  - Copy entire code from `esp32_sketch.ino` (see ESP32_WINDOWS_SETUP.md)

- [ ] **Configure WiFi**
  - Find line: `const char* ssid = "YOUR_WIFI_SSID";`
  - Replace `YOUR_WIFI_SSID` with your WiFi network name (exact spelling, case-sensitive)
  - Example: `const char* ssid = "Netgear_5G";`

- [ ] **Configure Password**
  - Find line: `const char* password = "YOUR_WIFI_PASSWORD";`
  - Replace with actual password
  - Example: `const char* password = "MyPassword123!";`

- [ ] **Configure MQTT Server IP**
  - Find line: `const char* mqtt_server = "192.168.1.100";`
  - Replace `192.168.1.100` with your Host Machine IP from ipconfig above
  - Example: `const char* mqtt_server = "192.168.1.42";`

- [ ] **Save Sketch**
  - File → Save As
  - Filename: `ESP32_MQTT_Sensor`
  - Choose a folder (e.g., Desktop)

### Phase 5: Flash to ESP32 (15 minutes)

- [ ] **Connect ESP32**
  - Plug ESP32 into USB port on Windows
  - Wait 2-3 seconds (driver loads)
  - Arduino IDE bottom toolbar should show COM port

- [ ] **Select Board & Port**
  - Tools → Board → Search "ESP32 Dev Module"
  - Tools → Port → Select your COM port (e.g., COM3)
  - If no port appears: reinstall USB driver

- [ ] **Upload Sketch**
  - Click Upload button (→ arrow)
  - Wait for "Connecting..."
  - If times out, hold BOOT button on ESP32 during upload
  - Watch for "Leaving... Hard resetting via RTS pin"

- [ ] **Verify Serial Monitor**
  - Tools → Serial Monitor (Ctrl+Shift+M)
  - Baud rate: 115200 (bottom right dropdown)
  - Should see:
    ```
    === ESP32 MQTT Sensor Client ===
    Connecting to WiFi: [Your SSID]
    .....
    ✓ WiFi connected!
    IP: 192.168.1.xxx
    
    Attempting MQTT connection to 192.168.1.xxx:1883
    ✓ MQTT connected!
    
    Published [5s]: {"temp":24.5,"humidity":48.2,...}
    ```

### Phase 6: End-to-End Verification (5 minutes)

- [ ] **ESP32 Serial Monitor Shows Messages**
  - Keep Arduino Serial Monitor open
  - Messages appear every 5 seconds
  - Check: temperature/humidity changing slightly

- [ ] **Docker Bridge Receiving**
  - PowerShell: `docker logs esp32_bridge`
  - Should show:
    ```
    [ESP32] Connected to MQTT broker mqtt_broker:1883
    [ESP32] RX esp32/sensors/data: {'temp': XX, 'humidity': XX, ...}
    [ESP32] Sealed to XYO: esp32/sensors/data
    ```

- [ ] **Real-time Log Monitoring**
  - PowerShell: `docker logs -f esp32_bridge`
  - Watch messages appear every 5 seconds
  - Press Ctrl+C to stop

### Phase 7: Production Setup (Optional)

- [ ] **Auto-Start on Boot**
  - Create shortcut to `manage.bat` on Desktop
  - Right-click → Properties
  - Advanced... → Check "Run as administrator"
  - Use for quick container management

- [ ] **Disable Sleep**
  - Settings → System → Power
  - Screen: Never
  - Sleep: Never
  - (Keeps Docker containers running)

- [ ] **Monitor Logs**
  - Open PowerShell
  - Type: `docker logs -f esp32_bridge`
  - Leave running in background
  - Data streams in real-time

## Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| Arduino IDE shows no COM port | Reinstall USB driver (CH340/CP2102) |
| ESP32 upload times out | Hold BOOT button while uploading |
| WiFi connection fails (Serial) | Check SSID/password spelling in sketch, verify 2.4GHz |
| MQTT connection fails (Serial) | Verify Host Machine IP correct, check firewall port 1883 |
| Docker shows no messages | Run `docker logs esp32_bridge`, check containers running |
| Firewall blocking MQTT | Windows Defender → Allow port 1883 inbound |
| Can't find USB device in Device Manager | Try different USB cable, different USB port, restart Arduino IDE |

## Files Location

```
Project Folder
├── docker-compose.yml          (Container config)
├── esp32_sketch.ino            (Arduino code - reference)
├── esp32_bridge.py             (Bridge service - running in Docker)
├── Dockerfile                  (Bridge container definition)
├── requirements.txt            (Python dependencies)
├── config/
│   ├── mosquitto.conf         (MQTT config)
│   └── .env.lock              (Environment variables)
├── logs/
│   ├── esp32_bridge.log       (Bridge logs)
│   └── mosquitto/             (MQTT logs)
├── ESP32_WINDOWS_SETUP.md     (This Windows guide)
├── test_setup.ps1             (PowerShell test)
└── manage.bat                 (Batch file manager)
```

## Quick Command Reference

```powershell
# Get your IP
ipconfig

# Start Docker
docker compose up -d

# Stop Docker
docker compose down

# Check containers
docker ps

# View Bridge logs
docker logs esp32_bridge

# View MQTT logs
docker logs mqtt_broker

# Real-time logs
docker logs -f esp32_bridge

# Restart all
docker compose restart

# View specific logs with timestamps
docker logs --timestamps esp32_bridge

# Test MQTT (if mosquitto-clients installed)
mosquitto_pub -h localhost -t esp32/sensors/data -m '{"temp":25}'
```

## What's Running

- **MQTT Broker** (Mosquitto): Listens on `localhost:1883`
- **ESP32 Bridge** (Python): Subscribes to MQTT, forwards to XYO
- **Your ESP32** (Hardware): Publishes temperature/humidity/motion every 5 seconds

## Data Flow

```
ESP32 (WiFi)
   ↓ MQTT publish
MQTT Broker (Docker, port 1883)
   ↓ subscribe
ESP32 Bridge (Docker, Python)
   ↓ POST request
XYO Oracle (http://localhost:8004/seal)
   ↓
Witness Network
```

## Success Indicators

✓ Arduino Serial Monitor shows messages every 5 seconds  
✓ `docker logs esp32_bridge` shows "Connected to MQTT"  
✓ `docker logs esp32_bridge` shows "RX esp32/sensors/data"  
✓ `docker logs esp32_bridge` shows "Sealed to XYO"  
✓ No errors in PowerShell when running containers  

## Support

- Arduino IDE docs: https://docs.arduino.cc/
- ESP32 docs: https://docs.espressif.com/projects/esp-idf/
- Docker docs: https://docs.docker.com/
- MQTT: https://mosquitto.org/

---

**Status**: Ready for deployment
**Estimated total setup time**: 1-2 hours (mostly waiting for downloads)
