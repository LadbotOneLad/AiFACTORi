# ESP32 Setup on Windows — Complete Guide

## Prerequisites (Install in Order)

### 1. Arduino IDE 2.x
- Download: https://www.arduino.cc/en/software
- Run installer, accept defaults
- Launch Arduino IDE

### 2. ESP32 Board Support
In Arduino IDE:
1. Go to **File** → **Preferences**
2. In "Additional boards manager URLs", paste:
   ```
   https://dl.espressif.com/dl/package_esp32_index.json
   ```
3. Click **OK**
4. Go to **Tools** → **Board Manager**
5. Search "ESP32" → Click **Espressif Systems** → Install latest version
6. Wait ~2 minutes for download/install

### 3. USB Driver (if needed)
Most ESP32 boards use CH340 or CP2102 chip:
- **CH340**: Download from https://sparks.gogo.co.nz/ch340.html (Windows 10/11 driver)
- **CP2102**: Download from https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

Plug in ESP32 and Windows should auto-detect. If not:
1. Download driver for your chip
2. Extract .zip
3. Right-click .inf file → Install
4. Restart computer

## Get Your Network Info

**Open Command Prompt** (Win + R, type `cmd`):

```cmd
ipconfig
```

Find your WiFi adapter. Look for line:
```
IPv4 Address. . . . . . . . . . : 192.168.x.xxx
```

This is your **Host Machine IP**. You'll use it in the ESP32 sketch below.

Example: `192.168.1.100`

## Configure ESP32 Sketch

1. In Arduino IDE, go to **File** → **New**
2. Paste this code:

```cpp
/*
  ESP32 MQTT Sensor Client (Windows)
  WiFi + Temperature + Humidity + Motion
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ===== CONFIG: CHANGE THESE =====
const char* ssid = "YOUR_WIFI_SSID";           // Replace with your WiFi name
const char* password = "YOUR_WIFI_PASSWORD";   // Replace with WiFi password
const char* mqtt_server = "192.168.1.100";     // Replace with Host Machine IP from ipconfig
// ================================

const int mqtt_port = 1883;
const char* mqtt_user = "";
const char* mqtt_password = "";

WiFiClient espClient;
PubSubClient client(espClient);

// Sensor pins
const int TEMP_PIN = 34;    // Analog pin for temp sensor
const int HUM_PIN = 35;     // Analog pin for humidity sensor
const int MOTION_PIN = 32;  // Digital pin for motion sensor

unsigned long lastPublish = 0;
const unsigned long PUBLISH_INTERVAL = 5000;  // Every 5 seconds

void setup() {
  Serial.begin(115200);
  delay(100);
  
  pinMode(MOTION_PIN, INPUT);
  
  Serial.println("\n\n=== ESP32 MQTT Sensor Client ===");
  
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void setup_wifi() {
  delay(10);
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✓ WiFi connected!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("✗ WiFi connection FAILED");
    Serial.println("Check SSID and password in sketch");
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection to ");
    Serial.print(mqtt_server);
    Serial.print(":");
    Serial.println(mqtt_port);
    
    if (client.connect("ESP32_SENSOR")) {
      Serial.println("✓ MQTT connected!");
    } else {
      Serial.print("✗ MQTT failed, rc=");
      Serial.println(client.state());
      Serial.println("Retry in 5 seconds...");
      delay(5000);
    }
  }
}

void publishSensorData() {
  // Read raw ADC values
  int temp_raw = analogRead(TEMP_PIN);
  int hum_raw = analogRead(HUM_PIN);
  int motion = digitalRead(MOTION_PIN);
  
  // Convert to approximate values (adjust for your sensors)
  float temperature = (temp_raw / 4095.0) * 40.0;  // 0-40°C
  float humidity = (hum_raw / 4095.0) * 100.0;     // 0-100%
  
  // Create JSON
  DynamicJsonDocument doc(256);
  doc["temp"] = temperature;
  doc["humidity"] = humidity;
  doc["motion"] = motion;
  doc["rssi"] = WiFi.RSSI();
  doc["uptime"] = millis() / 1000;
  
  char buffer[256];
  serializeJson(doc, buffer);
  
  // Publish
  client.publish("esp32/sensors/data", buffer);
  
  Serial.print("Published [");
  Serial.print(lastPublish / 1000);
  Serial.print("s]: ");
  Serial.println(buffer);
}

void loop() {
  // Reconnect if needed
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Publish every 5 seconds
  unsigned long now = millis();
  if (now - lastPublish > PUBLISH_INTERVAL) {
    publishSensorData();
    lastPublish = now;
  }
}
```

3. **IMPORTANT**: Replace these 3 lines with YOUR values:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";           // Your WiFi network name
   const char* password = "YOUR_WIFI_PASSWORD";   // Your WiFi password
   const char* mqtt_server = "192.168.1.100";     // Your Host Machine IP
   ```

4. Save file as `ESP32_MQTT_Sensor.ino`

## Flash ESP32

### Connect ESP32 to Windows USB

1. Plug ESP32 into Windows machine via USB cable
2. Wait 2-3 seconds (driver install)
3. In Arduino IDE, go to **Tools** → **Board** → Select **ESP32 Dev Module**
4. Go to **Tools** → **Port** → Select your COM port (e.g., **COM3**)
   - If no port appears, check Device Manager (Win + X → Device Manager)
   - Look under "Ports (COM & LPT)" for "USB-SERIAL CH340" or similar

### Upload Sketch

1. Click **Upload** button (arrow icon) in Arduino IDE
2. Wait for "Connecting..." message
3. If stuck, hold **BOOT** button on ESP32 while uploading
4. Watch for "Leaving... Hard resetting via RTS pin"
5. Open **Tools** → **Serial Monitor** (Ctrl + Shift + M)
6. Set baud rate to **115200** (bottom right)

### Verify in Serial Monitor

You should see:
```
=== ESP32 MQTT Sensor Client ===
Connecting to WiFi: YOUR_SSID
.....
✓ WiFi connected!
IP: 192.168.1.xxx

Attempting MQTT connection to 192.168.1.100:1883
✓ MQTT connected!

Published [5s]: {"temp":24.5,"humidity":48.2,"motion":0,"rssi":-67,"uptime":5}
Published [10s]: {"temp":24.5,"humidity":48.1,"motion":1,"rssi":-67,"uptime":10}
...
```

**If WiFi fails:**
- Serial Monitor shows: `✗ WiFi connection FAILED`
- Check SSID and password spelling (case-sensitive)
- Verify WiFi is 2.4GHz (not 5GHz)
- Restart WiFi router

**If MQTT fails:**
- Serial Monitor shows: `✗ MQTT failed, rc=...`
- Check Host Machine IP is correct in sketch (ipconfig value)
- Verify Docker containers are running: `docker ps`
- Check firewall allows port 1883 (see below)

## Configure Windows Firewall for MQTT

If ESP32 can't connect to MQTT:

1. Open **Windows Defender Firewall** → **Advanced Settings**
2. Click **Inbound Rules** → **New Rule**
3. Select **Port** → **Next**
4. Select **TCP** → Port: **1883** → **Next**
5. Select **Allow the connection** → **Next**
6. Check all profiles (Domain, Private, Public) → **Next**
7. Name: "MQTT 1883" → **Finish**

## Verify Docker is Ready

On Windows, open PowerShell:

```powershell
docker ps
```

Should show:
```
CONTAINER ID   IMAGE                      STATUS         PORTS
xxx            eclipse-mosquitto:latest   Up 5 minutes   0.0.0.0:1883->1883/tcp
xxx            aifactori-esp32_bridge     Up 5 minutes
```

If containers not running:
```powershell
docker compose up -d
```

## Test End-to-End

### From Serial Monitor (ESP32 publishing)
1. Keep Serial Monitor open
2. Watch messages appear every 5 seconds
3. Should show: `Published [5s]: {"temp":...}`

### From Docker (Bridge receiving)
Open PowerShell:

```powershell
docker logs esp32_bridge
```

Should show:
```
[ESP32] Connected to MQTT broker mqtt_broker:1883
[ESP32] RX esp32/sensors/data: {'temp': 24.5, 'humidity': 48.2, ...}
[ESP32] Sealed to XYO: esp32/sensors/data
```

### Check Bridge is Processing
```powershell
docker logs -f esp32_bridge
```

(Press Ctrl+C to stop)

## Sensor Calibration

If readings are off, adjust constants in sketch:

```cpp
// For temperature sensor connected to TEMP_PIN
// Raw ADC value 0-4095 maps to 0-40°C
float temperature = (temp_raw / 4095.0) * 40.0;

// For humidity sensor connected to HUM_PIN  
// Raw ADC value 0-4095 maps to 0-100%
float humidity = (hum_raw / 4095.0) * 100.0;

// Adjust multiplier based on your actual sensor specs
// Example: If sensor spans 0-50°C:
// float temperature = (temp_raw / 4095.0) * 50.0;
```

## Troubleshooting

### "Port is grayed out in Arduino IDE"
- Restart Arduino IDE
- Check Device Manager for COM port
- Reinstall USB driver (CH340 or CP2102)

### "Upload fails / Timeout"
- Hold **BOOT** button while uploading
- Try different USB cable
- Try different USB port on computer
- Restart Arduino IDE

### "WiFi connects but MQTT fails"
1. Verify Host Machine IP is correct: `ipconfig` in PowerShell
2. Check firewall: **Windows Defender Firewall** → Allow port 1883
3. Verify Docker MQTT is running: `docker ps | findstr mqtt`
4. Test from computer: `mosquitto_sub -h localhost -t esp32/sensors/data`

### "Bridge shows no messages"
```powershell
docker logs esp32_bridge
```
- Should show: `Connected to MQTT broker mqtt_broker:1883`
- If shows error, restart: `docker compose restart esp32_bridge`

### "No sensor readings (all zeros)"
- Check GPIO pin numbers in sketch match your wiring
- Verify sensors are connected to correct pins (34, 35, 32)
- Test with Serial Monitor: `Serial.println(analogRead(34));`

## Next Steps

Once working:
1. Move ESP32 to deployment location
2. Keep powered via USB or battery
3. Monitor Docker logs periodically: `docker logs esp32_bridge`
4. Data is sealed to XYO witness network automatically
5. View logs: `.\logs\esp32_bridge.log`

## File Reference

- **esp32_sketch.ino** (Windows): Use the code block above
- **ESP32_SETUP.md**: Linux/Mac version (reference only)
- **docker-compose.yml**: Container config (auto-managed)
- **esp32_bridge.py**: Bridge service (running in Docker)

## Quick Reference Commands

PowerShell:
```powershell
# Check IP
ipconfig

# Check Docker
docker ps
docker logs esp32_bridge
docker compose up -d
docker compose down

# Find MQTT on network
netstat -an | findstr 1883

# Manual MQTT test (install mosquitto-clients first)
mosquitto_pub -h localhost -t esp32/sensors/data -m '{"temp":25}'
```

