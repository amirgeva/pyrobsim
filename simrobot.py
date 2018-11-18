import rclient
import math

R = rclient.Robot(1)
speed = 150
count = 0
sensor_angle = 0

def update_angle():
    global count
    (left,right)=R.read_encoders()
    angle = math.atan2(left-right,40)
    angle = math.degrees(angle)
    count = count - angle

def run():
    global count, speed, sensor_angle

    if count>0:
        R.drive(speed,-speed)
        update_angle()
    else:
        R.drive(speed,speed)
    R.sensor_angle(sensor_angle)
    sensor_angle = sensor_angle + 10
    if sensor_angle >= 90:
        sensor_angle = -90
    s = R.sense()
    if s>0 and s<100:
        count=10
    #print("count={}  s={}".format(count,s))
