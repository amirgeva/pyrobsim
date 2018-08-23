#!/usr/bin/env python3
import sys
import math
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from vtypes import matrix, pt, vec2
from geometry import check_intersection

draw_circles = False
start = time.time()
RAD2DEG = 180.0 / 3.14159265358979


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
        self.orig_pic = QtGui.QImage('robot.png')
        self.build_rect_poly(self.orig_pic.width(), self.orig_pic.height())
        self.orig_poly = self.poly
        self.pos = QtCore.QPointF(250, 250)
        self.width = self.orig_pic.width()
        self.angle = 0
        self.sensor_angle = 0
        self.mat = matrix(self.angle)
        self.velocity = vec2(20.0, 19.0)
        self.encoders = vec2(0.0, 0.0)
        self.pic = self.orig_pic.transformed(QtGui.QTransform())
        self.servo_pos = pt(0, -20)


    def set_sensor_angle(self, a):
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

    def set_pos(self, p):
        self.pos = p

    def pic_center(self):
        return 0.5 * pt(self.pic.width(), self.pic.height())

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
        while full_dt > 0:
            dt = min(0.001, full_dt)
            full_dt -= dt
            pl = dt * self.velocity[0]
            pr = dt * self.velocity[1]
            da = math.atan2(pr - pl, self.width)
            dp = 0.5 * (pl + pr)
            self.set_pos(self.pos + dp * self.mat.map(pt(0, -1)))
            self.rotate(-da * RAD2DEG)


class SandboxWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SandboxWidget, self).__init__(parent, QtCore.Qt.WindowFlags())
        self.over = False
        self.setMinimumSize(800, 600)
        self.robot = Robot()
        self.obstacles = [Obstacle(300, 100, 150, 30, 20)]

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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent, QtCore.Qt.WindowFlags())
        self.setWindowTitle('Robot Simulator')
        self.sandbox = SandboxWidget()
        self.setCentralWidget(self.sandbox)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(100)

    def on_timer(self):
        self.sandbox.advance(0.1)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
