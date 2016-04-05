# -*- coding: iso-8859-1 -*-
# !!!ENC NULL!!!
#TODO: XOR ENC
__SYSTEM=1

def handle_command(C,cmd):
	return True

class Encryption: # Classi di criptazione tutte uguali per poterle chiamare da drone
    def __init__(self,socket):
        self.s=socket
    def send(self,data):
        self.s.sendall(data)
    def recv(self,l):
        return self.s.recv(l)
