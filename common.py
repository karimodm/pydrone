# -*- coding: iso-8859-1 -*-
from __future__ import with_statement
import re
import zipimport 

plugs_file='pydrone_plugins.txt'

def extract_funcargstuple(s):
    split=re.match("([^ ]+)( .+)?",s)
    if not split: return (None,None)
    func=split.group(1)
    try:
	args=split.group(2).strip()
    except AttributeError:
	args=None
    return (func,args)
    
def unzip_dynamic(archive):
    zip=zipimport.zipimporter(archive)
    for item in zip._files:
	if item[-3:]=='.so' or item[-4:]=='.pyd':
	    with open(drone_dir+item,"wb") as fd: fd.write(zip.get_data(item))
