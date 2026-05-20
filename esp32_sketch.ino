/*
  ESP32 MQTT Sensor Client
  Publishes temperature, humidity, and analog readings to MQTT broker
  Configure WiFi and MQTT settings below
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// MQTT broker settings
const char* mqtt_server = "YOUR_HOST_IP";  // e.g., 192.168.1.100 (host machine IP)
const int mqtt_port = 1883;
const char* mqtt_user = "";  // Leave empty if anonymous
const char* mqtt_password = "";

WiFiClient espClient;
PubSubClient client(espClient);

// Sensor pins
const int TEMP_PIN = 34;    // ADC pin for temperature sensor
const int HUM_PIN = 35;     // ADC pin for humidity sensor
const int MOTION_PIN = 32;  // Digital pin for motion sensor

unsigned long lastPublish = 0;
const unsigned long PUBLISH_INTERVAL = 5000;  // Publish every 5 seconds

void setup() {
  Serial.begin(115200);
  delay(100);
  
  pinMode(MOTION_PIN, INPUT);
  
  Serial.println("\n\nESP32 MQTT Sensor Client");
  
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
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
    Serial.println("WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Failed to connect WiFi");
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Handle incoming MQTT messages (optional)
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("]: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    if (client.connect("ESP32_SENSOR")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void publishSensorData() {
  // Read sensors
  int temp_raw = analogRead(TEMP_PIN);
  int hum_raw = analogRead(HUM_PIN);
  int motion = digitalRead(MOTION_PIN);
  
  // Convert raw to approximate values (adjust calibration for your sensors)
  float temperature = (temp_raw / 4095.0) * 40.0;  // 0-40°C range
  float humidity = (hum_raw / 4095.0) * 100.0;     // 0-100% range
  
  // Create JSON payload
  DynamicJsonDocument doc(256);
  doc["temp"] = temperature;
  doc["humidity"] = humidity;
  doc["motion"] = motion;
  doc["rssi"] = WiFi.RSSI();
  doc["uptime"] = millis() / 1000;
  
  char buffer[256];
  serializeJson(doc, buffer);
  
  // Publish to MQTT
  client.publish("esp32/sensors/data", buffer);
  Serial.print("Published: ");
  Serial.println(buffer);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastPublish > PUBLISH_INTERVAL) {
    publishSensorData();
    lastPublish = now;
  }
}
