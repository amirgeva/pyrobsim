import rclient
import math

R = rclient.Robot(1)
speed = 100


def is_obstacle(angle):
    R.sensor_angle(angle)
    return R.sense() > 0


def driving_decision():
    if is_obstacle(-45):
        turning = 10
    else:
        turning = -10
    if is_obstacle(0):
        turning = 40
    return turning


def run():
    turning = driving_decision()
    R.drive(speed + turning, speed - turning)
