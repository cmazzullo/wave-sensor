import os
import sys
import pytz
import pandas
import re
import numpy as np

sys.path.append('..')

import NetCDF_Utils.DateTimeConvert as dateconvert
from NetCDF_Utils.Testing import DataTests
from NetCDF_Utils.edit_netcdf import NetCDFWriter 
   

class RBRSolo(NetCDFWriter):
    '''derived class for RBR solo engineer text files, (exported via ruskin software)
    '''
    def __init__(self):
        self.timezone_marker = "time zone"      
        super().__init__()
        
        self.tz_info = pytz.timezone("US/Eastern")
        self.frequency = 4
        self.date_format_string = '%d-%b-%Y %H:%M:%S.%f'  
        self.data_tests = DataTests()
        
    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        skip_index = self.read_start('^[0-9]{2}-[A-Z]{1}[a-z]{2,8}-[0-9]{4}$',' ')
        #for skipping lines in case there is calibration header data
        df = pandas.read_csv(self.in_filename,skiprows=skip_index, delim_whitespace=True, \
                            header=None, engine='c', usecols=[0,1,2])
        
        #This gets the date and time since they are in two separate columns
        self.utc_millisecond_data = dateconvert.convert_to_milliseconds(df.shape[0] - 1, \
                                                            ('%s %s' % (df[0][0],df[1][0])), \
                                                            self.date_format_string, self.frequency)
               
        self.pressure_data = [x for x in df[2][:-1]]
       
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
    
    def write(self):
        self.vstore.pressure_data = self.pressure_data
        self.vstore.utc_millisecond_data = self.utc_millisecond_data
        self.vstore.latitutde = self.latitude
        self.vstore.longitude = self.longitude
#       
        #Tests#
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')
        
        self.write_netCDF(self.vstore, len(self.pressure_data))      

if __name__ == "__main__":
    
    #--create an instance    
    lt = RBRSolo()        
    lt.creator_email = "a@aol.com"
    lt.creator_name = "Jurgen Klinnsmen"
    lt.creator_url = "www.test.com"
    #--for testing
    lt.in_filename = os.path.join("Instruments","benchmark","RBR_RSK.txt")
    lt.out_filename = os.path.join("Instruments","benchmark","RBRrsk.nc")
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
    
    
