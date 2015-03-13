import os
import pytz
import pandas
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

import NetCDF_Utils.DateTimeConvert as dateconvert
from NetCDF_Utils.Testing import DataTests
from NetCDF_Utils.edit_netcdf import NetCDFWriter


class Hobo(NetCDFWriter):
    '''derived class for hobo csv files
    '''
    def __init__(self):
        self.timezone_marker = "time zone"
        super().__init__()

        self.tz_info = pytz.timezone("US/Eastern")
        self.frequency = 1.0/30.0
        self.date_format_string = '%m/%d/%y %I:%M:%S %p'
        self.data_tests = DataTests()


    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        skip_index = self.read_start('"#"',',')
        # for skipping lines in case there is calibration header data
        df = pandas.read_table(self.in_filename,skiprows=skip_index, header=None, engine='c', sep=',')
        
        #apparently hobos have a mode to measure depth which triggers measurements at 2 second intervals
        #this may be arbitrary but a file with regular 30 second intervals breaks up in to 2 second intervals
        #with blank measurements for pressure at every interval between the initial
        #since we want evenly spaced data and interpolation would be a waste of time we will filter the records that are blank
        print(df[2][0], df[2][1])
        df.dropna()
        
        self.utc_millisecond_data = dateconvert.convert_to_milliseconds(df.shape[0], df[1][0], \
                                                                        self.date_format_string, self.frequency)

        self.pressure_data = [x for x in np.divide(df[2], 1.45037738)]

        print(len(self.pressure_data))


    def read_start(self, expression, delimeter):
        skip_index = 0;
        with open(self.in_filename,'r') as fileText:
            for x in fileText:
                file_string = x.split(delimeter)[0].strip()
                if expression == file_string:
                    print('Success! Index %s' % skip_index)
                    break
                skip_index += 1
        return skip_index + 1


    def write(self, sea_pressure = True):
        '''Write netCDF files

        sea_pressure - if true write sea_pressure data, otherwise write air_pressure data'''
        if sea_pressure == False:
            self.vstore.pressure_name = "air_pressure"
            self.vstore.pressure_var['standard_name'] = "air_pressure"

        self.vstore.pressure_data = self.pressure_data
        self.vstore.utc_millisecond_data = self.utc_millisecond_data
        self.vstore.latitude = self.latitude
        self.vstore.longitude = self.longitude

        #Tests#
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')

        self.write_netCDF(self.vstore, len(self.pressure_data))

if __name__ == "__main__":

    #--create an instance
    lt = Hobo()
    lt.creator_email = "a@aol.com"
    lt.creator_name = "Jurgen Klinnsmen"
    lt.creator_url = "www.test.com"
    #--for testing
    lt.in_filename = os.path.join("benchmark","Hobo.csv")
    lt.out_filename = os.path.join("benchmark","HoboTester.nc")
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
    lt.write(False)
