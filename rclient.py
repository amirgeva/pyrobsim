import socket
import threading
import time
import errno


class Robot:
    def __init__(self, host='127.0.0.1'):
        self.done = False
        self.address = (host, 9080)
        self.receive_thread = threading.Thread(target=self.receive_loop)
        self.receive_thread.start()
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sensor = None
        self.encoders = None

    def send_message(self, message):
        self.send_sock.sendto(bytes(message, 'utf-8'), self.address)

    def drive(self, l, r):
        self.send_message('V {} {}'.format(l, r))

    def sensor_angle(self,a):
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

    def shutdown(self):
        self.done=True
        time.sleep(0.5)

    def receive_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', 9081))
        sock.setblocking(0)
        while not self.done:
            try:
                data, addr = sock.recvfrom(256)
                if len(data) == 0:
                    time.sleep(0.05)
                else:
                    response = str(data, 'utf-8')
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
        time.sleep(0.05)


def unit_test():
    r=Robot()
    print(r.sense())
    r.drive(10,10)
    time.sleep(1)
    r.shutdown()


if __name__=='__main__':
    unit_test()
