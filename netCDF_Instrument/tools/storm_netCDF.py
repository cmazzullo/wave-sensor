'''
Created on Feb 4, 2016

@author: chogg
'''
from netCDF_Utils import nc
import uuid
import time

class Storm_netCDF(object):
    
    def __init__(self):
        pass
    
    def process_netCDFs(self,so):
        
        if so.netCDF['Storm Tide with Unfiltered Water Level'].get() == True:
            so.get_meta_data()
            so.get_raw_water_level()
            so.get_surge_water_level()
            so.get_wave_water_level()
            self.Storm_Tide_and_Unfiltered_Water_Level(so)
#           
        time.sleep(2)  
        if so.netCDF['Storm Tide Water Level'].get() == True:
            so.get_meta_data()
            so.get_raw_water_level()
            so.get_surge_water_level()
            self.Storm_Tide_Water_Level(so)
            
    def Common_Attributes(self,so,file_name,step):
        
        
        #nc.set_var_attribute(water_fname, 'sea_pressure', 'sea_uuid', sea_uuid)
        nc.set_global_attribute(file_name, 'uuid', str(uuid.uuid4()))
    
        #append air pressure
        instr_dict = nc.get_instrument_data(so.air_fname, 'air_pressure')
        nc.append_air_pressure(file_name, so.interpolated_air_pressure[::step], so.air_fname)
        nc.set_instrument_data(file_name, 'air_pressure', instr_dict)
    
        #update the lat and lon comments
        lat_comment = nc.get_variable_attr(file_name, 'latitude', 'comment')
        nc.set_var_attribute(file_name, 'latitude', 'comment',  \
                             ''.join([lat_comment, ' Latitude of sea pressure sensor used to derive ' \
                                      'sea surface elevation.']))
        lon_comment = nc.get_variable_attr(file_name, 'longitude', 'comment')
        nc.set_var_attribute(file_name, 'longitude', 'comment',  \
                             ''.join([lon_comment, ' Longitude of sea pressure sensor used to derive ' \
                                      'sea surface elevation.']))
    
        #set sea_pressure instrument data to global variables in water_level netCDF
        sea_instr_data = nc.get_instrument_data(so.sea_fname,'sea_pressure')
        for x in sea_instr_data:
            attrname = ''.join(['sea_pressure_',x])
            nc.set_global_attribute(file_name,attrname,sea_instr_data[x])
        lat = nc.get_variable_data(file_name, 'latitude')
        lon = nc.get_variable_data(file_name, 'longitude')
   
        first_stamp = nc.get_global_attribute(file_name, 'time_coverage_start')
        last_stamp = nc.get_global_attribute(file_name, 'time_coverage_end')
        
        nc.set_global_attribute(file_name,'title','Calculation of water level at %.4f latitude,'
                                ' %.4f degrees longitude from the date range of %s to %s.'
                                % (lat,lon,first_stamp,last_stamp))
        
            
    def Wave_Statistics(self,so):
        out_fname2 = ''.join([so.output_fname,'_stormtide_unfiltered','.nc'])
        
        step = 1
        nc.custom_copy(so.sea_fname, out_fname2, so.begin, so.end, mode = 'storm_surge', step=step)
        self.Common_Attributes(so, out_fname2, step)
        
        sea_uuid = nc.get_global_attribute(so.sea_fname, 'uuid')
        air_uuid = nc.get_global_attribute(so.air_fname, 'uuid')
        
        nc.wave_copy(so.sea_fname, out_fname2, so.begin, so.end, step = step, )
            
            
    def Storm_Tide_and_Unfiltered_Water_Level(self,so):
        
        out_fname2 = ''.join([so.output_fname,'_stormtide_unfiltered','.nc'])
        
        step = 1
        nc.custom_copy(so.sea_fname, out_fname2, so.begin, so.end, mode = 'storm_surge', step=step)
        self.Common_Attributes(so, out_fname2, step)
            
        nc.set_global_attribute(out_fname2,'summary','This file contains three time series: 1)' 
                                ' air pressure 2) sea surface elevation 3) unfiltered sea surface elevation.'
                                ' The second was derived'
                                ' from a time series of high frequency sea pressure measurements'
                                ' adjusted using the former and then lowpass filtered to remove'
                                ' waves of period 1 second or less. The third is also sea surface elevation'
                                ' with no such filter.')
        
        nc.append_depth(out_fname2, so.surge_water_level[::step])
        sea_uuid = nc.get_global_attribute(so.sea_fname, 'uuid')
        air_uuid = nc.get_global_attribute(so.air_fname, 'uuid')
        nc.set_var_attribute(out_fname2, 'air_pressure', 'air_uuid', air_uuid)
        
        nc.append_variable(out_fname2, 'unfiltered_water_surface_height_above_reference_datum', so.raw_water_level[::step], \
                            'Unfiltered Sea Surface Elevation', 'unfiltered_water_surface_height_above_reference_datum')
        nc.append_variable(out_fname2, 'wave_wl', so.wave_water_level[::step], \
                            'wave_wl', 'wave_wl')
        nc.set_var_attribute(out_fname2, 'water_surface_height_above_reference_datum', \
                             'air_uuid', air_uuid)
        nc.set_var_attribute(out_fname2, 'water_surface_height_above_reference_datum', \
                             'sea_uuid', sea_uuid)
        nc.set_var_attribute(out_fname2, 'unfiltered_water_surface_height_above_reference_datum', \
                             'air_uuid', air_uuid)
        nc.set_var_attribute(out_fname2, 'unfiltered_water_surface_height_above_reference_datum', \
                             'sea_uuid', sea_uuid)
        nc.set_var_attribute(out_fname2, 'unfiltered_water_surface_height_above_reference_datum', \
                             'units', 'meters')
        nc.set_var_attribute(out_fname2, 'unfiltered_water_surface_height_above_reference_datum', \
                             'nodc_name', 'WATER LEVEL')
        nc.set_var_attribute(out_fname2, 'unfiltered_water_surface_height_above_reference_datum', \
                             'ioos_category', 'sea_level')
    
       
    def Storm_Tide_Water_Level(self, so): 
        out_fname2 = ''.join([so.output_fname,'_stormtide','.nc'])
        
        step = 4
        nc.custom_copy(so.sea_fname, out_fname2, so.begin, so.end, mode = 'storm_surge', step=step)
        
        self.Common_Attributes(so,out_fname2,step)
        
            
        nc.set_global_attribute(out_fname2,'summary','This file contains two time series: 1)' 
                                'air pressure 2) sea surface elevation.  The latter was derived'
                                ' from a time series of high frequency sea pressure measurements '
                                ' adjusted using the former and then lowpass filtered to remove '
                                ' waves of period 1 second or less.')
        
        nc.append_depth(out_fname2, so.surge_water_level[::step])
        
        sea_uuid = nc.get_global_attribute(so.sea_fname, 'uuid')
        air_uuid = nc.get_global_attribute(so.air_fname, 'uuid')
        nc.set_var_attribute(out_fname2, 'air_pressure', 'air_uuid', air_uuid)
        nc.set_var_attribute(out_fname2, 'water_surface_height_above_reference_datum', \
                             'air_uuid', air_uuid)
        nc.set_var_attribute(out_fname2, 'water_surface_height_above_reference_datum', \
                             'sea_uuid', sea_uuid)