'''
Created on Feb 4, 2016

@author: chogg
'''
import pandas as pd
import unit_conversion
import pytz
import csv as csv_package

class StormCSV(object):
    
    def __init__(self):
        pass
    
    def process_csv(self,so):
        
#         if so.csv['Storm Tide with Unfiltered Water Level'].get() == True:
#             so.get_meta_data()
#             so.get_raw_water_level()
#             so.get_surge_water_level()
#             self.Storm_Tide_and_Unfiltered_Water_Level(so)
            
        if so.csv['Storm Tide Water Level'].get() == True:
            so.get_meta_data()
            so.get_raw_water_level()
            so.get_surge_water_level()
            self.Storm_Tide_Water_Level(so)
            
        if so.csv['Atmospheric Pressure'].get() == True:
            so.get_air_meta_data()
            so.get_air_time()
            so.get_raw_air_pressure()
            self.Atmospheric_Pressure(so)
            
    
    def Storm_Tide_and_Unfiltered_Water_Level(self,so):
        
        #adjust date times to appropriate time zone
        format_time = [unit_conversion.convert_ms_to_date(x, pytz.utc) for x in so.sea_time]
        format_time = unit_conversion.adjust_from_gmt(format_time, so.timezone, so.daylight_savings)
        format_time = [x.strftime('%m/%d/%y %H:%M:%S.%f') for x in format_time]
        format_time = [x[0:(len(x) - 4)] for x in format_time]
        #convert decibars to inches of mercury
        format_air_pressure = so.interpolated_air_pressure * unit_conversion.DBAR_TO_INCHES_OF_MERCURY
        format_surge_water_level = so.surge_water_level * unit_conversion.METER_TO_FEET
        format_unfiltered_water_level = so.raw_water_level * unit_conversion.METER_TO_FEET
        #convert meters to feet
        
        
        if so.daylight_savings != None and so.daylight_savings == True: 
            column1 = '%s Daylight Savings Time' % so.timezone 
        else:
            column1 = '%s Time' % so.timezone  
            
        excelFile = pd.DataFrame({column1: format_time, 
                                  'Air Pressure in Inches of Hg': format_air_pressure,
                                  'Storm Tide Water Level in Feet': format_surge_water_level,
                                  'Unfiltered Water Level in Feet': format_unfiltered_water_level
                                  })
        
        out_file_name = ''.join([so.output_fname,'_stormtide_unfiltered','.csv'])
            
        with open(out_file_name, 'w') as csvfile:
            writer = csv_package.writer(csvfile, delimiter=',')
            
            
            csv_header = ["","Latitude: %.4f" % so.latitude, 'Longitude: %.4f' % so.longitude, \
                'STN_Station_Number: %s' % so.stn_station_number]
            writer.writerow(csv_header)
           
        
        excelFile.to_csv(path_or_buf=out_file_name, mode='a', columns=[column1,
                                                             'Unfiltered Water Level in Feet',
                                                             'Storm Tide Water Level in Feet',
                                                             'Air Pressure in Inches of Hg'])
        
    def Storm_Tide_Water_Level(self, so):
        
        #adjust date times to appropriate time zone
        format_time = [unit_conversion.convert_ms_to_date(x, pytz.utc) for x in so.sea_time]
        format_time = unit_conversion.adjust_from_gmt(format_time, so.timezone, so.daylight_savings)
        format_time = [x.strftime('%m/%d/%y %H:%M:%S')for x in format_time]
        
        #convert decibars to inches of mercury
        format_air_pressure = so.interpolated_air_pressure * unit_conversion.DBAR_TO_INCHES_OF_MERCURY
        format_surge_water_level = so.surge_water_level * unit_conversion.METER_TO_FEET
        #convert meters to feet
        
        
        if so.daylight_savings != None and so.daylight_savings == True: 
            column1 = '%s Daylight Savings Time' % so.timezone 
        else:
            column1 = '%s Time' % so.timezone  
            
        excelFile = pd.DataFrame({column1: format_time[::4], 
                                  'Air Pressure in Inches of Hg': format_air_pressure[::4],
                                  'Storm Tide Water Level in Feet': format_surge_water_level[::4],
                                  })
        
        out_file_name = ''.join([so.output_fname,'_stormtide','.csv'])
            
        with open(out_file_name, 'w') as csvfile:
            writer = csv_package.writer(csvfile, delimiter=',')
            
            
            csv_header = ["","Latitude: %.4f" % so.latitude, 'Longitude: %.4f' % so.longitude, \
                'STN_Station_Number: %s' % so.stn_station_number]
            writer.writerow(csv_header)
           
        
        excelFile.to_csv(path_or_buf=out_file_name, mode='a', columns=[column1,
                                                             'Storm Tide Water Level in Feet',
                                                             'Air Pressure in Inches of Hg'])
        
    def Atmospheric_Pressure(self, so):
        
        #adjust date times to appropriate time zone
        format_time = [unit_conversion.convert_ms_to_date(x, pytz.utc) for x in so.air_time]
        format_time = unit_conversion.adjust_from_gmt(format_time, so.timezone, so.daylight_savings)
        format_time = [x.strftime('%m/%d/%y %H:%M:%S') for x in format_time]
        
        #convert decibars to inches of mercury
        format_air_pressure = so.raw_air_pressure * unit_conversion.DBAR_TO_INCHES_OF_MERCURY
        #convert meters to feet
        
        
        if so.daylight_savings != None and so.daylight_savings == True: 
            column1 = '%s Daylight Savings Time' % so.timezone 
        else:
            column1 = '%s Time' % so.timezone  
            
        excelFile = pd.DataFrame({column1: format_time, 
                                  'Air Pressure in Inches of Hg': format_air_pressure,
                                  })
        
        out_file_name = ''.join([so.output_fname,'_barometric_pressure','.csv'])
            
        with open(out_file_name, 'w') as csvfile:
            writer = csv_package.writer(csvfile, delimiter=',')
            
            
            csv_header = ["","Latitude: %.4f" % so.air_latitude, 'Longitude: %.4f' % so.air_longitude, \
                'STN_Station_Number: %s' % so.air_stn_station_number]
            writer.writerow(csv_header)
           
        
        excelFile.to_csv(path_or_buf=out_file_name, mode='a', columns=[column1,
                                                             'Air Pressure in Inches of Hg'])
         
        