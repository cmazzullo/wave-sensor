'''
Created on Jul 14, 2014

@author: Gregory
'''

import netCDF4
import numpy as np
import pandas as pd
import os
import re

class NetCDFReader(object):
    
    def __init__(self):
        self.in_file_name = os.path.join("benchmark","WaveLog.nc")
        self.pressure_data = None
        
        
    def read_file(self):
        nc = netCDF4.Dataset(self.in_file_name)
#         for p in nc.variables.keys():
#             print(p)
        pressure = nc.variables['sea_water_pressure']
        times = nc.variables['time']
        time_convert = netCDF4.num2date(times[:],'milliseconds since 1970-01-01 00:00:00')
        
        if str(nc.variables.keys).find('temperature_at_transducer') != -1:
            print('found')
            temperature = nc.variables['temperature_at_transducer']
            data = {'pressure': pd.Series(pressure,index=time_convert), \
                    'temperature': pd.Series(temperature,index=time_convert)}
            self.pressure_data = pd.DataFrame(data)
        else:
            self.pressure_data = pd.Series(pressure,index=time_convert)
        
        
       
        
        
if __name__ == "__main__":
    
    #--create an instance    
    editor = NetCDFReader()
    editor.read_file()