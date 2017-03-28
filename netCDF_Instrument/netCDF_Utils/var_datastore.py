from datetime import datetime
import pytz
import numpy as np
import uuid
import unit_conversion
from numpy import float64

class DataStore(object):
    '''Use this as an abstract data store, then pass a netcdf write stream to send data method'''
    def __init__(self, grouping):
        self.utc_millisecond_data = None
        self.data_start_date = None
        self.data_end_date = None
        self.data_duration = None
        self.datum = None
        self.pressure_data = None
        self.pressure_qc_data = None
        self.pressure_range = [float64(0),float64(50)]
        self.pressure_name = None
        self.temperature_data = None
        self.temperature_qc_data = None
        self.temperature_range = [float64(-20),float64(50)]
        self.z_data = 0
        self.z_qc_data = None
        self.z_range = [float64(-1000),float64(1000)]
        self.z_name = None
        self.u_data = 0
        self.v_data = 0
        self.w_data = 0
        self.gust_data = None
        self.latitude = 0
        self.latitude_range = [float64(-90),float64(90)]
        self.longitude = 0
        self.longitude_range = [float64(-180),float64(180)]
        self.z = 0
        self.salinity = 0
        self.data_grouping = grouping
        self.epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
        self.fill_value = float64(-1.0e+10)
        self.initial_land_surface_elevation = 0
        self.final_land_surface_elevation = 0
        self.sensor_orifice_elevation_at_deployment_time = None
        self.sensor_orifice_elevation_at_retrieval_time = None
        self.summary = None
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
                        'long_name': 'time',
                        'short_name': 'time',
                        'standard_name': "time",
                        'units': "milliseconds since " + self.epoch_start.strftime("%Y-%m-%d %H:%M:%S"),
                        'calendar': "Gregorian",
                        'axis': 'T',
                        'ancillary_variables': '',
                        'comment': "",
                        'ioos_category': "time",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time"}
        self.lon_var = {
                        'long_name': "longitude of sensor",
                        'standard_name': "longitude",
                        'short_name': 'longitude',
                        'units': "degrees_east",
                        'axis': 'X',
                        'valid_min': self.longitude_range[0],
                        'valid_max': self.longitude_range[1],
                        'ancillary_variables': '',
                        'comment': "longitude 0 = IERS Reference Meridian as used by WGS84 for longitude. East is positive.",
                        'ioos_category': "location",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time",
                        }
        self.lat_var = {
                        'long_name': "latitude of sensor",
                        'standard_name': "latitude",
                        'short_name': 'latitude',
                        'units': "degrees_north",
                        'axis': 'Y',
                        'valid_min': self.latitude_range[0],
                        'valid_max': self.latitude_range[1],
                        'ancillary_variables': '',
                        'comment': "latitude 0 equals equator. North is positive.",
                        'ioos_category': "location",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time",
                        }
        self.z_var = {
                        'long_name': "altitude of sensor",
                        'standard_name': "altitude",
                        'short_name': 'altitude',
                        'units': "meters",
                        'positive': 'up',
                        'datum': self.datum,
                        'axis': 'Z',
                        'valid_min': self.z_range[0],
                        'valid_max': self.z_range[1],
                        'ancillary_variables': '',
                        'comment': "altitude of sensor used to derive sea surface elevation (unused)",
                        'ioos_category': "location",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time",
                      }
        self.z_var_qc = {
                                'flag_masks': '11111111 11111110 11111101 11111011 11110111',
                                'flag_meanings': "no_bad_data last_five_vals_identical, outside_valid_range, invalid_rate_of_change, interpolated_data",
                                'comment': '1 signifies the value passed the test while a 0 flags a failed test, leading 1 is a placeholder'
                                }
        self.station_id = {
                                      'cf_role': 'time_series_id',
                                      'long_name': 'station identifier'
                                      }
        self.u_var = { 
                    'ioos_category': "wind",
                    'long_name': "Sea Surface Wind: x-component",
                    'standard_name': "x_wind",
                    'units': "m s-1"
                    }
        self.v_var = {
                    'ioos_category': "wind",
                    'long_name': "Sea Surface Wind: y-component",
                    'standard_name': "y_wind",
                    'units': "m s-1",
                    }
        self.w_var = {
                    'ioos_category': "wind",
                    'long_name': "Sea Surface Wind: wind speed average",
                    'standard_name': "wind_speed",
                    'units': "m s-1"
                    }
        self.gust_var = {
                    'ioos_category': "wind",
                    'long_name': "Sea Surface Wind: wind gust speed",
                    'standard_name': "wind_speed",
                    'units': "m s-1"
                    }

                    
        self.pressure_var = {
                             'long_name': "sensor pressure",
                             'standard_name': "sea_pressure",
                             'short_name': "pressure",
                             'nodc_name': "pressure".upper(),
                             'units': "decibar",
                             'scale_factor': np.float64(1.0),
                             'add_offset': np.float64(0.0),
                             'compression': "not used at this time",
                             'valid_min': self.pressure_range[0],
                             'valid_max': self.pressure_range[1],
                             'ancillary_variables': '',
                             'coordinates': "time latitude longitude altitude",
                             'ioos_category': "pressure",
                             'comment': "",
                             'instrument_manufacturer': "",
                             'instrument_make': "",
                             'instrument_model': "",
                             'instrument_serial_number': ""
                             }
        self.pressure_var_qc = {
                                 'flag_masks': '11111111 11111110 11111101 11111011 11110111 11101111',
                                'flag_meanings': "no_bad_data last_five_vals_identical, outside_valid_range, invalid_rate_of_change, interpolated_data, derived hydrostatic water level below sensor orifice elevation (for sea pressure files only)",
                                 'comment': '1 signifies the value passed the test while a 0 flags a failed test, leading 1 is a placeholder,\n stuck sensor test (last_five_vals_identical) is temporarily turned off and thus its corresponding bit is always one'
                                }
        self.temp_var= {
                             'long_name': "sensor temperature record",
                             'standard_name': "temperature",
                             'short_name': "temp",
                             'nodc_name': "temperature".upper(),
                             'units': "degree_Celsius",
                             'scale_factor': np.float64(1.0),
                             'add_offset': np.float64(0.0),
                             'compression': "not used at this time",
                             'valid_min': self.temperature_range[0],
                             'valid_max': self.temperature_range[1],
                             'ancillary_variables': '',
                             'coordinates': "time latitude longitude altitude",
                             'ioos_category': "Temperature",
                             'comment': "",
                             }
        self.temp_var_qc = {
                              'flag_masks': '11111111 11111110 11111101 11111011 11110111',
                                'flag_meanings': "no_bad_data last_five_vals_identical, outside_valid_range, invalid_rate_of_change, interpolated_data",
                             'comment': '1 signifies the value passed the test while a 0 flags a failed test, leading 1 is a placeholder'
                            }

        self.global_vars_dict = {"cdm_data_type": "station",
                                 "comment": "not used at this time",
                                 "Conventions": "CF-1.6",
                                 "date_created": datetime.strftime(datetime.now(tz=pytz.utc), "%Y-%m-%dT%H:%M:%SZ"),
                                 "date_modified": datetime.strftime(datetime.now(tz=pytz.utc), "%Y-%m-%dT%H:%M:%SZ"),
                                 "geospatial_lat_min": self.latitude_range[0],
                                 "geospatial_lat_max": self.latitude_range[1],
                                 "geospatial_lon_min": self.longitude_range[0],
                                 "geospatial_lon_max": self.longitude_range[1],
                                 "geospatial_lat_units": "degrees_north",
                                 "geospatial_lat_resolution": "point",
                                 "geospatial_lon_units": "degrees_east",
                                 "geospatial_lon_resolution": "point",
                                 "geospatial_vertical_min": self.z,
                                 "geospatial_vertical_max": self.z,
                                 "geospatial_vertical_units": "meters",
                                 "geospatial_vertical_reference": self.datum,
                                 "geospatial_vertical_reference_comment": "",
                                 "geospatial_vertical_resolution": "point",
                                 "geospatial_vertical_positive": "up",
                                 "Metadata_Conventions": "Unidata Dataset Discovery v1.0",
                                 "metadata_link": "http://cfconventions.org/Data/cf-standard-names/30/build/cf-standard-name-table.html",
                                 "naming_authority": "gov.usgs.water.stn",
                                 "readme": "File created by Wavelab Tool Suite version 1.0",
                                 "standard_name_vocabulary": "CF-1.6",
                                 "summary": "",
                                 "time_coverage_start": "utility coverage start",
                                 "time_coverage_end": "utility coverage end",
                                 "time_coverage_duration": "utility coverage duration",
                                 "time_coverage_resolution": "P0.25S",
                                 "time_zone": "GMT",
#                                  "title": 'Measure of pressure at %s degrees latitude, %s degrees longitude' \
#                                  ' from the date range of %s to %s' % (self.latitude, self.longitude,self.creator_name, \
#                                                                        self.data_start_date, self.data_end_date),
                                 "uuid": str(uuid.uuid4())
                                 }
    def send_data(self,ds):
        self.get_time_var(ds)
        self.get_pressure_var(ds)
        self.get_pressure_qc_var(ds)
        if self.temperature_data != None:
            self.get_temp_var(ds)

        if type(self.z_data) != list:
            self.get_z_var(ds, False)
        else:
            self.get_z_var(ds, True)
            self.get_z_qc_var(ds)
            
        self.get_lat_var(ds)
        self.get_lon_var(ds)
        self.get_time_duration()
        self.global_vars_dict['title'] = 'Measure of pressure at %s degrees latitude, %s degrees longitude  by %s' \
        ' from the date range of %s to %s' % (self.latitude, self.longitude, self.global_vars_dict["creator_name"], \
                                                  self.global_vars_dict["time_coverage_start"], \
                                                  self.global_vars_dict["time_coverage_end"])
        self.get_global_vars(ds)
        self.get_station_id(ds)
        
    def send_wind_data(self,ds):
        self.get_time_var(ds)
        self.get_lat_var(ds)
        self.get_lon_var(ds)
        self.get_time_duration()
        self.get_station_id(ds)
        self.get_u_var(ds)
        self.get_v_var(ds)
        
        if len(self.gust_data) == len(self.v_data):
            self.get_gust_var(ds)
            
        if len(self.pressure_data) == len(self.v_data):
            self.get_pressure_var(ds)
            
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
        lat = ds.createVariable("latitude","f8",fill_value=self.fill_value)
        for x in self.lat_var:
            lat.setncattr(x,self.lat_var[x])
        lat[:] = self.latitude

    def get_lon_var(self,ds):
        lon = ds.createVariable("longitude","f8",fill_value=self.fill_value)
        for x in self.lon_var:
            lon.setncattr(x,self.lon_var[x])
        lon[:] = self.longitude

    def get_z_var(self,ds,time_dimen_bool = False):
        if time_dimen_bool == False:
            z = ds.createVariable("altitude", "f8",
                                  fill_value=self.fill_value)
        else:
            z = ds.createVariable("altitude", "f8",("time",),
                                  fill_value=self.fill_value)
        for x in self.z_var:
            z.setncattr(x,self.z_var[x])
        z[:] = self.z_data

    def get_z_qc_var(self,ds):
        if self.z_name != None:
            z_qc = ds.createVariable(self.z_name,'i4',('time'))
        else:
            z_qc = ds.createVariable("altitude_qc",'i4',('time'))
        for x in self.z_var_qc:
            z_qc.setncattr(x,self.z_var_qc[x])
        z_qc[:] = self.z_qc_data
        
    def get_station_id(self,ds):
        st_id = ds.createVariable('station_id','S1',('station_id'))
        for x in self.station_id:
            st_id.setncattr(x,self.station_id[x])
        st_id[:] = list(self.global_vars_dict['stn_station_number'])

    def get_pressure_var(self,ds):
        if self.pressure_name != None:
            pressure = ds.createVariable(self.pressure_name,"f8",("time",))
        else:
            pressure = ds.createVariable("sea_water_pressure","f8",("time",))
        for x in self.pressure_var:
            pressure.setncattr(x,self.pressure_var[x])
        pressure[:] = self.pressure_data

    def get_pressure_qc_var(self,ds):
        pressure_qc = ds.createVariable("pressure_qc",'i4',('time'))
        for x in self.pressure_var_qc:
            pressure_qc.setncattr(x,self.pressure_var_qc[x])
        pressure_qc[:] = self.pressure_qc_data

    def get_temperature_var(self,ds):
        temperature = ds.createVariable("temperature_at_transducer","f8", ("time",))
        for x in self.temperature_var:
            temperature.setncattr(x,self.temp_var[x])
        temperature[:] = self.temperature_data

    def get_temperature_qc_var(self,ds):
        temperature_qc = ds.createVariable("temperature_qc",'i4',('time'))
        for x in self.temp_var_qc:
            temperature_qc.setncattr(x,self.temp_var_qc[x])
        temperature_qc[:] = self.temperature_qc_data
        
    def get_u_var(self,ds):
        u = ds.createVariable("u",'f8',('time'))
        for x in self.u_var:
            u.setncattr(x,self.u_var[x])
        u[:] = self.u_data
    
    def get_v_var(self,ds):
        v = ds.createVariable("v",'f8',('time'))
        for x in self.v_var:
            v.setncattr(x,self.v_var[x])
        v[:] = self.v_data
        
    def get_gust_var(self,ds):
        gust = ds.createVariable("wind_gust",'f8',('time'))
        for x in self.gust_var:
            gust.setncattr(x,self.gust_var[x])
        gust[:] = self.gust_data

    def get_global_vars(self, ds):
        for x in self.global_vars_dict:
            if self.global_vars_dict[x] is not None:
                ds.setncattr(x,self.global_vars_dict[x])

    def get_time_duration(self):
        first_milli = self.utc_millisecond_data[0]
        second_milli = self.utc_millisecond_data[-1]
        self.global_vars_dict["time_coverage_start"] = \
        unit_conversion.convert_ms_to_datestring(first_milli, pytz.utc)

        self.global_vars_dict["time_coverage_end"] = \
        unit_conversion.convert_ms_to_datestring(second_milli, pytz.utc)

        self.global_vars_dict["time_coverage_duration"] = \
        unit_conversion.get_time_duration(second_milli - first_milli)

        

    def set_attributes(self, var_dict):
        """Sets attributes in script

        var_dict -- key- attr name value- attr value"""

        for x in var_dict:
            for y in var_dict[x]:
                var1 = self.__dict__[x]
                var1[y] = var_dict[x][y]


#     'Measure of pressure at %s degrees latitude, %s degrees longitude, %s altitude by %s' \
#                                 ' from the date range of %s to %s' % (self.latitude, self.longitude, self.z,self.creator_name, \
#                                                                           self.data_start_date, self.data_end_date),
