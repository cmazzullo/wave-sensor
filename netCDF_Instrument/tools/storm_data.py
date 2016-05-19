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
        self.stats = stats.Stats()
    
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
        
   
        
    def derive_statistics(self, dchunks, tchunks, elevchunks = None ,pchunks=None, wchunks=None, meters=True):
        
        if meters is True:
            units = 1
        else:
            units = uc.METER_TO_FEET
       
        func_dict = {
                     'T1/3': lambda spec, freq, time, depth: self.stats.significant_wave_period(spec, freq, depth, time[1]-time[0]),
                     'H1/3 std': lambda spec, freq, time, depth: self.stats.significant_wave_height_standard(depth \
                                                                                * units),
                     'H1/3': lambda spec, freq, time, depth: self.stats.significant_wave_height(spec,freq, time, depth \
                                                                                * units),
                     'H10%': lambda spec, freq, time, depth: self.stats.ten_percent_wave_height(spec,freq, time, depth \
                                                                                * units),
                     'H1%': lambda spec, freq, time, depth: self.stats.one_percent_wave_height(spec,freq, time, depth \
                                                                                * units),
                     'RMS': lambda spec, freq, time, depth: self.stats.rms_wave_height(spec, freq, time, depth \
                                                                                * units),
                     'Median': lambda spec, freq, time, depth: self.stats.median_wave_height(spec, freq, time, depth \
                                                                                * units),
                     'Maximum': lambda spec, freq, time, depth: self.stats.maximum_wave_height(spec, freq, time, depth \
                                                                                * units),
                     'Average': lambda spec, freq, time, depth: self.stats.average_wave_height(spec, freq, time, depth \
                                                                                * units),
                     'Average Z Cross': lambda spec, freq, time, depth: self.stats.average_zero_crossing_period(spec, freq, time, depth),
                     'Mean Wave Period': lambda spec, freq, time, depth: self.stats.mean_wave_period(spec, freq, time, depth),
                     'Crest': lambda spec, freq,time, depth: self.stats.crest_wave_period(spec, freq, time, depth),
                     'Peak Wave': lambda spec, freq, time, depth: self.stats.peak_wave_period(spec, freq, time, depth)
                    }
        
        stat_dict = {}
        stat_dict['time'] = [np.average(t) * 1000 for t in tchunks]
    
        stat_dict['Frequency'], stat_dict['Spectrum'] = [], []
        stat_dict['LWTFrequency'], stat_dict['LWTSpectrum'] = [], []
        
        for x in range(0,len(tchunks)):
            
            freq, amp = self.stats.welch_power_spectrum(dchunks[x], tchunks[x][1]-tchunks[x][0])
            
            stat_dict['Frequency'].append(freq)
            stat_dict['Spectrum'].append(amp)
            
            freq2, amp2 = self.stats.lwt_pressure_to_wl_spectrum(tchunks[x], pchunks[x], elevchunks[x], elevchunks[x])
            
            stat_dict['LWTFrequency'].append(freq2)
            stat_dict['LWTSpectrum'].append(amp2)
            
        for y in func_dict:
            stat_dict[y] = []
            
        for x in range(0,len(stat_dict['time'])):
            for y in func_dict:
                stat_dict[y].append(\
                                    self.process_chunk(func_dict[y],tchunks[x],dchunks[x],\
                                                       stat_dict['Spectrum'][x],stat_dict['Frequency'][x]))
            self.stats.spectrum = None
      
        return stat_dict
    
    def process_chunk(self, stat_func, t_chunk,d_chunk,spec,freq):
        if np.isnan(np.sum(d_chunk)) == True:
            return np.NaN
        else:
            return stat_func(spec,freq,t_chunk,d_chunk)
           

    
    
    
    
        