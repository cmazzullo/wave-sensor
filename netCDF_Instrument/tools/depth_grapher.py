#!/usr/bin/env python3
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import mpl_toolkits.axes_grid1 as host_plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.image as image
import mpl_toolkits.axisartist as AA
import matplotlib.ticker as ticker
import matplotlib.backends.backend_tkagg
import pytz
import netCDF4
from netCDF4 import Dataset
import netCDF4_utils
import netcdftime
import pandas as pd
import NetCDF_Utils.nc as nc
import unit_conversion
from datetime import timedelta


tz_info = None

def format_date(x,arb=None):
    '''Format dates so that they are padded away from the x-axis'''
    date_str = mdates.num2date(x).strftime('%b-%d-%Y \n %H:%M')
    return ''.join([' ','\n',date_str])

def make_depth_graph(box_car_points, in_file_name, tz, daylightSavings, grid=None, \
                     extra=None, baroYlims = None, wlYLims = None, file_name = None):
        '''To compare air_pressure and depth in a graph by consuming a netCDF file'''

        plt.close()
        #global options for matplotlib
        font = {'family' : 'Bitstream Vera Sans',
            'size'   : 16}

        matplotlib.rc('font', **font)
        plt.rcParams['figure.figsize'] = (16,10)
        plt.rcParams['figure.facecolor'] = 'white'

        #reading
        time = nc.get_time(in_file_name)
        
        first_date = unit_conversion.convert_ms_to_date(time[0], pytz.UTC)
        last_date = unit_conversion.convert_ms_to_date(time[-1], pytz.UTC)
        new_dates = unit_conversion.adjust_from_gmt([first_date,last_date], \
                                          tz,daylightSavings)
         
        first_date = mdates.date2num(new_dates[0])
        last_date = mdates.date2num(new_dates[1])
        
#         if daylightSavings == True:
#             delta = timedelta(seconds=3600);
#             time = [x - delta for x in time]
        
        #assign time zone to display the time series in
        tz_info = tz
        
        #air info
        air_pressure = nc.get_air_pressure(in_file_name)
#         air_qc = nc.get_air_pressure_qc(in_file_name)
        
        #convert dbars to psi   *Possibly convert meters to feet later on*
        air_pressure = np.multiply(air_pressure,1.45037738)
 
        #depth info
        depth = nc.get_depth(in_file_name) * unit_conversion.METER_TO_FEET
#         depth_qc = nc.get_depth_qc(in_file_name)

        #get datum
        datum = nc.get_geospatial_vertical_reference(in_file_name)

        #create dataframe
        data = {'Pressure': pd.Series(air_pressure,index=time),
#                 'PressureQC': pd.Series(air_qc, index=time),
                'Depth': pd.Series(depth, index=time)}
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
        ax2 = host_plt.host_subplot(gs[0,0])
        ax2.imshow(logo)
        ax2.axes.get_yaxis().set_visible(False)
        ax2.axes.get_xaxis().set_visible(False)

        #-----------------------------------------Data Section

        #create mirror subplot of first so that there can be two overlapping y axis labels
       
        ax = host_plt.host_subplot(gs[1,0:],axes_class=AA.Axes)
        
        if extra != None and extra != '':
            ax.set_title("Water Level vs. Barometric Pressure (Time Zone %s)\n%s" % (tz,extra))
        else:
            ax.set_title("Water Level vs. Barometric Pressure (Time Zone %s)" % tz)
        par1 = ax.twinx()

        ax.set_ylabel('Barometric Pressure in Pounds Per Square Inch')
        par1.set_ylabel('Water Elevation in Feet above Datum (%s)' % datum)

        #plot major grid lines
        if grid == 'Barometric Pressure':
            ax.grid(b=True, which='major', color='grey', linestyle="-")
        else:
            par1.grid(b=True, which='major', color='grey', linestyle="-")

        #converts dates to numbers for matplotlib to consume
        time_nums = np.linspace(first_date, last_date, len(time))
       
        #x axis formatter for dates (function format_date() below)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))


        #for minimum
        sensor_min, sensor_min2 = nc.get_sensor_orifice_elevation(in_file_name)
        sensor_min = min(sensor_min,sensor_min2)
        
        
        #get minimum and maximum depth
        depth_min_start = np.min(df.Depth)
        depth_max = np.max(df.Depth)
        
        depth_min = np.floor(depth_min_start * 100.0)/100.0
        sensor_min = sensor_min * unit_conversion.METER_TO_FEET
        if depth_min > (sensor_min - .02):
            depth_min = sensor_min - .02
            
        depth_max = np.ceil(depth_max * 100.0)/100.0


        if wlYLims == None:
            par1.set_ylim([depth_min,depth_max])
        else:
            par1.set_ylim([wlYLims[0],wlYLims[1]])
        
       
        #changes scale so the air pressure is more readable
        minY = np.floor(np.min(df.Pressure))
        maxY = np.ceil(np.max(df.Pressure))
        
        if baroYlims == None:
            ax.set_ylim([minY,maxY])
        else:
            ax.set_ylim([baroYlims[0],baroYlims[1]])

        #plot the pressure, depth, and min depth
        
       # p4, = par1.plot(0,0)
        p1, = ax.plot(time_nums,df.Pressure, color="red")
        p2, = par1.plot(time_nums,df.Depth, color="blue")
        p3, = par1.plot(time_nums,np.repeat(sensor_min, len(df.Depth)), linestyle="--", color="orange")
        

        ax.toggle_axisline('')

        #Legend options not needed but for future reference
        ax.legend([p2,p3,p1],['Water Elevation',
        'Minimum Recordable Water Elevation','Barometric Pressure'], \
                  bbox_to_anchor=(.95, 1.37), loc=1, borderaxespad=0.0)

        
        if file_name == None:
            plt.draw()
        else:
            plt.savefig(file_name)
            plt.close()
       



# if __name__ == '__main__':
#     make_depth_graph(100, 'depth.nc',pytz.UTC)
