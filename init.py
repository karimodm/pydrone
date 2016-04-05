# -*- coding: iso-8859-1 -*-
from __future__ import with_statement
from threading import Thread,Event
from time import sleep
from os import getcwd
import sys
import re
from zipimport import ZipImportError
import common

#TODO MODO PER RIPORTARE ALLO STATO DI FABBRICA
continue_event=None

def Forker(*args):
	execfile(args[0],globals())

def initialize_drone():
    global continue_event
    common.plugins=[]
    common.drone_dir=getcwd()+'/'
    common.kill_myself=0
    common.kill_restart=0
    continue_event=Event()
    with open(common.plugs_file,"r") as fd:
	for plugin in fd.readlines():
	    if plugin[0:2]=='P:':
		location=plugin[2:].strip('\n').strip('\r')
		try:
		    common.unzip_dynamic(location)
		    sys.path.append(location)
		except ZipImportError: # Package deleted uncleanely
		    pass
	    else:
		try:
		    common.plugins.append(__import__(plugin.strip('\n').strip('\r')))
		    # Caricato, ma vediamo se ha le basi per un plugin...
		    # I __SYSTEM avranno il "pass", ma un plugin sempre si considera accettare comandi (almeno un help)
		    cur=len(common.plugins)-1
		    if not "handle_command" in dir(common.plugins[cur]): 
			del common.plugins[cur]
		    x=re.match('^.+/([^\.]+\.zip)/[^/]+$',common.plugins[cur].__file__)
		    if x: common.plugins[cur].package=x.group(1)
		    else: common.plugins[cur].package='*NP*'
		except ImportError:
		    pass
		
    continue_event.set()
    bind=Thread(name="Bind Main Thread",target=Forker,args=("base_bind.py",))
    reverse=Thread(name="Reverse Main Thread",target=Forker,args=("base_reverse.py",))
    bind.start(); reverse.start() 
    while not common.kill_myself:
	sleep(2)
    return common.kill_restart
    