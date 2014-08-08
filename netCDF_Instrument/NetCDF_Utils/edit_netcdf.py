try:        
    import netCDF4
except:
    raise Exception("netCDF4 is required") 
import numpy as np
import pandas as pd
import os
import pytz
from datetime import datetime

try:
    from NetCDF_Utils.VarDatastore import DataStore
    from NetCDF_Utils.Testing import DataTests
except:
    print('Check Packaging')

class NetCDFReader(object):
    """Reads netcdf4 file"""
    
    def __init__(self):
        self.in_file_name = os.path.join("..\Instruments","benchmark","RBRtester2.nc")
        self.file_names = None
        self.pressure_frame = None
        self.temperature_frame = None
        self.series = None
        self.dataframe_vals = dict()
        self.dataframe = None
        self.epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
        self.latitude = None
        self.longitude = None
        
    
      
    def read_file(self,file_name,pressure_bool = True, series_bool = True, milliseconds_bool = False):
        """Read a .nc file
        
        pressure_bool -- get pressure, otherwise get temperature
        series_bool -- get a series, otherwise get a dataframe
        milliseconds_bool -- get milliseconds as index (divide by 100 since panda series cannot take longs as indexes, 
        otherwise convert to datetime"""
        
        nc = netCDF4.Dataset(file_name)
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
        if milliseconds_bool == True:
            return self.return_data(pressure, temperature, times, series_bool, pressure_bool, True)
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
                if type(index) != 'datetime.datetime':  # PAndas series cannot take a long as an index
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

class NetCDFEditor(object):
    
    def __init__(self):
        self.dataset = None
        self.datetime_data = None
        self.pressure_data = None
        self.temperature_data = None
        self.in_file_name = os.path.join("..\Instruments","benchmark","RBRtester2.nc")
    
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
        self.out_filename = os.path.join("..\Instruments",'benchmark','DepthTest.nc')
        self.in_filename = None
        self.is_baro = None
        self.pressure_units = None
        self.z_units = 'meters'
        self.latitude = 0
        self.longitude = 0
        self.z = 0
        self.salinity_ppm = -1.0e+10
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
        
        self.initial_pressure = None
        self.water_depth = None
        self.device_depth = None
        
        print('Done with initialization')

    def write_netCDF(self,var_datastore,series_length):
        ds = netCDF4.Dataset(os.path.join(self.out_filename),'w',format="NETCDF4_CLASSIC")
        time_dimen = ds.createDimension("time",series_length)
        var_datastore.set_attributes(self.var_dict())
        var_datastore.send_data(ds)
        
    def var_dict(self):
        var_dict = dict()
        
        lat_dict = {'valid_min': self.latitude, 'valid_max': self.latitude}
        var_dict['lat_var'] = lat_dict
        lon_dict = {'valid_min': self.longitude, 'valid_max': self.longitude}
        var_dict['lon_var'] = lon_dict
        global_vars = {'creator_name': self.creator_name, 'creator_email': self.creator_email,
                       'creator_eamil': self.creator_email, 'geospatial_lat_min': self.latitude,
                       'geospatial_lat_max': self.latitude, 'geospatial_lon_min': self.longitude,
                       'geospatial_lon_max': self.longitude, 'geospatial_vertical_min': self.z,
                       'geospatial_vertical_max': self.z, 'sea_name': self.sea_name,
                       'initial_pressure': self.initial_pressure, 'water_depth': self.water_depth,
                       'device_depth': self.device_depth}
        var_dict['global_vars_dict'] = global_vars
        
        return var_dict
        
if __name__ == "__main__":
    
    #--create an instance    
    editor = NetCDFEditor()
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
    