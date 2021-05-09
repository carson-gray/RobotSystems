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
import rossros
import concurrent.futures
from threading import Lock
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

    def producer(self, sensor_bus_out, time_delay):
        lock = Lock()
        while True:
            with lock:
                a0_value = self.a0.read()
                a1_value = self.a1.read()
                a2_value = self.a2.read()
            reading = [a0_value, a1_value, a2_value]
            sensor_bus_out.set_message(reading)
            time.sleep(time_delay)


class Interpreter:
    @log_on_start(logging.DEBUG, "Creating an Interpreter.")
    @log_on_error(logging.DEBUG, "Failed to create an Interpreter")
    def __init__(self, reading, sensitivity=400, polarity=1):
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
        self.last_steer = 0.0

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
                # what is the change in the direction of the target line?
                # pos. polarity for dark line, neg. polarity for light line
                if d_a * self.polarity < 0:
                    self.on_line[AN] = False
                else:
                    self.on_line[AN] = True

        # store the most recent sensor reading
        self.last_poll = new_poll
        self.last_steer = self.output()
        return self.last_steer

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

        # if off the line (or a wacky case), so do what you did last
        else:
            return self.last_steer

    def consumer_producer(self, sensor_bus_in, offset_bus_out, time_delay):
        while True:
            sensor_reading = sensor_bus_in.get_message()
            offset = self.process(sensor_reading)
            offset_bus_out.set_message(offset)
            time.sleep(time_delay)


class Controller:
    @log_on_start(logging.DEBUG, "Creating a Controller.")
    @log_on_error(logging.DEBUG, "Failed to create a Controller.")
    def __init__(self, car, scalar=30):
        """ scalar is the angle by which to steer based on position error """
        self.scalar = scalar
        self.car = car
        self.speed = 25.0

    def route(self, offset):
        """ returns car steering angle """
        return offset * self.scalar

    def consumer(self, offset_bus_in, time_delay):
        while True:
            offset = offset_bus_in.get_message()
            angle = self.route(offset)
            self.car.drive(self.speed, angle, time_delay)


@log_on_start(logging.DEBUG, "Creating the sensor-control loop.")
def main():
    """ runs sensor, interpreter, and control loop concurrently """
    # create sensor and interpreter, give interpreter initial reading

    car = PicarX()
    car.set_steering_angle(0.0)

    sensor = Sensor()
    sensor_values_bus = rossros.Bus()
    sensor_delay = 1
    sensor_producer = rossros.Producer(sensor.producer,
                                       sensor_values_bus,
                                       sensor_delay)

    interpreter = Interpreter(sensor.take_reading())
    interpreter_bus = rossros.Bus()
    interpreter_delay = 2
    interpreter_consumer_producer = rossros.ConsumerProducer(interpreter.consumer_producer,
                                                             sensor_values_bus,
                                                             interpreter_bus,
                                                             interpreter_delay)

    controller = Controller(car)
    controller_delay = 1
    controller_consumer = rossros.Consumer(controller.consumer,
                                           interpreter_bus,
                                           controller_delay)

    # run concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # sensor produces new readings
        e_sensor = executor.submit(sensor_producer.__call__())
        # interpreter consumes sensor readings, produces the car offset calculation
        e_interpreter = executor.submit(interpreter_consumer_producer.__call__())
        # controller consumes car offset calculation, controls the car
        e_controller = executor.submit(controller_consumer.__call__())

    # reads after the with block
    e_sensor.result()
    e_interpreter.result()
    e_controller.result()


if __name__ == "__main__":
    main()
