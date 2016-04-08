import DataTests
from netCDF4 import Dataset
import numpy as np
import os
import pytz
from datetime import datetime
from netCDF_Utils.var_datastore import DataStore
import unit_conversion

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
        self.initial_sensor_orifice_elevation = None
        self.final_sensor_orifice_elevation = None
        self.datum = None
        self.summary = None
        self.stn_station_number = None
        self.stn_instrument_id = None
        self.daylight_savings = False
        self.instrument_name = None
        self.instrument_serial = None

    def write(self, pressure_type="Sea Pressure"):
        '''Writing a netCDF from the fields entered in either sea or air gui'''
        
        self.pressure_type = pressure_type
        #Assign variables according to the GUI used (air or sea)
        if pressure_type == "Air Pressure":
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
        
        pressure_test = 0
        if pressure_type == 'Air Pressure':
            pressure_test = 1
           
        self.vstore.pressure_qc_data, self.bad_data =  DataTests.run_tests(
                self.pressure_data.astype(np.double), \
                0,pressure_test) 
        
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
        self.initial_sensor_orifice_elevation = np.float64(self.initial_sensor_orifice_elevation)
        self.initial_water_depth = np.float64(self.initial_water_depth)
        self.final_water_depth = np.float64(self.final_water_depth)
        
        resolution_string = 'P{0}S';
        lat_dict = {'valid_min': self.valid_latitude[0], 'valid_max': self.valid_latitude[1]}
        var_dict['lat_var'] = lat_dict
        lon_dict = {'valid_min': self.valid_longitude[0], 'valid_max': self.valid_longitude[1]}
        var_dict['lon_var'] = lon_dict
        
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
                       'sensor_orifice_elevation_at_deployment_time':  np.float64("{0:.4f}".format( \
                                                float(self.initial_sensor_orifice_elevation) / unit_conversion.METER_TO_FEET)),
                       'sensor_orifice_elevation_at_retrieval_time':  np.float64("{0:.4f}".format( \
                                                float(self.final_sensor_orifice_elevation) / unit_conversion.METER_TO_FEET)),
                       'sensor_orifice_elevation_units' : 'meters',
                       'time_coverage_resolution': resolution_string.format(1/self.frequency),
                       'summary': self.summary,
                       'stn_station_number': self.stn_station_number,
                       'stn_instrument_id': self.stn_instrument_id,
                       'featureType': 'timeSeries'
                       }
        
        if self.pressure_type == 'Sea Pressure':
            #get deployment and retrieval time stamps
            #This will need to change based on the time zone formats of STN
            self.deployment_time = unit_conversion.convert_ms_to_datestring(self.deployment_time, pytz.utc)
            self.retrieval_time = unit_conversion.convert_ms_to_datestring(self.retrieval_time, pytz.utc)
            global_vars['deployment_time'] = self.deployment_time
            global_vars['retrieval_time'] = self.retrieval_time
            global_vars['salinity'] = self.salinity
            
            global_vars['initial_land_surface_elevation'] = np.float64("{0:.4f}".format( \
                            float(self.initial_land_surface_elevation) / unit_conversion.METER_TO_FEET))
            global_vars['final_land_surface_elevation'] = np.float64("{0:.4f}".format( \
                                                float(self.final_sensor_orifice_elevation) / unit_conversion.METER_TO_FEET))
            global_vars['land_surface_elevation_units'] = 'meters'

        var_dict['global_vars_dict'] = global_vars

        return var_dict


if __name__ == '__main__':
    pass
