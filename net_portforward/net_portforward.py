# -*- coding: iso-8859-1 -*-
from threading import Thread,Event
import re
import socket
import common

table=[]

# A TCP/UDP socket abstraction
class SocketAbstraction(socket.socket,object): # New-Style Class
    def __init__(self,destaddr,family=2,type=1,proto=0,_sock=None):
    	socket.__init__(self,family,type,proto,_sock)
    	self.destaddr=destaddr
	self.parent=super(SocketAbstraction,self)
    def send(self,data):
    	if self._sock.type==self.SOCK_STREAM:
    	    return self.parent.send(data)
    	else:
    	    return self.parent.sendto(data,self.destaddr)
    def recv(self,len):
    	if self._sock.type==self.SOCK_STREAM:
    	    return self.parent.recv(len)
    	else:
    	    return self.parent.recvfrom(len)[0]
    def listen(self,*backlog)
   	if self._sock.type==self.SOCK_STREAM:
	    self.parent.listen(backlog)
    def accept(self):
    	if self._sock.type==self.SOCK_STREAM:
	    return self.parent.accept()
	else:
    	    return (self,None)
    def connect(self,*addr)
   	if self._sock.type==self.SOCK_STREAM:
	    self.parent.connect(addr)
    	    
def forward(*args): # ID, sox_binded, proto
    global table
    #Chiamare comunque accept della Abstraction...tale funzione overloddata infatti
    #nel caso del TCP restituirá un socket.socket nell'UDP lascerá Abstract
    #cos¡ gestendo la nuova classe come fosse un generico socket TCP...
    #connect della Abstraction fa continuare ad agire sull'istanza Abstraction

#TODO: TUTTO
def handle_command(C,cmd):
    #TODO: rendere magari permanenti alcuni port forward mediante un file caricato all'avvio del modulo
    global table
    func,args=common.extract_funcargstuple(cmd)
    if func=='INFO':
    	C.send('TCP/UDP Port Forwarding Module\n*************************************\n')
    	C.send('#FORWARD $localport#int $destip#ip $destport#int $proto#bool\n')
    	C.send('proto is 0 for TCP 1 for UDP\n')
    	C.send('#DELETE $entry_num#int\n')
    	C.send('#SHOW\n'
    	C.send('Shows the Active Forwarding Entries\r\n')
    elif func=='FORWARD':
    	ex=re.match('^([0-9]{1,5}) ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}) ([0-9]{1,5}) (0|1)$',args)
    	if not ex:
    	    C.send_error('Invalid Arguments.')
    	    return True
    	ID=len(table)
    	if proto:
    	    sox=socket.socket(type=socket.SOCK_DGRAM)
    	else
    	    sox=socket.socket(type=socket.SOCK_DGRAM)
    elif func=='DELETE':
    else:
        return False
    return True
    
