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
matplotlib.use('TkAgg', warn=False)
import pytz
# import netCDF4_utils
import unit_conversion as uc
from matplotlib.ticker import FormatStrFormatter
from netCDF_Utils import nc

class StormStatistics(object):
    
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
    
    def get_data(self,so):
        so.get_meta_data()
        so.get_air_meta_data()
        so.get_raw_water_level()
        so.get_surge_water_level()
#         so.test_water_elevation_below_sensor_orifice_elvation()
        so.get_wave_water_level()
        so.chunk_data()
        so.get_wave_statistics()
        
    def just_chunks(self,so):
        so.chunk_data()
        so.get_wave_statistics()
        
    def process_graphs(self,so):
        
        self.get_data(so)
#         self.just_chunks(so)

        data = []
        
        if so.statistics['H1/3'].get() == True:
            data.append(['H1/3','Significant Wave Height in Feet','Significant Wave Height in Feet              '])
        if so.statistics['T1/3'].get() == True:
            data.append(['T1/3', 'Significant Wave Period in Seconds','Significant Wave Period in Seconds        '])
        if so.statistics['H10%'].get() == True:
            data.append(['H10%','Top Ten Percent Wave Height in Feet','Top Ten Percent Wave Height in Feet     '])
        if so.statistics['H1%'].get() == True:
            data.append(['H1%','Top One Percent Wave Height in Feet','Top One Percent Wave Height in Feet    '])
        if so.statistics['RMS'].get() == True:
            data.append(['RMS','Root Mean Squared Wave Height in Feet','Root Mean Squared Wave Height in Feet  '])
        if so.statistics['Median'].get() == True:
            data.append(['Median','Median Wave Height in Feet','Median Wave Height in Feet                    '])
        if so.statistics['Maximum'].get() == True:
            data.append(['Maximum','Maximum Wave Height in Feet','Maximum Wave Height in Feet               '])
        if so.statistics['Average'].get() == True:
            data.append(['Average','Average Wave Height in Feet','Average Wave Height in Feet                  '])
        if so.statistics['Average Z Cross'].get() == True:
            data.append(['Average Z Cross','Average Zero Crossing Period in Seconds','Average Zero Crossing Period in Seconds'])
        if so.statistics['Mean Wave Period'].get() == True:
            data.append(['Mean Wave Period','Mean Wave Period in Seconds','Mean Wave Period in Seconds                '])
        if so.statistics['Crest'].get() == True:
            data.append(['Crest','Crest Wave Period in Seconds','Crest Wave Period in Seconds                 '])
        if so.statistics['Peak Wave'].get() == True:
            data.append(['Peak Wave','Peak Wave Period in Seconds','Peak Wave Period in Seconds                  '])
            
        data_len, data_start, file_index =  len(data), 0, 1
        while data_start < data_len:
            if data_len - data_start > 1:
                self.create_header(so)
                self.plot_statistics(so, [data[data_start], data[data_start + 1]], file_index)
                data_start += 2
            else:
                self.create_header(so)
                self.plot_statistics(so, [data[data_start]], file_index)
                data_start += 1
                
            file_index += 1
        
    def create_header(self,so, wind=False):
        
        font = {'family' : 'Bitstream Vera Sans',
                'size'   : 14}
    
        matplotlib.rc('font', **font)
        plt.rcParams['figure.figsize'] = (16,10)
        plt.rcParams['figure.facecolor'] = 'white'
          
        self.figure = plt.figure(figsize=(16,10))
        
        #Get the time nums for the statistics
        first_date = uc.convert_ms_to_date(so.stat_dictionary['time'][0], pytz.UTC)
        last_date = uc.convert_ms_to_date(so.stat_dictionary['time'][-1], pytz.UTC)
        new_dates = uc.adjust_from_gmt([first_date,last_date], \
                                         so.timezone,so.daylight_savings)
        
        first_date = mdates.date2num(new_dates[0])
        last_date = mdates.date2num(new_dates[1])
       
        time = so.stat_dictionary['time']
        self.time_nums = np.linspace(first_date, last_date, len(time))
        
        #Get the time nums for the wave water level
        first_date = uc.convert_ms_to_date(so.sea_time[0], pytz.UTC)
        last_date = uc.convert_ms_to_date(so.sea_time[-1], pytz.UTC)
        new_dates = uc.adjust_from_gmt([first_date,last_date], \
                                         so.timezone,so.daylight_savings)
        
        first_date = mdates.date2num(new_dates[0])
        last_date = mdates.date2num(new_dates[1])
       
        time = so.sea_time
        self.time_nums2 = np.linspace(first_date, last_date, len(time))
        
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
    
    def plot_wave(self,so):
        
#         self.get_data(so)
#
        so.chunk_data()
        so.get_wave_statistics()
        self.create_header(so)
        
        ax = self.figure.add_subplot(self.grid_spec[1,0:])
#         pos1 = ax.get_position() # get the original position 
#         pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
#         ax.set_position(pos2) # set a new position
#         
#         first_title = "Wave Water Elevation and Statistics" 
#         second_title = "Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
#                 % (so.latitude,so.longitude,str(so.stn_station_number).replace('\n', ''))
#     #         if extra != None and extra != '':
#         titleText = ax.text(0.5, 1.065,first_title,  \
#                 va='center', ha='center', transform=ax.transAxes)
#         titleText2 = ax.text(0.5, 1.03,second_title,  \
#                 va='center', ha='center', transform=ax.transAxes)
# 
# #         ax.set_ylabel('%s' % data[0][1])
        
        
        #plot major grid lines
        ax.grid(b=True, which='major', color='grey', linestyle="-")
    
        #x axis formatter for dates (function format_date() below)
#         ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
        ax.set_xlabel('Timezone: %s' % so.timezone)
        
       
       
#         p2, = ax.plot(self.time_nums2,so.wave_water_level, color="#045a8d")
        p6,  = ax.plot(range(0,len(so.wave_water_level)),so.wave_water_level * uc.METER_TO_FEET, 
                       color='red', alpha=1)
        
        
         
        file_name = ''.join(['_wave2','.jpg'])
        plt.savefig(file_name)  
    def plot_statistics(self,so, data,index):
        
        ax = self.figure.add_subplot(self.grid_spec[1,0:])
        pos1 = ax.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
        ax.set_position(pos2) # set a new position
        
        first_title = "Wave Water Elevation Statistics" 
        second_title = "Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                % (so.latitude,so.longitude,str(so.stn_station_number).replace('\n', ''))
    #         if extra != None and extra != '':
        titleText = ax.text(0.5, 1.065,first_title,  \
                va='center', ha='center', transform=ax.transAxes)
        titleText2 = ax.text(0.5, 1.03,second_title,  \
                va='center', ha='center', transform=ax.transAxes)

        ax.set_ylabel('%s' % data[0][1])
        
        
        #plot major grid lines
        ax.grid(b=True, which='major', color='grey', linestyle="-")
    
        #x axis formatter for dates (function format_date() below)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
        ax.set_xlabel('Timezone: %s' % so.timezone)
        
       
        
#         p2, = ax.plot(self.time_nums2,so.wave_water_level, color="#045a8d")
        p6,  = ax.plot(self.time_nums,so.stat_dictionary[data[0][0]], color='red', alpha=1)
        
        if (len(data) > 1):
            par1 = ax.twinx()
            pos1 = par1.get_position() # get the original position 
            pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
            par1.set_position(pos2) # set a new position
            
            par1.set_ylabel(data[1][1])
#            
           
            p1, = par1.plot(self.time_nums,so.stat_dictionary[data[1][0]], color='#045a8d', alpha=1)
            
            
#             par1.set_ylim([np.min(so.stat_dictionary[data[1][0]]) * .9,
#                     np.max(so.stat_dictionary[data[1][0]]) * 1.1])
#             ax.set_ylim([np.min(so.stat_dictionary[data[0][0]]) * .9,
#                      np.max(so.stat_dictionary[data[0][0]]) * 1.1])

    
        #Legend options not needed but for future reference
            legend = ax.legend([p1,p6],[
            data[1][2],
            data[0][2]
            ], \
                      bbox_to_anchor=(.95, 1.355), loc=1, borderaxespad=0.0, prop={'size':10.3},frameon=False,numpoints=1, \
                      title="EXPLANATION")
            legend.get_title().set_position((-100, 0))
        else:
#             ax.set_ylim([np.min(so.stat_dictionary[data[0][0]]) * .9,
#                      np.max(so.stat_dictionary[data[0][0]]) * 1.1])
            legend = ax.legend([p6],[
            data[0][2]
            ], \
                      bbox_to_anchor=(.95, 1.355), loc=1, borderaxespad=0.0, prop={'size':10.3},frameon=False,numpoints=1, \
                      title="EXPLANATION")
            legend.get_title().set_position((-100, 0))
        
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
         
        file_name = ''.join([so.output_fname,'_statistics4',str(index),'.jpg'])
        plt.savefig(file_name)
        
#         plt.show()  
    
    
        
class Bool(object):
    
    def __init__(self, val):
        self.val = val
         
    def get(self):
        return self.val
        
if __name__ == '__main__':
  
    so = StormOptions()
    so.air_fname = 'bp.nc'
    so.sea_fname = 'true.nc'
#     so.wind_fname = 'jonas_wind-1.nc'

#should be an n _-_
#     so.air_fname = 'Joaquim-air-2.nc'
#     so.sea_fname = 'joaquin_chop_2.nc'
    
#     so.sea_time = nc.get_time('30_sec_wave.nc')
#     so.wave_water_level = nc.get_variable_data('30_sec_wave.nc', 'depth')
    so.timezone = 'GMT'
    so.daylight_savings = False
    ss = StormStatistics()
    
#     ss.plot_wave(so)
#     for x in so.statistics: 
    for y in so.statistics:
        so.statistics[y] = Bool(False)
        
    so.statistics['H1/3'] = Bool(True)
    so.statistics['Average Z Cross'] = Bool(True)
    so.format_output_fname('slide_graphs_stats2'.replace('/','-'))
    ss.process_graphs(so)
        
    
        
#     so.statistics['H1/3'] = Bool(True)
#     so.statistics['T1/3'] = Bool(False)      
#     so.statistics['T 10%'] = Bool(True)
#     so.statistics['T 1%'] = Bool(False)
#     so.statistics['RMS'] = Bool(False)
#     so.statistics['Median'] = Bool(False)
#     so.statistics['Maximum'] = Bool(False)
#     so.statistics['Average'] = Bool(False)
#     so.statistics['Average Z Cross'] = Bool(False)
#     so.statistics['Mean Wave Period'] = Bool(False)
#     so.statistics['Crest'] = Bool(False)
#     so.statistics['Peak Wave'] = Bool(False)
    
    