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


class Sensor:
    def __init__(self):
        self.a0 = ADC('A0')
        self.a1 = ADC('A1')
        self.a2 = ADC('A2')

    def take_reading(self):
        return [self.a0.read(), self.a1.read(), self.a2.read()]


class Interpreter:
    def __init__(self, sensitivity=3, polarity=3):
        """ Interprets the color sensor

        Keyword arguments:
        sensitivity: how different dark and light readings are expected to be
        polarity: is the line being followed darker or lighter than surrounding floor?
        """

        self.sensitivity = sensitivity
        self.polarity = polarity
        self.last_a0, self.last_a1, self.last_a2 = 0, 0, 0

    def process(self, sensor_reading):
        """ Takes in three item Sensor input list """
        new_a0, new_a1, new_a2 = sensor_reading[0], sensor_reading[1], sensor_reading[2]

        d_a0 = self.last_a0 - new_a0
        d_a1 = self.last_a1 - new_a1
        d_a2 = self.last_a2 - new_a2

        fancy_info = sensor_reading[0]

        # store the most recent sensor reading
        self.last_a0, self.last_a1, self.last_a2 = new_a0, new_a1, new_a2
        return self.output(fancy_info)

    def output(self, fancy_info):
        """ Returns robot position relative to line on continuum of [-1, 1],
        where -1 is left and 1 is right """
        return fancy_info


if __name__ == "__main__":
    sensor = Sensor()
    interpreter = Interpreter()

    for n in range(10):
        robot_position = interpreter.process(sensor.take_reading())
        print(robot_position)
        time.sleep(1)
