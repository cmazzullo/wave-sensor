'''
Created on Feb 4, 2016

@author: chogg
'''
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.image as image
import matplotlib.ticker as ticker
from matplotlib.patches import Polygon
from tools.storm_options import StormOptions
matplotlib.use('TkAgg', warn=False)
import pytz
import unit_conversion as uc
from matplotlib.ticker import FormatStrFormatter
from datetime import datetime

class StormStatistics(object):
    
    def __init__(self):
        self.figure = None
        self.grid_spec = None
        self.time_nums = None
        self.wind_time_nums = None
        self.df = None
        self.int_units = True
        
    def format_date(self,x,arb=None):
        '''Format dates so that they are padded away from the x-axis'''
        date_str = mdates.num2date(x).strftime('%b-%d-%Y \n %H:%M')
        return ''.join([' ','\n',date_str])
    
    def get_data(self,so):
        so.get_meta_data()
        so.get_air_meta_data()
        so.get_wave_water_level()
        so.test_water_elevation_below_sensor_orifice_elvation()
        so.get_wave_statistics()
        
    def just_chunks(self,so):
        so.chunk_data()
        so.get_wave_statistics()
        
    def process_graphs(self,so):
        
        self.get_data(so)
        
        if so.statistics['H1/3'].get() == True:
            self.create_header(so)
            self.plot_h13(so)
            
        if so.statistics['Average Z Cross'].get() == True:
            self.create_header(so)
            self.plot_avgz(so)
            
        if so.statistics['Peak Wave'].get() == True:
            self.create_header(so)
            self.plot_peak(so)
        
        if so.statistics['PSD Contour'].get() == True:
            self.create_header(so, True)
            self.spectra_plot(so)      
        
    def create_header(self,so, psd=False):
        
        #matplotlib options for graph
        font = {'family' : 'Bitstream Vera Sans',
                'size'   : 14}
        matplotlib.rc('font', **font)
        plt.rcParams['figure.figsize'] = (16,10)
        plt.rcParams['figure.facecolor'] = 'white'
          
        #make the figure 
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
        
        if psd == False:
            self.grid_spec = gridspec.GridSpec(2, 2,
                                   width_ratios=[1,2],
                                   height_ratios=[1,4]
                                   )
        else:
            self.grid_spec = gridspec.GridSpec(2, 2,
                               width_ratios=[1,2],
                               height_ratios=[1,7]
                               )
        #---------------------------------------Logo Section
        ax2 = self.figure.add_subplot(self.grid_spec[0,0])
        ax2.set_axis_off()
       
        ax2.axes.get_yaxis().set_visible(False)
        ax2.axes.get_xaxis().set_visible(False)
        pos1 = ax2.get_position() # get the original position 
        
        if psd == False:
            pos2 = [pos1.x0, pos1.y0 + .07,  pos1.width, pos1.height] 
            ax2.set_position(pos2) # set a new position
        else:
            pos2 = [pos1.x0 - .062, pos1.y0 + .01,  pos1.width + .1, pos1.height + .05] 
            ax2.set_position(pos2) # set a new position
           
        #display logo 
        ax2.imshow(logo)
   
    def plot_avgz(self,so):
        ax = self.figure.add_subplot(self.grid_spec[1,0:])
        pos1 = ax.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
        ax.set_position(pos2) # set a new position
        
        first_title = "Average Zero-Up-Crossing Period" 
        second_title = "Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                % (so.latitude,so.longitude,str(so.stn_station_number).replace('\n', ''))
    
        ax.text(0.5, 1.065,first_title,  \
                va='center', ha='center', transform=ax.transAxes)
        ax.text(0.5, 1.03,second_title,  \
                va='center', ha='center', transform=ax.transAxes)

        ax.set_ylabel('Average Zero-Up-Crossing Period in Seconds')
        
        #plot major grid lines
        ax.grid(b=True, which='major', color='grey', linestyle="-")
    
        #x axis formatter for dates (function format_date() below)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
        ax.set_xlabel('Timezone: %s' % so.timezone)
        
        p6, = ax.plot(self.time_nums,so.stat_dictionary['Average Z Cross'], color='blue')
        
        #THE COMMENTED CODE BELOW WHICH SETS YLIMITS MAY BE IMPLEMENTED IN THE FUTURE
#             ax.set_ylim([np.min(so.stat_dictionary[data[0][0]]) * .9,
#                      np.max(so.stat_dictionary[data[0][0]]) * 1.1])

        legend = ax.legend([p6],[
        'Average Zero-Up-Crossing Period',
        ], \
                  bbox_to_anchor=(.95, 1.355), loc=1, borderaxespad=0.0, prop={'size':10.3},frameon=False,numpoints=1, \
                  title="EXPLANATION")
        legend.get_title().set_position((-80, 0))
        
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
         
        file_name = ''.join([so.output_fname,'_avg_z_cross','.jpg'])
        plt.savefig(file_name)
        
    def plot_peak(self,so):
        ax = self.figure.add_subplot(self.grid_spec[1,0:])
        pos1 = ax.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
        ax.set_position(pos2) # set a new position
        
        first_title = "Peak Wave Period" 
        second_title = "Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                % (so.latitude,so.longitude,str(so.stn_station_number).replace('\n', ''))
    
        ax.text(0.5, 1.065,first_title,  \
                va='center', ha='center', transform=ax.transAxes)
        ax.text(0.5, 1.03,second_title,  \
                va='center', ha='center', transform=ax.transAxes)

        ax.set_ylabel('Peak Wave Period in Seconds')
        
        #plot major grid lines
        ax.grid(b=True, which='major', color='grey', linestyle="-")
    
        #x axis formatter for dates (function format_date() below)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
        ax.set_xlabel('Timezone: %s' % so.timezone)
        
        p6, = ax.plot(self.time_nums,so.stat_dictionary['Peak Wave'], color='blue')
        
        #THE COMMENTED CODE BELOW WHICH SETS YLIMITS MAY BE IMPLEMENTED IN THE FUTURE
#             ax.set_ylim([np.min(so.stat_dictionary[data[0][0]]) * .9,
#                      np.max(so.stat_dictionary[data[0][0]]) * 1.1])

        legend = ax.legend([p6],[
        'Peak Wave Period',
        ], \
                  bbox_to_anchor=(.95, 1.355), loc=1, borderaxespad=0.0, prop={'size':10.3},frameon=False,numpoints=1, \
                  title="EXPLANATION")
        legend.get_title().set_position((-80, 0))
        
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
         
        file_name = ''.join([so.output_fname,'_peak_wave','.jpg'])
        plt.savefig(file_name)
        
        
    def plot_h13(self,so):
        
        ax = self.figure.add_subplot(self.grid_spec[1,0:])
        pos1 = ax.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
        ax.set_position(pos2) # set a new position
        
        first_title = "90% Confidence Intervals for Significant Wave Height" 
        second_title = "Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                % (so.latitude,so.longitude,str(so.stn_station_number).replace('\n', ''))
    
        ax.text(0.5, 1.065,first_title,  \
                va='center', ha='center', transform=ax.transAxes)
        ax.text(0.5, 1.03,second_title,  \
                va='center', ha='center', transform=ax.transAxes)

        if self.int_units == True:
            ax.set_ylabel('Significant Wave Height in Meters')
        else:
            ax.set_ylabel('Significant Wave Height in Feet')
        
        #plot major grid lines
        ax.grid(b=True, which='major', color='grey', linestyle="-")
    
        #x axis formatter for dates (function format_date() below)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
        ax.set_xlabel('Timezone: %s' % so.timezone)
        
#         p7, = ax.plot(self.time_nums, so.upper_stat_dictionary['H1/3'],"--", \
#                       alpha=0,color="red")
    
        p7 = ax.fill_between(self.time_nums,so.upper_stat_dictionary['H1/3'], \
                        so.lower_stat_dictionary['H1/3'], facecolor='#969696', alpha=0.3, edgecolors=None)
        p6, = ax.plot(self.time_nums,so.stat_dictionary['H1/3'],color='red',linewidth=2)
        
        
        ax.set_ylim([0,np.nanmax(so.upper_stat_dictionary['H1/3']) * 1.1])
        #THE COMMENTED CODE BELOW WHICH SETS YLIMITS MAY BE IMPLEMENTED IN THE FUTURE
#             ax.set_ylim([np.min(so.stat_dictionary[data[0][0]]) * .9,
#                      np.max(so.stat_dictionary[data[0][0]]) * 1.1])

        legend = ax.legend([p6,p7],[
        'Original Estimate',
        '90% Confidence Bound',
        ], \
                  bbox_to_anchor=(.95, 1.355), loc=1, borderaxespad=0.0, prop={'size':10.3},frameon=False,numpoints=1, \
                  title="EXPLANATION")
        legend.get_title().set_position((-25, 0))
        
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
         
        file_name = ''.join([so.output_fname,'_h13','.jpg'])
        plt.savefig(file_name)
        
    def spectra_plot(self, so):
        '''Plot of spectral wave energy vs. wave period in seconds over time'''
    
        #assign vars for variable name terse...ness, tersity? tersation, tersocity, tersitude
        spectra = np.sqrt(so.stat_dictionary['Spectrum'])
        freqs = so.stat_dictionary['Frequency'][0]
        fname = so.output_fname
        sea_time = so.sea_time
        
        #transpose the data so the time axis is the x axis
        data = np.transpose(spectra)
        
        #matplotlib params
        font = {'family' : 'Bitstream Vera Sans',
                            'size'   : 13}
        matplotlib.rc('font', **font)
        plt.rcParams['figure.facecolor'] = 'white'

        #get the energy min and max to create a linspace between the two for
        #the color bar
        
        smax = np.nanmax(np.nanmax(data, axis = 1))
        smin = np.nanmin(np.nanmin(data, axis = 1))
        
        def format_spec(x,arb=None):
            '''Format dates so that they are padded away from the x-axis'''
            index = int(x*10.0)
            if index -1 >=0:
                return '%.6f' % np.linspace(smin,smax,10)[index-1]
            else:
                return 0
        
        def my_formatter_fun(x, p):
            '''Format the frequencies of the spectra plot'''
        
            index = int(x/(2048/len(freqs)))
            if index >= 0 and index <= 1024:
                fl = '%.1f' % (1 / freqs[int(index)])
                if fl[len(fl) - 1] == '1':
                    fl = ''.join([fl[0:len(fl)-1],'0'])
                return fl
            
        def format_spec_date(x,arb=None):
            '''Format dates so that they are padded away from the x-axis in a spectra plot'''
            times = convert_ms_to_date(sea_time)
        
            scale_index = int(float(len(times)/4000.0) * x)
        
            if scale_index >= len(times):
                scale_index = len(times) -1
        
            date_str = mdates.num2date(times[scale_index]).strftime('%b-%d-%Y \n %H:%M')
            return ''.join([' ','\n',date_str])
        
        #set up subplot and adjust its position
        ax = self.figure.add_subplot(self.grid_spec[1,0:])
        pos1 = ax.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
        ax.set_position(pos2) # set a new position
        
        #graph title options
        first_title = "Contours of Power Spectral Density"
        second_title = "Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                % (so.latitude,so.longitude,so.stn_station_number)
  
        ax.text(0.5, 1.065,first_title,  \
                va='center', ha='center', transform=ax.transAxes)
        ax.text(0.5, 1.03,second_title,  \
                va='center', ha='center', transform=ax.transAxes)
        
        #plot the PSD contour and label its colorbar
        image = ax.imshow(data, extent=[0,4000,2448,0],vmin=0, vmax=1, aspect='auto')
        colorbar = self.figure.colorbar(image)
        colorbar.set_label('Power Spectral Density in $m^{2} / Hz$')
        colorbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(format_spec))
        
        #format axes and set labels
        ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(my_formatter_fun))
        ax.set_ylabel('Time in GMT')
        ax.set_ylabel('Wave Period in Seconds')
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_spec_date))
        ax.set_yticks([100,200,500,1000,2000])
        ax.grid(b=True, which='major', color='black', linestyle="-")
    
        plt.savefig(''.join([fname, '_psd_contours','.jpg']))
    
def convert_ms_to_date(time):
    '''Format the date of a time series plot'''
    first_date = datetime.fromtimestamp(time[0] / 1000, pytz.UTC)
    last_date = datetime.fromtimestamp(time[-1] / 1000, pytz.UTC)
   
    first_date = mdates.date2num(first_date)
    last_date = mdates.date2num(last_date)
    
    return np.linspace(first_date, last_date, len(time))
        
        
class Bool(object):
    
    def __init__(self, val):
        self.val = val
         
    def get(self):
        return self.val
        
if __name__ == '__main__':
  
    so = StormOptions()
    so.clip = False
    so.air_fname = 'NCDAR00003_1511478_stormtide_unfiltered.nc'
    so.sea_fname = 'NCDAR00003_1511478_stormtide_unfiltered.nc'
    so.int_units = False
    so.high_cut = 1.0
    so.low_cut = 0.045
    so.from_water_level_file = True

    so.timezone = 'GMT'
    so.daylight_savings = False
    ss = StormStatistics()
    
    for y in so.statistics:
        so.statistics[y] = Bool(False)
        
    so.statistics['H1/3'] = Bool(True)
    so.statistics['Average Z Cross'] = Bool(True)
    so.statistics['PSD Contour'] = Bool(True)
    so.statistics['Peak Wave'] = Bool(True)
    so.format_output_fname('FEVTest2'.replace('/','-'))
    ss.process_graphs(so)
        
    