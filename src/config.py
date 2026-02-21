from os import system
import numpy as np

movePoints = [19, 14]
moveDistanceTrigger = 0.04

cursorPoint = 12

pressPoints = [8, 4]
pressDistanceTrigger = 0.06

monitorResolution = (2560, 1440)

drawPointsNums = True


def mouseSetPoint(x: int, y: int):
    x = np.clip(x, 0, monitorResolution[0])
    y = np.clip(y, 0, monitorResolution[1])

    x = np.floor(x / 2)
    y = np.floor(y / 2)
    system(f"ydotool mousemove --absolute {x} {y}")


def mouseDown():
    system("ydotool click 0x40")


def mouseUp():
    system("ydotool click 0x80")
