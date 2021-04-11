import picarx_improved as car
from ezblock import __reset_mcu__
import time

__reset_mcu__()
time.sleep(0.01)

car.forward(75)
time.sleep(10)
#car.dir_servo_angle_calibration()

