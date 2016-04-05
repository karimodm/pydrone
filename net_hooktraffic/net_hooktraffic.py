# -*- coding: iso-8859-1 -*-
# Hook Traffic Plugin
# *******************
# through libcap captures the user->router router->user http traffic
# the DLL (pyd) part should be compiled accordingly to underlying
# operating system.

import re
import common
import hooktraffic

hooked=False
cur_filter=None

def handle_command(C,cmd):
    global hooked,cur_filter
    (func,args)=common.extract_funcargstuple(cmd)
    if func=='INFO':
	C.send("Hook Traffic Plugin\n********************\n")
	C.send('#START_HOOK $pcapfilter#str\n')
	C.send('#STOP_HOOK\n')
	C.send('This Plugin, due to his Ideation, is Unable to determine the successfulness of an Operation.\r\n')
    elif func=='START_HOOK':
	ex=re.match('^\"[^\"]+\"$',args)
	if not ex: # if not only one string between ""...
	    C.send_error('Invalid Syntax')
	    return True
	if hooked:
	    C.send_error('A previous Hook was Set with Filter: '+cur_filter)
	    return True
	hooktraffic.start_hook(args.strip('"'))
	hooked=True
	cur_filter=args
	C.send_warning('Unable do Determinate if Succesfull (check creation of a hook_<time>.cap file).')
	return True
    elif func=='STOP_HOOK':
	hooktraffic.stop_hook()
	hooked=False
	cur_filter=None
	C.send_warning('Unable do Determinate if Succesfull.')
	return True
    else:
	return False
    return True
    