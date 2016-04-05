# -*- coding: iso-8859-1 -*-
import common
from threading import Thread
import ftpserver
import socket
#TODO: pdb
import pdb

yet=None
t=None 

def ftp_jumper(arg):
    ftpserver.RUNNING=True
    arg[0].serve_forever()

def handle_command(C,cmd):
    global yet,t
    #TODO: pdb
    pdb.set_trace()
    func,args=common.extract_funcargstuple(cmd)
    if func=='INFO':
        C.send('FTP BiPlex Server Plugin\n***************************\n')
        C.send('#START_FTP $localport#int $reverse#bool $remoteip#ip $remoteport#int\n')
        C.send('Se il parametro reverse è falso remoteip e remoteport verranno ignorati ma dovranno comunque avere un formato valido. Solo un server alla volta è ammesso.\n')
        C.send('#STOP_FTP\n')
        C.send('#STATUS\r\n')
        return True
    elif func=='START_FTP':
        ex=re.match('^([0-9]+) (0|1) ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}) ([0-9]+)$',args)
        if not ex:
            C.send_error('Invalid Parameters')
            return True
        if yet:
            C.send_error('FTP Server Yet Started '+yet)
            return True 
        ftp_handler=ftpserver.FTPHandler
        ftp_handler.authorizer=ftpserver.DummyAuthorizer().add_anonymous('/')
        if ex.group(2)=='1': 
            yet='Reversed on '+ex.group(3)+':'+ex.group(4)
            reverse=True
        else:
            yet='Locally on 127.0.0.1:'+ex.group(1)
            reverse=False
        ftpd=ftpserver.FTPServer(("127.0.0.1",ex.group(1)),ftp_handler,reverse,(ex.group(3),ex.group(4)))
        t=Thread(target=ftp_jumper,args=(ftpd,))
        t.start()
	# If Reversed stimulate connect
	if reverse:
	    sox=socket.socket()
	    sox.connect(('127.0.0.1',ex.group(1)))
	    sox.close()
        C.send_ok('FTP Server Succesfully Started '+yet)
        return True
    elif func=='STOP_FTP':
        ftpserver.RUNNING=False
        t=None
        yet=None
        C.send_ok('Succesfully Stopped FTP Server.')
        return True
    elif func=='STATUS':
        if yet: C.send_ok('FTP Server Running %s.' % yet)
        else: C.send_ok('FTP Server not Running.')
        return True
    else:
        return False
