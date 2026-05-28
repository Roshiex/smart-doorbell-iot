from picamera2 import Picamera2
from datetime import datetime
import os
import subprocess
from time import sleep

topic = "doorcam_roshie"

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()

sleep(2)

home = os.path.expanduser("~")
filename = f"{home}/doorbell_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

picam2.capture_file(filename)
picam2.stop()

print("Photo saved:", filename)

# Upload image + send notification in ONE step
subprocess.run([
    "curl",
    "-T",
    filename,
    f"https://ntfy.sh/{topic}"
])
