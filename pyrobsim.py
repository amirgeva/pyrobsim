#!/usr/bin/env python3
import sys
import math
import time
from PyQt4 import QtCore,QtGui

draw_circles=False
start=time.time()
RAD2DEG = 180.0 / 3.14159265358979

def rotate(x,y,a):
    c=math.cos(a)
    s=math.sin(a)
    return QtCore.QPointF(c*x+s*y,c*y-s*x)

def pt(x,y):
    return QtCore.QPointF(x,y)

class vec2:
    def __init__(self,*args):
        self.x=0.0
        self.y=0.0
        if len(args)==2:
            self.x=args[0]
            self.y=args[1]
        elif len(args)==1:
            p=args[0]
            self.x = p.x()
            self.y = p.y()

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other):
        return vec2(self.x-other.x,self.y-other.y)

    def __add__(self, other):
        return vec2(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        return self.x*other.x+self.y*other.y

    def __getitem__(self, item):
        if item==0:
            return self.x
        if item==1:
            return self.y
        return 0.0

    def norm(self):
        return math.sqrt(self*self)

    def normalized(self):
        n=self.norm()
        return vec2(self.x/n,self.y/n)

def norm(p):
    return vec2(p.x(),p.y()).norm()

class Segment:
    def __init__(self,poly,i):
        self.p1=vec2(poly.at(i))
        self.p2=vec2(poly.at((i+1)%poly.size()))
        D=self.p2 - self.p1;
        self.N=vec2(-D.y,D.x).normalized()
        self.d=self.p1*self.N

def check_segment_intersection(s1,s2):
    return (s1.p1*s2.N-s2.d)*(s1.p2*s2.N-s2.d)<0 and (s2.p1*s1.N-s1.d)*(s2.p2*s1.N-s1.d)<0

def check_poly_intersection(p1,p2):
    s1 = [Segment(p1, i) for i in range(p1.size())]
    s2 = [Segment(p2, i) for i in range(p2.size())]
    for si in s1:
        for sj in s2:
            if check_segment_intersection(si,sj):
                return True
    return False

def check_intersection(o1,o2):
    dist=norm(o1.pos-o2.pos)
    sum_rad = o1.radius + o2.radius
    if dist > sum_rad:
        return False
    return check_poly_intersection(o1.poly,o2.poly)


class Object:
    def __init__(self):
        self.poly = QtGui.QPolygonF()
        self.pos = QtCore.QPointF(0, 0)

    def build_rect_poly(self,w,h):
        self.poly.append(0.5*pt(-w,-h))
        self.poly.append(0.5*pt( w,-h))
        self.poly.append(0.5*pt( w, h))
        self.poly.append(0.5*pt(-w, h))
        self.radius = math.sqrt(0.25*w*w+0.25*h*h)

    def draw(self,qp):
        if draw_circles:
            qp.setPen(QtGui.QPen(QtGui.QColor(255,0,0)))
            qp.setBrush(QtCore.Qt.NoBrush)
            qp.drawEllipse(self.pos,self.radius,self.radius)



class Obstacle(Object):
    def __init__(self,x,y,w,h,angle):
        super(Obstacle, self).__init__()
        self.build_rect_poly(w,h)
        self.pos=pt(x,y)
        mat = QtGui.QMatrix()
        mat.rotate(angle)
        self.poly=mat.map(self.poly)
        self.poly.translate(self.pos)

    def draw(self,qp):
        color=QtGui.QColor(0,0,255)
        qp.setBrush(QtGui.QBrush(color))
        qp.setPen(color)
        qp.drawPolygon(self.poly)
        super(Obstacle, self).draw(qp)



class Robot(Object):
    def __init__(self):
        super(Robot,self).__init__()
        self.orig_pic=QtGui.QImage('robot.png')
        self.build_rect_poly(self.orig_pic.width(), self.orig_pic.height())
        self.orig_poly=self.poly
        self.pos = QtCore.QPointF(250,250)
        self.width = self.orig_pic.width()
        self.angle = 0
        self.sensor_angle=0
        self.mat=QtGui.QMatrix()
        self.mat.rotate(self.angle)
        self.velocity=vec2(20.0,19.0)
        self.encoders=vec2(0.0,0.0)

    def set_sensor_angle(self,a):
        self.sensor_angle=a

    def set_angle(self,a):
        self.angle = a
        self.mat=QtGui.QMatrix()
        self.mat.rotate(self.angle)

    def rotate(self,da):
        self.angle += da
        self.mat.rotate(da)

    def set_pos(self,p):
        self.pos=p

    def pic_center(self):
        return 0.5*pt(self.pic.width(),self.pic.height())

    def update_image(self):
        self.pic = self.orig_pic.transformed(self.mat, QtCore.Qt.SmoothTransformation)
        self.poly=self.mat.map(self.orig_poly)
        self.poly.translate(self.pos)
        qp=QtGui.QPainter()
        qp.begin(self.pic)
        self.draw_sensor(qp,self.pic_center())
        qp.end()

    def draw_sensor(self,qp,pos):
        servo_mat=QtGui.QMatrix()
        servo_mat.rotate(self.sensor_angle)
        servo_pos=QtCore.QPointF(0,-20)
        p1 = servo_mat.map(QtCore.QPointF(-5, -5))+servo_pos
        p2 = servo_mat.map(QtCore.QPointF( 5, -5))+servo_pos
        p1 = self.mat.map(p1)
        p2 = self.mat.map(p2)
        qp.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(0,0,255)),2))
        qp.drawLine(pos+p1,pos+p2)

    def draw(self,qp):
        self.update_image()
        draw_pos = self.pos - self.pic_center()
        qp.drawImage(draw_pos,self.pic)
        super(Robot,self).draw(qp)

    def advance(self,full_dt):
        while full_dt>0:
            dt=min(0.001,full_dt)
            full_dt-=dt
            Pl = dt * self.velocity[0]
            Pr = dt * self.velocity[1]
            da = math.atan2(Pr-Pl,self.width)
            dp = 0.5*(Pl+Pr)
            self.set_pos(self.pos + dp * self.mat.map(pt(0,-1)))
            self.rotate(-da*RAD2DEG)


class SandboxWidget(QtGui.QWidget):
    def __init__(self,parent=None):
        super(SandboxWidget,self).__init__(parent)
        self.over=False
        self.setMinimumSize(800,600)
        self.robot=Robot()
        self.obstacles = [Obstacle(300,100,150,30,20)]

    def drawGrid(self,qp):
        w=self.width()
        h=self.height()
        step=20
        x=0
        y=0
        if self.over:
            qp.fillRect(0,0,w,h,QtGui.QColor(255,0,0))
        p1 = QtGui.QPen(QtGui.QBrush(QtGui.QColor(128, 128, 128)), 1)
        p2 = QtGui.QPen(QtGui.QBrush(QtGui.QColor(0,0,0)), 2)
        while x<w or y<h:
            qp.setPen(p2 if (y%100)==0 else p1)
            qp.drawLine(0,y,w,y)
            qp.setPen(p2 if (x%100)==0 else p1)
            qp.drawLine(x,0,x,h)
            y+=step
            x+=step

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawGrid(qp)
        for o in self.obstacles:
            o.draw(qp)
        self.robot.draw(qp)
        qp.end()

    def check_intersections(self):
        for o in self.obstacles:
            if check_intersection(self.robot,o):
                self.over=True

    def advance(self,dt):
        if self.over:
            return False
        self.robot.advance(dt)
        self.check_intersections()
        self.update()
        return True



class MainWindow(QtGui.QMainWindow):
    def __init__(self,parent=None):
        super(MainWindow,self).__init__(parent)
        self.sandbox=SandboxWidget()
        self.setCentralWidget(self.sandbox)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.onTimer)
        self.timer.start(100)

    def onTimer(self):
        self.sandbox.advance(0.1)

def main():
    app=QtGui.QApplication(sys.argv)
    w=MainWindow()
    w.show()
    app.exec_()

if __name__=='__main__':
    main()

