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
        self.in_file_name = os.path.join("benchmark","Neag2-1.nc")
        self.pressure_frame = None
        self.temperature_frame = None
        self.series = None
        self.dataframe_vals = dict()
        self.dataframe = None
        
        
    def read_file(self,x,pressure_bool, series_bool):
        
        nc = netCDF4.Dataset(x)
        times = nc.variables['time']
        
        temperature = None
        pressure = nc.variables['sea_water_pressure']
        #checks to see if ther is temperature or not
        if str(nc.variables.keys).find('temperature_at_transducer') != -1:
                temperature = nc.variables['temperature_at_transducer']
      
        #this method converts the milliseconds in to date times
        time_convert = netCDF4.num2date(times[:],times.units)
        if series_bool == True:
            if pressure_bool == True:
                return pd.Series(pressure,index=time_convert)
            else:
                if temperature != None:
                    return pd.Series(temperature,index=time_convert)
                else: return None
        else:
            if temperature != None:
                data = {'pressure': pd.Series(pressure,index=time_convert), \
                        'temperature': pd.Series(temperature,index=time_convert)}
                return pd.DataFrame(data)
            else:
                return pd.DataFrame({'pressure': pd.Series(pressure,index=time_convert)})
        
    def get_series(self, filename):
        return self.read_file(filename)
    
    def get_pressures_only_dataframe(self):
        for x in self.file_names:
            self.dataframe_vals[x] = self.read_file(x, True, True)
        self.dataframe = pd.DataFrame(self.dataframe_vals)
        
    def get_temperatures_only_dataframe(self):
        for x in self.file_names:
            self.dataframe_vals[x] = self.read_file(x, False, True)
        self.dataframe = pd.DataFrame(self.dataframe_vals)
        
    def get_pressure_temperature_data(self):
        for x in self.file_names:
            self.dataframe_vals[x] = self.read_file(x, True, True)
        self.pressure_frame = pd.DataFrame(self.dataframe_vals)
        self.dataframe_vals = dict()
        for x in self.file_names:
            self.dataframe_vals[x] = self.read_file(x, False, True)
        self.temperature_frame = pd.DataFrame(self.dataframe_vals)
        
if __name__ == "__main__":
    
    #--create an instance    
    editor = NetCDFReader()
    editor.read_file(editor.in_file_name)