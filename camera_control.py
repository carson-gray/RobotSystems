#!/usr/bin/python3
import time
import sys
import atexit
sys.path.append(r'/opt/ezblock')
from vilib import Vilib
from urllib.request import urlopen
import cv2
import numpy as np
try:
    from ezblock import *
    from ezblock import __reset_mcu__
    __reset_mcu__()
    time.sleep(0.02)
except ImportError:
    print("This computer does not appear to be a PiCar-X system"
          " (/opt/ezblock is not present). Shadowing hardware calls"
          " with substitute functions.")
    from sim_ezblock import *
from picarx_class import PicarX
import logging
logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO,
                    datefmt="%H:%M:%S")
# comment out this line to disable logging
logging.getLogger().setLevel(logging.DEBUG)


class CameraController:
    def __init__(self):
        # start streaming
        Vilib.camera_start(True)
        time.sleep(3)
        atexit.register(self.cleanup)

        self.lower_blue = np.array([60, 40, 40])
        self.upper_blue = np.array([150, 255, 255])

    def cleanup(self):
        Vilib.camera_start(False)

    def detect_edges(self):
        # get image
        frame = Vilib.img_array[0]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # blue edges
        mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        edges = cv2.Canny(mask, 200, 400)

        return edges


if __name__ == "main":
    picam = CameraController()
    while True:
        logging.debug(picam.detect_edges())
        time.sleep(1)
