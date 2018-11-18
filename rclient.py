import socket
import threading
import time
import errno
import sys

DEBUG = False
simhook=[None]

class SocketRobot:
    def __init__(self,host):
        self.done = False
        self.address = (host, 9080)
        self.receive_thread = threading.Thread(target=self.receive_loop)
        self.receive_thread.start()
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sensor = None
        self.encoders = None
        self.send_message('RESET')

    def send_message(self, message):
        self.send_sock.sendto(bytes(message, 'utf-8'), self.address)

    def read_encoders(self):
        self.send_message('E')
        result = (0.0, 0.0)
        for i in range(10):
            if self.encoders:
                result = self.encoders
                self.encoders = None
                break
            time.sleep(0.02)
        return result

    def drive(self, l, r):
        self.send_message('V {} {}'.format(l, r))

    def stop(self):
        self.drive(0,0)

    def sensor_angle(self, a):
        self.send_message('SA {}'.format(a))

    def sense(self):
        self.send_message('S')
        result = -1.0
        for i in range(10):
            if not self.sensor is None:
                result = self.sensor
                self.sensor = None
                break
            time.sleep(0.02)
        return result

    def __del__(self):
        if self.receive_thread:
            self.shutdown()

    def shutdown(self):
        if self.receive_thread:
            self.stop()
            self.done = True
            self.receive_thread.join()
            self.receive_thread=None

    def receive_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', 9081))
        sock.setblocking(0)
        while not self.done:
            try:
                data, addr = sock.recvfrom(256)
                if len(data) == 0:
                    time.sleep(0.01)
                else:
                    response = str(data, 'utf-8')
                    if DEBUG:
                        print("Received from '{}' data='{}'".format(addr, response))
                    try:
                        p = response.strip().split()
                        if p[0] == 'S':
                            self.sensor = float(p[1])
                        if p[0] == 'E':
                            self.encoders = (float(p[1]), float(p[2]))
                    except ValueError:
                        pass
            except OSError as e:
                errnum = e.errno
                if errnum != errno.EAGAIN and errnum != errno.EWOULDBLOCK:
                    reason = ''  # get_error_name(errnum)
                    print("Socket Error ({}): {}".format(errnum, reason))


class DirectRobot:
    def __init__(self):
        self.hook = simhook[0]

    def drive(self,l,r):
        if self.hook:
            self.hook.command_velocity([l,r])

    def stop(self):
        self.drive(0,0)

    def sensor_angle(self, a):
        if self.hook and (isinstance(a,int) or isinstance(a,float)):
            self.hook.command_sensor_angle([a])

    def read_encoders(self):
        if self.hook:
            s=self.hook.command_encoders(None)
            s=s.strip().split()
            return (float(s[1]),float(s[2]))
        return (0,0)

    def sense(self):
        if self.hook:
            s=self.hook.command_sensor(None)
            s=s.strip().split()
            return float(s[1])
        return -1

class Robot:
    def __init__(self, param):
        if isinstance(param,int):
            self.impl = DirectRobot()
        if isinstance(param,str):
            self.impl = SocketRobot(param)

    def drive(self,l,r):
        self.impl.drive(l,r)

    def stop(self):
        self.impl.stop()

    def sensor_angle(self, a):
        self.impl.sensor_angle(a)

    def read_encoders(self):
        return self.impl.read_encoders()

    def sense(self):
        return self.impl.sense()


def unit_test():
    r = Robot()
    # print(r.sense())
    # r.drive(10,10)
    # time.sleep(1)
    for i in range(-45, 45):
        r.sensor_angle(i)
        time.sleep(0.1)
    r.shutdown()


if __name__ == '__main__':
    unit_test()
