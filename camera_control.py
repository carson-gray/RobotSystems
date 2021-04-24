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

Vilib.camera_start(True)
time.sleep(3)

while True:
    resp = urlopen('http://raspberrypi.local:9000/mjpg')
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    logging.debug(image)
    time.sleep(1)

