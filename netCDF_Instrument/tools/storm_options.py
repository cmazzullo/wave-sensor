'''
Created on Feb 4, 2016

@author: chogg
'''
from tools.storm_data import StormData
import numpy as np
from netCDF_Utils import nc
import unit_conversion


class StormOptions(StormData):
    '''options to interface between main gui and storm operations'''
    def __init__(self):
        
        self.netCDF = {
                        'Storm Tide with Unfiltered Water Level': None,
                       'Storm Tide Water Level': None,
                       }
        
        self.csv = {
                    'Storm Tide with Unfiltered Water Level': None,
                    'Storm Tide Water Level': None,
                    'Atmospheric Pressure': None
                    
                    }
        
        self.graph = {
                    'Storm Tide with Unfiltered Water Level and Wind Data' : None,
                    'Storm Tide with Unfiltered Water Level': None,
                    'Storm Tide Water Level': None,
                    'Atmospheric Pressure': None
                      }
        
        self.statistics = {'H1/3': None,
                           'H1/32': None, # contains functions and labels
                     'T1/3': None,
                     'H10%': None,
                     'H1%': None,
                     'RMS' : None,
                     'Median': None,
                     'Maximum': None,
                     'Average': None,
                     'Average Z Cross': None,
                     'Mean Wave Period': None,
                     'Crest': None,
                     'Peak Wave': None}
        
        #not using the formatted time properties thus far...
        self.sea_fname = None
        self.air_fname = None
        self.wind_fname = None
        self.output_fname = None
        self.sea_time = None
        self.formatted_sea_time = None
        self.air_time = None
        self.formatted_air_time = None
        self.wind_time = None
        self.formatted_wind_time = None
        self.wind_time = None
        self.timezone = None
        self.daylight_savings = None
        self.raw_air_pressure = None
        self.raw_sea_pressure = None
        self.corrected_sea_pressure = None
        self.interpolated_air_pressure = None
        self.sea_pressure_mean = None
        self.surge_sea_pressure = None
        self.wave_sea_pressure = None
        self.raw_water_level = None
        self.surge_water_level = None
        self.wave_water_level = None
        self.wave_water_level_chunks = None
        self.elevation_chunks = None
        self.wave_time_chunks = None
        self.wind_speed_chunks = None
        self.sensor_orifice_elevation = None
        self.land_surface_elevation = None
        self.derived_water_depth = None
        self.wind_direction = None
        self.u = None
        self.v = None
        self.wind_speed = None
        self.surge_peak = None
        self.wave_peak = None
        self.total_peak = None
        self.datum = None
        self.latitude = None
        self.longitude = None
        self.stn_station_number = None
        self.air_latitude = None
        self.air_longitude = None
        self.air_stn_station_number = None
        self.wind_latitude = None
        self.wind_longitude = None
        self.wind_stn_station_number = None
        self.sliced = False
        self.wind_sliced = False
        self.begin = None
        self.end = None
        self.baroYLims = None
        self.wlYLims = None
        self.stat_dictionary = None
        self.stn_instrument_id = None
        self.air_stn_instrument_id = None
        
    def get_sea_time(self):
        if self.sea_time is None:
            self.sea_time = self.extract_time(self.sea_fname)
            
        return self.sea_time
    
    def get_formatted_sea_time(self):
        if self.formatted_sea_time is None:
            
            self.get_sea_time()
                
            self.formatted_sea_time = self.convert_formatted_time(self.sea_time, self.timezone, \
                                         self.daylight_savings)
    
    def get_air_time(self):
        if self.air_time is None:
            self.air_time = self.extract_time(self.air_fname)
            
    #focus
    def get_wind_time(self):
        if self.wind_time is None:
            self.wind_time = self.extract_time(self.wind_fname) 
   
    def get_sea_pressure(self):
        if self.raw_sea_pressure is None:
            self.raw_sea_pressure = self.extract_raw_sea_pressure(self.sea_fname)
            
    def get_raw_air_pressure(self):
        if self.raw_air_pressure is None:
            self.raw_air_pressure = self.extract_raw_air_pressure(self.air_fname)
            
    def get_interpolated_air_pressure(self):
        if self.interpolated_air_pressure is None:
            
            self.get_sea_time()
            self.get_air_time()
            self.get_raw_air_pressure()
            self.interpolated_air_pressure = self.interpolate_air_pressure(self.sea_time, self.air_time, \
                                            self.raw_air_pressure)
    def get_wind_speed(self):
        if self.u is None:
            self.u = self.extract_wind_u(self.wind_fname)
            self.v = self.extract_wind_v(self.wind_fname)
            self.wind_speed = self.derive_wind_speed(self.u,self.v)
 
    def get_sensor_orifice_elevation(self):
        if self.sensor_orifice_elevation is None:
            
            self.get_sea_pressure()
            self.sensor_orifice_elevation = np.array(self.extract_sensor_orifice_elevation(self.sea_fname, \
                                            len(self.raw_sea_pressure)))
            
    def get_land_surface_elevation(self):
        if self.land_surface_elevation is None:
            
            self.get_sea_pressure()
            self.land_surface_elevation = self.extract_land_surface_elevation(self.sea_fname, \
                                            len(self.raw_sea_pressure))
            
    def get_derived_water_depth(self):
        if self.derived_water_depth is None:
            self.get_land_surface_elevation()
            self.get_sensor_orifice_elevation()
            self.derived_water_depth = self.sensor_orifice_elevation - self.land_surface_elevation
            
    def get_corrected_pressure(self):
        if self.corrected_sea_pressure is None:
            self.slice_series()
            self.corrected_sea_pressure = self.raw_sea_pressure - self.interpolated_air_pressure
            
    def get_pressure_mean(self):
        if self.sea_pressure_mean is None:
            
            self.get_corrected_pressure()
            self.sea_pressure_mean = np.mean(self.corrected_sea_pressure)
        
    def slice_series(self):
        if self.sliced == False:
            self.get_interpolated_air_pressure()
            self.get_sea_pressure()
            self.get_sensor_orifice_elevation()
            self.get_land_surface_elevation()
            #get the indexes for the first and last point which the sea and air times overlap
            
            itemindex = np.where(~np.isnan(self.interpolated_air_pressure))
            self.begin = begin = itemindex[0][0]
            self.end = end = itemindex[0][len(itemindex[0]) - 1]
            print(self.begin,self.end)
            #slice all data to include all instances where the times overlap
            self.interpolated_air_pressure = self.interpolated_air_pressure[begin:end]
            self.raw_sea_pressure = self.raw_sea_pressure[begin:end]
            self.sea_time = self.sea_time[begin:end]
            self.sensor_orifice_elevation = self.sensor_orifice_elevation[begin:end]
            self.land_surface_elevation = self.land_surface_elevation[begin:end]
            
            self.sliced = True
            
    
    def slice_wind_data(self):
        '''Slice off portions of the wind time that do not overlap with the sea time
        *I may want to make sure ALL data is sliced together in the future'''
        if self.wind_sliced == False:
            self.get_wind_time()
            self.get_wind_speed()
#             self.get_wind_direction()
            
            self.wind_time[np.where(self.wind_time < self.sea_time[0])] = np.NaN
            self.wind_time[np.where(self.wind_time > self.sea_time[-1])] = np.NaN
            wind_itemindex = np.where(~np.isnan(self.wind_time))
            
            wind_begin = wind_itemindex[0][0]
            wind_end = wind_itemindex[0][len(wind_itemindex[0]) - 1]
            
            self.wind_time = self.wind_time[wind_begin:wind_end]
            self.wind_speed = self.wind_speed[wind_begin:wind_end]
            self.u = self.u[wind_begin:wind_end]
            self.v = self.v[wind_begin:wind_end]
#             self.wind_direction = self.wind_direction[wind_begin:wind_end]
            self.wind_sliced = True
        
    
    def get_surge_sea_pressure(self):
        if self.surge_sea_pressure is None:
            self.slice_series()
            self.get_corrected_pressure()
            
            self.surge_sea_pressure = self.derive_surge_sea_pressure(self.corrected_sea_pressure, \
                                                                     self.sea_pressure_mean)
            
    def get_wave_sea_pressure(self):
        if self.wave_sea_pressure is None:
            self.get_surge_sea_pressure()
            self.wave_sea_pressure = (self.corrected_sea_pressure - self.sea_pressure_mean) 
            - self.surge_sea_pressure
            
    def get_raw_water_level(self):
        if self.raw_water_level is None:
            self.get_corrected_pressure()
            self.get_sensor_orifice_elevation()
            
            self.raw_water_level =  np.array(self.derive_raw_water_level(self.corrected_sea_pressure, 
                                                                self.sensor_orifice_elevation)) 
            
    def get_surge_water_level(self): 
        if self.surge_water_level is None:
            self.get_corrected_pressure()
            self.get_sensor_orifice_elevation()
            self.get_pressure_mean()
            self.get_surge_sea_pressure()
            
            self.surge_water_level = np.array(self.derive_filtered_water_level(self.surge_sea_pressure, 
                                                                      self.sea_pressure_mean, 
                                                                      self.sensor_orifice_elevation))
            
    def test_water_elevation_below_sensor_orifice_elvation(self):
        self.raw_water_level[np.where(self.raw_water_level < self.sensor_orifice_elevation)] = np.NaN
        self.surge_water_level[np.where(self.surge_water_level < self.sensor_orifice_elevation)] = np.NaN
        
        
        
        
                  
    def get_wave_water_level(self, method = 'hyrdostatic'):
        if self.wave_water_level_chunks is None:
            self.get_raw_water_level()
            self.get_surge_water_level()
                
#             if method == 'hyrdostatic':
            self.wave_water_level = self.raw_water_level - self.surge_water_level
            
            self.chunk_data()
#             else:
#                 self.wave_water_level_chunks, self.wave_time_chunks = self.derive_lwt_wave_water_level(self.sea_time, 
#                                                                          self.wave_sea_pressure,
#                                                                          self.land_surface_elevation, 
#                                                                          self.sensor_orifice_elevation,)
                
    def chunk_data(self):
        start_index = 0
        end_index = 4096
        increment = 2048
        self.wave_time_chunks, self.wave_water_level_chunks, self.wind_speed_chunks = [], [], []
        
        if self.wind_speed is not None:
            ws = np.interp(self.sea_time,self.wind_time,self.wind_speed)
        else:
            self.wind_speed_chunks = None
        
        while end_index < len(self.wave_water_level):
            self.wave_time_chunks.append(self.sea_time[start_index:end_index] / 1000)
            self.wave_water_level_chunks.append(self.wave_water_level[start_index:end_index])
            
            if self.wind_speed is not None:
                self.wind_speed_chunks.append(ws[start_index:end_index] / 
                                          unit_conversion.METERS_PER_SECOND_TO_MILES_PER_HOUR)
            
            
            start_index += increment
            end_index += increment

    def get_wave_statistics(self):
        if self.stat_dictionary is None:
            self.get_wave_water_level()
            self.stat_dictionary = self.derive_statistics(self.wave_water_level_chunks, self.wave_time_chunks, \
                                                          self.wind_speed_chunks)
            
    def check_file_types(self):
        try:
            nc.get_air_pressure(self.air_fname)
            nc.get_pressure(self.sea_fname)
        except:
            return False
        
        return True
        
            
    def check_selected(self):
        for x in self.netCDF:
            if self.netCDF[x].get() == True:
                return True
            
        for x in self.csv:
            if self.csv[x].get() == True:
                return True
            
        for x in self.graph:
            if self.graph[x].get() == True:
                return True
            
        for x in self.statistics:
            if self.statistics[x].get() == True:
                return True
            
        return False
    
    def air_check_selected(self):
        for x in self.netCDF:
            if self.netCDF[x].get() == True:
                return True
            
        for x in self.csv:
            if x != 'Atmospheric Pressure' and self.csv[x].get() == True:
                return True
            
        for x in self.graph:
            if x != 'Atmospheric Pressure' and self.graph[x].get() == True:
                return True
            
        return False  
       
    
    def wind_check_selected(self):
        for x in self.graph:
            if x == 'Storm Tide with Unfiltered Water Level and Wind Data' and self.graph[x].get() == True:
                return True
            
        return False
    
    def stat_check_selected(self):
        count = 0
        for x in self.statistics:
            if self.statistics[x].get() == True:
                count += 1
                
        if count > 2:
            return False
        else:
            return True
    
    def time_comparison(self):
        '''Checks to see the overlap of the two pressure files.  Returns 1 if there is some overlap, 
        2 if none, 0 if all overlaps'''
        self.get_sea_time()
        self.get_air_time()
        
        if (self.air_time[-1] < self.sea_time[0]) or (self.air_time[0] > self.sea_time[-1]):
            return 2
        
        elif (self.air_time[0] > self.sea_time[0] or self.air_time[-1] < self.sea_time[-1]):
            return 1
            
        return 0
    
    def format_output_fname(self, og_fname):
        if og_fname != None and og_fname != '' :
            last_index = og_fname.find('.')
            if last_index != -1:
                self.output_fname = og_fname[0:last_index]
            else:
                self.output_fname = og_fname
        else:
            self.output_fname = 'output'
            
    
    def get_meta_data(self):
        if self.datum is None:
            self.datum = nc.get_geospatial_vertical_reference(self.sea_fname)
            self.latitude = nc.get_variable_data(self.sea_fname,'latitude')
            self.longitude = nc.get_variable_data(self.sea_fname,'longitude')
            self.stn_station_number = nc.get_global_attribute(self.sea_fname, 'stn_station_number')
            self.stn_instrument_id = nc.get_global_attribute(self.sea_fname, 'stn_instrument_id')
            
    def get_air_meta_data(self):
        if self.air_latitude is None:
            self.air_latitude = nc.get_variable_data(self.air_fname,'latitude')
            self.air_longitude = nc.get_variable_data(self.air_fname,'longitude')
            self.air_stn_station_number = nc.get_global_attribute(self.air_fname, 'stn_station_number')
            self.air_stn_instrument_id = nc.get_global_attribute(self.air_fname, 'stn_instrument_id')
            
    def get_wind_meta_data(self):
        if self.wind_latitude is None:
            self.wind_latitude = nc.get_variable_data(self.wind_fname,'latitude')
            self.wind_longitude = nc.get_variable_data(self.wind_fname,'longitude')
            self.wind_stn_station_number = nc.get_global_attribute(self.wind_fname, 'stn_station_number')
            
   
            
    def clear_data(self):
        self.sea_fname = None
        self.air_fname = None
        self.wind_fname = None
        self.output_fname = None
        self.sea_time = None
        self.formatted_sea_time = None
        self.air_time = None
        self.formatted_air_time = None
        self.wind_time = None
        self.formatted_wind_time = None
        self.wind_time = None
        self.timezone = None
        self.daylight_savings = None
        self.raw_air_pressure = None
        self.raw_sea_pressure = None
        self.corrected_sea_pressure = None
        self.interpolated_air_pressure = None
        self.sea_pressure_mean = None
        self.surge_sea_pressure = None
        self.wave_sea_pressure = None
        self.raw_water_level = None
        self.surge_water_level = None
        self.wave_water_level = None
        self.wave_water_level_chunks = None
        self.elevation_chunks = None
        self.wave_time_chunks = None
        self.sensor_orifice_elevation = None
        self.land_surface_elevation = None
        self.derived_water_depth = None
        self.wind_direction = None
        self.u = None
        self.v = None
        self.wind_speed = None
        self.surge_peak = None
        self.wave_peak = None
        self.total_peak = None
        self.datum = None
        self.latitude = None
        self.longitude = None
        self.stn_station_number = None
        self.air_latitude = None
        self.air_longitude = None
        self.air_stn_station_number = None
        self.wind_latitude = None
        self.wind_longitude = None
        self.wind_stn_station_number = None
        self.sliced = False
        self.wind_sliced = False
        self.begin = None
        self.end = None
        self.baroYLims = None
        self.wlYLims = None
        self.stat_dictionary = None
        self.stn_instrument_id = None
        self.air_stn_instrument_id = None
        
            
        