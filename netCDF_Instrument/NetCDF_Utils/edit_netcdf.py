import DataTests
from netCDF4 import Dataset
import numpy as np
import pandas as pd
import os
import pytz
from datetime import datetime
import netCDF4
import netcdftime
import netCDF4.utils
from NetCDF_Utils.VarDatastore import DataStore
import unit_conversion


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

        try:
            self.air_pressure_data = nc.variables['air_pressure'][:]
        except:
            print('No air pressure')
        try:
            self.pressure_data = nc.variables['sea_water_pressure'][:]
        except:
            print('No sea pressure')



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
            pressure_array = self.pressure_data
            return self.return_data(pressure_array, temperature, index, series_bool, pressure_bool, True)
        else:
            return self.return_data(self.pressure_data, temperature, time_convert, series_bool, pressure_bool)

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
#         self.tz_info = pytz.timezone('US/Eastern')
        self.date_format_string = None
        self.frequency = None
        self.valid_pressure_units = ["psi","pascals","atm"]
        self.valid_z_units = ["meters","feet"]
        self.valid_latitude = (np.float64(-90),np.float64(90))
        self.valid_longitude = (np.float64(-180),np.float64(180))
        self.valid_z = (np.float64(-10000),np.float64(10000))
        self.valid_salinity = (np.float64(0.0),np.float64(40000))
        self.valid_pressure = (np.float64(-10000),np.float64(10000))
        self.valid_temp = (np.float64(-10000), np.float64(10000))
        self.fill_value = np.float64(-1.0e+10)
        self.creator_name = ""
        self.creator_email = ""
        self.creator_url = ""
        self.sea_name = ""
        self.user_data_start_flag = None
        self.vstore = DataStore(1)
        self.vdict = dict()
        self.initial_water_depth = None
        self.final_water_depth = None
        self.device_depth = None
        self.deployment_time = None
        self.retrieval_time = None
        self.bad_data = False
        self.initial_land_surface_elevation = np.float64(0)
        self.final_land_surface_elevation = np.float64(0)
        self.device_depth = None
        self.device_depth2 = None
        self.datum = None
        self.summary = None
        self.stn_station_number = None
        self.stn_instrument_id = None
        self.daylightSavings = False
        self.instrument_name = None
        self.instrument_serial = None

    def write(self, sea_pressure=True):
        '''Writing a netCDF from the fields entered in either sea or air gui'''
        
        self.is_Sea_pressure = sea_pressure
        #Assign variables according to the GUI used (air or sea)
        if sea_pressure == False:
            self.vstore.pressure_name = "air_pressure"
            self.vstore.pressure_var['standard_name'] = "air_pressure"
            self.summary = "These data were collected by an unvented pressure logger deployed in the air"
            self.vstore.pressure_range = [np.float64(0),np.float64(20)]
        else:
            self.vstore.pressure_name = "sea_pressure"
            self.vstore.pressure_var['standard_name'] = "sea_pressure"
            self.summary = "These data were collected by an unvented pressure logger deployed in the sea" 
            self.vstore.pressure_range = [np.float64(0),np.float64(50)]
            
        #Get Instrument Data
        self.instrument_info(self.instrument_name,self.vstore.pressure_var) 
        
        # Assign pressure, time, lat. lon, and time resolution
        self.vstore.pressure_data = self.pressure_data
        self.vstore.utc_millisecond_data = self.utc_millisecond_data
        self.vstore.latitude = self.latitude
        self.vstore.longitude = self.longitude
        self.vstore.time_coverage_resolution = ''.join(["P", str(1 / self.frequency), "S"])
        
        #perform data test and assign qc data flags
        if sea_pressure == False:
            self.vstore.pressure_qc_data, self.bad_data = DataTests.run_tests(self.pressure_data.astype(np.double), 0,1)
        else:
            self.vstore.pressure_qc_data, self.bad_data = DataTests.run_tests(self.pressure_data.astype(np.double), 0,0)
        
        #write the netCDF file using the vstore dictionary
        self.write_netCDF(self.vstore, len(self.pressure_data))
        
    def instrument_info(self,inst, vstore):
        '''Instrument info data based on selected instrument'''
        
        if inst == "Onset Hobo U20":
            vstore["instrument_manufacturer"] = "Onset"
            vstore["instrument_make"] = "Hobo"
            vstore["instrument_model"] = "U20"
            vstore["instrument_serial_number"] = self.instrument_serial
        else:
            vstore["instrument_manufacturer"] = "Measurement Specialties"
            vstore["instrument_make"] = "TruBlue"
            vstore["instrument_model"] = "255"
            vstore["instrument_serial_number"] = self.instrument_serial

    def write_netCDF(self,var_datastore,series_length):
        with Dataset(self.out_filename, 'w', format="NETCDF4_CLASSIC") as ds:
            time_dimen = ds.createDimension("time", series_length)
            station_dimen = ds.createDimension("station_id", len(self.stn_station_number))
            var_datastore.set_attributes(self.var_dict())
            var_datastore.z_var['datum'] = self.datum
            var_datastore.send_data(ds)

    def var_dict(self):
        var_dict = dict()
        
        #convert values to doubles
        self.z = np.float64(self.z)
        self.latitude = np.float64(self.latitude)
        self.longitude = np.float64(self.longitude)
        self.device_depth = np.float64(self.device_depth)
        self.initial_water_depth = np.float64(self.initial_water_depth)
        self.final_water_depth = np.float64(self.final_water_depth)
        
        resolution_string = 'P{0}S';
        lat_dict = {'valid_min': self.valid_latitude[0], 'valid_max': self.valid_latitude[1]}
        var_dict['lat_var'] = lat_dict
        lon_dict = {'valid_min': self.valid_longitude[0], 'valid_max': self.valid_longitude[1]}
        var_dict['lon_var'] = lon_dict
        
        if self.is_Sea_pressure:
            #get deployment and retrieval timestamps
            dep_time = unit_conversion.datestring_to_ms(self.deployment_time, '%Y%m%d %H%M', \
                                                         self.timezone_string,
                                                         self.daylightSavings)
            self.deployment_time = unit_conversion.convert_ms_to_datestring(dep_time, pytz.utc)
            
            ret_time = unit_conversion.datestring_to_ms(self.retrieval_time, '%Y%m%d %H%M', \
                                                         self.timezone_string,
                                                         self.daylightSavings)
            self.retrieval_time = unit_conversion.convert_ms_to_datestring(ret_time, pytz.utc)
        
        
        global_vars = {'creator_name': self.creator_name,
                       'creator_email': self.creator_email,
                       'creator_url': self.creator_url,
                       'geospatial_vertical_reference': self.datum,
                       'geospatial_lat_min': self.valid_latitude[0],
                       'geospatial_lat_max': self.valid_latitude[1],
                       'geospatial_lon_min': self.valid_longitude[0],
                       'geospatial_lon_max': self.valid_longitude[1],
                       'geospatial_vertical_min': self.z,
                       'geospatial_vertical_max': self.z,
                       'sea_name': self.sea_name,
                       'initial_water_depth': np.float64("{0:.4f}".format(self.initial_water_depth)),
                       'initial_land_surface_elevation': np.float64("{0:.4f}".format( \
                            float(self.initial_land_surface_elevation) / unit_conversion.METER_TO_FEET)),
                       'final_land_surface_elevation': np.float64("{0:.4f}".format( \
                            float(self.final_land_surface_elevation) / unit_conversion.METER_TO_FEET)),
                       'land_surface_elevation_units': 'meters',
                       'final_water_depth': np.float64("{0:.4f}".format(self.final_water_depth)),
                       'water_depth_units': 'meters',
                       'deployment_time': self.deployment_time,
                       'retrieval_time': self.retrieval_time,
#                        'device_depth': self.device_depth,
                       'salinity' : self.salinity,
#                        'salinity_ppm': self.salinity,
                       'sensor_orifice_elevation_at_deployment_time' : np.float64("{0:.4f}".format( \
                                                float(self.device_depth) / unit_conversion.METER_TO_FEET)),
                       'sensor_orifice_elevation_at_retrieval_time' : np.float64("{0:.4f}".format( \
                                                float(self.device_depth2) / unit_conversion.METER_TO_FEET)),
                       'sensor_orifice_elevation_units' : 'meters',
                       'time_coverage_resolution': resolution_string.format(1/self.frequency),
                       'summary': self.summary,
                       'stn_station_number': self.stn_station_number,
                       'stn_instrument_id': self.stn_instrument_id,
                       'featureType': 'timeSeries'
                       }

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
