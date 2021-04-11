import time
from ezblock import __reset_mcu__
__reset_mcu__()
time.sleep(0.01)

import picarx_improved as car

__reset_mcu__()
time.sleep(0.01)

car.set_dir_servo_angle(0)
time.sleep(0.1)
car.forward(30)
time.sleep(1)
car.set_dir_servo_angle(30)
time.sleep(2)
car.set_dir_servo_angle(0)
time.sleep(2)
car.set_dir_servo_angle(-30)
time.sleep(2)

#car.dir_servo_angle_calibration()

