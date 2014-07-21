import netCDF4
from datetime import datetime
import pytz
import numpy as np
import uuid
import NetCDF_Utils.DateTimeConvert as timeconvert
import pytz

class DataStore(object):
    
    def __init__(self, grouping, var_list= None):
        self.utc_millisecond_data = None
        self.data_start_date = None
        self.data_end_date = None
        self.data_duration = None
        self.pressure_data = None
        self.pressure_qc_data = None
        self.temperature_data = None
        self.temperature_qc_data = None
        self.z_data = None
        self.z_qc_data = None
        self.latitutde = None
        self.longitude = None
        self.data_grouping = grouping
        self.epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
        self.fill_value = np.float64(-1.0e+10)
        self.instrument_var = { 'long_name': 'Attributes for instrument 1',
                                'make_model': '',
                                'serial_number': '',
                                'calibration_date': '',
                                'factory_calibration': '',
                                'user_calibrated': '',
                                'calibration_report': '',
                                'accuracy': '',
                                'valid_range': [0,1],
                                'precision': '',
                                'comment': '',
                                'ancillary_variables': ''}
        self.time_var = {
                        'long_name': 'Time',
                        'short_name': 'time',
                        'standard_name': "time",
                        'units': "milliseconds since " + self.epoch_start.strftime("%Y-%m-%d %H:%M:%S"),
                        'calendar': "gregorian",
                        'axis': 'T',
                        'ancillary_variables': '',
                        'comment': "Original time zone future gui",
                        'ioos_category': "Time",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time"}
        self.lon_var = {
                        'long_name': "longitude of sensor",
                        'standard_name': "longitude",
                        'short_name': 'longitude',
                        'units': "degrees",
                        'axis': 'X',
                        'valid_min': self.longitude,
                        'valid_max': self.longitude,
                        'ancillary_variables': '',
                        'comment': "longitude 0 equals prime meridian",
                        'ioos_category': "Location",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time",
                        }
        self.lat_var = {
                        'long_name': "latitude of sensor",
                        'standard_name': "latitude",
                        'short_name': 'latitude',
                        'units': "degrees",
                        'axis': 'Y',
                        'valid_min': self.latitutde,
                        'valid_max': self.latitutde,
                        'ancillary_variables': '',
                        'comment': "latitude 0 equals equator",
                        'ioos_category': "Location",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time",
                        }
        self.z_var = {
                        'long_name': "altitude of sensor",
                        'standard_name': "altitude",
                        'short_name': 'altitude',
                        'units': "degrees",
                        'axis': 'Z',
                        'valid_min': "utility valid min",
                        'valid_max': "utility valid max",
                        'ancillary_variables': '',
                        'comment': "latitiude 0 equals equator",
                        'ioos_category': "Location",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time",
                      }
        self.z_var_qc = {
                                'flag_masks': ['0000', '0001', '0010', '0100', '1000'],
                                'flag_meanings': "pass_less_than_3_vals_identical suspicious_last_3_to_4_vals_identical, fail_last_5_vals_identical",
                                'comment': '0 means pass and 1 flags a failed test'
                                }
        self.pressure_var = {
                             'long_name': "sensor pressure record",
                             'standard_name': "sea_water_pressure",
                             'short_name': "pressure",
                             'nodc_name': "pressure".upper(),
                             'units': "decibar",
                             'scale_factor': np.float32(1.0),
                             'add_offset': np.float32(0.0),
                             'compression': "not used at this time",
                             'min': "utility valid pressure",
                             'max': "utilility valid max",
                             'ancillary_variables': '',
                             'coordinates': "time latitude longitude altitude",
                             'ioos_category': "Pressure",
                             'comment': "",
                             } 
        self.pressure_var_qc = {
                                'flag_masks': ['0000', '0001', '0010', '0100', '1000'],
                                'flag_meanings': "pass_less_than_3_vals_identical suspicious_last_3_to_4_vals_identical, fail_last_5_vals_identical",
                                'comment': '0 means pass and 1 flags a failed test'
                                }
        self.temp_var= {
                             'long_name': "sensor temperature record",
                             'standard_name': "temperature",
                             'short_name': "temp",
                             'nodc_name': "temperature".upper(),
                             'units': "degree_Celsius",
                             'scale_factor': np.float32(1.0),
                             'add_offset': np.float32(0.0),
                             'compression': "not used at this time",
                             'min': "utility valid pressure",
                             'max': "utilility valid max",
                             'ancillary_variables': '',
                             'coordinates': "time latitude longitude altitude",
                             'ioos_category': "Pressure",
                             'comment': "",
                             } 
        self.temp_var_qc = {
                             'flag_masks': ['0000', '0001', '0010', '0100', '1000'],
                             'flag_meanings': "pass_less_than_3_vals_identical suspicious_last_3_to_4_vals_identical, fail_last_5_vals_identical",
                             'comment': '0 means pass and 1 flags a failed test'
                            }
       
        self.global_vars_dict = {"cdm_data_type": "station",
                                 "comment": "not used at this time",
                                 "contributor_name": "USGS",
                                 "contributor_role": "data collector",
                                 "Conventions": "CF-1.6",
                                 "creator_email": "gui email",
                                 "creator_name": "gui name",
                                 "creator_url": "gui url",
                                 "date_created": datetime.strftime(datetime.now(tz=pytz.utc), "%Y-%m-%dT%H:%M:%SZ"),
                                 "date_modified": datetime.strftime(datetime.now(tz=pytz.utc), "%Y-%m-%dT%H:%M:%SZ"),
                                 "geospatial_lat_min": "guilat",
                                 "geospatial_lat_max": "guilat",
                                 "geospatial_lon_min": "guilon",
                                 "geospatial_lon_max": "guilon",
                                 "geospatial_lat_units": "degrees_north",
                                 "geospatial_lat_resolution": "point",
                                 "geospatial_lon_units": "degrees_east",
                                 "geospatial_lon_resolution": "point",
                                 "geospatial_vertical_min": "gui z",
                                 "geospatial_vertical_max": "gui z",
                                 "geospatial_vertical_units": "meters",
                                 "geospatial_vertical_resolution": "point",
                                 "geospatial_vertical_positive": "up",
                                 "history": "not used at this time",
                                 "id": "not used at this time",
                                 "institution": "USGS",
                                 "keywords": "not used at this time",
                                 "keywords_vocabulary": "not used at this time",
                                 "license": "This data may only be used upon the consent of the USGS",
                                 "Metadata_Conventions": "Unidata Dataset Discovery v1.0",
                                 "metadata_link": "usgs.katrinamapperinfo.com",
                                 "naming_authority": "not used at this time",
                                 "processing_level": "deferred with intention to implement",
                                 "project": "deferred with intention to implement",
                                 "publisher_email": "deferred with intention to implement",
                                 "publisher_name": "deferred with intention to implement",
                                 "publisher_url": "deferred with intention to implement",
                                 "readme": "file created by "+ "gui creator" +str(datetime.now()) +"with files" + "gui filenames",
                                 "salinity_ppm": "gui salinity",
                                 "sea_name": "gui sea name",
                                 "standard_name_vocabulary": "CF-1.6",
                                 "summary": "This is data collected by a pressure instrument used for extrapolating information regarding weather patterns",
                                 "time_coverage_start": "utilitiy coverage start",
                                 "time_coverage_end": "utility coverage end",
                                 "time_coverage_duration": "utility coverage duration",
                                 "time_coverage_resolution": "P0.25S",
                                 "time_zone": "UTC",
                                 "title": 'Measure of pressure at %s degrees latitude, %s degrees longitude' \
                                 ' from the date range of %s to %s' % (self.latitude, self.longitude,self.creator_name, \
                                                                       self.data_start_date, self.data_end_date),
                                 "uuid": str(uuid.uuid4())
                                 }
    def send_data(self,ds):
        self.get_time_var(ds)
        self.get_pressure_var(ds)
        if self.temperature_data != None:
            self.get_temp_var(ds)
            
        if type(self.z_data) != list:
            self.get_z_var(ds, False)
        else:
            self.get_z_var(ds, True)
       
        self.get_lat_var(ds)
        self.get_lon_var(ds)
        self.get_global_vars(ds)
        
    def get_instrument_var(self,ds):
        instrument = ds.createVariable("instrument","i4")
        for x in self.instrument_var:
            instrument.setncattr(x,self.instrument_var[x])
        
       
    def get_time_var(self,ds):
        time = ds.createVariable("time","f8",("time",))
        for x in self.time_var:
            time.setncattr(x,self.time_var[x]) 
        time[:] = self.utc_millisecond_data
        
    def get_lat_var(self,ds):
        lat = ds.createVariable("latitude","f4",fill_value=self.fill_value)
        for x in self.lat_var:
            lat.setncattr(x,self.lat_var[x])
        lat[:] = self.latitutde
            
    def get_lon_var(self,ds):
        lon = ds.createVariable("longitude","f4",fill_value=self.fill_value)
        for x in self.lon_var:
            lon.setncattr(x,self.lon_var[x])
        lon[:] = self.longitude
          
    def get_z_var(self,ds,time_dimen_bool = False):
        if time_dimen_bool == False:
            z = ds.createVariable("altitude", "f4",
                                  fill_value=self.fill_value)
        else:
            z = ds.createVariable("altitude", "f8",("time",),
                                  fill_value=self.fill_value)
        for x in self.z_var:
            z.setncattr(x,self.z_var[x])
        z[:] = self.z_data
           
    def get_z_qc_var(self,ds):
        z_qc = ds.createVariable("altitude_qc",'i4',('time'))
        for x in self.z_qc_var:
            z_qc.setncattr(x,self.z_qc_var[x])
        z_qc[:] = self.z_qc_data
                   
    def get_pressure_var(self,ds):
        pressure = ds.createVariable("sea_water_pressure","f8",("time",))
        for x in self.pressure_var:
            pressure.setncattr(x,self.pressure_var[x])
        pressure[:] = self.pressure_data
            
    def get_pressure_qc_var(self,ds):
        pressure_qc = ds.createVariable("pressure_qc",'i4',('time'))
        for x in self.z_qc_var:
            pressure_qc.setncattr(x,self.pressure_qc_var[x])
        pressure_qc[:] = self.pressure_qc_data
        
    def get_temperature_var(self,ds):
        temperature = ds.createVariable("temperature_at_transducer","f8", ("time",))
        for x in self.temperature_var:
            temperature.setncattr(x,self.temp_var[x])
        temperature[:] = self.temperature_data
            
    def get_temperature_qc_var(self,ds):
        temperature_qc = ds.createVariable("temperature_qc",'i4',('time'))
        for x in self.temperature_qc_var:
            temperature_qc.setncattr(x,self.pressure_qc_var[x])
        temperature_qc[:] = self.temperature_qc_data
            
    def get_global_vars(self, ds):
        for x in self.global_vars_dict:
            ds.setncattr(x,self.global_vars_dict[x])
        
    def get_time_duration(self):
        self.data_start_date = timeconvert.convert_milliseconds_to_datetime(self.utc_millisecond_data[0], pytz.utc)
        self.data_end_date = timeconvert.convert_milliseconds_to_datetime(self.utc_millisecond_data[::-1][0], pytz.utc)   
    def gui_fill_values(self, data_class):
        pass  
      
    
    
#     'Measure of pressure at %s degrees latitude, %s degrees longitude, %s altitude by %s' \
#                                 ' from the date range of %s to %s' % (self.latitude, self.longitude, self.z,self.creator_name, \
#                                                                           self.data_start_date, self.data_end_date),
        