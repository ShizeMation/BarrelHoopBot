from mss import mss
from time import time
import cv2 as cv
import numpy as np
import pydirectinput as di
import pynput.keyboard as kb

STOP_KEY = 'k'
TOGGLE_KEY = 'f'
KICK_KEY = 'e'

LEFT_TEMPLATE = cv.cvtColor(cv.imread('assets/left.png'), cv.COLOR_BGRA2GRAY)
MIDDLE_TEMPLATE = cv.cvtColor(cv.imread('assets/middle.png'), cv.COLOR_BGRA2GRAY)
RIGHT_TEMPLATE = cv.cvtColor(cv.imread('assets/right.png'), cv.COLOR_BGRA2GRAY)

LEFT_DIM = {"top": 626, "left": 462, "width": 27, "height": 27}
MIDDLE_DIM = {"top": 629, "left": 744, "width": 27, "height": 27}

MATCH_METHOD = cv.TM_SQDIFF_NORMED

runProgram = True
runBot = True

def stop():
    global runProgram
    runProgram = False

def toggle():
    global runBot
    runBot = not runBot

listener = kb.GlobalHotKeys({
    STOP_KEY: stop,
    TOGGLE_KEY: toggle
})
listener.start()

state = "waiting"
delay = 0

right_dim = {"top": 608, "left": 0, "width": 19, "height": 19}

with mss() as sct:
    while (runProgram):
        if (runBot):
            match state:
                case "waiting":
                    leftSS = cv.cvtColor(np.array(sct.grab(LEFT_DIM)), cv.COLOR_BGRA2GRAY)
                    resLeft = cv.matchTemplate(leftSS, LEFT_TEMPLATE, MATCH_METHOD)
                    if (cv.minMaxLoc(resLeft)[0] < 0.2):
                        delay = time()
                        print("Started timing")
                        state = "timing"
                case "timing":
                    middleSS = cv.cvtColor(np.array(sct.grab(MIDDLE_DIM)), cv.COLOR_BGRA2GRAY)
                    resMiddle = cv.matchTemplate(middleSS, MIDDLE_TEMPLATE, MATCH_METHOD)
                    if (cv.minMaxLoc(resMiddle)[0] < 0.05):
                        delay = time() - delay
                        print(f"Finished timing: {delay}")
                        if (delay < 0.5):
                            right_dim["left"] = 1155
                        elif (delay < 0.6):
                            right_dim["left"] = 1200
                        elif (delay < 0.65):
                            right_dim["left"] = 1315
                        else:
                            right_dim["left"] = 1320
                        state = "kicking"
                case "kicking":
                    rightSS = cv.cvtColor(np.array(sct.grab(right_dim)), cv.COLOR_BGRA2GRAY)
                    resRight = cv.matchTemplate(rightSS, RIGHT_TEMPLATE, MATCH_METHOD)
                    if (cv.minMaxLoc(resRight)[0] < 0.2):
                        di.press(KICK_KEY)
                        print("Kicked")
                        state = "waiting"
