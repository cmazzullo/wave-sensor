'''
Created on Feb 4, 2016

@author: chogg
'''
from tools.storm_data import StormData
import numpy as np
from netCDF_Utils import nc
from tools.storm_options import StormOptions


class MultiOptions():
    '''options to interface between main gui and storm operations'''
    def __init__(self):
        
        self.graph = {
                    'Atmospheric Pressure' : None,
                    'Storm Tide Water Level': None,
                    'Unfiltered Water Level': None,
                    'Wave Water Level': None
                      }
        
        #not using the formatted time properties thus far...
        self.sea_fnames = []
        self.air_fnames = []
        self.output_fname = None
        self.storm_objects = []
        self.timezone = None
        self.daylight_savings = None
        self.baroYLims = None
        self.wlYLims = None
       
    def file_check(self, mode = 'both'): 
        if mode == 'sea' or mode == 'both':
            for x in self.sea_fnames:
                if x != '':
                    return True
         
        if mode == 'air' or mode == 'both':       
            for x in self.air_fnames:
                if x != '':
                    return True
            
        return False
            

    def check_selected(self):
        for x in self.graph:
            if self.graph[x].get() == True:
                return True
        
        return False
    
    def option_check_selected(self):
        for x in self.graph:
            if x == 'Atmospheric Pressure': 
                if self.graph[x].get() == True and self.file_check(mode='air') == False:
                    return False
            else: 
                if self.graph[x].get() == True and self.file_check(mode='sea') == False:
                    return False
            
        return True
    
    def create_storm_objects(self):
        last_water_index, last_air_index, latest_change = -1, -1, -1
        for x in range (0, len(self.sea_fnames)):
            if self.sea_fnames[x] != '':
                last_water_index = x
            if self.air_fnames[x] != '':
                last_air_index = x
                
            if (last_water_index > -1 and last_air_index > -1) and \
                (last_water_index > latest_change or last_air_index > latest_change):
                so = StormOptions()
                so.sea_fname = self.sea_fnames[last_water_index]
                so.air_fname = self.air_fnames[last_air_index]
                so.get_meta_data()
                so.get_air_meta_data()
                so.get_raw_water_level()
                so.get_surge_water_level()
                so.test_water_elevation_below_sensor_orifice_elvation()
                so.get_wave_water_level()
                
                self.storm_objects.append(so)
                
                latest_change = x
            
            elif last_air_index > -1 and last_air_index > latest_change:
                so = StormOptions()
                so.air_fname = self.air_fnames[last_air_index]
                so.get_air_meta_data()
                so.get_air_time()
                so.get_raw_air_pressure()
                
                self.storm_objects.append(so)
                
                latest_change = x
    
    def format_output_fname(self, og_fname):
        if og_fname != None and og_fname != '' :
            last_index = og_fname.find('.')
            if last_index != -1:
                self.output_fname = og_fname[0:last_index]
            else:
                self.output_fname = og_fname
        else:
            self.output_fname = 'output'
            
    def clear_data(self):
        self.sea_fnames = []
        self.air_fnames = []
        self.output_fname = None
        self.storm_objects = []
        self.timezone = None
        self.daylight_savings = None
        self.baroYLims = None
        self.wlYLims = None
        
            
        