'''
Created on Jul 7, 2014

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

class House(Sensor, PressureTests):
    '''derived class for house ascii files
    '''
    def __init__(self):
        self.timezone_marker = "time zone"   
        self.temperature_data = None   
        super(House,self).__init__()
        self.tz_info = pytz.timezone("US/Eastern")
        self.frequency = 4
       
        self.date_format_string = '%Y.%m.%d %H:%M:%S '
    

    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
       
        skip_index = self.read_start('^[0-9]{4},[0-9]{4}$',' ') 
        df = pandas.read_table(self.in_filename,skiprows=skip_index, header=None, engine='c', sep=',', names=('a','b'))
       
        self.pressure_data = [self.pressure_convert(np.float64(x)) for x in df[df.b.isnull() == False].a]
        self.temperature_data = [self.temperature_convert(np.float64(x)) for x in df[df.b.isnull() == False].b]
            
        with open(self.in_filename, 'r') as wavelog:
            for x in wavelog:
                if re.match('^[0-9]{4}.[0-9]{2}.[0-9]{2}', x):
                    self.utc_millisecond_data = self.convert_to_milliseconds(len(self.pressure_data), x) #second arg has extra space that is unnecessary
                    break
       
        self.data_end_date = self.convert_milliseconds_to_datetime(self.utc_millisecond_data[::-1][0])
        print('time', self.utc_millisecond_data[::-1][0], self.utc_millisecond_data[0])
        self.get_time_duration(self.utc_millisecond_data[::-1][0] - self.utc_millisecond_data[0])
        self.test_16_stucksensor()
        self.test_17_frequencyrange()
        self.test_20_rateofchange()
        self.get_15_value()
        
    def pressure_convert(self, x):
        # gets volt to psig
        # gets psig to pascals
        return ((x * (30 / 8184) - 6) + 14.7) * 6894.75729
    
    def temperature_convert(self, x):
        # gets volts to farenheit
        # gets farenheit to celsius
        return (x * (168 / 8184) - 32) * (5.0/9)
    
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

if __name__ == "__main__":
    
    #--create an instance    
    lt = House()        
    lt.creator_email = "a@aol.com"
    lt.creator_name = "Jurgen Klinnsmen"
    lt.creator_url = "www.test.com"
    #--for testing
    lt.in_filename = 'C:\\Users\\Gregory\\Documents\\GitHub\\WaveLog.csv'
    #os.path.join("benchmark","WaveLog.csv")
    lt.out_filename = os.path.join("benchmark","WaveLog.nc")
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
    
    
