import time
from ezblock import __reset_mcu__
__reset_mcu__()
time.sleep(0.01)

import picarx_improved as car

time.sleep(0.01)

car.set_dir_servo_angle(60)

#car.dir_servo_angle_calibration()

