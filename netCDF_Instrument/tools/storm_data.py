'''
Created on Feb 4, 2016

@author: chogg
'''
import numpy as np
from scipy import signal
from NetCDF_Utils import nc
import unit_conversion as uc
import pressure_to_depth as p2d

class StormData(object):
    '''Interface for master Storm GUI to manipulate data files'''
    
    def __init__(self):
        pass
    
    def extract_time(self, fname):
        return nc.get_time(fname)
    
    def convert_formatted_time(self, time_data, tzinfo, daylight_savings):
        '''Converts ms to date time objects and formats to desired timezone'''
        date_times = uc.convert_ms_to_date(time_data, tzinfo)
        return uc.adjust_from_gmt(date_times, tzinfo, daylight_savings)
    
    def extract_raw_sea_pressure(self, fname):
        return nc.get_pressure(fname)
    
    def extract_raw_air_pressure(self, fname):
        return nc.get_air_pressure(fname)
    
    def extract_wind_speed(self, fname):
        return nc.get_variable_data(fname, 'wind_speed')
    
    def extract_wind_direction(self, fname):
        return nc.get_variable_data(fname, 'wind_direction')
    
    def interpolate_air_pressure(self, sea_time, air_time, raw_air_pressure):
        return np.interp(sea_time, air_time, raw_air_pressure,
                             left=np.NaN, right=np.NaN)
        
    def extract_sensor_orifice_elevation(self, fname, series_len):
        init, final = nc.get_sensor_orifice_elevation(fname)
        return np.linspace(init, final, series_len)
    
    def extract_land_surface_elevation(self, fname, series_len):
        init, final = nc.get_land_surface_elevation(fname)
        return np.linspace(init, final, series_len)
    
    def derive_surge_sea_pressure(self, sea_pressure_data, sea_pressure_mean):
        return p2d.lowpass_filter(sea_pressure_data - sea_pressure_mean)
    
    def derive_wave_sea_pressure(self, sea_pressure_data, surge_pressure_data):
        return sea_pressure_data - surge_pressure_data
    
    def derive_raw_water_level(self, sea_pressure_data, sensor_orifice_elevation):
        print(len(sea_pressure_data), len(sensor_orifice_elevation))
        return sensor_orifice_elevation + p2d.hydrostatic_method(sea_pressure_data)
    
    def derive_filtered_water_level(self, pressure_data, pressure_mean, \
                                 sensor_orifice_elevation):
        
    
        return sensor_orifice_elevation + p2d.hydrostatic_method(pressure_data + pressure_mean)
    
    def derive_lwt_wave_water_level(self, sea_time, pressure_data, water_depth, sensor_orifice_elevation):
        '''ugh I'm using the term water depth again... ill change it'''
        
        #removed parameter for timestep since 4hz is necessary for accurate linear wave theory calculations
        return p2d.combo_method(sea_time, pressure_data,
                                sensor_orifice_elevation, water_depth)
    
    
    
    
        