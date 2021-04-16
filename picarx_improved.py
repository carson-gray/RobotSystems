import time
import sys

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
from math import tan, pi
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

CAR_LENGTH = 3.6
CAR_WIDTH = 4.4

dir_servo_pin = Servo(PWM('P2'))
camera_servo_pin1 = Servo(PWM('P0'))
camera_servo_pin2 = Servo(PWM('P1'))
left_rear_pwm_pin = PWM("P13")
right_rear_pwm_pin = PWM("P12")
left_rear_dir_pin = Pin("D4")
right_rear_dir_pin = Pin("D5")

S0 = ADC('A0')
S1 = ADC('A1')
S2 = ADC('A2')

servo_dir_flag = 1
steering_calibration = 25
cam_cal_value_1 = 0
cam_cal_value_2 = 0
motor_direction_pins = [left_rear_dir_pin, right_rear_dir_pin]
motor_speed_pins = [left_rear_pwm_pin, right_rear_pwm_pin]
cali_dir_value = [1, -1]
cali_speed_value = [0, 0]
steering_angle = 0

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
    global steering_calibration
    steering_calibration = value
    set_steering_angle(steering_calibration)
    # dir_servo_pin.angle(steering_calibration)


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "{result!r}")
def set_steering_angle(value):
    global steering_calibration, steering_angle
    dir_servo_pin.angle(value + steering_calibration)
    steering_angle = value
    return f"Steering angle set to {steering_angle} degrees"


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
@log_on_end(logging.DEBUG, "{result!r}")
def forward(speed):
    """ forward is + speed, backwards - speed"""
    global steering_calibration, steering_angle, CAR_LENGTH, CAR_WIDTH
    if steering_angle != 0:
        # (-) t_r if left, (+) t_r if right
        turning_radius = CAR_LENGTH / tan(steering_angle * pi / 180)
        # adjustments are correct for either turning direction
        right_radius = turning_radius - CAR_WIDTH / 2
        left_radius = turning_radius + CAR_WIDTH / 2
        # ratio relative to center of CAR_WIDTH
        right_ratio = right_radius / turning_radius
        left_ratio = left_radius / turning_radius
        set_motor_speed(1, -1 * right_ratio * speed)
        set_motor_speed(2, -1 * left_ratio * speed)
        return f"steering angle {steering_angle}, turning radius {turning_radius}, left radius {left_radius}, " \
               f"right radius {right_radius}, left {left_ratio}, right {right_ratio}"
    else:
        set_motor_speed(1, -1 * speed)
        set_motor_speed(2, -1 * speed)
        return 0


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def stop():
    set_motor_speed(1, 0)
    set_motor_speed(2, 0)


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def get_distance():
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


@log_on_start(logging.DEBUG, "Message when function starts")
@log_on_error(logging.DEBUG, "Message when function encounters an error before completing")
@log_on_end(logging.DEBUG, "Message when function ends successfully")
def drive(speed, turn_angle, duration=3.0):
    set_steering_angle(turn_angle)
    forward(speed)
    time.sleep(duration)


def stop_car():
    drive(0, 0, .1)


@log_on_start(logging.DEBUG, "Parallel parking to the right")
@log_on_error(logging.DEBUG, "Error occurred while parallel parking right")
@log_on_end(logging.DEBUG, "Parallel parking complete")
def parallel_park_right():
    drive(20, 0, 1)
    drive(-20, 30, 0.5)
    drive(-20, -30, 0.5)
    drive(20, 0, 0.2)
    stop_car()


@log_on_start(logging.DEBUG, "Parallel parking to the left")
@log_on_error(logging.DEBUG, "Error occurred while parallel parking left")
@log_on_end(logging.DEBUG, "Parallel parking complete")
def parallel_park_left():
    drive(20, 0, 1)
    drive(-20, -30, 0.5)
    drive(-20, 30, 0.5)
    drive(20, 0, 0.2)
    stop_car()


@log_on_start(logging.DEBUG, "K-turning to the right")
@log_on_error(logging.DEBUG, "Error occurred while K-turning right")
@log_on_end(logging.DEBUG, "K-turning complete")
def k_turn_right():
    drive(30, 30, 1)
    drive(-30, -30, 1)
    drive(30, 0, 0.5)
    stop_car()


@log_on_start(logging.DEBUG, "K-turning to the left")
@log_on_error(logging.DEBUG, "Error occurred while K-turning left")
@log_on_end(logging.DEBUG, "K-turning complete")
def k_turn_left():
    drive(30, -30, 1)
    drive(-30, 30, 1)
    drive(30, 0, 0.5)
    stop_car()


def clamp(value, value_id, lower_bound, upper_bound):
    """ Clamp the value within a bounded range """
    if value < lower_bound:
        logging.debug(f"Adjusting {value_id} value [{value}] to [{lower_bound}]")
        return lower_bound
    if value > upper_bound:
        logging.debug(f"Adjusting {value_id} value [{value}] to [{upper_bound}]")
        return upper_bound
    return value


@log_on_start(logging.DEBUG, "Starting control terminal")
@log_on_error(logging.DEBUG, "Error occurred during control")
@log_on_end(logging.DEBUG, "Closing control terminal")
def control_terminal():
    while True:
        user_in = input("Please enter "
                        "[d] for drive, "
                        "[p] for parallel park, "
                        "[k] for k-turn, or "
                        "[q] for quit: ")

        if user_in.lower() == 'd':
            try:
                input_speed = int(input("What speed do you want?"
                                        "\nPositive values are forward, negative backwards: "))
                input_angle = int(input("What angle do you want?"
                                        "\nPositive values are right, negative left: "))
                input_time = int(input("How many seconds do you want the car to do this? "))
            except ValueError:
                logging.debug("Please enter an integer!")
                continue
            drive(clamp(input_speed, "speed", -100, 100),
                  clamp(input_angle, "angle", -45, 45),
                  clamp(input_time, "time", 1, 30))
            stop_car()

        elif user_in.lower() == 'p':
            input_direction = input("Do you want to go left or right? [l]/[r]: ")
            if input_direction.lower() == 'l':
                parallel_park_left()
            elif input_direction.lower() == 'r':
                parallel_park_right()
            else:
                logging.debug("Please try again with 'l' or 'r'")
                continue

        elif user_in.lower() == 'k':
            input_direction = input("Do you want to go left or right? [l]/[r]: ")
            if input_direction.lower() == 'l':
                k_turn_left()
            elif input_direction.lower() == 'r':
                k_turn_right()
            else:
                logging.debug("Please try again with 'l' or 'r'")
                continue

        elif user_in.lower() == 'q':
            sys.exit()

        else:
            logging.debug("Please pick a valid option")
            continue


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
    pass
    # dir_servo_angle_calibration(-10)
    # set_steering_angle(-40)
    # time.sleep(1)
    # set_steering_angle(0)
    # time.sleep(1)
    # set_motor_speed(1, 1)
    # set_motor_speed(2, 1)
    # camera_servo_pin.angle(0)


if __name__ == "__main__":
    control_terminal()
