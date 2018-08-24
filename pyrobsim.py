#!/usr/bin/env python3
import sys
import math
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from vtypes import matrix, pt, vec2
from geometry import check_intersection, ray_intersection
from server import API

draw_circles = False
start = time.time()
RAD2DEG = 180.0 / 3.14159265358979
DEBUG = False
START_POS=pt(150,150)

class Object:
    def __init__(self):
        self.poly = QtGui.QPolygonF()
        self.pos = QtCore.QPointF(0, 0)
        self.radius = 0.0

    def build_rect_poly(self, w, h):
        self.poly.append(0.5 * pt(-w, -h))
        self.poly.append(0.5 * pt(w, -h))
        self.poly.append(0.5 * pt(w, h))
        self.poly.append(0.5 * pt(-w, h))
        self.radius = vec2(0.5 * w, 0.5 * h).norm()

    def draw(self, qp):
        if draw_circles:
            qp.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0)))
            qp.setBrush(QtCore.Qt.NoBrush)
            qp.drawEllipse(self.pos, self.radius, self.radius)


class Obstacle(Object):
    def __init__(self, x, y, w, h, angle):
        super(Obstacle, self).__init__()
        self.build_rect_poly(w, h)
        self.pos = pt(x, y)
        mat = matrix(angle)
        self.poly = mat.map(self.poly)
        self.poly.translate(self.pos)

    def draw(self, qp):
        color = QtGui.QColor(0, 0, 255)
        qp.setBrush(QtGui.QBrush(color))
        qp.setPen(color)
        qp.drawPolygon(self.poly)
        super(Obstacle, self).draw(qp)


class Robot(Object):
    def __init__(self):
        super(Robot, self).__init__()
        self.obstacles = []
        self.orig_pic = QtGui.QImage('robot.png')
        self.build_rect_poly(self.orig_pic.width(), self.orig_pic.height())
        self.orig_poly = self.poly
        self.pos = START_POS
        self.width = self.orig_pic.width()
        self.angle = 0
        self.sensor_angle = 0
        self.mat = matrix(self.angle)
        self.velocity = vec2(0.0, 0.0)
        self.encoders = vec2(0.0, 0.0)
        self.encoder_clicks = (0, 0)
        self.pic = self.orig_pic.transformed(QtGui.QTransform())
        self.servo_pos = pt(0, -20)
        self.api = API(self.process_command)
        self.commands = {'V': self.command_velocity, 'SA': self.command_sensor_angle, 'S': self.command_sensor,
                         'E': self.command_encoders}

    def restart(self):
        self.set_pos(START_POS)
        self.set_angle(0.0)
        self.set_sensor_angle(0.0)
        self.velocity = vec2(0.0,0.0)
        self.encoders = vec2(0.0, 0.0)
        self.encoder_clicks = (0, 0)

    def shutdown(self):
        self.api.shutdown()

    def process_command(self, cmd, args):
        if not cmd in self.commands:
            return ''
        handler = self.commands.get(cmd)
        return handler(args)

    def command_velocity(self, args):
        if len(args) == 2:
            self.velocity = vec2(args[0], args[1])
        return ''

    def command_sensor_angle(self, args):
        if len(args) == 1:
            self.set_sensor_angle(args[0])
        return ''

    def command_sensor(self, args):
        position = self.get_sensor_position()
        direction = self.get_sensor_direction()
        minimum_distance = -1
        for o in self.obstacles:
            distance = ray_intersection(position, direction, 200.0, o)
            if distance >= 0 or minimum_distance < 0:
                minimum_distance = distance
        return 'S {}'.format(minimum_distance)

    def command_encoders(self, args):
        result = 'E {} {}'.format(*self.encoder_clicks)
        self.encoder_clicks = (0, 0)
        return result

    def set_sensor_angle(self, a):
        if 45 >= a >= -45:
            self.sensor_angle = a

    def get_sensor_position(self):
        mat = matrix(self.sensor_angle)
        p = mat.map(pt(0, -5)) + self.servo_pos
        mat = matrix(self.angle)
        p = mat.map(p) + self.pos
        return vec2(p)

    def get_sensor_direction(self):
        mat = matrix(self.sensor_angle)
        mat.rotate(self.angle)
        return vec2(mat.map(pt(0, -1)))

    def set_angle(self, a):
        self.angle = a
        self.mat = matrix(self.angle)

    def rotate(self, da):
        self.angle += da
        self.mat.rotate(da)

    def set_pos(self, *args):
        if len(args)==2:
            self.pos = pt(args[0],args[1])
        elif len(args)==1:
            a=args[0]
            if isinstance(a,vec2):
                self.pos=pt(a.x,a.y)
            else:
                self.pos=a

    def pic_center(self):
        return 0.5 * pt(self.pic.width(), self.pic.height())

    def set_obstacles(self, obs):
        self.obstacles = obs

    def update_image(self):
        self.pic = self.orig_pic.transformed(self.mat, QtCore.Qt.SmoothTransformation)
        self.poly = self.mat.map(self.orig_poly)
        self.poly.translate(self.pos)
        qp = QtGui.QPainter()
        qp.begin(self.pic)
        self.draw_sensor(qp, self.pic_center())
        qp.end()

    def draw_sensor(self, qp, pos):
        servo_mat = matrix(self.sensor_angle)
        p1 = servo_mat.map(pt(-5, -5)) + self.servo_pos
        p2 = servo_mat.map(pt(5, -5)) + self.servo_pos
        p1 = self.mat.map(p1)
        p2 = self.mat.map(p2)
        qp.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(0, 0, 255)), 2))
        qp.drawLine(pos + p1, pos + p2)

    def draw(self, qp):
        self.update_image()
        draw_pos = self.pos - self.pic_center()
        qp.drawImage(draw_pos, self.pic)
        super(Robot, self).draw(qp)

    def advance(self, full_dt):
        start = (math.floor(self.encoders[0]), math.floor(self.encoders[1]))
        while full_dt > 0:
            dt = min(0.001, full_dt)
            full_dt -= dt
            pl = dt * self.velocity[0]
            pr = dt * self.velocity[1]
            da = math.atan2(pr - pl, self.width)
            dp = 0.5 * (pl + pr)
            self.set_pos(self.pos + dp * self.mat.map(pt(0, -1)))
            self.rotate(-da * RAD2DEG)
            self.encoders += vec2(pl, pr)
        stop = (math.floor(self.encoders[0]), math.floor(self.encoders[1]))
        self.encoder_clicks = (self.encoder_clicks[0] + int(stop[0] - start[0]),
                               self.encoder_clicks[1] + int(stop[1] - start[1]))


class SandboxWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SandboxWidget, self).__init__(parent, QtCore.Qt.WindowFlags())
        self.over = False
        self.setMinimumSize(800, 600)
        self.obstacles = [Obstacle(300, 100, 150, 30, 20)]
        self.robot = Robot()
        self.robot.set_obstacles(self.obstacles)

    def restart(self):
        self.over=False
        self.robot.restart()

    def load_scene(self,path):
        del self.obstacles[:]
        try:
            with open(path,'r') as f:
                for line in f.readlines():
                    p=line.strip().split()
                    if len(p)==5:
                        try:
                            p=[float(v) for v in p]
                            self.obstacles.append(Obstacle(*p))
                        except ValueError:
                            pass
        except IOError:
            QtWidgets.QMessageBox(None,"Error","{} not found".format(path))

    def draw_grid(self, qp):
        w = self.width()
        h = self.height()
        step = 20
        x = 0
        y = 0
        if self.over:
            qp.fillRect(0, 0, w, h, QtGui.QColor(255, 0, 0))
        p1 = QtGui.QPen(QtGui.QBrush(QtGui.QColor(128, 128, 128)), 1)
        p2 = QtGui.QPen(QtGui.QBrush(QtGui.QColor(0, 0, 0)), 2)
        while x < w or y < h:
            qp.setPen(p2 if (y % 100) == 0 else p1)
            qp.drawLine(0, y, w, y)
            qp.setPen(p2 if (x % 100) == 0 else p1)
            qp.drawLine(x, 0, x, h)
            y += step
            x += step

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw_grid(qp)
        for o in self.obstacles:
            o.draw(qp)
        self.robot.draw(qp)
        qp.end()

    def check_intersections(self):
        for o in self.obstacles:
            if check_intersection(self.robot, o):
                self.over = True

    def advance(self, dt):
        if self.over:
            return False
        self.robot.advance(dt)
        self.check_intersections()
        self.update()
        return True

    def shutdown(self):
        self.robot.shutdown()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, scene_path, parent=None):
        super(MainWindow, self).__init__(parent, QtCore.Qt.WindowFlags())
        self.setWindowTitle('Robot Simulator')
        self.sandbox = SandboxWidget()
        self.setCentralWidget(self.sandbox)
        self.last_time = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(100)
        self.setup_toolbar()
        self.done=False
        self.paused=False
        if self.sandbox.robot.api.done:
            self.done=True
        if scene_path:
            self.sandbox.load_scene(scene_path)

    def setup_toolbar(self):
        tb = self.addToolBar('Actions')
        tb.setObjectName("Toolbar")
        tb.addAction(QtGui.QIcon('open.png'), 'Open').triggered.connect(self.open_scene)
        tb.addAction(QtGui.QIcon('restart.png'), 'Restart').triggered.connect(self.restart)
        tb.addAction(QtGui.QIcon('pause.png'), 'Pause').triggered.connect(self.pause)
        tb.addAction(QtGui.QIcon('play.png'), 'Play').triggered.connect(self.play)

    def open_scene(self):
        path, filter = QtWidgets.QFileDialog.getOpenFileName(self,'Open Scene File','.','*.scene')
        if path:
            self.sandbox.load_scene(path)

    def restart(self):
        self.sandbox.restart()

    def pause(self):
        self.paused=True
        self.last_time=0

    def play(self):
        self.paused=False

    def shutdown(self):
        self.sandbox.shutdown()

    def on_timer(self):
        if not self.paused:
            dt = 0.1
            current_time = time.time()
            if self.last_time > 0:
                dt = current_time - self.last_time
            self.last_time = current_time
            self.sandbox.advance(dt)


def main():
    scene_path=''
    for arg in sys.argv:
        if arg == 'dbg':
            global DEBUG
            DEBUG = True
        if arg.endswith('.scene'):
            scene_path=arg
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(scene_path)
    if not w.done:
        w.show()
        app.exec_()
    else:
        QtWidgets.QMessageBox.critical(None,'Error','Simulator Already Running')
    w.shutdown()


if __name__ == '__main__':
    main()
