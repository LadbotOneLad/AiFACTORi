# ESP32 + Docker on Windows — Quick Start (5 Minutes)

## Prerequisites Installed
- ✓ Docker Desktop (running)
- ✓ Arduino IDE 2.x
- ✓ ESP32 board package
- ✓ USB driver (CH340 or CP2102)

If not done: See **WINDOWS_CHECKLIST.md** first.

## 3 Steps to Deploy

### Step 1: Configure ESP32 Sketch (2 min)

1. Open Arduino IDE
2. File → New
3. Copy code from **esp32_sketch.ino**
4. Edit these 3 lines:
   ```cpp
   const char* ssid = "YOUR_SSID";              // Your WiFi name
   const char* password = "YOUR_PASSWORD";      // Your WiFi password
   const char* mqtt_server = "192.168.1.100";   // Your Host Machine IP (from: ipconfig)
   ```
5. File → Save As → `ESP32_MQTT_Sensor.ino`

### Step 2: Flash to ESP32 (2 min)

1. Plug ESP32 into USB
2. Arduino IDE:
   - Tools → Board → **ESP32 Dev Module**
   - Tools → Port → Select your **COM port**
3. Click **Upload** (→ arrow)
4. Open **Tools → Serial Monitor** (Ctrl+Shift+M)
5. Set baud rate to **115200** (bottom right)
6. You should see:
   ```
   ✓ WiFi connected!
   ✓ MQTT connected!
   Published [5s]: {"temp":24.5, ...}
   ```

### Step 3: Verify Docker (1 min)

Open PowerShell:

```powershell
cd C:\path\to\project
docker ps
```

Should show `mqtt_broker` and `esp32_bridge` as "Up".

If not running:
```powershell
docker compose up -d
```

Check logs:
```powershell
docker logs esp32_bridge
```

Should show:
```
[ESP32] Connected to MQTT broker mqtt_broker:1883
[ESP32] RX esp32/sensors/data: {'temp': XX, 'humidity': XX, ...}
[ESP32] Sealed to XYO: esp32/sensors/data
```

## Done

✓ ESP32 publishing sensor data  
✓ Docker receiving and sealing to XYO  
✓ System running 24/7  

## Manage Containers

**Windows Menu** (easiest):
```powershell
.\manage.bat
```
Choose 1-7 for options.

**PowerShell Commands**:
```powershell
docker compose up -d       # Start
docker compose down        # Stop
docker ps                  # Check status
docker logs -f esp32_bridge # Watch logs (Ctrl+C to exit)
```

## Troubleshooting

**Serial Monitor shows `✗ WiFi connection FAILED`**
→ Check SSID/password spelling (case-sensitive), verify 2.4GHz

**Serial Monitor shows `✗ MQTT failed`**
→ Check Host Machine IP is correct (ipconfig)
→ Check firewall allows port 1883

**Docker logs show no messages**
→ Verify Serial Monitor shows MQTT connected
→ Run: `docker logs esp32_bridge`

**No COM port in Arduino IDE**
→ Reinstall USB driver (CH340 or CP2102)
→ Try different USB cable/port
→ Restart Arduino IDE

## Files

| File | Purpose |
|------|---------|
| `WINDOWS_CHECKLIST.md` | Step-by-step setup (first time) |
| `ESP32_WINDOWS_SETUP.md` | Detailed configuration guide |
| `esp32_sketch.ino` | Arduino code for ESP32 |
| `manage.bat` | Easy container manager |
| `test_setup.ps1` | Verify setup is working |
| `docker-compose.yml` | Container configuration |

## Full Setup (First Time Only)

See **WINDOWS_CHECKLIST.md** for complete 1-2 hour setup with all tools.

---

**Status**: Ready  
**Next**: Flash your ESP32 and check Docker logs
