from sense_hat import SenseHat
from picamera2 import Picamera2
from datetime import datetime
import subprocess
import os
from signal import pause
from time import sleep

sense = SenseHat()
topic = "doorcam_roshie"

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()

sleep(2)

def take_photo():
    home = os.path.expanduser("~")
    filename = f"{home}/doorbell_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    picam2.capture_file(filename)
    print("Captured:", filename)

    subprocess.run([
        "curl",
        "-T",
        filename,
        f"https://ntfy.sh/{topic}"
    ])

def pressed(event):
    if event.action == "pressed":
        print("Doorbell pressed!")
        take_photo()

sense.stick.direction_middle = pressed

print("Doorbell ready. Press Sense HAT button.")
pause()

