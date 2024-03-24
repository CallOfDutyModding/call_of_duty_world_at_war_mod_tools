#####################################################################################################################################################
# Copyright (c) 2006 Activision, Inc
#   Confidential Information of Activision.
#   Not for disclosure or distribution without Activision's prior written consent.
#####################################################################################################################################################

#!/usr/bin/env python

from distutils.core import setup
import sys,os,py2exe


name = sys.argv[1]
sys.argv[1] = 'py2exe'
sys.path.append(os.path.dirname(os.path.abspath(name)))

print name

options = {
        "bundle_files": 1, # create singlefile exe
        "compressed": 1, # compress the library archive
        "optimize": 2,
        "dll_excludes": ["w9xpopen.exe"], # we don't need this
        "dist_dir":os.path.dirname(os.path.abspath(name)),
        }
    
setup(
    options = {"py2exe": options},
    name = name[:-3],   
    zipfile = None, 
    console=[name],
    )


