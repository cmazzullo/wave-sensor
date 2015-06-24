import os
import pytz
import pandas
import re
from unit_conversion import PSI_TO_DBAR

#--some import error trapping
try:
    import numpy as np
except:
    raise Exception("numpy is required")

import NetCDF_Utils.DateTimeConvert as dateconvert
from NetCDF_Utils.Testing import DataTests
from NetCDF_Utils.edit_netcdf import NetCDFWriter

class MeasureSysLogger(NetCDFWriter):
    '''derived class for Measurement Systems cvs files
    '''
    def __init__(self):
        self.timezone_marker = "time zone"
        super(MeasureSysLogger,self).__init__()
        self.tz_info = pytz.timezone("US/Eastern")
        self.frequency = 4
        self.date_format_string = '%m/%d/%Y %I:%M:%S.%f %p'
        self.data_tests = DataTests()

    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        skip_index = self.read_start('^ID$',',')
        #for skipping lines in case there is calibration header data
        df = pandas.read_table(self.in_filename,skiprows=skip_index + 1, header=None, engine='c', sep=',', usecols=[3,4,5,6])

        #right now getting from the third and fourth point because the firmware upgrade skips a measurement in the first
        self.data_start = dateconvert.convert_date_to_milliseconds(df[3][3][1:],
                                                   self.date_format_string)
        second_stamp = dateconvert.convert_date_to_milliseconds(df[3][4][1:],
                                                    self.date_format_string)
        self.frequency = 1000 / (second_stamp - self.data_start)
        print('freq',self.frequency)
        #Since the instrument is not reliably recording data at 4hz we have decided to
        #interpolate the data to avoid any potential complications in future data analysis
        self.pressure_data = df[5].values * PSI_TO_DBAR

        self.utc_millisecond_data = dateconvert.convert_to_milliseconds(df.shape[0], \
                                                            ('%s' % (df[3][0][1:])), \
                                                            self.date_format_string, self.frequency)

#         self.pressure_data = np.interp(self.utc_millisecond_data, original_dates, instrument_pressure)

        if re.match('^[0-9]{1,3}.[0-9]+$', str(df[6][0])):
            self.temperature_data = [x for x in df[6]]

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
        
        time_resolution = 1000 / (self.frequency * 1000)
        self.vstore.time_coverage_resolution = ''.join(["P",str(time_resolution),"S"])

        #Tests#
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')

        self.write_netCDF(self.vstore, len(self.pressure_data))

if __name__ == "__main__":

    #--create an instance
    lt = MeasureSysLogger()
    lt.creator_email = "a@aol.com"
    lt.creator_name = "Jurgen Klinnsmen"
    lt.creator_url = "www.test.com"
    #--for testing
    lt.in_filename = "measure.csv"
    lt.out_filename = "measure_special2.csv.nc"
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
