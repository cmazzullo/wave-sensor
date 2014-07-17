'''
Created on Jul 9, 2014

@author: Gregory
'''
'''
Created on Jun 20, 2014

@author: Gregory
'''
from Instruments.sensor import Sensor
from Instruments.InstrumentTests import PressureTests
import os
import sys
from datetime import datetime
import pytz
import pandas
import re
import netCDF4

import sys
sys.path.append('..')

#--python 3 compatibility
pyver = sys.version_info
if pyver[0] == 3:
    raw_input = input

#--some import error trapping
try:
    import numpy as np
except:
    raise Exception("numpy is required")
try:        
    import netCDF4
except:
    raise Exception("netCDF4 is required")        

class MeasureSysLogger(Sensor, PressureTests):
    '''derived class for leveltroll ascii files
    '''
    def __init__(self):
        self.timezone_marker = "time zone"      
        super(MeasureSysLogger,self).__init__()
        self.tz_info = pytz.timezone("US/Eastern")
        self.frequency = 4
        self.date_format_string = '%m/%d/%Y %H:%M:%S.%f %p'  
        
    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        skip_index = self.read_start('^ID$',',')
        #for skipping lines in case there is calibration header data
        df = pandas.read_table(self.in_filename,skiprows=skip_index + 1, header=None, engine='c', sep=',', usecols=[3,4,5,6])
       
        first_date = df[3][0][1:]
        self.data_start = self.convert_date_to_milliseconds(first_date)
        self.utc_millisecond_data = [(x * 1000) + self.data_start for x in df[4]]
       
#         self.utc_millisecond_data = self.convert_to_milliseconds(df.shape - 1, \
#                                                                          ('%s %s' % (x[1],x[2])))
#                 break
        
        self.pressure_data = [x / 14.5037738 for x in df[5]]
        print(df[6][0])
        print(len(str(df[6][0])))
        if re.match('^[0-9]{1,3}.[0-9]+$', str(df[6][0])):
            self.temperature_data = [x for x in df[6]]
            
        self.data_end_date = self.convert_milliseconds_to_datetime(self.utc_millisecond_data[::-1][0])
       
        self.get_time_duration(self.utc_millisecond_data[::-1][0] - self.utc_millisecond_data[0])
        self.test_16_stucksensor()
        self.test_17_frequencyrange()
        self.test_20_rateofchange()
        self.get_15_value()
        print(len(self.pressure_data))
        
    def read_start(self, expression, delimeter):
        skip_index = 0;
        with open(self.in_filename,'r') as fileText:
            for x in fileText:
                file_string = x.split(delimeter)[0]
                if re.match(expression, file_string):
                    print('Success! Index %s' % skip_index)
                    break
                skip_index += 1   
        return skip_index 
    
    @property    
    def offset_seconds(self):
        '''offsets seconds from specified epoch using UTC time
        '''        
        offset = self.data_start - self.epoch_start            
        return offset.total_seconds()      

if __name__ == "__main__":
    
    #--create an instance    
    lt = MeasureSysLogger()        
    lt.creator_email = "a@aol.com"
    lt.creator_name = "Jurgen Klinnsmen"
    lt.creator_url = "www.test.com"
    #--for testing
    lt.in_filename = os.path.join("benchmark","logger1.csv")
    lt.out_filename = os.path.join("benchmark","infosys2.nc")
    if os.path.exists(lt.out_filename):
        os.remove(lt.out_filename)
    lt.is_baro = True
    lt.pressure_units = "psi"
    lt.z_units = "meters"
    lt.longitude = np.float32(0.0)
    lt.latitude = np.float(0.0)
    lt.salinity_ppm = np.float32(0.0)
    lt.z = np.float32(0.0)
    
    #--get input
    #lt.get_user_input()
    
    #--read the ASCII level troll file
    lt.read()    

    #--write the netcdf file
    lt.write()
    
    
