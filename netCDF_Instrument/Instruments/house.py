import os
import sys
import pytz
import pandas
import re
from datetime import datetime

#--python 3 compatibility
pyver = sys.version_info
if pyver[0] == 3:
    raw_input = input

#--some import error trapping
try:
    import numpy as np
except:
    raise Exception("numpy is required")

import NetCDF_Utils.DateTimeConvert as dateconvert
from NetCDF_Utils.Testing import DataTests
from NetCDF_Utils.edit_netcdf import NetCDFWriter 

        
class House(NetCDFWriter):
    '''derived class for house csv files
    '''
    def __init__(self):
        self.timezone_marker = "time zone"   
        self.temperature_data = None   
        super(House,self).__init__()
        self.tz_info = pytz.timezone("US/Eastern")
        self.frequency = 4
       
        self.date_format_string = '%Y.%m.%d %H:%M:%S '
        self.data_tests = DataTests() 
        self.transducer_distance_from_seabed = [0,0]
        self.reference_point_distance_to_transducer = [0,0]
        self.deployment_time = datetime.now(tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.retrieval_time = datetime.now(tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    

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
                    self.utc_millisecond_data = dateconvert.convert_to_milliseconds(len(self.pressure_data), x, \
                                                                        self.date_format_string, self.frequency) #second arg has extra space that is unnecessary
                    break
       
        print(len(self.pressure_data))
        
    def pressure_convert(self, x):
        # gets volt to psig
        # gets psig to pascals
        return ((x * (30 / 8184) - 6) + 14.7) / 1.45037738
    
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
    
    def write(self, sea_pressure = True):
        '''Write netCDF files
        
        sea_pressure - if true write sea_pressure data, otherwise write air_pressure data'''
        
        if sea_pressure == False:
            self.vstore.pressure_name = "air_pressure"
            self.vstore.pressure_var['standard_name'] = "air_pressure"
        else:
            self.vstore.global_vars_dict['distance_from_referencepoint_to_transducer'] = \
            'When Deployed: %s - When Retrieved: %s' % (self.reference_point_distance_to_transducer[0], \
                                                        self.reference_point_distance_to_transducer[1])
            self.vstore.global_vars_dict['distance_from_transducer_to_seabed'] = \
            'When Deployed: %s - When Retrieved: %s' % (self.transducer_distance_from_seabed[0],self.transducer_distance_from_seabed[1])
            self.vstore.global_vars_dict['time_of_deployment'] = self.deployment_time
            self.vstore.global_vars_dict['time_of_retrieval'] = self.retrieval_time
        self.vstore.pressure_data = self.pressure_data
        self.vstore.utc_millisecond_data = self.utc_millisecond_data
        self.vstore.latitutde = self.latitude
        self.vstore.longitude = self.longitude
       
        #Tests#
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')
        
        self.write_netCDF(self.vstore, len(self.pressure_data)) 

if __name__ == "__main__":
    
    #--create an instance    
    lt = House()        
    lt.creator_email = "a@aol.com"
    lt.creator_name = "Jurgen Klinnsmen"
    lt.creator_url = "www.test.com"
    #--for testing
    lt.in_filename = os.path.join("benchmark","NEAG2_716.csv")
    #os.path.join("benchmark","WaveLog.csv")
    lt.out_filename = os.path.join("benchmark","NEAG2_716.nc")
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
    
    
