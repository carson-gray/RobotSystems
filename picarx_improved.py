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
from math import tan
import logging
from logdecorator import log_on_start, log_on_end, log_on_error
logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO,
                    datefmt="%H:%M:%S")
# # Comment this line out to disable logging!
logging.getLogger().setLevel(logging.DEBUG)
# logging.debug("This is how you should print!")

PERIOD = 4095
PRESCALER = 10
TIMEOUT = 0.02

dir_servo_pin = Servo(PWM('P2'))
camera_servo_pin1 = Servo(PWM('P0'))
camera_servo_pin2 = Servo(PWM('P1'))
left_rear_pwm_pin = PWM("P13")
right_rear_pwm_pin = PWM("P12")
left_rear_dir_pin = Pin("D4")
right_rear_dir_pin = Pin("D5")
car_len = 3.6
wheel_base = 4.4

S0 = ADC('A0')
S1 = ADC('A1')
S2 = ADC('A2')

Servo_dir_flag = 1
dir_cal_value = 25
cam_cal_value_1 = 0
cam_cal_value_2 = 0
motor_direction_pins = [left_rear_dir_pin, right_rear_dir_pin]
motor_speed_pins = [left_rear_pwm_pin, right_rear_pwm_pin]
cali_dir_value = [1, -1]
cali_speed_value = [0, 0]
steering_angle = 0

out_vals = []

for pin in motor_speed_pins:
    pin.period(PERIOD)
    pin.prescaler(PRESCALER)


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def set_motor_speed(motor, speed):
    global cali_speed_value, cali_dir_value
    motor -= 1
    if speed >= 0:
        direction = 1 * cali_dir_value[motor]
    elif speed < 0:
        direction = -1 * cali_dir_value[motor]
    speed = abs(speed)
    # if speed != 0:
    #     speed = int(speed / 2) + 50
    # speed = speed - cali_speed_value[motor]
    if direction < 0:
        motor_direction_pins[motor].high()
        motor_speed_pins[motor].pulse_width_percent(speed)
    else:
        motor_direction_pins[motor].low()
        motor_speed_pins[motor].pulse_width_percent(speed)


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def motor_speed_calibration(value):
    global cali_speed_value, cali_dir_value
    cali_speed_value = value
    if value < 0:
        cali_speed_value[0] = 0
        cali_speed_value[1] = abs(cali_speed_value)
    else:
        cali_speed_value[0] = abs(cali_speed_value)
        cali_speed_value[1] = 0


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def motor_direction_calibration(motor, value):
    # 0: positive direction
    # 1:negative direction
    global cali_dir_value
    motor -= 1
    if value == 1:
        cali_dir_value[motor] = -1 * cali_dir_value[motor]


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def dir_servo_angle_calibration(value):
    global dir_cal_value
    dir_cal_value = value
    set_dir_servo_angle(dir_cal_value)
    # dir_servo_pin.angle(dir_cal_value)


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "{result!r}")
def set_dir_servo_angle(value):
    global dir_cal_value, steering_angle
    dir_servo_pin.angle(value + dir_cal_value)
    steering_angle = value
    return steering_angle


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def camera_servo1_angle_calibration(value):
    global cam_cal_value_1
    cam_cal_value_1 = value
    set_camera_servo1_angle(cam_cal_value_1)
    # camera_servo_pin1.angle(cam_cal_value)


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def camera_servo2_angle_calibration(value):
    global cam_cal_value_2
    cam_cal_value_2 = value
    set_camera_servo2_angle(cam_cal_value_2)
    # camera_servo_pin2.angle(cam_cal_value)


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def set_camera_servo1_angle(value):
    global cam_cal_value_1
    camera_servo_pin1.angle(-1 * (value + cam_cal_value_1))


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def set_camera_servo2_angle(value):
    global cam_cal_value_2
    camera_servo_pin2.angle(-1 * (value + cam_cal_value_2))


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def get_adc_value():
    adc_value_list = []
    adc_value_list.append(S0.read())
    adc_value_list.append(S1.read())
    adc_value_list.append(S2.read())
    return adc_value_list


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def set_power(speed):
    set_motor_speed(1, speed)
    set_motor_speed(2, speed)


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def backward(speed):
    set_motor_speed(1, speed)
    set_motor_speed(2, speed)


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, f"{out_vals}")
def forward(speed):
    global dir_cal_value, steering_angle, car_len, wheel_base, out_vals
    if steering_angle != 0:
        # (-) t_r if left, (+) t_r if right
        turning_radius = car_len / tan(steering_angle)
        # adjustments are correct for either turning direction
        right_radius = turning_radius - wheel_base / 2
        left_radius = turning_radius + wheel_base / 2
        # ratio relative to center of wheel_base
        right_ratio = right_radius / turning_radius
        left_ratio = left_radius / turning_radius
        out_vals.append((left_ratio, right_ratio))
        set_motor_speed(1, -1 * left_ratio * speed)
        set_motor_speed(2, -1 * right_ratio * speed)
    else:
        set_motor_speed(1, -1 * speed)
        set_motor_speed(2, -1 * speed)


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def stop():
    set_motor_speed(1, 0)
    set_motor_speed(2, 0)


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def Get_distance():
    timeout = 0.01
    trig = Pin('D8')
    echo = Pin('D9')

    trig.low()
    time.sleep(0.01)
    trig.high()
    time.sleep(0.000015)
    trig.low()
    pulse_end = 0
    pulse_start = 0
    timeout_start = time.time()
    while echo.value() == 0:
        pulse_start = time.time()
        if pulse_start - timeout_start > timeout:
            return -1
    while echo.value() == 1:
        pulse_end = time.time()
        if pulse_end - timeout_start > timeout:
            return -2
    during = pulse_end - pulse_start
    cm = round(during * 340 / 2 * 100, 2)
    # print(cm)
    return cm


@log_on_start(logging.DEBUG, "Program shutting down...")
@log_on_end(logging.DEBUG, "Program shut down successfully")
def exit_function():
    set_motor_speed(1, 0)
    set_motor_speed(2, 0)
import atexit
atexit.register(exit_function)


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def test():
    # dir_servo_angle_calibration(-10)
    set_dir_servo_angle(-40)
    # time.sleep(1)
    # set_dir_servo_angle(0)
    # time.sleep(1)
    # set_motor_speed(1, 1)
    # set_motor_speed(2, 1)
    # camera_servo_pin.angle(0)

# if __name__ == "__main__":
#     try:
#         # dir_servo_angle_calibration(-10)
#         while 1:
#             test()
#     finally:
#         stop()
