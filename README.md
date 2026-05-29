#  Smart Doorbell IoT System

A Raspberry Pi-based smart doorbell camera system that detects motion and button presses, captures images, stores events, sends push notifications, and displays
 a live web dashboard.

---

## Architecture
Raspberry Pi (Device)
├── Sense HAT (button input)
├── Camera Module (image capture)
└── Motion Detection (OpenCV)
│
│ MQTT (doorcam/events)
▼
Mosquitto Broker (localhost)
│
▼
Backend Service (app.py)
├── Saves to SQLite database
└── Sends push notification (ntfy)
│
▼
Flask Dashboard (port 5000)
├── /api/events  → recent events JSON
├── /api/stats   → summary + daily counts
└── /image/<filename> → captured images

---

## Message Schema (MQTT)

Topic: `doorcam/events`

```json
{
  "device": "doorcam_01",
  "type": "motion",
  "timestamp": "2026-05-28T20:35:14.088822",
  "image": "/home/roshie/doorbell_motion_20260528_203514.jpg"
}
```

| Field | Type | Description |
|-------|------|-------------|
| device | string | Device identifier |
| type | string | `motion` or `button` |
| timestamp | string | ISO 8601 datetime |
| image | string | Path to captured image |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web dashboard |
| `/api/events` | GET | Last 50 events as JSON |
| `/api/stats` | GET | Total counts + daily chart data |
| `/image/<filename>` | GET | Serve captured image |

---

## Hardware

- Raspberry Pi 4
- Raspberry Pi Camera Module 3
- Sense HAT (joystick button + LED matrix)

---

## Software Stack

- Python 3
- Paho MQTT
- Mosquitto broker
- OpenCV (motion detection)
- SQLite (event storage)
- Flask (dashboard + API)
- ntfy.sh (push notifications)

---

## Setup

### 1. Install dependencies
```bash
pip3 install paho-mqtt flask opencv-python picamera2 requests --break-system-packages
sudo apt install mosquitto mosquitto-clients sqlite3 -y
```

### 2. Run the system (3 terminals)
```bash
# Terminal 1 - Backend
python3 ~/smart-doorbell-iot/backend/app.py

# Terminal 2 - Dashboard
python3 ~/smart-doorbell-iot/dashboard/app.py

# Terminal 3 - Device
python3 ~/smart-doorbell-iot/device/doorbell_combo.py
```

### 3. View dashboard
Open browser and go to: `http://<raspberry-pi-ip>:5000`

### 4. Push notifications
Install the ntfy app and subscribe to topic: `doorcam-roshie`

---

## Project Structure
smart-doorbell-iot/
├── backend/
│   └── app.py          # MQTT listener, DB writer, ntfy notifications
├── dashboard/
│   ├── app.py          # Flask API + web server
│   └── templates/
│       └── index.html  # Dashboard UI
├── device/
│   └── doorbell_combo.py  # Motion detection + button + camera
├── data/
│   └── doorcam.db      # SQLite database (gitignored)
└── README.md

---

## How It Works

1. The device continuously captures frames and compares them using OpenCV frame differencing
2. When motion exceeds the threshold (3000) or the Sense HAT button is pressed, an image is captured
3. The event is published to the MQTT broker as a JSON payload
4. The backend service receives the event, saves it to SQLite, and sends a push notification via ntfy
5. The dashboard polls `/api/events` and `/api/stats` every 10 seconds to display live updates

## Reflection
**What I'd do differently:**
- Deploy the dashboard to a cloud server so it is accessible remotely
- Add a proper WebSocket connection for instant dashboard updates
