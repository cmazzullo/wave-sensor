'''
Created on Mar 23, 2016

@author: chogg
'''
import netCDF_Utils.nc as nc
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['backend'] = 'TkAgg'
# matplotlib.rcParams['interactive'] = True
import unit_conversion
import matplotlib.dates as mdates
import numpy as np
import pytz
import matplotlib.gridspec as gridspec
import matplotlib.image as image
import matplotlib.ticker as ticker
from tools.storm_options import StormOptions
import time


class MultiSeries():
    
    def __init__(self):
        self.figure = None
        
    def format_date(self,x,arb=None):
        '''Format dates so that they are padded away from the x-axis'''
        date_str = mdates.num2date(x).strftime('%b-%d-%Y \n %H:%M')
        return ''.join([' ','\n',date_str])
    
    def process_graphs(self, mo):
        
        
        if mo.graph['Atmospheric Pressure'].get() == True:
            self.create_header()
            self.multi_air_pressure(mo, 'Delaware')
       
        if mo.graph['Storm Tide Water Level'].get() == True:
            self.create_header()
            self.multi_water_level(mo, 'Delaware', mode = 'Surge')
            
        if mo.graph['Unfiltered Water Level'].get() == True:
            self.create_header()
            self.multi_water_level(mo, 'Delaware')
            
        if mo.graph['Wave Water Level'].get() == True:
            self.create_header()
            self.multi_water_level(mo, 'Delaware', mode='Wave')
            
    
    def create_header(self):
            
            font = {'family' : 'Bitstream Vera Sans',
                    'size'   : 14}
        
            matplotlib.rc('font', **font)
            plt.rcParams['figure.figsize'] = (16,10)
            plt.rcParams['figure.facecolor'] = 'white'
              
#             if self.figure is None:
            self.figure = plt.figure(figsize=(16,10))
            
           
            
            
            #Read images
            logo = image.imread('usgs.png', None)
        
            #Create grids for section formatting
            
            self.grid_spec = gridspec.GridSpec(2, 2,
                                   width_ratios=[1,3],
                                   height_ratios=[1,4]
                                   )
            #---------------------------------------Logo Section
            ax2 = self.figure.add_subplot(self.grid_spec[0,0])
            ax2.set_axis_off()
           
            ax2.axes.get_yaxis().set_visible(False)
            ax2.axes.get_xaxis().set_visible(False)
            pos1 = ax2.get_position() # get the original position 
            pos2 = [pos1.x0, pos1.y0 + .07,  pos1.width, pos1.height] 
            ax2.set_position(pos2) # set a new position
            ax2.imshow(logo)
            
    def multi_air_pressure(self, mo, title):
        
        ax = self.figure.add_subplot(self.grid_spec[1,0:])
        pos1 = ax.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
        ax.set_position(pos2) # set a new position
        
        #create the second graph title
        first_title = "%s Air Pressure Time Series Comparison" % title
       
        titleText = ax.text(0.5, 1.065,first_title,  \
            va='center', ha='center', transform=ax.transAxes)
      
        ax.set_ylabel('Air Pressure in Inches of Mercury')
        ax.set_xlabel('Timezone GMT')
        
        #plot major grid lines
        ax.grid(b=True, which='major', color='grey', linestyle="-")

        #x axis formatter for dates (function format_date() below)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
        
        legend_list, label_list = [], []
        
        for x in mo.storm_objects: 
            air_pressure = x.raw_air_pressure * unit_conversion.DBAR_TO_INCHES_OF_MERCURY
            time = x.air_time
             
            first_date = unit_conversion.convert_ms_to_date(time[0], pytz.UTC)
            last_date = unit_conversion.convert_ms_to_date(time[-1], pytz.UTC)
            new_dates = unit_conversion.adjust_from_gmt([first_date,last_date], \
                                         mo.timezone,mo.daylight_savings)
        
            first_date = mdates.date2num(new_dates[0])
            last_date = mdates.date2num(new_dates[1])
        
            self.time_nums = np.linspace(first_date, last_date, len(time))
             
            p1, = ax.plot(self.time_nums, air_pressure, alpha=.5)
            legend_list.append(p1)
            label_list.append('STN Site ID: %s, STN Instrument ID: %s, Lat: %s, Lon: %s' \
                               %(x.air_stn_station_number, x.air_stn_instrument_id, 
                                 x.air_latitude, x.air_longitude))
            
            
                        
        legend = ax.legend(legend_list,label_list
        , \
                  bbox_to_anchor=(.95, 1.355), loc=1, borderaxespad=0.0, prop={'size':10.3},frameon=False,numpoints=1, \
                  title="EXPLANATION")
        legend.get_title().set_position((-340, 0))
                    
        plt.savefig(''.join([mo.output_fname,'_multi_baro.jpg']))
#         plt.close(self.figure)
    
#     def multi_sea_pressure(self,path,title):
#         
#         self.create_header()
#         
#         ax = self.figure.add_subplot(self.grid_spec[1,0:])
#         pos1 = ax.get_position() # get the original position 
#         pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
#         ax.set_position(pos2) # set a new position
#         
#         #create the second graph title
#         first_title = "%s Sea Pressure Time Series Comparison" % title
#        
#         titleText = ax.text(0.5, 1.065,first_title,  \
#             va='center', ha='center', transform=ax.transAxes)
#       
#         ax.set_ylabel('Sea Pressure in Inches of Mercury')
#         ax.set_xlabel('Timezone GMT')
#         
#         #plot major grid lines
#         ax.grid(b=True, which='major', color='grey', linestyle="-")
# 
#         #x axis formatter for dates (function format_date() below)
#         ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
#         
#         legend_list, label_list = [], []
#         
#         file_types = ['.nc']
#         for root, sub_folders, files in os.walk(path):
#             for file_in_root in files:
#                 
#                 index = file_in_root.rfind('.')
#                 if file_in_root[index:] in file_types:    
#                     file = ''.join([root,'\\',file_in_root])
#                     try:         
#                         pressure = nc.get_pressure(file) * unit_conversion.DBAR_TO_INCHES_OF_MERCURY
#                         time = nc.get_time(file)
#                         
#                         first_date = unit_conversion.convert_ms_to_date(time[0], pytz.UTC)
#                         last_date = unit_conversion.convert_ms_to_date(time[-1], pytz.UTC)
# 
#                         first_date = mdates.date2num(first_date)
#                         last_date = mdates.date2num(last_date)
#            
#                         self.time_nums = np.linspace(first_date, last_date, len(time))
#                         
#                         lat = nc.get_variable_data(file, 'latitude')
#                         lon = nc.get_variable_data(file, 'longitude')
# 
#                         stn_id = nc.get_global_attribute(file, 'stn_instrument_id')
#                         stn_station = nc.get_global_attribute(file, 'stn_station_number')
# 
#                         p1, = ax.plot(self.time_nums, pressure, alpha=.5)
#                         legend_list.append(p1)
#                         label_list.append('STN Site ID: %s, STN Instrument ID: %s, Lat: %s, Lon: %s' \
#                                           %(stn_id, stn_station, lat, lon))
#                         
#                     except:
#                         pass
#                     
#         legend = ax.legend(legend_list,label_list
#         , \
#                   bbox_to_anchor=(.95, 1.355), loc=1, borderaxespad=0.0, prop={'size':10.3},frameon=False,numpoints=1, \
#                   title="EXPLANATION")
#         legend.get_title().set_position((-340, 0))
                    
#         plt.savefig('a')
        
    def multi_water_level(self,mo,title, mode='Raw'):
        
        self.create_header()
        
        ax = self.figure.add_subplot(self.grid_spec[1,0:])
        pos1 = ax.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
        ax.set_position(pos2) # set a new position
        
        #create the second graph title
        first_title = "%s %s Water Level Time Series Comparison" % (title, mode)
       
        titleText = ax.text(0.5, 1.065,first_title,  \
            va='center', ha='center', transform=ax.transAxes)
      
        ax.set_ylabel('Water Level in Feet')
        ax.set_xlabel('Timezone GMT')
        
        #plot major grid lines
        ax.grid(b=True, which='major', color='grey', linestyle="-")

        #x axis formatter for dates (function format_date() below)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
        
        legend_list, label_list = [], []
        air, sea, sea_file, air_file = False, False, '', ''
        file_types = ['.nc']
        for x in mo.storm_objects:
                        
            first_date = unit_conversion.convert_ms_to_date(x.sea_time[0], pytz.UTC)
            last_date = unit_conversion.convert_ms_to_date(x.sea_time[-1], pytz.UTC)
            new_dates = unit_conversion.adjust_from_gmt([first_date,last_date], \
                                         mo.timezone,mo.daylight_savings)
        
            first_date = mdates.date2num(new_dates[0])
            last_date = mdates.date2num(new_dates[1])
        
            self.time_nums = np.linspace(first_date, last_date, len(x.sea_time))
               
            if mode=='Surge':
                p1, = ax.plot(self.time_nums, x.surge_water_level * unit_conversion.METER_TO_FEET, alpha=.5)
                legend_list.append(p1)
                label_list.append('STN Site ID: %s, STN Instrument ID: %s, Lat: %s, Lon: %s' \
                               %(x.stn_station_number, x.stn_instrument_id, 
                                 x.latitude, x.longitude))
            if mode=='Wave':
                p1, = ax.plot(self.time_nums, x.wave_water_level * unit_conversion.METER_TO_FEET, alpha=.5)
                legend_list.append(p1)
                label_list.append('STN Site ID: %s, STN Instrument ID: %s, Lat: %s, Lon: %s' \
                               %(x.stn_station_number, x.stn_instrument_id, 
                                 x.latitude, x.longitude))
            if mode=='Raw':
                p1, = ax.plot(self.time_nums, x.raw_water_level * unit_conversion.METER_TO_FEET, alpha=.5)
                legend_list.append(p1)
                label_list.append('STN Site ID: %s, STN Instrument ID: %s, Lat: %s, Lon: %s' \
                               %(x.stn_station_number, x.stn_instrument_id, 
                                 x.latitude, x.longitude))
                
            print(x.latitude,',',x.longitude)
                        
                   
        legend = ax.legend(legend_list,label_list
        , \
                  bbox_to_anchor=(.95, 1.355), loc=1, borderaxespad=0.0, prop={'size':10.3},frameon=False,numpoints=1, \
                  title="EXPLANATION")
        legend.get_title().set_position((-340, 0))
                    
        plt.savefig(''.join([mo.output_fname,'_multi_',mode.lower(),'.jpg']))
        plt.close(self.figure)
        
            
if __name__ == '__main__':
    ms = MultiSeries()
#     ms.multi_air_pressure('C:\\Users\\chogg\\Desktop\\NY NC Data','New York')
#     ms.multi_sea_pressure('C:\\Users\\chogg\\Desktop\\NY NC Data','New York')
    ms.multi_water_level('C:\\Users\\chogg\\Desktop\\NY NC Data','New York')
    ms.multi_water_level('C:\\Users\\chogg\\Desktop\\NY NC Data','New York', mode='Surge')
    ms.multi_water_level('C:\\Users\\chogg\\Desktop\\NY NC Data','New York', mode='Wave')
                    
                   
                   
                
                   
