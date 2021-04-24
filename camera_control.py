#!/usr/bin/python3
import time
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
from logdecorator import log_on_start, log_on_end, log_on_error
logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO,
                    datefmt="%H:%M:%S")
# comment out this line to disable logging
logging.getLogger().setLevel(logging.DEBUG)

import sys
sys.path.append(r'/opt/ezblock')
from vilib import Vilib

Vilib.camera_start(True)
Vilib.color_detect_switch(True)
Vilib.detect_color_name('red')

def forever():
  pass

if __name__ == "__main__":
    while True:
        forever()
