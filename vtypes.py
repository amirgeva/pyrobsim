import math
from PyQt5 import QtGui,QtCore


def matrix(angle):
    mat=QtGui.QTransform()
    mat.rotate(angle)
    return mat

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

