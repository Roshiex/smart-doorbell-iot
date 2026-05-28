import sqlite3
import json
import paho.mqtt.client as mqtt
from datetime import datetime
import os
import requests
# ---------------- MQTT ----------------
MQTT_BROKER = "localhost"
MQTT_TOPIC = "doorcam/events"

# ---------------- DATABASE ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "doorcam.db")

print("Using database:", DB_PATH)

# ---------------- CREATE DATABASE ----------------
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device TEXT,
    type TEXT,
    timestamp TEXT,
    image TEXT
)
""")

conn.commit()
conn.close()

# ---------------- MQTT CALLBACKS ----------------
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print("Event received:", payload)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO events (device, type, timestamp, image)
        VALUES (?, ?, ?, ?)
        """, (
            payload.get("device"),
            payload.get("type"),
            payload.get("timestamp"),
            payload.get("image")
        ))
        conn.commit()
        conn.close()
        print("Saved to database")

        # ---------------- NTFY NOTIFICATION ----------------
        event_type = payload.get("type", "event")
        title = "Doorbell Alert" if event_type == "button" else "Motion Detected"
        body = f"{event_type.capitalize()} detected at {payload.get('timestamp', '')[:19]}"
        try:
            requests.post(
                "https://ntfy.sh/doorcam-roshie",
                data=body,
                headers={"Title": title, "Priority": "high"},
                timeout=5
            )
            print("Notification sent")
        except Exception as ne:
            print("Ntfy error:", ne)

    except Exception as e:
        print("ERROR:", e)

# ---------------- MQTT CLIENT ----------------
client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, 1883, 60)

print("Backend running... listening for events")

client.loop_forever()
