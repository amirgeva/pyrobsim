import socket


s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.sendto(b'V 30 25',('127.0.0.1',9080))
