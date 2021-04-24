#!/usr/bin/python3
import time
import sys
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

# start streaming
Vilib.camera_start(True)
time.sleep(3)

while True:
    # get image
    last = Vilib.img_array[0]
    cv2.imshow("last", last)
    cv2.waitKey()
    cv2.destroyAllWindows()
    # frame = cv2.imread(last)
    # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #
    # # blue mask
    # lower_blue = np.array([60, 40, 40])
    # upper_blue = np.array([150, 255, 255])
    # mask = cv2.inRange(hsv, lower_blue, upper_blue)
    #
    # # canny
    # edges = cv2.Canny(mask, 200, 400)
    # logging.debug(edges)

    time.sleep(1)

