'''
Created on Jun 20, 2014

@author: Gregory
'''
import os
import sys
from datetime import datetime, timedelta
import pytz
import pandas
import re
import uuid

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

class Sensor(object):
    '''super class for reading raw wave data and writing to netcdf file
    this class should not be instantiated directly
    '''

    def __init__(self):
        self.in_filename = None
        self.out_filename = None
        self.is_baro = None
        self.pressure_units = None
        self.z_units = 'meters'
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
        self.tz_info = pytz.timezone('US/Eastern')
        self.date_format_string = None
        self.frequency = None
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
        self.valid_temp = (np.float32(-10000), np.float32(10000))
        self.fill_value = np.float32(-1.0e+10)
        self.creator_name = None
        self.sea_name = "The Red Sea"
        self.pressure_test16_data = None
        self.pressure_test17_data = None
        self.pressure_test20_data = None
        print('Done with initialization')

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
        minutes =  int(((seconds_difference / 1000) / 60)  % 60)
        seconds = (seconds_difference / 1000) % 60

        self.data_duration_time = "P%sDT%sH%sM%sS" % (days, hours, minutes, seconds)
        print(self.data_duration_time)

    def instrument_var(self,ds):
        instr_var = ds.createVariable("instrument1","i4")
        instr_var.long_name = 'Attributes for instrument 1'
        instr_var.make_model = ''
        instr_var.serial_number = ''
        instr_var.calibration_date = ''
        instr_var.factory_calibration = ''
        instr_var.user_calibrated = ''
        instr_var.calibration_report = ''
        instr_var.accuracy = ''
        instr_var.valid_range = 0
        instr_var.precision = ''
        instr_var.comment = ''
        instr_var.ancillary_variables = ''
        return instr_var
        
    def time_var(self,ds):
        time_var = ds.createVariable("time","f8",("time",))
        time_var.long_name = ''
        time_var.standard_name = "time"
        time_var.units = "milliseconds since "+self.epoch_start.strftime("%Y-%m-%d %H:%M:%S")
        time_var.calendar = "gregorian"
        time_var.axis = 'T'
        time_var.ancillary_variables = ''
        time_var.comment = "Original time zone: "+str(self.timezone_string)
        time_var.ioos_category = "Time" ;
        time_var.add_offset = 0
        time_var.scale_factor = 1
        time_var.compression = "not used at this time"
        time_var[:] = self.utc_millisecond_data
        return time_var


    def longitude_var(self,ds):
        longitude_var = ds.createVariable("longitude","f4",fill_value=self.fill_value)
        longitude_var.long_name = "longitude of sensor"
        longitude_var.standard_name = "longitude"
        longitude_var.units = "degrees_east"
        longitude_var.axis = 'X'
        longitude_var.valid_min = self.valid_longitude[0]
        longitude_var.valid_max = self.valid_longitude[1]
        longitude_var.ancillary_variables = ''
        longitude_var.comment = "longitude 0 equals prime meridian"
        longitude_var.ioos_category = "Location" ;
        longitude_var.add_offset = 0
        longitude_var.scale_factor = 1
        longitude_var.compression = "not used at this time"
        longitude_var[:] = self.longitude
        return longitude_var


    def latitude_var(self,ds):
        latitude_var = ds.createVariable("latitude","f4",fill_value=self.fill_value)
        latitude_var.long_name = "latitude of sensor"
        latitude_var.standard_name = "latitude"
        latitude_var.units = "degrees_north"
        latitude_var.axis = 'Y'
        latitude_var.valid_min = self.valid_latitude[0]
        latitude_var.valid_max = self.valid_latitude[1]
        latitude_var.ancillary_variables = ''
        latitude_var.comment = "latitude 0 equals equator"    
        latitude_var.ioos_category = "Location" ;    
        latitude_var.sea_name = self.sea_name
        latitude_var.add_offset = 0
        latitude_var.scale_factor = 1
        latitude_var.compression = "not used at this time"
        latitude_var[:] = self.latitude
        return latitude_var


    def z_var(self,ds):
        z_var = ds.createVariable("altitude","f4",fill_value=self.fill_value)
        z_var.long_name = "altitude of sensor"
        z_var.standard_name = "altitude"
        z_var.units = self.z_units
        z_var.axis = 'Z'
        z_var.valid_min = self.valid_z[0]
        z_var.valid_max = self.valid_z[1]
        z_var.ancillary_variables = ''
        z_var.comment = "altitude above NAVD88"
        z_var.ioos_category = "Location" ;
        z_var.add_offset = 0
        z_var.scale_factor = 1
        z_var.compression = "not used at this time"
        z_var[:] = self.z
        return z_var

#MR SNAKES  MR NOT OSMR CMBDIS LB MR SNAKES
    def pressure_var(self,ds):
        pressure_var = ds.createVariable("pressure","f8",("time",),fill_value=self.fill_value)#fill_value is the default
        pressure_var.long_name = "sensor pressure record"
        pressure_var.standard_name = "sea_water_pressure"    
        pressure_var.nodc_name = "pressure".upper()    
        pressure_var.units = "decibar"
        pressure_var.standard_name = "pressure"
        pressure_var.nodc_name = "pressure".upper()
        pressure_var.units = self.pressure_units
        pressure_var.scale_factor = np.float32(1.0)
        pressure_var.add_offset = np.float32(0.0)
        pressure_var.compression = "not used at this time"
        pressure_var.min = self.valid_pressure[0]
        pressure_var.max = self.valid_pressure[1]
        pressure_var.ancillary_variables = ''
        pressure_var.coordinates = "time latitude longitude altitude"
        pressure_var.ioos_category = "Pressure" ;
        pressure_var[:] = self.pressure_data
        return pressure_var

    def temp_var(self,ds):
        temp_var = ds.createVariable("temperature_at_transducer", "f8", ("time",),
                                     fill_value=self.fill_value)
        temp_var.long_name = "sensor temperature record"
        temp_var.standard_name = "temperature"
        temp_var.nodc_name = "TEMPERATURE"
        temp_var.units = 'degree_Celsius'
        temp_var.scale_factor = np.float32(1.0)
        temp_var.add_offset = np.float32(0.0)
        temp_var.min = self.valid_temp[0]
        temp_var.max = self.valid_temp[1]
        temp_var.ancillary_variables = ''
        temp_var.coordinates = "time latitude longitude altitude"
        temp_var.sea_name = self.sea_name
        temp_var.add_offset = 0
        temp_var.scale_factor = 1
        temp_var.compression = "not used at this time"
        temp_var[:] = self.temperature_data
        return temp_var
    
    def pressure_test16(self,ds):
        pressure_test16 = ds.createVariable("pressure_stuck_sensor_qc","b",("time",))
        pressure_test16.flag_values = [1, 3, 4]
        pressure_test16.flag_meanings = "pass_less_than_3_vals_identical suspicious_last_3_to_4_vals_identical, fail_last_5_vals_identical"
        pressure_test16[:] = self.pressure_test16_data
        return pressure_test16
 
    def pressure_test17(self,ds):
        pressure_test17 = ds.createVariable("pressure_valid_range_qc","b",("time",))
        pressure_test17.flag_values = [1, 4]
        pressure_test17.flag_meanings = "pass_data_within_local_range fail_data_not_within_local_range"
        pressure_test17[:] = self.pressure_test17_data
        return pressure_test17
 
    def pressure_test20(self,ds):
        pressure_test20 = ds.createVariable("pressure_valid_rate_of_change_qc","b",("time",))
        pressure_test20.flag_values = [1, 4]
        pressure_test20.flag_meanings = "pass_data_within_acceptable_rate_of_change fail_data_not_within_acceptable_rate_of_change"
        pressure_test20[:] = self.pressure_test20_data
        return pressure_test20


    def write(self):
        #assert not os.path.exists(self.out_filename),"out_filename already exists"
        #--create variables and assign data

        ds = netCDF4.Dataset(self.out_filename,'w',format="NETCDF4_CLASSIC")
        time_dimen = ds.createDimension("time",len(self.pressure_data))
        instrument_var = self.instrument_var(ds)
        time_var = self.time_var(ds)
        latitude_var = self.latitude_var(ds)
        longitude_var = self.longitude_var(ds)
        z_var = self.z_var(ds)
        pressure_var = self.pressure_var(ds)
        pressure_test16 = self.pressure_test16(ds)
        pressure_test17 = self.pressure_test17(ds)
        pressure_test20 = self.pressure_test20(ds)

        print('In the write method')
        if hasattr(self, 'temperature_data'):
            temp_var = self.temp_var(ds)
            print('Adding temperature data. This should only happen '
                  'for the USGS Homebrew instrument.')
        else: print('No temperature data found.')
 
        ds.cdm_data_type = "station"
        ds.comment = "not used at this time"
        ds.contributor_name = "USGS"
        ds.contributor_role = "data collector"
        ds.Conventions = "CF-1.6"
        ds.creator_email = self.creator_email
        ds.creator_name = self.creator_name
        ds.creator_url = self.creator_url
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
        ds.geospatial_vertical_min = self.z
        ds.geospatial_vertical_max = self.z
        ds.geospatial_vertical_units = "meters"
        ds.geospatial_vertical_resolution = "point"
        ds.geospatial_vertical_positive = "up"
        ds.history = "not used at this time"
        ds.id = "not used at this time"
        ds.institution = "USGS"
        ds.keywords = "not used at this time"
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
        ds.readme = "file created by "+sys.argv[0]+" on "+str(datetime.now())+" from source file "+self.in_filename
        ds.salinity_ppm = np.float32(self.salinity_ppm)
        ds.sea_name = self.sea_name
        ds.standard_name_vocabulary = "CF-1.6"
        ds.summary = "This is data collected by a pressure instrument used for extrapolating information regarding weather patterns"
        ds.time_coverage_start = self.data_start_date
        ds.time_coverage_end = self.data_end_date
        ds.time_coverage_duration = self.data_duration_time
        ds.time_coverage_resolution = "P0.25S"
        ds.time_zone = "UTC"
        ds.title = 'Measure of pressure at %s degrees latitude, %s degrees longitude, %s altitude by %s' \
        ' from the date range of %s to %s' % (self.latitude, self.longitude, self.z,self.creator_name, \
                                                   self.data_start_date, self.data_end_date)
        ds.uuid = str(uuid.uuid4())
        print('done write')

    def read(self):
        raise Exception("read() must be implemented in the derived classes")

    def read_start(self):
        raise Exception("read_start() must be implemented in the derived classes")
