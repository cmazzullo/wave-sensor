from netCDF4 import Dataset
import numpy as np
import pandas as pd
import os
import pytz
from datetime import datetime
import netCDF4

try:
    from NetCDF_Utils.VarDatastore import DataStore
    from NetCDF_Utils.Testing import DataTests
except:
    print('Check Packaging')

class NetCDFReader(object):
    """Reads netcdf4 file"""

    def __init__(self):
        self.in_file_name = os.path.join("..\\Instruments","benchmark","RBRtester2.nc")
        self.file_names = None
        self.pressure_frame = None
        self.temperature_frame = None
        self.series = None
        self.dataframe_vals = dict()
        self.dataframe = None
        self.epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
        self.latitude = None
        self.longitude = None
        self.pressure_data = None
        self.pressure_qc = None
        self.air_pressure_data = None
        self.depth_data = None
        self.times = None

    def get_test_data(self, file_name, time_convert = False):
        """Read .nc file and set all variables to object properties

        Arguments
        file_name -- location of input file
        time_convert -- boolean whether to convert milliseconds to time
        """
        nc = Dataset(file_name)
        if time_convert:
            self.times = netCDF4.num2date(nc.variables['time'][:],nc.variables['time'].units)
        else:
            self.times = nc.variables['time'][:]
        self.pressure_data = nc.variables['sea_water_pressure'][:]
        self.pressure_qc = nc.variables['pressure_qc'][:]
        self.latitude = nc.variables['latitude'][:]
        self.longitude = nc.variables['longitude'][:]

        try:
            self.air_pressure_data = nc.variables['air_pressure'][:]
        except:
            print('No air pressure')

        try:
            self.depth_data = nc.variables['depth'][:]
        except:
            print('No Depth')
            
        nc.close()

    def read_file(self,file_name,pressure_bool = True, series_bool=True, milliseconds_bool=False):
        """Read a .nc file

        pressure_bool -- get pressure, otherwise get temperature
        series_bool -- get a series, otherwise get a dataframe
        milliseconds_bool -- get milliseconds as index (divide by 100 since panda series cannot take longs as indexes,
        otherwise convert to datetime"""

        nc = Dataset(file_name)
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
        print('milliseconds_bool =', milliseconds_bool)
        if milliseconds_bool:
            time_array = times[:]
            index = pd.Index(time_array)
            pressure_array = pressure[:]
            return self.return_data(pressure_array, temperature, index, series_bool, pressure_bool, True)
        else:
            return self.return_data(pressure, temperature, time_convert, series_bool, pressure_bool)

    def return_data(self, pressure, temperature, index, series_bool, pressure_bool, milli_bool = False):
        """Read a .nc file

        pressure_bool -- get pressure, otherwise get temperature
        series_bool -- get a series, otherwise get a dataframe
        milliseconds_bool -- get milliseconds as index (divide by 100 since panda series cannot take longs as indexes,
        otherwise convert to datetime"""
        if series_bool == True:
            if milli_bool == True:
                print('pressure type =', type(pressure))
                print(type(pressure[0]))
                print('index type =', type(index))
                print(type(index[0]))
                if type(index) != 'datetime.datetime':  # PAndas series cannot take a long as an index
                    print('index != datetime.datetime')
                    #index = np.divide(index, 1000)
                print(len(pressure), len(index))
                ts = pd.Series(pressure, index=index)
                return ts
            else:
                if temperature != None:
                    print('this file contains temperature')
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


class NetCDFWriter(object):

    def __init__(self):
        self.pressure_comments = None
        self.temperature_comments = None
        self.depth_comments = None
        self.out_filename = os.path.join("..\\Instruments",'benchmark','DepthTest.nc')
        self.in_filename = None
        self.is_baro = None
        self.pressure_units = None
        self.z_units = 'meters'
        self.latitude = 0
        self.longitude = 0
        self.z = 0
        self.salinity = -1.0e+10
        self.utc_millisecond_data = None
        self.pressure_data = None
        self.presure_data_flags = None
        self.epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
        self.data_start = None
        self.timezone_string = None
        self.tz_info = pytz.timezone('US/Eastern')
        self.date_format_string = None
        self.frequency = None
        self.valid_pressure_units = ["psi","pascals","atm"]
        self.valid_z_units = ["meters","feet"]
        self.valid_latitude = (np.float32(-90),np.float32(90))
        self.valid_longitude = (np.float32(-180),np.float32(180))
        self.valid_z = (np.float32(-10000),np.float32(10000))
        self.valid_salinity = (np.float32(0.0),np.float32(40000))
        self.valid_pressure = (np.float32(-10000),np.float32(10000))
        self.valid_temp = (np.float32(-10000), np.float32(10000))
        self.fill_value = np.float64(-1.0e+10)
        self.creator_name = ""
        self.creator_email = ""
        self.creator_url = ""
        self.sea_name = "The Red Sea"
        self.user_data_start_flag = None
        self.vstore = DataStore(1)
        self.vdict = dict()
        self.data_tests = DataTests()

        self.initial_water_depth = None
        self.final_water_depth = None
        self.device_depth = None
        self.deployment_time = None
        self.retrieval_time = None

    def write_netCDF(self,var_datastore,series_length):
        ds = Dataset(os.path.join(self.out_filename),'w',format="NETCDF4_CLASSIC")
        time_dimen = ds.createDimension("time",series_length)
        var_datastore.set_attributes(self.var_dict())
        var_datastore.send_data(ds)
        ds.close()

    def var_dict(self):
        var_dict = dict()

        lat_dict = {'valid_min': self.latitude, 'valid_max': self.latitude}
        var_dict['lat_var'] = lat_dict
        lon_dict = {'valid_min': self.longitude, 'valid_max': self.longitude}
        var_dict['lon_var'] = lon_dict
        global_vars = {'creator_name': self.creator_name,
                       'creator_email': self.creator_email,
                       'creator_url': self.creator_url,
                       'geospatial_lat_min': self.latitude,
                       'geospatial_lat_max': self.latitude,
                       'geospatial_lon_min': self.longitude,
                       'geospatial_lon_max': self.longitude,
                       'geospatial_vertical_min': self.z,
                       'geospatial_vertical_max': self.z,
                       'sea_name': self.sea_name,
                       'initial_water_depth': self.initial_water_depth,
                       'final_water_depth': self.final_water_depth,
                       'deployment_time': self.deployment_time,
                       'retrieval_time': self.retrieval_time,
                       'device_depth': self.device_depth,
                       'salinity' : self.salinity}
        var_dict['global_vars_dict'] = global_vars

        return var_dict
    

class NetCDFToCSV(NetCDFReader):

    def __init__(self):
        self.file_name = None
        self.time_convert = True
        self.out_file_name = 'C:\\Tappy\\test{0}.csv'

    def convert_to_csv(self):
        self.get_test_data(self.file_name, self.time_convert)

        test = pd.DataFrame(pd.Series(self.pressure_data,index=self.times))
        test.columns = ['Pressure']
        chunk_size = int((test.shape[0] / 800000) + 1)
        
        for x in np.arange(0,chunk_size):
            data_slice = test[(x*800000):np.min([test.shape[0],(x+1) * 800000])]
            
            data_slice.to_csv(path_or_buf= self.out_file_name.format(x))

if __name__ == '__main__':
    a = NetCDFToCSV()
    a.file_name = 'C:/Tappy/logger3.csv.nc'
    a.convert_to_csv()
