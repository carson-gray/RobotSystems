import time
from ezblock import __reset_mcu__
__reset_mcu__()
time.sleep(0.01)

import picarx_improved as car

time.sleep(0.01)
car.set_dir_servo_angle(0)
car.forward(60)
time.sleep(1)
car.set_dir_servo_angle(15)
car.forward(60)
time.sleep(3)
car.set_dir_servo_angle(0)
car.forward(60)
time.sleep(1)
car.set_dir_servo_angle(-15)
car.forward(60)
time.sleep(3)
car.set_dir_servo_angle(0)

#car.dir_servo_angle_calibration()

