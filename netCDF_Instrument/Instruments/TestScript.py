'''
Created on Jul 3, 2014

@author: Gregory
'''
'''
Created on Jun 20, 2014

@author: Gregory
'''
import os
import sys
from datetime import datetime
import pytz
from pytz import timezone, all_timezones, tzinfo
import pandas
import re
import numpy as np
import netCDF4
import netCDF4_utils
import netcdftime
#--python 3 compatibility
pyver = sys.version_info
if pyver[0] == 3:
    raw_input = input

for tz in pytz.all_timezones:   
    print(tz)
    
class Sensor(object):
    '''super class for reading raw wave data and writing to netcdf file
    this class should not be instantiated directly
    '''
    
    def __init__(self):
        self.in_filename = None
        self.out_filename = None
        self.is_baro = None
        self.pressure_units = None
        self.z_units = None
        self.latitude = None
        self.longitude = None
        self.z = None
        self.salinity_ppm = -1.0e+10
        self.utc_millisecond_data = None
        self.pressure_data = None
        self.presure_data_flags = None
        self.epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
        self.data_start = None
        self.timezone_string = None
        self.tz_info = timezone("US/Eastern")
        self.date_format_string = None
        self.frequency = None
        self.local_frequency_range = None
        self.mfg_frequency_range = None
        self.data_start_date = None
        self.data_end_date = None
        self.data_duration_time = None

        self.valid_pressure_units = ["psi","pascals","atm"]
        self.valid_z_units = ["meters","feet"]
        self.valid_latitude = (np.float32(-90),np.float32(90))
        self.valid_longitude = (np.float32(-180),np.float32(180))
        self.valid_z = (np.float32(-10000),np.float32(10000))
        self.valid_salinity = (np.float32(0.0),np.float32(40000))
        self.valid_pressure = (np.float32(-10000),np.float32(10000))

        self.fill_value = np.float32(-1.0e+10)
        self.creator_name = "Tim Howard"
        
        self.pressure_test16_data = None
        self.pressure_test17_data = None
        self.pressure_test20_data = None
        
    
    def convert_to_milliseconds(self, series_length, datestring):
        return  np.arange(series_length, dtype='int64') * (1000 / self.frequency)\
          + self.convert_date_to_milliseconds(datestring)
            
    
    def convert_date_to_milliseconds(self, datestring):
        first_date = pytz.utc.localize(datetime.strptime(datestring, self.date_format_string))
        self.data_start_date = datetime.strftime(first_date, "%Y-%m-%dT%H:%M:%SZ")
        print(self.data_start_date)
        return (first_date - self.epoch_start).total_seconds() * 1000
    
    def convert_milliseconds_to_datetime(self, milliseconds):
        date = datetime.fromtimestamp(milliseconds / 1000)
        new_dt = self.tz_info.localize(date)
        final_date = new_dt.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        print('lastdate',final_date)
        return(final_date)
        
    def get_time_duration(self, seconds_difference):
      
        days = int((((seconds_difference / 1000) / 60) / 60) / 24)
        hours =  int((((seconds_difference / 1000) / 60) / 60) % 24)
        minutes = hours % 60
        seconds = minutes % 60
         
        self.data_duration_time = "P%sDT%sH%sM%sS" % (days, hours, minutes, seconds)
        print(self.data_duration_time)

    def time_var(self,ds):
        time_var = ds.createVariable("time","f8",("time",))
        time_var.long_name = ''
        time_var.standard_name = "time"
        time_var.units = "milliseconds since "+self.epoch_start.strftime("%Y-%m-%d %H:%M:%S")
        time_var.calendar = "gregorian"
        time_var.axis = 't'
        time_var.ancillary_variables = ''        
        time_var.comment = "Original time zone: "+str(self.timezone_string)
        time_var[:] = self.utc_millisecond_data
        return time_var

    
    def longitude_var(self,ds):
        longitude_var = ds.createVariable("longitude","f4",fill_value=self.fill_value)
        longitude_var.long_name = "longitude of sensor"
        longitude_var.standard_name = "longitude"
        longitude_var.units = "degrees east"
        longitude_var.axis = 'X'
        longitude_var.min = self.valid_longitude[0]
        longitude_var.max = self.valid_longitude[1]        
        longitude_var.ancillary_variables = ''
        longitude_var.comment = "longitude 0 equals prime meridian"
        longitude_var[:] = self.longitude
        return longitude_var


    def latitude_var(self,ds):
        latitude_var = ds.createVariable("latitude","f4",fill_value=self.fill_value)
        latitude_var.long_name = "latitude of sensor"
        latitude_var.standard_name = "latitude"
        latitude_var.units = "degrees north"
        latitude_var.axis = 'Y'
        latitude_var.min = self.valid_latitude[0]
        latitude_var.max = self.valid_latitude[1]        
        latitude_var.ancillary_variables = ''
        latitude_var.comment = "latitude 0 equals equator"        
        latitude_var[:] = self.latitude
        return latitude_var


    def z_var(self,ds):    
        z_var = ds.createVariable("altitude","f4",fill_value=self.fill_value)
        z_var.long_name = "altitude of sensor"
        z_var.standard_name = "altitude"    
        z_var.units = self.z_units
        z_var.axis = 'Z'
        z_var.min = self.valid_z[0]
        z_var.max = self.valid_z[1]        
        z_var.ancillary_variables = ''
        z_var.comment = "altitude above NAVD88"
        z_var[:] = self.z
        return z_var


    def pressure_var(self,ds):
        pressure_var = ds.createVariable("pressure","f8",("time",),fill_value=self.fill_value)#fill_value is the default
        pressure_var.long_name = "sensor pressure record"
        pressure_var.standard_name = "pressure"    
        pressure_var.nodc_name = "pressure".upper()    
        pressure_var.units = self.pressure_units
        pressure_var.scale_factor = np.float32(1.0)
        pressure_var.add_offset = np.float32(0.0)        
        pressure_var.min = self.valid_pressure[0]
        pressure_var.max = self.valid_pressure[1]        
        pressure_var.ancillary_variables = ''
        pressure_var.coordinates = "time latitude longitude z"
        pressure_var[:] = self.pressure_data
        return pressure_var
    
    def pressure_test16(self,ds):
        pressure_test16 = ds.createVariable("pressure_test16","b",("time",))
        pressure_test16[:] = self.pressure_test16_data
        return pressure_test16
    
    def pressure_test17(self,ds):
        pressure_test17 = ds.createVariable("pressure_test17","b",("time",))
        pressure_test17[:] = self.pressure_test17_data
        return pressure_test17
    
    def pressure_test20(self,ds):
        pressure_test20 = ds.createVariable("pressure_test20","b",("time",))
        pressure_test20[:] = self.pressure_test20_data
        return pressure_test20
    
    
    def write(self):
        #assert not os.path.exists(self.out_filename),"out_filename already exists"
        #--create variables and assign data
        ds = netCDF4.Dataset(self.out_filename,'w',format="NETCDF4_CLASSIC")
        time_dimen = ds.createDimension("time",len(self.pressure_data))   
        print(len(self.pressure_data))  
        time_var = self.time_var(ds)
        latitude_var = self.latitude_var(ds)
        longitude_var = self.longitude_var(ds)
        z_var = self.z_var(ds)
        pressure_var = self.pressure_var(ds)
        pressure_test16 = self.pressure_test16(ds)
        pressure_test17 = self.pressure_test17(ds)
        pressure_test20 = self.pressure_test20(ds)
        ds.salinity_ppm = np.float32(self.salinity_ppm)        
        ds.time_zone = "UTC"
        ds.readme = "file created by "+sys.argv[0]+" on "+str(datetime.now())+" from source file "+self.in_filename
        ds.cdm_datatype = "station"
        ds.comment = "not used at this time"
        ds.contributor_name = "USGS"
        ds.contributor_role = "data collector"
        ds.creator_email = "not used at this time"
        ds.creator_name = "not used at this time"
        ds.creator_url = "not used at this time"
        ds.date_created = datetime.strftime(datetime.now(tz=pytz.utc), "%Y-%m-%dT%H:%M:%SZ")
        ds.date_modified = datetime.strftime(datetime.now(tz=pytz.utc), "%Y-%m-%dT%H:%M:%SZ")
        ds.geospatial_lat_min = self.latitude
        ds.geospatial_lat_max = self.latitude
        ds.geospatial_lon_min = self.longitude
        ds.geospatial_lon_max = self.longitude
        ds.geospatial_lat_units = "degrees_north"
        ds.geospatial_lat_resolution = "point"
        ds.geospatial_lon_units = "degrees_east"
        ds.geospatial_lon_resolution = "point"
        ds.geospatial_vertical_min = "GUI"
        ds.geospatial_vertical_max = "GUI"
        ds.geospatial_vertical_units = "meters"
        ds.geospatial_vertical_resolution = "point"
        ds.geospatial_vertical_positive = "up"
        ds.history = "not used at this time"
        ds.id = "not used at this time"
        ds.institution = "USGS"
        ds.keywords = "GUI"
        ds.keywords_vocabulary = "not used at this time"
        ds.license = "This data may only be used upon the consent of the USGS"
        ds.Metadata_Conventions = "Unidata Dataset Discovery v1.0"
        ds.metadata_link = "usgs.katrinamapperinfo.com"
        ds.naming_authority = "not used at this time"
        ds.processing_level = "deferred with intention to implement"
        ds.project = "deferred with intention to implement"
        ds.publisher_email = "deferred with intention to implement"
        ds.publisher_name = "deferred with intention to implement"
        ds.publisher_url = "deferred with intention to implement"
        ds.standard_name_vocabulary = "CF-1.6"
        ds.summary = "This is data collected by a pressure instrument used for extrapolating information regarding weather patterns"
        ds.time_coverage_start = self.data_start_date
        ds.time_coverage_end = self.data_end_date
        ds.time_coverage_duration = self.data_duration_time
        ds.time_coverage_resolution = "P0.25S"
        ds.title = 'Measure of pressure at %s degrees latitude, %s degrees longitude, %s alittude by %s' \
        ' from the date range of %s to %s' % (self.latitude, self.longitude, self.z,self.creator_name, \
                                                   self.data_start_date, self.data_end_date)
        print('done write')

#     def inrange(self,val,limits):
#         if val >= limits[0] and val <= limits[1]:
#             return True
#         else:
#             return False


    def read(self):
        raise Exception("read() must be implemented in the derived classes")
    
    def read_start(self):
        raise Exception("read_start() must be implemented in the derived classes")

'''
Created on Jun 20, 2014

@author: Gregory
'''
   


#--python 3 compatibility
pyver = sys.version_info
if pyver[0] == 3:
    raw_input = input
        

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
    
    
