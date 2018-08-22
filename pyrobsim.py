#!/usr/bin/env python3
import sys
import math
import time
from PyQt4 import QtCore,QtGui

start=time.time()

def rotate(x,y,a):
    c=math.cos(a)
    s=math.sin(a)
    return QtCore.QPointF(c*x+s*y,c*y-s*x)

class SandboxWidget(QtGui.QWidget):
    def __init__(self,parent=None):
        super(SandboxWidget,self).__init__(parent)
        self.setMinimumSize(800,600)
        self.pic=QtGui.QImage('robot.png')

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        for y in range(10):
            qp.drawLine(0,y*100,1000,y*100)
            qp.drawLine(y*100,0,y*100,1000)
        a=time.time()-start
        mat=QtGui.QMatrix()
        mat.rotate(a*45)
        tr=self.pic.transformed(mat,QtCore.Qt.SmoothTransformation)
        dx=0.5*(tr.width())#-self.pic.width())
        dy=0.5*(tr.height())#-self.pic.height())
        ofs=QtCore.QPointF(200-dx,200-dy)
        qp.drawImage(ofs,tr)
        qp.end()



class MainWindow(QtGui.QMainWindow):
    def __init__(self,parent=None):
        super(MainWindow,self).__init__(parent)
        self.sandbox=SandboxWidget()
        self.setCentralWidget(self.sandbox)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.onTimer)
        self.timer.start(100)

    def onTimer(self):
        self.sandbox.update()

def main():
    app=QtGui.QApplication(sys.argv)
    w=MainWindow()
    w.show()
    app.exec_()

if __name__=='__main__':
    main()

