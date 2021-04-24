#!/usr/bin/python3
import time
from vilib import Vilib
import cv2
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
# Vilib.color_detect_switch(True)
# Vilib.detect_color_name('blue')

while True:
    last = Vilib.front_view_img
    frame = cv2.imread(last)
    time.sleep(0.25)

