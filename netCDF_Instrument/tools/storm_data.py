'''
Created on Feb 4, 2016

@author: chogg
'''
import numpy as np
from scipy import signal
from netCDF_Utils import nc
import unit_conversion as uc
import pressure_to_depth as p2d
import unit_conversion
import stats

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
    
    def derive_wind_speed(self, u, v):
        return [(np.sqrt(x**2 + y**2)) * \
                 unit_conversion.METERS_PER_SECOND_TO_MILES_PER_HOUR \
                 for x, y in zip(u,v)]
    
#     def extract_wind_direction(self, fname):
#         return nc.get_variable_data(fname, 'wind_direction')
    
    def extract_wind_u(self, fname):
        return nc.get_variable_data(fname, 'u')
    
    def extract_wind_v(self, fname):
        return nc.get_variable_data(fname, 'v')
    

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
        return sensor_orifice_elevation + p2d.hydrostatic_method(sea_pressure_data)
    
    def derive_filtered_water_level(self, pressure_data, pressure_mean, \
                                 sensor_orifice_elevation):
        
    
        return sensor_orifice_elevation + p2d.hydrostatic_method(pressure_data + pressure_mean)
    
    def derive_lwt_wave_water_level(self, sea_time, pressure_data, water_depth, sensor_orifice_elevation):
        '''ugh I'm using the term water depth again... ill change it'''
        
        #removed parameter for timestep since 4hz is necessary for accurate linear wave theory calculations
        return p2d.combo_method(sea_time, pressure_data,
                                sensor_orifice_elevation, water_depth)
        
   
        
    def derive_statistics(self, dchunks, tchunks, wchunks=None):
       
        func_dict = {
                     'T1/3': lambda time, depth: stats.significant_wave_period(depth, time[1]-time[0]),
                     'H1/3 std': lambda time, depth: stats.significant_wave_height_standard(depth \
                                                                                * uc.METER_TO_FEET),
                     'H1/3': lambda time, depth: stats.significant_wave_height(time, depth \
                                                                                * uc.METER_TO_FEET),
                     'H1/32': lambda time, depth, wind: stats.significant_wave_height2(time, depth \
                                                                                * uc.METER_TO_FEET, wind),
                     'H10%': lambda time, depth: stats.ten_percent_wave_height(time, depth \
                                                                                * uc.METER_TO_FEET),
                     'H1%': lambda time, depth: stats.one_percent_wave_height(time, depth \
                                                                                * uc.METER_TO_FEET),
                     'RMS': lambda time, depth: stats.rms_wave_height(time, depth \
                                                                                * uc.METER_TO_FEET),
                     'Median': lambda time, depth: stats.median_wave_height(time, depth \
                                                                                * uc.METER_TO_FEET),
                     'Maximum': lambda time, depth: stats.maximum_wave_height(time, depth \
                                                                                * uc.METER_TO_FEET),
                     'Average': lambda time, depth: stats.average_wave_height(time, depth \
                                                                                * uc.METER_TO_FEET),
                     'Average Z Cross': lambda time, depth: stats.average_zero_crossing_period(time, depth),
                     'Mean Wave Period': lambda time, depth: stats.mean_wave_period(time, depth),
                     'Crest': lambda time, depth: stats.crest_wave_period(time, depth),
                     'Peak Wave': lambda time, depth: stats.peak_wave_period(time, depth)
                    }
        stat_dict = {}
        stat_dict['time'] = [np.average(t) * 1000 for t in tchunks]
        
        for x in func_dict:
            if x == 'H1/32':
                if wchunks is not None:
                    stat_dict[x] = [self.process_chunk(func_dict[x],y,z,w) for [y,z,w] in zip(tchunks,dchunks,wchunks)]
            else:
                stat_dict[x] = [self.process_chunk(func_dict[x],y,z) for (y,z) in zip(tchunks,dchunks)]
      
        return stat_dict
    
    def process_chunk(self, stat_func, t_chunk,d_chunk, wchunk = None):
        if np.isnan(np.sum(d_chunk)) == True:
            return np.NaN
        else:
            if wchunk is None:
                return stat_func(t_chunk,d_chunk)
            else:
                return stat_func(t_chunk,d_chunk,wchunk)

    
    
    
    
        