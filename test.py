import time
import rclient

r=rclient.Robot()
x=0.0
r.drive(50, 50)
while x<400:
    e=r.read_encoders()
    if e:
        x=x+e[0]
        if e[0] > 0:
            print(x)
    time.sleep(0.01)
r.shutdown()

