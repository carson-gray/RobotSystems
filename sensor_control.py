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


class Sensor:
    @log_on_start(logging.DEBUG, "Creating a Sensor.")
    @log_on_error(logging.DEBUG, "Failed to create a Sensor")
    def __init__(self):
        self.a0 = ADC('A0')
        self.a1 = ADC('A1')
        self.a2 = ADC('A2')

    @log_on_error(logging.DEBUG, "Failed to take a sensor reading")
    @log_on_end(logging.DEBUG, "New sensor poll: {result!r}")
    def take_reading(self):
        return [self.a0.read(), self.a1.read(), self.a2.read()]


class Interpreter:
    @log_on_start(logging.DEBUG, "Creating an Interpreter.")
    @log_on_error(logging.DEBUG, "Failed to create an Interpreter")
    def __init__(self, reading, sensitivity=600, polarity=1):
        """ Interprets the color sensor. Start robot with middle sensor on the line.

        Keyword arguments:
            reading: an initial sensor reading
            sensitivity: how different dark and light readings are expected to be
            polarity: if line is darker than floor, 1. If line is lighter, -1.
        """

        self.sensitivity = sensitivity
        if polarity > 0:
            self.polarity = 1
        else:
            self.polarity = -1

        # robot starts with middle sensor on the line
        self.on_line = [False, True, False]
        # initialize sensor reading
        self.last_poll = [reading[0], reading[1], reading[2]]

    @log_on_start(logging.DEBUG, "Processing sensor reading.")
    @log_on_error(logging.DEBUG, "Failed to process sensor reading.")
    def process(self, sensor_reading):
        """ Takes in three item Sensor input list """
        new_poll = sensor_reading

        # For sensor AN: A0, A1, A2
        for AN in range(3):
            # find change in sensor value
            d_a = self.last_poll[AN] - new_poll[AN]
            # check if it crossed the sensitivity threshold
            if abs(d_a) > self.sensitivity:
                # is the change in the direction of the target line?
                # pos. polarity for dark line, neg. polarity for light line
                if d_a * self.polarity < 0:
                    self.on_line[AN] = False
                else:
                    self.on_line[AN] = True

        # store the most recent sensor reading
        self.last_poll = new_poll
        return self.output()

    @log_on_error(logging.DEBUG, "Failed to process output.")
    @log_on_end(logging.DEBUG, "Robot position: {result!r}")
    def output(self):
        """ Returns robot position relative to line on continuum of [-1, 1],
        where -1 means the robot should go left, +1 should go right """

        # robot is positioned correctly
        if self.on_line == [False, True, False]:
            return 0.0

        # robot is slightly to the right
        elif self.on_line == [True, True, False]:
            return -0.5
        # robot is slightly to the left
        elif self.on_line == [False, True, True]:
            return 0.5

        # robot is significantly to the right
        elif self.on_line == [True, False, False]:
            return -1.0
        # robot is significantly to the left
        elif self.on_line == [False, False, True]:
            return 1.0

        # something is wrong
        else:
            return 0.0


class Controller:
    @log_on_start(logging.DEBUG, "Creating a Controller.")
    @log_on_error(logging.DEBUG, "Failed to create a Controller.")
    def __init__(self, scalar=20):
        """ scalar is the angle by which to steer based on position error """
        self.scalar = scalar

    def route(self, offset):
        """ returns car steering angle """
        return offset * self.scalar


if __name__ == "__main__":
    sensor = Sensor()
    interpreter = Interpreter(sensor.take_reading())
    controller = Controller()
    car = PicarX()
    car.set_steering_angle(0.0)
    car.go(20.0)

    for n in range(10000):
        reading = sensor.take_reading()
        offset = interpreter.process(reading)
        angle = controller.route(offset)
        car.set_steering_angle(angle)

    car.stop_car()
