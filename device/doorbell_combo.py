from sense_hat import SenseHat
from picamera2 import Picamera2
from datetime import datetime
import time
import os
import json
import cv2
import numpy as np
import paho.mqtt.client as mqtt

# =========================
# CONFIG
# =========================
MQTT_BROKER = "localhost"
MQTT_TOPIC = "doorcam/events"
DEVICE_ID = "doorcam_01"

sense = SenseHat()

BLUE = (0, 0, 255)
OFF = (0, 0, 0)

# =========================
# MQTT SETUP
# =========================
client = mqtt.Client()
client.connect(MQTT_BROKER, 1883, 60)

def send_event(event_type, image_path=None):
    payload = {
        "device": DEVICE_ID,
        "type": event_type,
        "timestamp": datetime.now().isoformat(),
        "image": image_path
    }

    client.publish(MQTT_TOPIC, json.dumps(payload))
    print("MQTT sent:", payload)

# =========================
# CAMERA SETUP
# =========================
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (1280, 720)}))
picam2.start()

time.sleep(2)

# warm-up frames (IMPORTANT)
for _ in range(10):
    picam2.capture_array()
    time.sleep(0.1)

# =========================
# MOTION STATE
# =========================
prev_frame = None
MOTION_THRESHOLD = 3000   # tuned for your camera
motion_active = False
last_motion_time = 0
COOLDOWN = 3

def detect_motion(gray):
    global prev_frame

    if prev_frame is None:
        prev_frame = gray
        return 0

    diff = cv2.absdiff(prev_frame, gray)
    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]

    score = cv2.countNonZero(thresh)

    # smooth baseline (prevents stuck high values)
    prev_frame = cv2.addWeighted(gray, 0.05, prev_frame, 0.95, 0)

    return score

# =========================
# IMAGE CAPTURE
# =========================
def capture_image(prefix):
    home = os.path.expanduser("~")
    filename = f"{home}/doorbell_{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    picam2.capture_file(filename)
    return filename

# =========================
# BUTTON
# =========================
def button_pressed(event):
    if event.action == "pressed":
        print("Button pressed")

        sense.clear(BLUE)

        img = capture_image("button")
        send_event("button", img)

        time.sleep(2)
        sense.clear(OFF)

sense.stick.direction_middle = button_pressed

# =========================
# MAIN LOOP
# =========================
print("Doorbell running...")

while True:

    frame = picam2.capture_array()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
    score = detect_motion(gray)

    print("Motion score:", score)

    now = time.time()

    # =========================
    # MOTION DEBOUNCE LOGIC
    # =========================
    if score > MOTION_THRESHOLD and not motion_active:
        if now - last_motion_time > COOLDOWN:

            motion_active = True
            last_motion_time = now

            print("Motion detected")

            img = capture_image("motion")
            send_event("motion", img)

    elif score < MOTION_THRESHOLD:
        motion_active = False

    time.sleep(0.2)
