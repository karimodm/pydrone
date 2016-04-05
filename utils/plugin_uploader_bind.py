# -*- coding: iso-8859-1 -*-
import socket

fn=raw_input("File to Bind For: ")
port=int(raw_input("Port to Bind With: "))
fd=open(fn,"rb")
fd.seek(0,2)
print 'File is '+str(fd.tell())+' Bytes Long'
fd.seek(0,0)
s=socket.socket()
s.connect(('127.0.0.1',port))
#s.listen(1)
#sox=s.accept()[0]
while True:
    t=fd.read()
    if not t: break
    s.send(t)
fd.close()
s.close()
