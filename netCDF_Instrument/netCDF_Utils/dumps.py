'''
Created on Apr 21, 2016

@author: chogg
'''

import os
print(os.environ)
import nco

os.environ['NCOpath'] = 'C:\\nco'

def nc_dump(command):
    nc_obj = nco.Nco()
    nc_obj.ncdump(command)

