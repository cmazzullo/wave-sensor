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
        self.series = None
        self.dataframe_vals = dict()
        self.dataframe = None
        
        
    def read_file(self,x):
        nc = netCDF4.Dataset(x)
        
        pressure = nc.variables['sea_water_pressure']
        times = nc.variables['time']
        #this method converts the milliseconds in to date times
        time_convert = netCDF4.num2date(times[:],times.units)
        
#         if str(nc.variables.keys).find('temperature_at_transducer') != -1:
#             print('found')
#             temperature = nc.variables['temperature_at_transducer']
#             data = {'pressure': pd.Series(pressure,index=time_convert), \
#                     'temperature': pd.Series(temperature,index=time_convert)}
#             return pd.DataFrame(data)
#         else:
        return pd.Series(pressure,index=time_convert)
        
    def get_series(self, filename):
        return self.read_file(filename)
    
    def get_dataframe(self):
        for x in self.file_names:
            self.dataframe_vals[x] = self.read_file(x)
        self.dataframe = pd.DataFrame(self.dataframe_vals)
        
if __name__ == "__main__":
    
    #--create an instance    
    editor = NetCDFReader()
    editor.read_file()