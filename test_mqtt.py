#!/usr/bin/env python3
"""
Quick test: Publish a test message to MQTT from container
"""
import paho.mqtt.client as mqtt
import json
import time

broker = "mqtt_broker"
port = 1883
topic = "esp32/sensors/data"

client = mqtt.Client()
client.connect(broker, port, 60)

payload = {
    "temp": 23.5,
    "humidity": 45.2,
    "motion": 1,
    "rssi": -68,
    "uptime": 3600
}

client.publish(topic, json.dumps(payload))
print(f"Published to {topic}: {payload}")
client.disconnect()
