#!/usr/bin/env python3
"""
ESP32 MQTT Bridge — Receives sensor data from ESP32 over WiFi/MQTT
Bridges to XYO witness network and local services
"""

import os
import json
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
import requests

# Config
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt_broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "esp32/sensors/#")
XYO_ENDPOINT = os.getenv("XYO_ENDPOINT", "http://e14_oracle:8004/seal")
LOG_FILE = "/app/logs/esp32_bridge.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ESP32] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ESP32Bridge:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.connected = False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info(f"Connected to MQTT broker {MQTT_BROKER}:{MQTT_PORT}")
            client.subscribe(MQTT_TOPIC)
        else:
            logger.error(f"MQTT connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            
            logger.info(f"RX {topic}: {payload}")
            
            # Forward to XYO witness
            self.seal_witness(topic, payload)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
        except Exception as e:
            logger.error(f"Message handler error: {e}")

    def seal_witness(self, topic, payload):
        """Post ESP32 data to XYO witness"""
        try:
            witness_data = {
                "source": "esp32",
                "topic": topic,
                "data": payload,
                "timestamp": datetime.utcnow().isoformat()
            }
            resp = requests.post(XYO_ENDPOINT, json=witness_data, timeout=5)
            if resp.status_code == 200:
                logger.info(f"Sealed to XYO: {topic}")
            else:
                logger.warning(f"XYO seal failed: {resp.status_code}")
        except Exception as e:
            logger.error(f"Witness seal error: {e}")

    def run(self):
        logger.info("ESP32 Bridge starting...")
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            self.client.loop_forever()
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise

if __name__ == "__main__":
    bridge = ESP32Bridge()
    bridge.run()
