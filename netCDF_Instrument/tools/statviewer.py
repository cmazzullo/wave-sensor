#!/usr/bin/env python3
"""View wave statistics using a graphical interface"""
import numpy as np
import NetCDF_Utils.nc as nc
import tkinter as tk
from tkinter.constants import W, E, LEFT, BOTH, RIGHT
from tkinter.filedialog import askopenfilename
import matplotlib
matplotlib.use('TkAgg', warn=False)
import matplotlib.pyplot as plt
import sys
import stats
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import pytz
import unit_conversion as uc
import easygui
from datetime import timedelta






class StatsViewer:
    def __init__(self, root):
        '''Sets up GUI with options to display statistical graphs'''
        self.root = root
        root.focus_force()
        root.title('Wave Statistics')
        
        self.emptyLabel1 = tk.Label(self.root, text='', font=("Helvetica", 2))
        self.emptyLabel1.pack(anchor=W,padx = 15,pady = 0)
        
        tk.Button(root, text='Load File', command=self.load_file) \
        .pack(anchor=W, pady=2, padx=15)
        
        self.emptyLabel2 = tk.Label(self.root, text='', font=("Helvetica", 2))
        self.emptyLabel2.pack(anchor=W,padx = 15,pady = 0)
        
        self.b1 = tk.Label(self.root, text='Options').pack(anchor=W, pady=2, padx=15)
        
        self.TzLabel = tk.Label(self.root, text='Time zone to display dates in:')
        self.TzLabel.pack(anchor=W,padx = 15,pady = 2)
        options=('GMT',
                'US/Aleutian',
                'US/Central',
                'US/Eastern',
                'US/Hawaii',
                'US/Mountain',
                'US/Pacific')
        self.tzstringvar = tk.StringVar()
        self.tzstringvar.set(options[0])
        
        self.datePickFrame = tk.Frame(root)
        
        tk.OptionMenu(self.datePickFrame, self.tzstringvar, *options).pack(side=LEFT, pady=2, padx=15)
        
        self.daylightSavings = tk.BooleanVar()
        tk.Checkbutton(self.datePickFrame, text="Daylight Savings", variable=self.daylightSavings).pack(side=RIGHT)
        self.datePickFrame.pack()
        
       
        self.statLabel = tk.Label(self.root, text='Statistic and time increment:').pack(anchor=W, pady=2, padx=15)
        self.stat = tk.StringVar()
        self.stat.set('H1/3')
        
        #OPTIONS FOR DISPLAYING STATISTICAL GRAPHS
        tk.OptionMenu(root, self.stat, 
                      'H1/3', 
                      'T1/3', 
                      'T 10%',
                      'T 1%',
                      'RMS',
                      'Median',
                      'Maximum',
                      'Average',
                      'Average Z Cross',
                      'Mean Wave Period',
                      'Crest',
                      'Peak Wave') \
                      .pack(anchor=W, pady=2, padx=15)
        
                      
        self.chunk_size = tk.StringVar()
        self.sizes = {
            'minute(s)': 60,
            'second(s)': 1,
            'hour(s)': 60 * 60,
            'day(s)': 60 * 60 * 24}
        self.chunk_size.set('hour(s)')
        self.number = tk.StringVar()
        self.number.set('1')
        
        #CREATES SUB FRAME FOR CHUNKING OPTIONS
        subframe = tk.Frame(root)
        tk.Entry(subframe, textvariable=self.number).pack(side='left')
        tk.OptionMenu(subframe, self.chunk_size, *self.sizes.keys()) \
        .pack(anchor=W, pady=2, padx=15)
        
        subframe.pack(anchor=W, pady=2, padx=15)
        
        self.emptyLabel3 = tk.Label(self.root, text='', font=("Helvetica", 2))
        self.emptyLabel3.pack(anchor=W,padx = 15,pady = 0)
        
        self.display_button = tk.Button(root, text='Display', command=self.display,
                                        state='disabled')
        self.display_button.pack(anchor=W, pady=2, padx=15)
        
        self.emptyLabel4 = tk.Label(self.root, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W,padx = 15,pady = 0)

    def load_file(self):
        self.filename = askopenfilename()
        self.display_button['state'] = 'normal'
        self.root.focus_force()

    def display(self):
        try:
            t = nc.get_time(self.filename) / 1000

            #get datum
            datum = nc.get_geospatial_vertical_reference(self.filename)
#             times =  nc.get_datetimes(self.file_name)
            
            d = nc.get_depth(self.filename) * uc.METER_TO_FEET
            tstep = t[1] - t[0]
            
            #STATISTICS FUNCTION AVAILABLE FOR PLOTTING
            periodfunc = lambda depth: stats.significant_wave_period(depth, tstep)
            sigfunc = stats.significant_wave_height_standard
            t10func = lambda depth: stats.ten_percent_wave_height(t, depth)
            t1func = lambda depth: stats.one_percent_wave_height(t, depth)
            rms_func = lambda depth: stats.rms_wave_height(t, depth)
            median_func = lambda depth: stats.median_wave_height(t, depth)
            maximum_func = lambda depth: stats.maximum_wave_height(t, depth)
            average_func = lambda depth: stats.average_wave_height(t, depth)
            average_z_func = lambda depth: stats.average_zero_crossing_period(t, depth)
            mean_func = lambda depth: stats.mean_wave_period(t, depth)
            crest_func = lambda depth: stats.crest_wave_period(t, depth)
            peak_wave_func = lambda depth: stats.peak_wave_period(t, depth)
            
            funcs = {'H1/3': (sigfunc, 'H 1/3 (feet)'), # contains functions and labels
                     'T1/3': (periodfunc, 'T 1/3 (seconds)'),
                     'T 10%': (t10func, 'T 10%'),
                     'T 1%': (t1func, 'T 1%'),
                     'RMS' : (rms_func, 'RMS'),
                     'Median': (median_func, 'Median'),
                     'Maximum': (maximum_func, 'Maximum'),
                     'Average': (average_func, 'Average'),
                     'Average Z Cross': (average_z_func, 'Average Z Cross'),
                     'Mean Wave Period': (mean_func, 'Mean Wave Period'),
                     'Crest': (crest_func, 'Crest'),
                     'Peak Wave': (peak_wave_func, 'Peak')}
            
            size = self.sizes[self.chunk_size.get()] * float(self.number.get())
            try:
                tchunks = stats.split_into_chunks(t, tstep, size)
                dchunks = stats.split_into_chunks(d, tstep, size)
            except ValueError:
                tchunks = [t]
                dchunks = [d]
            t_stat = [np.average(tchunk) for tchunk in tchunks]
            # t_stat = [uc.convert_ms_to_datestring(t, pytz.utc) for t in t_stat]
            func = funcs[self.stat.get()][0]
            label = funcs[self.stat.get()][1]
            d_stat = [func(dchunk) for dchunk in dchunks]
            
            #The first x axis time conversion
            t = [uc.convert_ms_to_date(x * 1000, pytz.UTC) for x in t]
            t = uc.adjust_from_gmt(t, self.tzstringvar.get(), self.daylightSavings.get())
            t = [mdates.date2num(x) for x in t]
            
            #The second x axis time conversion
            t_stat = [uc.convert_ms_to_date(x * 1000, pytz.UTC) for x in t_stat]
            t_stat = uc.adjust_from_gmt(t_stat, self.tzstringvar.get(), self.daylightSavings.get())
            t_stat = [mdates.date2num(x) for x in t_stat]
            
            self.plot_stats(t, d, t_stat, d_stat, label, datum)
            plt.show()
        except:
            easygui.msgbox('Could not plot file, please check the file type', 'Error')

    def plot_stats(self,time, depth, stat_time, stat, ylabel, datum):
    
        #plotting options for the depth axis
        fig, ax1 = plt.subplots()
        ax1.set_title('Wave Statistics for Water Elevation')
        ax1.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
        ax1.plot(time, depth, label='Depth')
        #ax1.set_xlabel('time (s)')
        ax1.set_ylabel('Water Elevation in Feet above Datum (%s)' % datum, color='b')
        
        #Plotting options for the stat axis
        ax2 = ax1.twinx()
        ax2.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
        ax2.plot(stat_time, stat, 'ro-')
        ax2.set_ylabel(ylabel, color='r')
        plt.tight_layout()
        
    def format_date(self,x,arb=None):
        '''Format dates so that they are padded away from the x-axis'''
      
        date_str = mdates.num2date(x).strftime('%b-%d-%Y \n %H:%M')
        return ''.join([' ','\n',date_str])
        

if __name__ == '__main__':
    root = tk.Tk()
    StatsViewer(root)
    root.mainloop()
