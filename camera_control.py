#!/usr/bin/python3
import time
import sys
import atexit
sys.path.append(r'/opt/ezblock')
from vilib import Vilib
from urllib.request import urlopen
import cv2
import numpy as np
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
logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO,
                    datefmt="%H:%M:%S")
# comment out this line to disable logging
logging.getLogger().setLevel(logging.DEBUG)


class CameraController:
    def __init__(self):
        # start stream
        self.stream = Vilib()
        self.stream.camera_start(True)
        time.sleep(3)

        self.lower_blue = np.array([60, 40, 40])
        self.upper_blue = np.array([150, 255, 255])

        # changes later
        self.height, self.width = 100, 100

        atexit.register(self.cleanup)

    def cleanup(self):
        pass

    def get_frame(self):
        return self.stream.img_array[0]

    def detect_edges(self, frame):
        # get image
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # blue edges
        mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        edges = cv2.Canny(mask, 200, 400)

        return edges

    def region_of_interest(self, edges):
        height, width = edges.shape
        mask = np.zeros_like(edges)

        # bottom half of screen
        polygon = np.array([[
            (0, height * 1/2),
            (width, height * 1/2),
            (width, height),
            (0, height),
        ]], np.int32)

        cv2.fillPoly(mask, polygon, 255)
        cropped_edges = cv2.bitwise_and(edges, mask)
        return cropped_edges

    def detect_line_segments(self, cropped_edges):
        # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
        rho = 1  # distance precision in pixels
        angle = np.pi / 180  # angular precision in radians
        min_threshold = 10  # minimal of votes
        line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold,
                                        np.array([]), minLineLength=8, maxLineGap=4)
        return line_segments

    def average_slope_intercept(self, frame, line_segments):
        """
        This function combines line segments into one or two lane lines
        If all line slopes are < 0: then we only have detected left lane
        If all line slopes are > 0: then we only have detected right lane
        """
        lane_lines = []
        if line_segments is None:
            logging.info('No line_segment segments detected')
            return lane_lines

        height, width, _ = frame.shape
        left_fit = []
        right_fit = []

        boundary = 1/3
        left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
        right_region_boundary = width * boundary  # right lane line segment should be on left 2/3 of the screen

        for line_segment in line_segments:
            for x1, y1, x2, y2 in line_segment:
                if x1 == x2:
                    logging.info('skipping vertical line segment (slope=inf): %s' % line_segment)
                    continue
                fit = np.polyfit((x1, x2), (y1, y2), 1)
                slope = fit[0]
                intercept = fit[1]
                if slope < 0:
                    if x1 < left_region_boundary and x2 < left_region_boundary:
                        left_fit.append((slope, intercept))
                else:
                    if x1 > right_region_boundary and x2 > right_region_boundary:
                        right_fit.append((slope, intercept))

        left_fit_average = np.average(left_fit, axis=0)
        if len(left_fit) > 0:
            lane_lines.append(self.make_points(frame, left_fit_average))

        right_fit_average = np.average(right_fit, axis=0)
        if len(right_fit) > 0:
            lane_lines.append(self.make_points(frame, right_fit_average))

        logging.debug('lane lines: %s' % lane_lines)  # [[[316, 720, 484, 432]], [[1009, 720, 718, 432]]]

        return lane_lines

    def make_points(self, frame, line):
        self.height, self.width, _ = frame.shape
        slope, intercept = line
        y1 = self.height  # bottom of the frame
        y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

        # bound the coordinates within the frame
        x1 = max(-self.width, min(2 * self.width, int((y1 - intercept) / slope)))
        x2 = max(-self.width, min(2 * self.width, int((y2 - intercept) / slope)))
        return [[x1, y1, x2, y2]]

    def heading(self, lanes):
        _, _, left_x2, _ = lanes[0][0]
        _, _, right_x2, _ = lanes[1][0]
        mid = int(self.width / 2)
        x_offset = (left_x2 + right_x2) / 2 - mid
        y_offset = int(self.height / 2)

        angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
        angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
        steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel

        return steering_angle

    def navigate(self):
        frame = self.get_frame()
        edges = self.detect_edges(frame)
        cropped_edges = self.region_of_interest(edges)
        line_segments = self.detect_line_segments(cropped_edges)
        lane_lines = self.average_slope_intercept(frame, line_segments)
        angle = self.heading(lane_lines)
        return angle


if __name__ == "main":
    picam = CameraController()
    picar = PicarX()
    picar.set_steering_angle(0.0)

    while True:
        picar.drive(25.0, picam.navigate(), .3)
        time.sleep(1)
