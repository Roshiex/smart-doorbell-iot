from sense_hat import SenseHat
from signal import pause

sense = SenseHat()

def pressed(event):
    if event.action == "pressed":
        print("Button pressed!")

sense.stick.direction_middle = pressed

pause()
