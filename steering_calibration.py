import picarx_improved as car
from ezblock import __reset_mcu__
__reset_mcu__()
import time

car.set_dir_servo_angle(0)
car.forward(100)
time.sleep(10)
#car.dir_servo_angle_calibration()

