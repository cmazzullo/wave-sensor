# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 13:11:49 2014

@author: cmazzullo
"""

import netCDF4
import numpy as np
import pandas as pd
import os
import pytz
from datetime import datetime


class NetCDFReader(object):
    
    def __init__(self):
        self.in_file_name = os.path.join("..\Instruments","benchmark","RBRtester2.nc")
        self.file_names = None
        self.pressure_frame = None
        self.temperature_frame = None
        self.series = None
        self.dataframe_vals = dict()
        self.dataframe = None
        self.epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
        self.latitude = None
        self.longitude = None
    
      
    def read_file(self,file_name,pressure_bool = True, series_bool = True, milliseconds_bool = False):
        
        nc = netCDF4.Dataset(file_name)
        times = nc.variables['time']
        
        temperature = None
        pressure = nc.variables['sea_water_pressure']
        latitude = nc.variables['latitude']
        self.latitude = latitude[:]
        longitude = nc.variables['longitude']
        self.longitude = longitude[:]
       
        print(self.latitude,self.longitude)
        #checks to see if ther is temperature or not
        if str(nc.variables.keys).find('temperature_at_transducer') != -1:
                temperature = nc.variables['temperature_at_transducer']
      
        #this method converts the milliseconds in to date times
        time_convert = netCDF4.num2date(times[:],times.units)
        if milliseconds_bool == True:
            return self.return_data(pressure, temperature, times, series_bool, pressure_bool, True)
        else:
            return self.return_data(pressure, temperature, time_convert, series_bool, pressure_bool)
        
    def return_data(self, pressure, temperature, index, series_bool, pressure_bool, milli_bool = False):
        if series_bool == True:
            if milli_bool == True:
                if type(index) != 'datetime.datetime':  # PAndas series cannot take a long as an index
                    index = np.divide(index,1000)
                return pd.Series(pressure,index=index)
            else:
                if temperature != None:
                    return pd.Series(temperature,index=index)
                else: return None
        else:
            if temperature != None:
                data = {'pressure': pd.Series(pressure,index=index), \
                        'temperature': pd.Series(temperature,index=index)}
                return pd.DataFrame(data)
            else:
                data = pd.DataFrame({'pressure': pd.Series(pressure,index=index)})
                return data
        
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
