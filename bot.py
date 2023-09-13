from os import path
from mss import mss
from time import time
import cv2 as cv
import numpy as np
import pydirectinput as di
import pynput.keyboard as kb

STOP_KEY = 'k'
TOGGLE_KEY = 'f'
KICK_KEY = 'e'

def imgpath(filename):
    filename = path.join('assets', filename)
    return path.abspath(path.join(path.dirname(__file__), filename))

LEFT_TEMPLATE = cv.cvtColor(cv.imread(imgpath('left.png')), cv.COLOR_BGRA2GRAY)
MIDDLE_TEMPLATE = cv.cvtColor(cv.imread(imgpath('middle.png')), cv.COLOR_BGRA2GRAY)
RIGHT_TEMPLATE = cv.cvtColor(cv.imread(imgpath('right.png')), cv.COLOR_BGRA2GRAY)

LEFT_DIM = {"top": 626, "left": 462, "width": 27, "height": 27}
MIDDLE_DIM = {"top": 629, "left": 744, "width": 27, "height": 27}

MATCH_METHOD = cv.TM_SQDIFF_NORMED

runProgram = True
runBot = False
state = "waiting"

def stop():
    global runProgram
    runProgram = False

def toggle():
    global runBot, state
    runBot = not runBot
    state = "waiting"

listener = kb.GlobalHotKeys({
    STOP_KEY: stop,
    TOGGLE_KEY: toggle
})
listener.start()

hoop_time = 0
kick_time = 0

right_dim = {"top": 608, "left": 0, "width": 19, "height": 19}

with mss() as sct:
    while (runProgram):
        if (runBot):
            match state:
                case "waiting":
                    leftSS = cv.cvtColor(np.array(sct.grab(LEFT_DIM)), cv.COLOR_BGRA2GRAY)
                    resLeft = cv.matchTemplate(leftSS, LEFT_TEMPLATE, MATCH_METHOD)
                    if (cv.minMaxLoc(resLeft)[0] < 0.2):
                        hoop_time = time()
                        print("Started timing")
                        state = "timing"
                case "timing":
                    middleSS = cv.cvtColor(np.array(sct.grab(MIDDLE_DIM)), cv.COLOR_BGRA2GRAY)
                    resMiddle = cv.matchTemplate(middleSS, MIDDLE_TEMPLATE, MATCH_METHOD)
                    if (cv.minMaxLoc(resMiddle)[0] < 0.05):
                        hoop_time = time() - hoop_time
                        print(f"  Finished timing: {hoop_time:.3f}")
                        if (hoop_time < 0.45):
                            right_dim["left"] = 1130
                        elif (hoop_time < 0.48):
                            right_dim["left"] = 1160
                        elif (hoop_time < 0.51):
                            right_dim["left"] = 1190
                        elif (hoop_time < 0.54):
                            right_dim["left"] = 1230
                        elif (hoop_time < 0.56):
                            right_dim["left"] = 1260
                        elif (hoop_time < 0.58):
                            right_dim["left"] = 1280
                        elif (hoop_time < 0.6):
                            right_dim["left"] = 1290
                        elif (hoop_time < 0.65):
                            right_dim["left"] = 1300
                        elif (hoop_time < 0.7):
                            right_dim["left"] = 1340
                        elif (hoop_time < 0.73):
                            right_dim["left"] = 1360
                        elif (hoop_time < 1):
                            right_dim["left"] = 1380
                        else:
                            print("    Kick cancelled: missed timing")
                            state = "waiting"
                            continue
                        state = "kicking"
                case "kicking":
                    rightSS = cv.cvtColor(np.array(sct.grab(right_dim)), cv.COLOR_BGRA2GRAY)
                    resRight = cv.matchTemplate(rightSS, RIGHT_TEMPLATE, MATCH_METHOD)
                    if (cv.minMaxLoc(resRight)[0] < 0.2):
                        if ((time() - kick_time) > 2.9):
                            di.press(KICK_KEY)
                            print(f"    Kicked on: {right_dim['left']}")
                            kick_time = time()
                        else:
                            print("    Kick cancelled: too fast")
                        state = "waiting"
