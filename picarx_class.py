import time
import sys
from math import tan, pi
import atexit
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
import logging
from logdecorator import log_on_start, log_on_end, log_on_error
logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO,
                    datefmt="%H:%M:%S")
# comment out this line to disable logging
# logging.getLogger().setLevel(logging.DEBUG)


class PicarX:
    """ Motor controls for the Picar-X system """
    def __init__(self):
        self.PERIOD = 4095
        self.PRESCALER = 10
        self.TIMEOUT = 0.02
        self.CAR_LENGTH = 3.6
        self.CAR_WIDTH = 4.4

        self.dir_servo_pin = Servo(PWM('P2'))
        self.camera_servo_pin1 = Servo(PWM('P0'))
        self.camera_servo_pin2 = Servo(PWM('P1'))
        self.left_rear_pwm_pin = PWM("P13")
        self.right_rear_pwm_pin = PWM("P12")
        self.left_rear_dir_pin = Pin("D4")
        self.right_rear_dir_pin = Pin("D5")

        self.S0 = ADC('A0')
        self.S1 = ADC('A1')
        self.S2 = ADC('A2')

        self.servo_dir_flag = 1
        self.steering_calibration = 25
        self.cam_cal_value_1 = 0
        self.cam_cal_value_2 = 0
        self.motor_direction_pins = [self.left_rear_dir_pin, self.right_rear_dir_pin]
        self.motor_speed_pins = [self.left_rear_pwm_pin, self.right_rear_pwm_pin]
        self.cali_dir_value = [1, -1]
        self.cali_speed_value = [0, 0]
        self.steering_angle = 0

        for pin in self.motor_speed_pins:
            pin.period(self.PERIOD)
            pin.prescaler(self.PRESCALER)

        atexit.register(self.cleanup)

    @log_on_start(logging.DEBUG, "Stopping car and shutting down program")
    def cleanup(self):
        self.set_motor_speed(1, 0)
        self.set_motor_speed(2, 0)

    @log_on_start(logging.DEBUG, "Setting motor {motor:d}'s speed to {speed:f}")
    def set_motor_speed(self, motor, speed):
        motor -= 1
        if speed >= 0:
            direction = 1 * self.cali_dir_value[motor]
        elif speed < 0:
            direction = -1 * self.cali_dir_value[motor]
        speed = abs(speed)
        if direction < 0:
            self.motor_direction_pins[motor].high()
            self.motor_speed_pins[motor].pulse_width_percent(speed)
        else:
            self.motor_direction_pins[motor].low()
            self.motor_speed_pins[motor].pulse_width_percent(speed)

    @log_on_start(logging.DEBUG, "Setting steering angle to {value:d}")
    def set_steering_angle(self, value):
        self.dir_servo_pin.angle(value + self.steering_calibration)
        self.steering_angle = value

    @log_on_end(logging.DEBUG, "{result!r}")
    def go(self, speed):
        """ forward is positive speed, backwards negative speed"""
        if self.steering_angle != 0:
            # (-) t_r if left, (+) t_r if right
            turning_radius = self.CAR_LENGTH / tan(self.steering_angle * pi / 180)
            # adjustments are correct for either turning direction
            right_radius = turning_radius - self.CAR_WIDTH / 2
            left_radius = turning_radius + self.CAR_WIDTH / 2
            # ratio relative to center of CAR_WIDTH
            right_ratio = right_radius / turning_radius
            left_ratio = left_radius / turning_radius
            self.set_motor_speed(1, -1 * right_ratio * speed)
            self.set_motor_speed(2, -1 * left_ratio * speed)
            return f"Wheel speed ratios: left {left_ratio}, right {right_ratio}"
        else:
            self.set_motor_speed(1, -1 * speed)
            self.set_motor_speed(2, -1 * speed)
            return f"Wheel speed ratios: left {1}, right {1}"

    @log_on_start(logging.DEBUG, "Driving with Speed: {speed:d}, Angle: {turn_angle:d}, & Duration: {duration:f}")
    def drive(self, speed, turn_angle, duration=3.0):
        self.set_steering_angle(turn_angle)
        self.go(speed)
        time.sleep(duration)

    @log_on_start(logging.DEBUG, "Stopping car")
    def stop_car(self):
        self.drive(0, 0, .1)

    @log_on_start(logging.DEBUG, "Parallel parking to the right")
    def parallel_park_right(self):
        self.drive(20, 0, 1)
        self.drive(-30, 30, 1)
        self.drive(-30, -30, 1)
        self.drive(20, 0, 0.5)
        self.stop_car()

    @log_on_start(logging.DEBUG, "Parallel parking to the left")
    def parallel_park_left(self):
        self.drive(20, 0, 1)
        self.drive(-20, -30, 1)
        self.drive(-20, 30, 1)
        self.drive(20, 0, 0.5)
        self.stop_car()

    @log_on_start(logging.DEBUG, "K-turning to the right")
    def k_turn_right(self):
        self.drive(30, 30, 1)
        self.drive(-30, -30, 1)
        self.drive(30, 30, 1)
        self.drive(30, 0, 0.5)
        self.stop_car()

    @log_on_start(logging.DEBUG, "K-turning to the left")
    def k_turn_left(self):
        self.drive(30, -30, 1)
        self.drive(-30, 30, 1)
        self.drive(30, -30, 1)
        self.drive(30, 0, 0.5)
        self.stop_car()

    def clamp(self, value, value_id, lower_bound, upper_bound):
        """ Clamp the value within a bounded range """
        if value < lower_bound:
            logging.debug(f"Adjusting {value_id} value [{value}] to [{lower_bound}]")
            return lower_bound
        if value > upper_bound:
            logging.debug(f"Adjusting {value_id} value [{value}] to [{upper_bound}]")
            return upper_bound
        return value

    @log_on_start(logging.DEBUG, "Starting the control terminal")
    def control_terminal(self):
        """ Drive, parallel park, and k-turn robot """
        while True:
            user_in = input("\nPlease enter "
                            "\n[d] for drive, "
                            "\n[p] for parallel park, "
                            "\n[k] for k-turn, or "
                            "\n[q] for quit: ")

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
                self.drive(self.clamp(input_speed, "speed", -100, 100),
                           self.clamp(input_angle, "angle", -45, 45),
                           self.clamp(input_time, "time", 1, 30))
                self.stop_car()

            elif user_in.lower() == 'p':
                input_direction = input("Do you want to go left or right? [l]/[r]: ")
                if input_direction.lower() == 'l':
                    self.parallel_park_left()
                elif input_direction.lower() == 'r':
                    self.parallel_park_right()
                else:
                    logging.debug("Please try again with 'l' or 'r'")
                    continue

            elif user_in.lower() == 'k':
                input_direction = input("Do you want to go left or right? [l]/[r]: ")
                if input_direction.lower() == 'l':
                    self.k_turn_left()
                elif input_direction.lower() == 'r':
                    self.k_turn_right()
                else:
                    logging.debug("Please try again with 'l' or 'r'")
                    continue

            elif user_in.lower() == 'q':
                sys.exit()

            else:
                logging.debug("Please pick a valid option")
                continue


if __name__ == "__main__":
    car = PicarX()
    car.control_terminal()
