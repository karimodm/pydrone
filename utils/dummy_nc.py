#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
import socket
sox=socket.socket()
sox.bind(("127.0.0.1",5858))
sox.listen(1)
s=sox.accept()[0]
while True:
  print s.recv(128)
  s.sendall(raw_input('')+"\r\n")
