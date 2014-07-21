'''
Created on Jul 14, 2014

@author: Gregory
'''

import netCDF4
import numpy as np
import pandas as pd
import os
import re
import pytz
from datetime import datetime

class NetCDFReader(object):
    
    def __init__(self):
        self.in_file_name = os.path.join("benchmark","RBRtester2.nc")
        self.file_names = None
        self.pressure_frame = None
        self.temperature_frame = None
        self.series = None
        self.dataframe_vals = dict()
        self.dataframe = None
        self.epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
    
      
    def read_file(self,file_name,pressure_bool = True, series_bool = True, milliseconds_bool = False):
        
        nc = netCDF4.Dataset(file_name)
        times = nc.variables['time']
        
        temperature = None
        pressure = nc.variables['sea_water_pressure']
        #checks to see if ther is temperature or not
        if str(nc.variables.keys).find('temperature_at_transducer') != -1:
                temperature = nc.variables['temperature_at_transducer']
      
        #this method converts the milliseconds in to date times
        time_convert = netCDF4.num2date(times[:],times.units)
        if milliseconds_bool == True:
            return self.return_data(pressure, temperature, times, series_bool, pressure_bool)
        else:
            return self.return_data(pressure, temperature, time_convert, series_bool, pressure_bool)
        
    def return_data(self, pressure, temperature, index, series_bool, pressure_bool):
        if series_bool == True:
            if pressure_bool == True:
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

class NEtCDFEditor(object):
    
    def __init__(self):
        self.dataset = None
        self.datetime_data = None
        self.pressure_data = None
        self.temperature_data = None
        self.in_file_name = os.path.join("benchmark","RBRtester2.nc")
    
    def readedit_file(self, file_name):
        print(file_name)
        nc = netCDF4.Dataset(file_name,mode = 'r+',format = 'NETCDF4_CLASSIC')
        self.dataset = nc
        self.datetime_data = nc.variables['time']
        
        self.pressure_data = nc.variables['sea_water_pressure']
        #checks to see if there is temperature or not
        if str(nc.variables.keys).find('temperature_at_transducer') != -1:
                self.temperature_data = nc.variables['temperature_at_transducer']
      
        #this method converts the milliseconds in to date times
        #self.datetime_data = netCDF4.num2date(times[:],times.units)
        
    def edit_pressure(self, pressure_change_dict = dict()):
        if(len(pressure_change_dict) > 0):
            for x in pressure_change_dict:
                self.pressure_data[x] = pressure_change_dict[x]
                
    def edit_temperature(self, temperature_change_dict = dict()):
        if(len(temperature_change_dict) > 0):
            for x in temperature_change_dict:
                self.temperature_data[x] = temperature_change_dict[x]
        
    def edit_times(self, time_change_dict = dict()):
        if(len(time_change_dict) > 0):
            for x in time_change_dict:
                self.datetime_data[x] = time_change_dict[x]
        
                
    def close_file(self):
        self.dataset.close()
        
class NetCDFWriter(object):
    
    def __init__(self):
        self.pressure_comments = None
        self.temperature_comments = None
        self.depth_comments = None
        self.out_filename = os.path.join('benchmark','DepthTest.nc')

    def write_netCDF(self,var_datastore,series_length):
        ds = netCDF4.Dataset(os.path.join('benchmark','DepthTest.nc'),'w',format="NETCDF4_CLASSIC")
        time_dimen = ds.createDimension("time",series_length)
        var_datastore.send_data(ds)
        
if __name__ == "__main__":
    
    #--create an instance    
    editor = NEtCDFEditor()
    editor.readedit_file(editor.in_file_name)
    print('first run through...')
    for x in range(0,4):
        print (x, editor.datetime_data[x])
    print('changing values in file...')
    change_dict = {1: np.float64(1399977901500), 2: np.float64(1399977903000), 3:np.float64(1499977903000)}
    editor.edit_times(change_dict)
    print('second run through...')
    for x in range(0,4):
            print (x, editor.datetime_data[x])
    