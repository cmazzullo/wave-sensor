#!/usr/bin/env python3
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
# import mpl_toolkits.axes_grid1 as host_plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.image as image
# import mpl_toolkits.axisartist as AA
import matplotlib.ticker as ticker
# from tests.test_script2 import water_fname
matplotlib.use('TkAgg', warn=False)
import pytz
# import netCDF4_utils
import pandas as pd
import NetCDF_Utils.nc as nc
import unit_conversion
from matplotlib.ticker import FormatStrFormatter

tz_info = None

def format_date(x,arb=None):
    '''Format dates so that they are padded away from the x-axis'''
    date_str = mdates.num2date(x).strftime('%b-%d-%Y \n %H:%M')
    return ''.join([' ','\n',date_str])

def make_depth_graph(box_car_points, in_file_name, tz, daylightSavings, grid='water_level', \
                     extra=None, baroYlims = None, wlYLims = None, file_name = None):
        '''To compare air_pressure and depth in a graph by consuming a netCDF file'''

        
        font = {'family' : 'Bitstream Vera Sans',
            'size'   : 14}

        matplotlib.rc('font', **font)
        plt.rcParams['figure.figsize'] = (16,10)
        plt.rcParams['figure.facecolor'] = 'white'
       
        figure = plt.figure(figsize=(16,10))
        #global options for matplotlib
       

        #reading
        time = nc.get_time(in_file_name)
        
        first_date = unit_conversion.convert_ms_to_date(time[0], pytz.UTC)
        last_date = unit_conversion.convert_ms_to_date(time[-1], pytz.UTC)
        new_dates = unit_conversion.adjust_from_gmt([first_date,last_date], \
                                          tz,daylightSavings)
         
        first_date = mdates.date2num(new_dates[0])
        last_date = mdates.date2num(new_dates[1])
        
        #air info
        
#         air_qc = nc.get_air_pressure_qc(in_file_name)
        
        #convert dbars to psi   *Possibly convert meters to feet later on*
#         air_pressure = np.multiply(air_pressure,1.45037738)
 
        #depth info
        depth = nc.get_depth(in_file_name) * unit_conversion.METER_TO_FEET
        
        raw_depth = nc.get_variable_data(in_file_name, 'raw_depth') * unit_conversion.METER_TO_FEET
        
        air_pressure = nc.get_air_pressure(in_file_name) * unit_conversion.DBAR_TO_INCHES_OF_MERCURY
        
        time = unit_conversion.generate_ms(time[0], len(depth), 4)
        print(len(raw_depth), len(depth))
#         return
#         
#         depth_qc = nc.get_depth_qc(in_file_name)

        #get datum
        datum = nc.get_geospatial_vertical_reference(in_file_name)
        
        #get variable data for latitude, longitude, and get stn global attribute
        lat = nc.get_variable_data(in_file_name,'latitude')
        lon = nc.get_variable_data(in_file_name,'longitude')
        stn_station = nc.get_global_attribute(in_file_name, 'stn_station_number')
       

        #create dataframe
        data = {'Pressure': pd.Series(air_pressure,index=time),
#                 'PressureQC': pd.Series(air_qc, index=time),
                'Depth': pd.Series(depth, index=time),
                'RawDepth': pd.Series(raw_depth, index=time)
                }
#                 'DepthQC': pd.Series(depth_qc, index=time)}
        df = pd.DataFrame(data)
        
        #check if the pressure and depth pints do not pass QC
        #if points did not pass QC assign NaN to its value (aside from stuck sensor and interpolation)
#         df.Pressure[(df['PressureQC'] != 11111111) & (df['PressureQC'] != 11110111)
#                 & (df['PressureQC'] != 11111110) & (df['PressureQC'] != 11110110)] = np.NaN;
# 
#         df.Depth[(df['DepthQC'] != 11111111) & (df['DepthQC'] != 11110111)
#                 & (df['DepthQC'] != 11111110) & (df['DepthQC'] != 11110110)] = np.NaN;

        #Boxcar average for aesthetic purposes if desired
#         if box_car_points > 0:
#             df.Pressure = pd.rolling_window(df.Pressure,center=True,window=box_car_points, win_type='boxcar')
#             df.Depth = pd.rolling_window(df.Depth,center=True,window=box_car_points, win_type='boxcar')

        #Read images
        logo = image.imread('usgs.png', None)

        #Create grids for section formatting
        gs = gridspec.GridSpec(2, 2,
                           width_ratios=[1,2],
                           height_ratios=[1,4]
                           )

        #---------------------------------------Logo Section
        ax2 = figure.add_subplot(gs[0,0])
        ax2.set_axis_off()
       
        ax2.axes.get_yaxis().set_visible(False)
        ax2.axes.get_xaxis().set_visible(False)
        pos1 = ax2.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0 + .07,  pos1.width, pos1.height] 
        ax2.set_position(pos2) # set a new position
        ax2.imshow(logo)


        #-----------------------------------------Data Section

        #create mirror subplot of first so that there can be two overlapping y axis labels
       
        ax = figure.add_subplot(gs[1,0:])
        pos1 = ax.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
        ax.set_position(pos2) # set a new position
        
        #create the second graph title
        second_title = "Latitude: %.4f, Longitude: %.4f, STN Site ID: %s" \
            % (lat,lon,stn_station)
#         if extra != None and extra != '':
        ax.set_title("Storm Tide Water Elevation and Barometric Pressure (Time Zone %s)\n%s" \
                     % (tz,second_title),y=1.010)
#         else:
#             ax.set_title("Storm Tide Water Elevation and Barometric Pressure (Time Zone %s)" % tz,y=1.015)
        
        par1 = ax.twinx()
        pos1 = par1.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
        par1.set_position(pos2) # set a new position

        ax.set_ylabel('Water Elevation in Feet above Datum (%s)' % datum)
        par1.set_ylabel('Barometric Pressure in Inches of Mercury')

        #plot major grid lines
        if grid == 'Barometric Pressure':
            par1.grid(b=True, which='major', color='grey', linestyle="-")
        else:
            ax.grid(b=True, which='major', color='grey', linestyle="-")

        #converts dates to numbers for matplotlib to consume
        time_nums = np.linspace(first_date, last_date, len(time))
       
        #x axis formatter for dates (function format_date() below)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))


        #for minimum
        sensor_min, sensor_min2 = nc.get_sensor_orifice_elevation(in_file_name)
        sensor_min = min(sensor_min,sensor_min2)
        
        
        #get minimum and maximum depth
        
        #plan on rebuilding the flow of execution, ignore spaghetti for now
        depth_min_start = np.min(df.RawDepth)
        
        depth_idx = raw_depth.argmax()
        tide_idx = depth.argmax()
       
        depth_max = raw_depth[depth_idx]
        depth_time = unit_conversion.convert_ms_to_date(time[depth_idx], pytz.UTC)
        tide_max = depth[tide_idx]
        tide_time = unit_conversion.convert_ms_to_date(time[tide_idx], pytz.UTC)
        format_times = unit_conversion.adjust_from_gmt([depth_time,tide_time], \
                                          tz,daylightSavings)
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


        if wlYLims == None:
            if depth_min < 0:
                ax.set_ylim([depth_min * 1.10,lim_max * 1.20])
            else:
                ax.set_ylim([depth_min * .9,lim_max * 1.20])
        else:
            ax.set_ylim([wlYLims[0],wlYLims[1]])
        
         
        #changes scale so the air pressure is more readable
        minY = np.floor(np.min(df.Pressure))
        maxY = np.ceil(np.max(df.Pressure))
        
        if baroYlims == None:
            par1.set_ylim([minY,maxY])
        else:
            par1.set_ylim([baroYlims[0],baroYlims[1]])

        #plot the pressure, depth, and min depth
        
        p4, = ax.plot(time_nums,df.RawDepth,color='#969696', alpha=.75)
        p1, = par1.plot(time_nums,df.Pressure, color="red")
        p2, = ax.plot(time_nums,df.Depth, color="#045a8d")
        p3, = ax.plot(time_nums,np.repeat(sensor_min, len(df.Depth)), linestyle="--", color="#fd8d3c")
        p5,  = ax.plot(depth_num,depth_max, 'o', markersize=10, color='#969696', alpha=1)
        p6,  = ax.plot(tide_num,tide_max, '^', markersize=10, color='#045a8d', alpha=1)
        
        max_storm_tide = "Maximum Unfiltered Water Elevation, feet above datum = %.2f at %s\nMaximum Storm Tide Water Elevation, feet above datum = %.2f at %s" % (depth_max, depth_time,tide_max, tide_time)
        
        stringText = ax.text(0.5, 0.948,max_storm_tide,  \
                bbox={'facecolor':'white', 'alpha':1, 'pad':10}, \
                va='center', ha='center', transform=ax.transAxes)
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
        
        if file_name == None:
            plt.draw()
        else:
          
            plt.savefig(file_name)
            plt.show()
            
       



if __name__ == '__main__':
    make_depth_graph(0, 'new_test2.nc', \
                                         'US/Eastern', False,
                                         'water_level', None,
                                         None, None, 'test_2-2.jpg')
    

