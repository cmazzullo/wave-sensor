'''
Created on Jun 20, 2014

@author: Gregory
'''
from Instruments.sensor import Sensor
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

class RBRSolo(Sensor):
    '''derived class for leveltroll ascii files
    '''
    def __init__(self):
        self.timezone_marker = "time zone"      
        super(RBRSolo,self).__init__()
    

    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        self.tz_info = pytz.timezone("US/Eastern")
        self.frequency = 4
        self.local_frequency_range = [11, 19] # for IOOS test 17
        self.mfg_frequency_range = [10, 20] # for IOOS test 17
        self.max_rate_of_change = 20
        self.prev_value = True # for IOOS test 20
        self.date_format_string = '%d-%b-%Y %H:%M:%S.%f'  
        skip_index = self.read_start('^[0-9]{2}-[A-Z]{1}[a-z]{2,8}-[0-9]{4}$',' ')
        self.five_count_list = list() #for skipping lines in case there is calibration header data
        df= pandas.read_csv(self.in_filename,skiprows=skip_index, delim_whitespace=True, \
                            header=None, engine='c', usecols=[0,1,2])
        for x in df[0:1].itertuples():
            if x[0] == 0:
                self.utc_millisecond_data = self.convert_to_milliseconds(df.shape[0] - 1, \
                                                                         ('%s %s' % (x[1],x[2])))
                break
        
        self.pressure_data = [x[1] for x in df[2][:-1].iteritems()]
        self.data_end_date = self.convert_milliseconds_to_datetime(self.utc_millisecond_data[::-1][0])
        self.get_time_duration(self.utc_millisecond_data[::-1][0] - self.utc_millisecond_data[0])
        self.test_16_stucksensor()
        self.test_17_frequencyrange()
        self.test_20_rateofchange()
        self.get_15_value()
                
    def test_16_stucksensor(self):
        self.pressure_test16_data = [self.get_16_value(x) for x in self.pressure_data]
        
    def test_17_frequencyrange(self):
        self.pressure_test17_data = [self.get_17_value(x) for x in self.pressure_data]
        
    def test_20_rateofchange(self):
        self.pressure_test20_data = [self.get_20_value(x) for x in self.pressure_data]
   
            
    def get_15_value(self):
        print('start mean')
        print('mean', np.mean(self.pressure_data))
        print('mean', np.mean(self.pressure_data))
        
               
    def get_16_value(self,x):
           
           
       
        if len(self.five_count_list) > 5:
            self.five_count_list.pop()
            
        flags = np.count_nonzero(np.equal(x,self.five_count_list))
        self.five_count_list.insert(0,x)
        
        if flags <= 2:
            return 1
        elif flags <= 4:
            return 3
        else:
            return 4  
            
    def get_17_value(self, x):
        
        if np.greater_equal(x,self.local_frequency_range[0]) and \
        np.less_equal(x,self.local_frequency_range[1]):
            return 1
        elif np.greater_equal(x,self.mfg_frequency_range[0]) and \
                            np.less_equal(x,self.mfg_frequency_range[1]):
            return 3
        else:
            return 4
        
    def get_20_value(self, x):
      
        if np.isnan(self.prev_value) or \
        np.less_equal(np.abs(np.subtract(x,self.prev_value)), self.max_rate_of_change):
            self.prev_value = x
            return 1
        else:
            self.prev_value = x
            return 4
        
        
#         mfg_check1 = np.less(self.pressure_data, self.mfg_frequency_range[0])
#         mfg_check2 = np.greater(self.pressure_data, self.mfg_frequency_range[1])
#         mfg_check = [np.maximum(x, y) for x in mfg_check1 for y in mfg_check2]
#         
#         for x in range(0,10):
#             print(mfg_check[x])
#         
#         local_check1 = np.less(self.pressure_data, self.local_frequency_range[0])
#         local_check2 = np.greater(self.pressure_data, self.local_frequency_range[1])
#         local_check = [np.maximum(x, y) for x in local_check1 for y in local_check2]
                
        
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
    lt = RBRSolo()        
    
    #--for testing
    lt.in_filename = os.path.join("benchmark","RBR_RSK.txt")
    lt.out_filename = os.path.join("benchmark","RBR.csv.nc")
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
    
    
