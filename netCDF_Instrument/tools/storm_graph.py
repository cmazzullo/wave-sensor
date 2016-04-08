'''
Created on Feb 4, 2016

@author: chogg
'''
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
# import mpl_toolkits.axes_grid1 as host_plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.image as image
# import mpl_toolkits.axisartist as AA
import matplotlib.ticker as ticker
from tools.storm_options import StormOptions
# from tests.test_script2 import water_fname
import pytz
# import netCDF4_utils
import pandas as pd
import unit_conversion
from matplotlib.ticker import FormatStrFormatter
import tools.storm_graph_utilities as graph_util


class StormGraph(object):
    
    def __init__(self):
        self.figure = None
        self.grid_spec = None
        self.time_nums = None
        self.wind_time_nums = None
        self.df = None
        
    def format_date(self,x,arb=None):
        '''Format dates so that they are padded away from the x-axis'''
        date_str = mdates.num2date(x).strftime('%b-%d-%Y \n %H:%M')
        return ''.join([' ','\n',date_str])
    
    def process_graphs(self,so):
        
        if so.graph['Storm Tide with Unfiltered Water Level and Wind Data'].get() == True:
            so.get_meta_data()
            so.get_air_meta_data()
            so.get_wind_meta_data()
            so.get_raw_water_level()
            so.get_surge_water_level()
            so.slice_wind_data()
            so.test_water_elevation_below_sensor_orifice_elvation()
            self.create_header(so, wind=True)
            self.Storm_Tide_Unfiltered_and_Wind(so)
            
            #To avoid over allocating memory for the graphs
#             plt.close()
              
        if so.graph['Storm Tide with Unfiltered Water Level'].get() == True:
            so.get_meta_data()
            so.get_air_meta_data()
            so.get_raw_water_level()
            so.get_surge_water_level()
            so.test_water_elevation_below_sensor_orifice_elvation()
            self.create_header(so)
            self.Storm_Tide_and_Unfiltered_Water_Level(so)
        
            #To avoid over allocating memory for the graphs
#             plt.close()
            
        if so.graph['Storm Tide Water Level'].get() == True:
            so.get_meta_data()
            so.get_air_meta_data()
            so.get_raw_water_level()
            so.get_surge_water_level()
            so.test_water_elevation_below_sensor_orifice_elvation()
            self.create_header(so)
            self.Storm_Tide_Water_Level(so)
        
            #To avoid over allocating memory for the graphs
#             plt.close()
            
        if so.graph['Atmospheric Pressure'].get() == True:
            so.get_air_meta_data()
            so.get_air_time()
            so.get_raw_air_pressure()
            self.create_baro_header(so)
            self.Atmospheric_Graph(so)
            
            #To avoid over allocating memory for the graphs
#             plt.close()
        
        
        
    def create_header(self,so, wind=False):
#         if self.figure is not None:
#             
#             self.figure.cla()
        if wind == True:
            font = {'family' : 'Bitstream Vera Sans',
                    'size'   : 10}
        
            matplotlib.rc('font', **font)
            plt.rcParams['figure.facecolor'] = 'white'
              
            self.figure = plt.figure(figsize=(16,10))
        else: 
            font = {'family' : 'Bitstream Vera Sans',
                    'size'   : 14}
        
            matplotlib.rc('font', **font)
            plt.rcParams['figure.figsize'] = (16,10)
            plt.rcParams['figure.facecolor'] = 'white'
              
            self.figure = plt.figure(figsize=(16,10))
        
        first_date = unit_conversion.convert_ms_to_date(so.sea_time[0], pytz.UTC)
        last_date = unit_conversion.convert_ms_to_date(so.sea_time[-1], pytz.UTC)
        new_dates = unit_conversion.adjust_from_gmt([first_date,last_date], \
                                         so.timezone,so.daylight_savings)
        
        first_date = mdates.date2num(new_dates[0])
        last_date = mdates.date2num(new_dates[1])
       
        time = so.sea_time
        self.time_nums = np.linspace(first_date, last_date, len(time))
        
        
        #create dataframe
        graph_data = {'Pressure': pd.Series(so.interpolated_air_pressure * unit_conversion.DBAR_TO_INCHES_OF_MERCURY,index=time),
    #                 'PressureQC': pd.Series(air_qc, index=time),
                'SurgeDepth': pd.Series(so.surge_water_level * unit_conversion.METER_TO_FEET, index=time),
                'RawDepth': pd.Series(so.raw_water_level * unit_conversion.METER_TO_FEET, index=time)
                }
    #                 'DepthQC': pd.Series(depth_qc, index=time)}
        self.df = pd.DataFrame(graph_data)
       
        #Read images
        logo = image.imread('usgs.png', None)
    
        #Create grids for section formatting
        if wind == False:
            self.grid_spec = gridspec.GridSpec(2, 2,
                               width_ratios=[1,2],
                               height_ratios=[1,4]
                               )
        else:
            
            first_date = unit_conversion.convert_ms_to_date(so.wind_time[0], pytz.UTC)
            print(so.wind_time[-1])
            last_date = unit_conversion.convert_ms_to_date(so.wind_time[-1], pytz.UTC)
            new_dates = unit_conversion.adjust_from_gmt([first_date,last_date], \
                                         so.timezone,so.daylight_savings)
        
            first_date = mdates.date2num(new_dates[0])
            last_date = mdates.date2num(new_dates[1])
       
            self.wind_time_nums = np.linspace(first_date, last_date, len(so.wind_time))
            self.grid_spec = gridspec.GridSpec(3, 2,
                               width_ratios=[1,2],
                               height_ratios=[1,2,2]
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
        
    def create_baro_header(self, so):
#         if self.figure is not None:
#             self.figure.cla()
            
        font = {'family' : 'Bitstream Vera Sans',
                'size'   : 14}
    
        matplotlib.rc('font', **font)
        plt.rcParams['figure.figsize'] = (16,10)
        plt.rcParams['figure.facecolor'] = 'white'
          
        self.figure = plt.figure(figsize=(16,10))
        
        first_date = unit_conversion.convert_ms_to_date(so.air_time[0], pytz.UTC)
        last_date = unit_conversion.convert_ms_to_date(so.air_time[-1], pytz.UTC)
        new_dates = unit_conversion.adjust_from_gmt([first_date,last_date], \
                                         so.timezone,so.daylight_savings)
        
        first_date = mdates.date2num(new_dates[0])
        last_date = mdates.date2num(new_dates[1])
       
        self.time_nums = np.linspace(first_date, last_date, len(so.air_time))
        
        #create dataframe
       
        #Read images
        logo = image.imread('usgs.png', None)
    
        #Create grids for section formatting
        self.grid_spec = gridspec.GridSpec(2, 2,
                           width_ratios=[1,2],
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
    
    def Storm_Tide_and_Unfiltered_Water_Level(self,so):
        
            ax = self.figure.add_subplot(self.grid_spec[1,0:])
            pos1 = ax.get_position() # get the original position 
            pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
            ax.set_position(pos2) # set a new position
            
            #create the second graph title
            first_title = "Storm Tide Water Elevation, Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                % (so.latitude,so.longitude,so.stn_station_number)
            second_title = "Barometric Pressure, Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                % (so.air_latitude,so.air_longitude,so.air_stn_station_number)
    #         if extra != None and extra != '':
            titleText = ax.text(0.5, 1.065,first_title,  \
                va='center', ha='center', transform=ax.transAxes)
            titleText2 = ax.text(0.5, 1.03,second_title,  \
                va='center', ha='center', transform=ax.transAxes)
            
            ax.set_xlabel('Timezone: %s' % so.timezone)
    #         else:
    #             ax.set_title("Storm Tide Water Elevation and Barometric Pressure (Time Zone %s)" % tz,y=1.015)
            
            par1 = ax.twinx()
            pos1 = par1.get_position() # get the original position 
            pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
            par1.set_position(pos2) # set a new position
    
            ax.set_ylabel('Water Elevation in Feet above Datum (%s)' % so.datum)
            par1.set_ylabel('Barometric Pressure in Inches of Mercury')
    
            #plot major grid lines
            
            ax.grid(b=True, which='major', color='grey', linestyle="-")
    
            #x axis formatter for dates (function format_date() below)
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
    
    
            sensor_min = np.min(so.sensor_orifice_elevation)
            
            
            #get minimum and maximum depth
            
            #plan on rebuilding the flow of execution, ignore spaghetti for now
            depth_min_start = np.min(self.df.RawDepth)
            
            depth_idx = np.nanargmax(so.raw_water_level)
            tide_idx = np.nanargmax(so.surge_water_level)
           
            depth_max = so.raw_water_level[depth_idx] * unit_conversion.METER_TO_FEET
            depth_time = unit_conversion.convert_ms_to_date(so.sea_time[depth_idx], pytz.UTC)
            tide_max = so.surge_water_level[tide_idx] * unit_conversion.METER_TO_FEET
            tide_time = unit_conversion.convert_ms_to_date(so.sea_time[tide_idx], pytz.UTC)
            format_times = unit_conversion.adjust_from_gmt([depth_time,tide_time], \
                                              so.timezone,so.daylight_savings)
            tide_time = format_times[1].strftime('%m/%d/%y %H:%M:%S')
            depth_time = format_times[0].strftime('%m/%d/%y %H:%M:%S.%f')
            depth_time = depth_time[0:(len(depth_time) - 4)]
                    
            depth_num = mdates.date2num(format_times[0])
            tide_num = mdates.date2num(format_times[1])
            
            depth_min = np.floor(depth_min_start * 100.0)/100.0
            sensor_min = sensor_min * unit_conversion.METER_TO_FEET
            if depth_min > (sensor_min - .02):
                depth_min = sensor_min - .02
                
            lim_max = np.ceil(depth_max * 100.0)/100.0
    
    
            if so.wlYLims is None:
                if depth_min < 0:
                    ax.set_ylim([depth_min * 1.10,lim_max * 1.20])
                else:
                    ax.set_ylim([depth_min * .9,lim_max * 1.20])
            else:
                so.wlYLims[0] = float("{0:.2f}".format(so.wlYLims[0]))
                so.wlYLims[1] = float("{0:.2f}".format(so.wlYLims[1]))
                ax.set_ylim([so.wlYLims[0],so.wlYLims[1]])
    #
            #changes scale so the air pressure is more readable
            minY = np.floor(np.min(self.df.Pressure))
            maxY = np.ceil(np.max(self.df.Pressure))
            print('minm_max:', np.min(self.df.Pressure),minY,np.max(self.df.Pressure),maxY)
        
            
            if so.baroYLims is None:
                par1.set_ylim([minY,maxY])
                par1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
            else:
                so.baroYLims[0] = float("{0:.1f}".format(so.baroYLims[0]))
                so.baroYLims[1] = float("{0:.1f}".format(so.baroYLims[1]))
                if so.baroYLims[1] - so.baroYLims[0] < .5:
                    par1.set_yticks(np.arange(so.baroYLims[0],so.baroYLims[1],.1))
                    
                par1.set_ylim([so.baroYLims[0],so.baroYLims[1]])
    
            #plot the pressure, depth, and min depth
            
            p4, = ax.plot(self.time_nums,self.df.RawDepth,color='#969696', alpha=.75)
            p1, = par1.plot(self.time_nums,self.df.Pressure, color="red")
            p2, = ax.plot(self.time_nums,self.df.SurgeDepth, color="#045a8d")
            p3, = ax.plot(self.time_nums,np.repeat(sensor_min, len(self.df.SurgeDepth)), linestyle="--", color="#fd8d3c")
            p5,  = ax.plot(depth_num,depth_max, 'o', markersize=10, color='#969696', alpha=1)
            p6,  = ax.plot(tide_num,tide_max, '^', markersize=10, color='#045a8d', alpha=1)
            
            max_storm_tide = "Maximum Unfiltered Water Elevation, feet above datum = %.2f at %s\nMaximum Storm Tide Water Elevation, feet above datum = %.2f at %s" % (depth_max, depth_time,tide_max, tide_time)
            
            stringText = par1.text(0.5, 0.948,max_storm_tide,  \
                    bbox={'facecolor':'white', 'alpha':1, 'pad':10}, \
                    va='center', ha='center', transform=par1.transAxes)
            stringText.set_size(11)
    
    
            #Legend options not needed but for future reference
            legend = ax.legend([p4,p2,p3,p1,p5,p6],['Unfiltered Water Elevation','Storm Tide (Lowpass Filtered) Water Elevation',
            'Minimum Recordable Water Elevation','Barometric Pressure',
            'Maximum Unfiltered Water Elevation',
            'Maximum Storm Tide Water Elevation'
            ], \
                      bbox_to_anchor=(.95, 1.355), loc=1, borderaxespad=0.0, prop={'size':10.3},frameon=False,numpoints=1, \
                      title="EXPLANATION")
            legend.get_title().set_position((-120, 0))
            
            ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
             
            file_name = ''.join([so.output_fname,'_stormtide_unfiltered','.jpg'])
            plt.savefig(file_name)
#             plt.show()

    def Storm_Tide_Unfiltered_and_Wind(self,so):
        
            ax = self.figure.add_subplot(self.grid_spec[1,0:])
            ax2 = self.figure.add_subplot(self.grid_spec[2,0:],sharex=ax)
            pos1 = ax.get_position() # get the original position 
            pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
            ax.set_position(pos2) # set a new position
            
            first_title = "Storm Tide Water Elevation, Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                % (so.latitude,so.longitude,so.stn_station_number)
            second_title = "Barometric Pressure, Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                % (so.air_latitude,so.air_longitude,so.air_stn_station_number)
                
            titleText = ax.text(0.5, 1.08,first_title,  \
                va='center', ha='center', transform=ax.transAxes)
            titleText2 = ax.text(0.5, 1.03,second_title,  \
                va='center', ha='center', transform=ax.transAxes)
    #         if extra != None and extra != '':
#             ax.set_title("%s\n%s" \
#                          % (first_title,second_title))#,y=1.010)
            
            third_title = "Wind Speed and Direction, Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                % (so.wind_latitude,so.wind_longitude,so.wind_stn_station_number)
                
            titleText3 = ax2.text(0.5, -.1,third_title,  \
                va='center', ha='center', transform=ax.transAxes)
            
            ax2.set_xlabel('Timezone: %s' % so.timezone)
            
            par1 = ax.twinx()
            pos1 = par1.get_position() # get the original position 
            pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
            par1.set_position(pos2) # set a new position
    
            ax.set_ylabel('Water Elevation in Feet above Datum (%s)' % so.datum)
            par1.set_ylabel('Barometric Pressure in Inches of Mercury')
    
            #plot major grid lines
            
            ax.grid(b=True, which='major', color='grey', linestyle="-")
    
            #x axis formatter for dates (function format_date() below)
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
            
    
            sensor_min = np.min(so.sensor_orifice_elevation)
            
            
            #get minimum and maximum depth
            
            #plan on rebuilding the flow of execution, ignore spaghetti for now
            depth_min_start = np.min(self.df.RawDepth)
            
            depth_idx = np.nanargmax(so.raw_water_level)
            tide_idx = np.nanargmax(so.surge_water_level)
           
            depth_max = so.raw_water_level[depth_idx] * unit_conversion.METER_TO_FEET
            depth_time = unit_conversion.convert_ms_to_date(so.sea_time[depth_idx], pytz.UTC)
            tide_max = so.surge_water_level[tide_idx] * unit_conversion.METER_TO_FEET
            tide_time = unit_conversion.convert_ms_to_date(so.sea_time[tide_idx], pytz.UTC)
            format_times = unit_conversion.adjust_from_gmt([depth_time,tide_time], \
                                              so.timezone,so.daylight_savings)
            tide_time = format_times[1].strftime('%m/%d/%y %H:%M:%S')
            depth_time = format_times[0].strftime('%m/%d/%y %H:%M:%S.%f')
            depth_time = depth_time[0:(len(depth_time) - 4)]
                    
            depth_num = mdates.date2num(format_times[0])
            tide_num = mdates.date2num(format_times[1])
            
            depth_min = np.floor(depth_min_start * 100.0)/100.0
            sensor_min = sensor_min * unit_conversion.METER_TO_FEET
            if depth_min > (sensor_min - .02):
                depth_min = sensor_min - .02
                
            lim_max = np.ceil(depth_max * 100.0)/100.0
    
    
            if so.wlYLims is None:
                if depth_min < 0:
                    ax.set_ylim([depth_min * 1.10,lim_max * 1.30])
                else:
                    ax.set_ylim([depth_min * .9,lim_max * 1.30])
            else:
                so.wlYLims[0] = float("{0:.2f}".format(so.wlYLims[0]))
                so.wlYLims[1] = float("{0:.2f}".format(so.wlYLims[1]))
                ax.set_ylim([so.wlYLims[0],so.wlYLims[1]])
    #
            #changes scale so the air pressure is more readable
            minY = np.floor(np.min(self.df.Pressure))
            maxY = np.ceil(np.max(self.df.Pressure))
            
            if so.baroYLims is None:
                par1.set_ylim([minY,maxY])
                par1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
            else:
                so.baroYLims[0] = float("{0:.1f}".format(so.baroYLims[0]))
                so.baroYLims[1] = float("{0:.1f}".format(so.baroYLims[1]))
                if so.baroYLims[1] - so.baroYLims[0] < .5:
                    par1.set_yticks(np.arange(so.baroYLims[0],so.baroYLims[1],.1))
                    
                par1.set_ylim([so.baroYLims[0],so.baroYLims[1]])
                
            scale = (self.time_nums[1] - self.time_nums[0]) * (len(self.time_nums) * .1)
            ax.set_xlim([self.time_nums[0] - scale, self.time_nums[-1] + scale])
    
            #plot the pressure, depth, and min depth
            
            p4, = ax.plot(self.time_nums,self.df.RawDepth,color='#969696', alpha=.75)
            p1, = par1.plot(self.time_nums,self.df.Pressure, color="red")
            p2, = ax.plot(self.time_nums,self.df.SurgeDepth, color="#045a8d")
            p3, = ax.plot(self.time_nums,np.repeat(sensor_min, len(self.df.SurgeDepth)), linestyle="--", color="#fd8d3c")
            p5,  = ax.plot(depth_num,depth_max, 'o', markersize=10, color='#969696', alpha=1)
            p6,  = ax.plot(tide_num,tide_max, '^', markersize=10, color='#045a8d', alpha=1)
            
            max_storm_tide = "Maximum Unfiltered Water Elevation, feet above datum = %.2f at %s\nMaximum Storm Tide Water Elevation, feet above datum = %.2f at %s" % (depth_max, depth_time,tide_max, tide_time)
            
            stringText = par1.text(0.5, 0.928,max_storm_tide,  \
                    bbox={'facecolor':'white', 'alpha':1, 'pad':5}, \
                    va='center', ha='center', transform=par1.transAxes)
            stringText.set_size(9)
            
            plt.setp( ax.get_xticklabels(), visible=False)
            plt.setp( ax2.get_yaxis(), visible=False)
            
            ax2.set_ylim([-.75,.75])
            
            
            graph_util.plot_wind_data2(ax2, so, self.wind_time_nums)
    
            #Legend options not needed but for future reference
            legend = ax.legend([p4,p2,p3,p1,p5,p6],[
            'Unfiltered Water Elevation','Storm Tide (Lowpass Filtered) Water Elevation',
            'Minimum Recordable Water Elevation','Barometric Pressure',
            'Maximum Unfiltered Water Elevation',
            'Maximum Storm Tide Water Elevation'
            ], \
                      bbox_to_anchor=(.95, 1.59), loc=1, borderaxespad=0.0, prop={'size':10.3},frameon=False,numpoints=1, \
                      title="EXPLANATION")
            legend.get_title().set_position((-138, 0))
            
            ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
            
             
            file_name = ''.join([so.output_fname,'_stormtide_unfiltered_wind','.jpg'])
            
            plt.savefig(file_name)
          
            
    def Storm_Tide_Water_Level(self,so):
        ax = self.figure.add_subplot(self.grid_spec[1,0:])
        pos1 = ax.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
        ax.set_position(pos2) # set a new position
        
        first_title = "Storm Tide Water Elevation, Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                % (so.latitude,so.longitude,so.stn_station_number)
        second_title = "Barometric Pressure, Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                % (so.air_latitude,so.air_longitude,so.air_stn_station_number)
    #         if extra != None and extra != '':
        titleText = ax.text(0.5, 1.065,first_title,  \
                va='center', ha='center', transform=ax.transAxes)
        titleText2 = ax.text(0.5, 1.03,second_title,  \
                va='center', ha='center', transform=ax.transAxes)
        
        par1 = ax.twinx()
        pos1 = par1.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
        par1.set_position(pos2) # set a new position
    
        ax.set_ylabel('Water Elevation in Feet above Datum (%s)' % so.datum)
        par1.set_ylabel('Barometric Pressure in Inches of Mercury')
    
        #plot major grid lines
        
        ax.grid(b=True, which='major', color='grey', linestyle="-")
    
        #x axis formatter for dates (function format_date() below)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
        ax.set_xlabel('Timezone: %s' % so.timezone)
    
        sensor_min = np.min(so.sensor_orifice_elevation)
        
        
        #get minimum and maximum depth
        
        #plan on rebuilding the flow of execution, ignore spaghetti for now
        depth_min_start = np.min(self.df.SurgeDepth)
        
        depth_idx = np.nanargmax(so.raw_water_level)
        tide_idx = np.nanargmax(so.surge_water_level)
       
       
        depth_time = unit_conversion.convert_ms_to_date(so.sea_time[depth_idx], pytz.UTC)
        tide_max = so.surge_water_level[tide_idx] * unit_conversion.METER_TO_FEET
        tide_time = unit_conversion.convert_ms_to_date(so.sea_time[tide_idx], pytz.UTC)
        format_times = unit_conversion.adjust_from_gmt([depth_time,tide_time], \
                                          so.timezone,so.daylight_savings)
        tide_time = format_times[1].strftime('%m/%d/%y %H:%M:%S')
        depth_time = format_times[0].strftime('%m/%d/%y %H:%M:%S.%f')
        depth_time = depth_time[0:(len(depth_time) - 4)]
                
       
        tide_num = mdates.date2num(format_times[1])
        
        depth_min = np.floor(depth_min_start * 100.0)/100.0
        sensor_min = sensor_min * unit_conversion.METER_TO_FEET
        if depth_min > (sensor_min - .02):
            depth_min = sensor_min - .02
            
        lim_max = np.ceil(tide_max * 100.0)/100.0
    
    
        if so.wlYLims is None:
                if depth_min < 0:
                    ax.set_ylim([depth_min * 1.10,lim_max * 1.20])
                else:
                    ax.set_ylim([depth_min * .9,lim_max * 1.20])
        else:
            so.wlYLims[0] = float("{0:.2f}".format(so.wlYLims[0]))
            so.wlYLims[1] = float("{0:.2f}".format(so.wlYLims[1]))
            ax.set_ylim([so.wlYLims[0],so.wlYLims[1]])
#
        #changes scale so the air pressure is more readable
        minY = np.floor(np.min(self.df.Pressure))
        maxY = np.ceil(np.max(self.df.Pressure))
        
      
        if so.baroYLims is None:
                par1.set_ylim([minY,maxY])
                par1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        else:
            so.baroYLims[0] = float("{0:.1f}".format(so.baroYLims[0]))
            so.baroYLims[1] = float("{0:.1f}".format(so.baroYLims[1]))
            if so.baroYLims[1] - so.baroYLims[0] < .5:
                par1.set_yticks(np.arange(so.baroYLims[0],so.baroYLims[1],.1))
                
            par1.set_ylim([so.baroYLims[0],so.baroYLims[1]])
    
        #plot the pressure, depth, and min depth
        
        p1, = par1.plot(self.time_nums,self.df.Pressure, color="red")
        p2, = ax.plot(self.time_nums,self.df.SurgeDepth, color="#045a8d")
        p3, = ax.plot(self.time_nums,np.repeat(sensor_min, len(self.df.SurgeDepth)), linestyle="--", color="#fd8d3c")
        p6,  = ax.plot(tide_num,tide_max, '^', markersize=10, color='#045a8d', alpha=1)
        
        max_storm_tide = "Maximum Storm Tide Water Elevation, feet above datum = %.2f at %s" % (tide_max, tide_time)
        
        stringText = par1.text(0.5, 0.948,max_storm_tide,  \
                bbox={'facecolor':'white', 'alpha':1, 'pad':10}, \
                va='center', ha='center', transform=par1.transAxes)
        stringText.set_size(11)
    
    
        #Legend options not needed but for future reference
        legend = ax.legend([p2,p3,p1,p6],[
        'Storm Tide (Lowpass Filtered) Water Elevation',
        'Minimum Recordable Water Elevation',
        'Barometric Pressure',
        'Maximum Storm Tide Water Elevation'
        ], \
                  bbox_to_anchor=(.95, 1.355), loc=1, borderaxespad=0.0, prop={'size':10.3},frameon=False,numpoints=1, \
                  title="EXPLANATION")
        legend.get_title().set_position((-120, 0))
        
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
         
        file_name = ''.join([so.output_fname,'_stormtide','.jpg'])
        plt.savefig(file_name)
#         plt.show()  
    
    def Atmospheric_Graph(self,so):
        ax = self.figure.add_subplot(self.grid_spec[1,0:])
        pos1 = ax.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
        ax.set_position(pos2) # set a new position
        
       
        first_title = "Barometric Pressure, Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                % (so.air_latitude,so.air_longitude,so.air_stn_station_number)
    #         if extra != None and extra != '':
        titleText = ax.text(0.5, 1.03,first_title,  \
                va='center', ha='center', transform=ax.transAxes)
        
        ax.set_xlabel('Timezone: %s' % so.timezone)
    #         else:
    #             ax.set_title("Storm Tide Water Elevation and Barometric Pressure (Time Zone %s)" % tz,y=1.015)
        
        ax.set_ylabel('Barometric Pressure in Inches of Mercury')
    
        #plot major grid lines
        
        ax.grid(b=True, which='major', color='grey', linestyle="-")
    
        #x axis formatter for dates (function format_date() below)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
    
    
        #get minimum and maximum depth
        
        #plan on rebuilding the flow of execution, ignore spaghetti for now
        
    #         else:
    #             ax.set_ylim([wlYLims[0],wlYLims[1]])
    #
        #changes scale so the air pressure is more readable
        air_pressure = so.raw_air_pressure * unit_conversion.DBAR_TO_INCHES_OF_MERCURY
#         minY = np.floor(np.min(air_pressure))
#         maxY = np.ceil(np.max(air_pressure))
#         
        if so.baroYLims is not None:
            so.baroYLims[0] = float("{0:.1f}".format(so.baroYLims[0]))
            so.baroYLims[1] = float("{0:.1f}".format(so.baroYLims[1]))
            if so.baroYLims[1] - so.baroYLims[0] < .5:
                    ax.set_yticks(np.arange(so.baroYLims[0],so.baroYLims[1],.1))
            ax.set_ylim([so.baroYLims[0],so.baroYLims[1]])
        else:
            ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    #         else:
    #             par1.set_ylim([baroYLims[0],baroYLims[1]])
    
        #plot the pressure, depth, and min depth
        
        p1, = ax.plot(self.time_nums,air_pressure, color="red")
        
    
        #Legend options not needed but for future reference
        legend = ax.legend([p1],[
        'Barometric Pressure',
        ], \
                  bbox_to_anchor=(.89, 1.355), loc=1, borderaxespad=0.0, prop={'size':10.3},frameon=False,numpoints=1, \
                  title="EXPLANATION")
        legend.get_title().set_position((-28, 0))
         
        file_name = ''.join([so.output_fname,'_barometric_pressure','.jpg'])
        plt.savefig(file_name)
        
class Bool(object):
    
    def __init__(self, val):
        self.val = val
         
    def get(self):
        return self.val
        
if __name__ == '__main__':
  
    so = StormOptions()
    so.air_fname = 'Assateague Baro.csv.nc'
    so.sea_fname = 'MDWOR04586.csv.nc'
    so.wind_fname = 'joachim_wind-2.nc'
    so.format_output_fname('test')
    so.timezone = 'GMT'
    so.daylight_savings = False
    so.graph['Storm Tide with Unfiltered Water Level and Wind Data'] = Bool(True)
    so.graph['Storm Tide with Unfiltered Water Level'] = Bool(True)
    so.graph['Storm Tide Water Level'] = Bool(False)
    so.graph['Atmospheric Pressure'] = Bool(False)
                    
    sg = StormGraph()
    sg.process_graphs(so)
    