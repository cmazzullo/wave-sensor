#!/usr/bin/env python3
import numpy as np
import matplotlib
matplotlib.use('TkAgg', warn=False)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import pytz
import tkinter as Tk
from tkinter.constants import W, LEFT, RIGHT
from tkinter import filedialog
# import pandas as pd
from NetCDF_Utils import nc
from NetCDF_Utils.nc import chop_netcdf
from datetime import datetime
# from datetime import timedelta
# from pytz import timezone
import easygui
import numpy
import unit_conversion as uc
# import traceback
# import sys


def find_index(array, value):
    
    array = numpy.array(array)
    idx = (np.abs(array-value)).argmin()
    
    return idx

    

class Chopper:
    def __init__(self, root):
        
        #file name and title
        self.fname = ''
        self.root = root
        self.root.focus_force()
        self.root.title("Chopper GUI")
        self.canvas = None
        self.toolbar = None
        self.frame = Tk.Frame(root)
        
        #used for spacing
        self.emptyLabel1 = Tk.Label(self.frame, text='', font=("Helvetica", 2))
        self.emptyLabel1.pack(anchor=W, padx=15, pady=0)
        self.plot_event = False
        
        # radio button for sea or air pressure
        methods = [('Sea Pressure', 'sea'),
                   ('Air Pressure', 'air')]

        self.methodvar = Tk.StringVar()
        self.methodvar.set('sea')

        self.label1 = Tk.Label(root, text='What type of file would you like to chop?').pack(anchor=W)
        for name, kwarg in methods:
            Tk.Radiobutton(root, text=name, variable=self.methodvar,
                            value=kwarg).pack(anchor=W)
        
        # Date time options
        Tk.Label(root, text='Time zone to display dates in:').pack(anchor=W)
        options = ('GMT',
                'US/Aleutian',
                'US/Central',
                'US/Eastern',
                'US/Hawaii',
                'US/Mountain',
                'US/Pacific')
        self.tzstringvar = Tk.StringVar()
        self.tzstringvar.set(options[0])
        
        self.datePickFrame = Tk.Frame(self.frame)
        
        Tk.OptionMenu(self.datePickFrame, self.tzstringvar, *options).pack(side=LEFT, pady=2, padx=15)
        
        self.daylightSavings = Tk.BooleanVar()
        Tk.Checkbutton(self.datePickFrame, text="Daylight Savings", variable=self.daylightSavings).pack(side=RIGHT)
        self.datePickFrame.pack()
        
        # tkinter spacing
        self.emptyLabel4 = Tk.Label(self.frame, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W, padx=15, pady=0)
        
        # select file button
        self.b1 = Tk.Button(self.frame, text='Select File', command=self.select_input)
        self.b1.pack(anchor=W, pady=2, padx=15)
        
        # more spacing, tkinter spacing, this should be remedied some other way
        self.emptyLabel2 = Tk.Label(self.frame, text='', font=("Helvetica", 2))
        self.emptyLabel2.pack(anchor=W, padx=15, pady=0)
        
        # options
        Tk.Label(self.frame, text='Define Time Period to Export:').pack(anchor=W, padx=15, pady=2)
        
        # Start Date
        Tk.Label(self.frame, text='Start date (mm/dd/YY HH:MM:SS):').pack(anchor=W, pady=2, padx=15)
        self.date1 = Tk.StringVar()
      
        self.textEntry = Tk.Entry(self.frame, width=30, textvariable=self.date1).pack(anchor=W, pady=2, padx=15)
        
        # End Date
        Tk.Label(self.frame, text='End date (mm/dd/YY HH:MM:SS):').pack(anchor=W, pady=2, padx=15)
        self.date2 = Tk.StringVar()
        self.textEntry2 = Tk.Entry(self.frame, width=30, textvariable=self.date2).pack(anchor=W, pady=2, padx=15)
        
        # tkinter spacing
        self.emptyLabel3 = Tk.Label(self.frame, text='', font=("Helvetica", 2))
        self.emptyLabel3.pack(anchor=W, padx=15, pady=0)
        
        # Export the selected time series
        self.b = Tk.Button(self.frame, text='Export Selection', command=self.export, state='disabled')
        self.b.pack(anchor=W, pady=2, padx=15)
        self.emptyLabel4 = Tk.Label(self.frame, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W, padx=15, pady=0)
        
        self.frame.pack(side=Tk.LEFT)
        
    def plot_pressure(self):
        
        #check to see if there is already a graph if so destroy it
        if self.canvas != None:
            self.toolbar.destroy()
            self.canvas.get_tk_widget().destroy()
            
        font = {'family' : 'Bitstream Vera Sans',
            'size'   : 11}

        matplotlib.rc('font', **font)
        plt.rcParams['figure.figsize'] = (12,7)
        plt.rcParams['figure.facecolor'] = 'silver'
        
        #get date times from netCDF file
        self.t_dates = nc.get_time(self.fname)
        
        
        
        self.first_date = uc.convert_ms_to_date(self.t_dates[0], pytz.UTC)
        self.last_date = uc.convert_ms_to_date(self.t_dates[-1], pytz.UTC)
        self.new_dates = uc.adjust_from_gmt([self.first_date,self.last_date], \
                                          self.tzstringvar.get(),self.daylightSavings.get())
         
      
        self.first_date = mdates.date2num(self.new_dates[0])
        self.last_date = mdates.date2num(self.new_dates[1])
        
         
        #get sea or air pressure depending on the radio button
        if self.methodvar.get() == "sea":
            p = nc.get_pressure(self.fname)
        else:
            p = nc.get_air_pressure(self.fname)
          
        
        #get quality control data    
#         qc = nc.get_flags(self.fname)
        
        self.fig = fig = plt.figure(figsize=(12,7))

        self.ax = fig.add_subplot(111)
        
        #title
        self.ax.set_title('Chop Pressure File\n(Timezone in %s time)' % self.tzstringvar.get())
        
        #x axis formatter for dates (function format_date() below)
        self.ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
        
        #converts dates to numbers for matplotlib to consume
        self.time_nums = np.linspace(self.first_date, self.last_date, len(self.t_dates))
        
        #labels, and plot time series
        self.line = self.ax.plot(self.time_nums, p, color='blue')

#         plt.xlabel('Time (s)')
        plt.ylabel('Pressure (dBar)')
        
        #all points that were flagged in the qc data are stored in
        #bad_points and bad_times to draw a red x in the graph
#         data = {'Pressure': pd.Series(p,index=self.time_nums),
#                 'PressureQC': pd.Series(qc, index=self.time_nums)}
#         df = pd.DataFrame(data)
#            
#         df.Pressure[(df['PressureQC'] == 11111111) | (df['PressureQC'] == 1111011)
#                 | (df['PressureQC'] == 11111110) | (df['PressureQC'] == 11110110)] = np.NaN;
#           
#           
#         self.redx = self.ax.plot(df.index, df.Pressure, 'rx')
        
        #saves state for reloading
        
    
        #set initial bounds for the time series selection
        
        x1 = self.time_nums[0]
        x2 = self.time_nums[-1]
        self.left = self.ax.axvline(x1, color='black')
        self.right = self.ax.axvline(x2, color='black')
         
        #yellow highlight for selected area in graph    
        self.patch = self.ax.axvspan(x1, x2, alpha=0.25, color='yellow', linewidth=0)
        
        
        #initial set of datestring values
        temp_date = mdates.num2date(x1, tz=pytz.timezone("GMT"))#tz=pytz.timezone(str(self.tzstringvar.get())))
        datestring = temp_date.strftime('%m/%d/%y %H:%M:%S')
        self.date1.set(datestring)
        
       
        temp_date2 = mdates.num2date(x2, tz=pytz.timezone("GMT"))#tz=pytz.timezone(str(self.tzstringvar.get())))
        datestring2 = temp_date2.strftime('%m/%d/%y %H:%M:%S')
        self.date2.set(datestring2)
        
        
        events = []

 
        def on_click(event):
            
            #capture events and button pressed
            events.append(event)
            if event.button == 1:
                l = self.left
            elif event.button == 3:
                l = self.right
                

            l.set_xdata([event.xdata, event.xdata])
          
            #get the left slice time data, convert matplotlib num to date
            #format date string for the GUI start date field
            x1 = self.left.get_xdata()[0]
            temp_date = mdates.num2date(x1, tz=pytz.timezone("GMT"))#tz=pytz.timezone(str(self.tzstringvar.get())))
            datestring = temp_date.strftime('%m/%d/%y %H:%M:%S')
            self.plot_event = True
            self.date1.set(datestring)
              
            #get the left slice time data, convert matplotlib num to date
            #format date string for the GUI start date field
            x2 = self.right.get_xdata()[0]
            temp_date2 = mdates.num2date(x2, tz=pytz.timezone("GMT"))#tz=pytz.timezone(str(self.tzstringvar.get())))
            datestring2 = temp_date2.strftime('%m/%d/%y %H:%M:%S')
            self.plot_event = True
            self.date2.set(datestring2)
             
            xy = [[x1, 0], [x1, 1], [x2, 1], [x2, 0], [x1, 0]]
             
            self.patch.set_xy(xy)
            self.canvas.draw()
            
            
        def patch2(sv):
            if self.plot_event == True:
                self.plot_event = False
            else:
                try:
                    if sv == 1:
                        date = self.date1.get()
                        tz = pytz.timezone("GMT")#tz=pytz.timezone(str(self.tzstringvar.get())))
                        temp_dt = datetime.strptime(date, '%m/%d/%y %H:%M:%S')
                        #temp_dt = tz.localize(temp_dt, is_dst=None).astimezone(pytz.UTC)
                        x1 = mdates.date2num(temp_dt)
                        self.left.set_xdata([x1,x1])
                         
                        x2 = self.right.get_xdata()[0]
                         
                        xy = [[x1, 0], [x1, 1], [x2, 1], [x2, 0], [x1, 0]]
                  
                        #draw yellow highlight over selected area in graph
                      
                        self.patch.set_xy(xy)
                        self.canvas.draw()
                    else:
                        x1 = self.left.get_xdata()[0]
                         
                        date = self.date2.get()
                        tz = pytz.timezone("GMT")#tz=pytz.timezone(str(self.tzstringvar.get())))
                        temp_dt = datetime.strptime(date, '%m/%d/%y %H:%M:%S')
                        #temp_dt = tz.localize(temp_dt, is_dst=None).astimezone(pytz.UTC)
                        x2 = mdates.date2num(temp_dt)
                        self.right.set_xdata([x2,x2])
                      
                        xy = [[x1, 0], [x1, 1], [x2, 1], [x2, 0], [x1, 0]]
                  
                        #draw yellow highlight over selected area in graph
#                        
                        self.patch.set_xy(xy)
                        self.canvas.draw()
                       
                        
                except:
                    print('No event occurred')
  
         
          
        #add event listener for clicks on the graph
#         
        self.date1.trace("w", lambda name, index, mode, i = 1: patch2(i))
        self.date2.trace("w", lambda name, index, mode, i = 2: patch2(i))
        
        
        self.canvas = FigureCanvasTkAgg(self.fig, master= self.root)
        
        self.toolbar = NavigationToolbar2TkAgg( self.canvas, self.root )
        self.toolbar.update()
      
        self.canvas.mpl_connect('button_press_event', on_click)
        
       
        self.canvas.show()
        
        self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=2)
        
        
    def export(self):
        #exception handling for the export process
#         try:
            #get the beginning and end of the selection
            date1 = self.date1.get()
            date2 = self.date2.get()
            
            #ask to save file name and directory
            out_fname = filedialog.asksaveasfilename()
            if out_fname == '':
                return
                     
            #convert string to date time, then convert to matplotlib number
            #tz = pytz.timezone(str(self.tzstringvar.get()))
            temp_dt = datetime.strptime(date1, '%m/%d/%y %H:%M:%S')
            #temp_dt = tz.localize(temp_dt, is_dst=None).astimezone(pytz.UTC)
            t1 = mdates.date2num(temp_dt)
            
            #tz = pytz.timezone(str(self.tzstringvar.get()))
            temp_dt2 = datetime.strptime(date2, '%m/%d/%y %H:%M:%S')
            #temp_dt2 = tz.localize(temp_dt2, is_dst=None).astimezone(pytz.UTC)
            t2 = mdates.date2num(temp_dt2)
            
            i1 = find_index(self.time_nums, t1)
            i2 = find_index(self.time_nums, t2)
            
            #chop out selected time series given the chosen parameters
            if self.methodvar.get() == "sea":
                chop_netcdf(self.fname, out_fname, i1, i2, False)
            else:
                chop_netcdf(self.fname, out_fname, i1, i2, True)
            
            
            #success and close the GUI
            easygui.msgbox("Success chopping file!", "Success")
            self.root.quit()
            self.root.destroy()
#         except:
#             easygui.msgbox("Could not export file, check export parameters and try again.", "Error")

    def select_input(self):
        #general exception handling, finer details will be implemented as needed
        try:
            self.fname = filedialog.askopenfilename()
            if(self.fname != '' and self.fname != None):
                self.plot_pressure()
             
                #enable the export button once a file is selected
                #then force focus back on the gui
                self.b['state'] = 'normal'
                self.root.focus_force()
        except:

            easygui.msgbox('Cannot plot file, please check file type and try again', "Error")
             
    def format_date(self,x,arb=None):
        '''Format dates so that they are padded away from the x-axis'''
#         tz = timezone(self.tzstringvar.get())
        
      
        date_str = mdates.num2date(x).strftime('%b-%d-%Y \n %H:%M')
        return ''.join([' ','\n',date_str])
            

if __name__ == '__main__':
    root = Tk.Tk()
    gui = Chopper(root)
    root.mainloop()
