# -*- coding: iso-8859-1 -*-
from __future__ import with_statement
from time import sleep
from drone import main as drone_main
import socket

class BindNoReset(Exception):
        pass

while True:
        print "BASE_BIND"
	try:
        	sox=s.accept()[0]
	except (socket.error,NameError):
	        s=socket.socket()
		try:
	        	s.bind(('',5337)) # 5337 SEED
			s.listen(2)
		except socket.error:
			s.close()
			sleep(3)
		continue
        try:
                if not continue_event.isSet():
                        raise BindNoReset
                continue_event.clear()
                drone_main(sox)
        except KeyboardInterrupt:
                pdb.set_trace()
        except BindNoReset:
                pass
        except:
                continue_event.set()
        finally:
                sox.close()
