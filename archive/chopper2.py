#!/usr/bin/env python3
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg', warn=False)
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import pytz
import tkinter as Tk
from tkinter.constants import W
from tkinter import filedialog
import pandas as pd
from NetCDF_Utils import nc
from NetCDF_Utils.nc import chop_netcdf
from datetime import datetime
from pytz import timezone
import easygui
import numpy

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
        
        #used for spacing
        self.emptyLabel1 = Tk.Label(self.root, text='', font=("Helvetica", 2))
        self.emptyLabel1.pack(anchor=W,padx = 15,pady = 0)
        
        #radio button for sea or air pressure
        methods = [('Sea Pressure', 'sea'),
                   ('Air Pressure', 'air')]

        self.methodvar = Tk.StringVar()
        self.methodvar.set('sea')

        Tk.Label(root, text='What type of file would you like to chop?').pack(anchor=W)
        for name, kwarg in methods:
            Tk.Radiobutton(root, text=name, variable=self.methodvar,
                            value=kwarg).pack(anchor=W)
        
        #Date time options
        Tk.Label(root, text='Time zone to display dates in:').pack(anchor=W)
        options=('GMT',
                'US/Alaska',
                'US/Aleutian',
                'US/Arizona',
                'US/Central',
                'US/East-Indiana',
                'US/Eastern',
                'US/Hawaii',
                'US/Indiana-Starke',
                'US/Michigan',
                'US/Mountain',
                'US/Pacific',
                'US/Pacific-New',
                'US/Samoa')
        self.tzstringvar = Tk.StringVar()
        self.tzstringvar.set(options[0])
        Tk.OptionMenu(self.root, self.tzstringvar, *options).pack(anchor=W, pady=2, padx=15)
        
        #tkinter spacing
        self.emptyLabel4 = Tk.Label(self.root, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W,padx = 15,pady = 0)
        
        # select file button
        self.b1 = Tk.Button(self.root, text='Select File', command=self.select_input)
        self.b1.pack(anchor=W, pady=2, padx=15)
        
        #more spacing, tkinter spacing, this should be remedied some other way
        self.emptyLabel2 = Tk.Label(self.root, text='', font=("Helvetica", 2))
        self.emptyLabel2.pack(anchor=W,padx = 15,pady = 0)
        
        #options
        Tk.Label(self.root, text='Define Time Period to Export:').pack(anchor=W, padx=15, pady=2)
        
        #Start Date
        Tk.Label(self.root, text='Start date (mm/dd/YY HH:MM:SS):').pack(anchor=W, pady=2, padx=15)
        self.date1 = Tk.StringVar()
        self.textEntry = Tk.Entry(self.root, width=30, textvariable=self.date1).pack(anchor=W, pady=2, padx=15)
        
        #End Date
        Tk.Label(self.root,text='End date (mm/dd/YY HH:MM:SS):').pack(anchor=W, pady=2, padx=15)
        self.date2 = Tk.StringVar()
        self.textEntry2 = Tk.Entry(self.root,width=30, textvariable=self.date2).pack(anchor=W, pady=2, padx=15)
        
        #tkinter spacing
        self.emptyLabel3 = Tk.Label(self.root, text='', font=("Helvetica", 2))
        self.emptyLabel3.pack(anchor=W,padx = 15,pady = 0)
        
        #Export the selected time series
        self.b = Tk.Button(self.root, text='Export Selection', command=self.export, state='disabled')
        self.b.pack(anchor=W, pady=2, padx=15)
        self.emptyLabel4 = Tk.Label(self.root, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W,padx = 15,pady = 0)

    def plot_pressure(self):
        
        #get date times from netCDF file
        self.t_dates = nc.get_datetimes(self.fname)
         
        #get sea or air pressure depending on the radio button
        if self.methodvar.get() == "sea":
            p = nc.get_pressure(self.fname)
        else:
            p = nc.get_air_pressure(self.fname)
            
        #get quality control data    
        qc = nc.get_flags(self.fname)
        
        self.fig = fig = plt.figure()
        ax = fig.add_subplot(111)
        
        #title
        ax.set_title('Chop Pressure File\n(Timezone in %s time)' % self.tzstringvar.get())
        
        #x axis formatter for dates (function format_date() below)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
        
        #converts dates to numbers for matplotlib to consume
        self.time_nums = [mdates.date2num(x) for x in self.t_dates]
        
        #labels, and plot time series
        line = plt.plot(self.time_nums, p, color='blue')
        plt.xlabel('Time (s)')
        plt.ylabel('Pressure (dBar)')
        
        #all points that were flagged in the qc data are stored in
        #bad_points and bad_times to draw a red x in the graph
        data = {'Pressure': pd.Series(p,index=self.time_nums),
                'PressureQC': pd.Series(qc, index=self.time_nums)}
        df = pd.DataFrame(data)
        
        df.Pressure[(df['PressureQC'] == 11111111) | (df['PressureQC'] == 1111011)
                | (df['PressureQC'] == 11111110) | (df['PressureQC'] == 11110110)] = np.NaN;
        
        
        plt.plot(df.index, df.Pressure, 'rx')
        
        #set initial bounds for the time series selection
        
        x1 = self.time_nums[0]
        x2 = self.time_nums[-1]
        self.left = ax.axvline(x1, color='black')
        self.right = ax.axvline(x2, color='black')
         
        #yellow highlight for selected area in graph    
        patch = ax.axvspan(x1, x2, alpha=0.25, color='yellow', linewidth=0)
        events = []
 
        def on_click(event):
             
            #capture events and button pressed
            events.append(event)
            if event.button == 1:
                l = self.left
            elif event.button == 3:
                l = self.right
            l.set_xdata([event.xdata, event.xdata])
            l.figure.canvas.draw()
             
            #get the left slice time data, convert matplotlib num to date
            #format date string for the GUI start date field
            x1 = self.left.get_xdata()[0]
            temp_date = mdates.num2date(x1, tz=pytz.timezone(str(self.tzstringvar.get())))
            datestring = temp_date.strftime('%m/%d/%y %H:%M:%S')
            self.date1.set(datestring)
              
            #get the left slice time data, convert matplotlib num to date
            #format date string for the GUI start date field
            x2 = self.right.get_xdata()[0]
            temp_date2 = mdates.num2date(x2, tz=pytz.timezone(str(self.tzstringvar.get())))
            datestring2 = temp_date2.strftime('%m/%d/%y %H:%M:%S')
            self.date2.set(datestring2)
             
            xy = [[x1, 0], [x1, 1], [x2, 1], [x2, 0], [x1, 0]]
             
            #draw yellow highlight over selected area in graph
            patch.set_xy(xy)
            patch.figure.canvas.draw()
 
        self.canvas = canvas = self.fig.canvas
         
        #add event listener for clicks on the graph
        canvas.mpl_connect('button_press_event', on_click)
        plt.draw()
        
        plt.show()


    def export(self):
        #exception handling for the export process
        try:
            #get the beginning and end of the selection
            date1 = self.date1.get()
            date2 = self.date2.get()
            
            #ask to save file name and directory
            out_fname = filedialog.asksaveasfilename()
            if out_fname == '':
                return
            
                      
            #convert string to date time, then convert to matplotlib number
            tz = pytz.timezone(str(self.tzstringvar.get()))
            temp_dt = datetime.strptime(date1, '%m/%d/%y %H:%M:%S')
            temp_dt = tz.localize(temp_dt, is_dst=None).astimezone(pytz.UTC)
            t1 = mdates.date2num(temp_dt)
            
            tz = pytz.timezone(str(self.tzstringvar.get()))
            temp_dt2 = datetime.strptime(date2, '%m/%d/%y %H:%M:%S')
            temp_dt2 = tz.localize(temp_dt2, is_dst=None).astimezone(pytz.UTC)
            t2 = mdates.date2num(temp_dt2)
            
            i1 = find_index(self.time_nums, t1)
            i2 = find_index(self.time_nums, t2)
            
            #just a print statement
            print('self.fname = ', self.fname)
            
            #chop out selected time series given the chosen parameters
            chop_netcdf(self.fname, out_fname, i1, i2)
            plt.close('all')
            
            #success and close the GUI
            easygui.msgbox("Success chopping file!", "Success")
            self.root.quit()
            self.root.destroy()
        except:
            easygui.msgbox("Could not export file, check file type and try again.", "Error")

    def select_input(self):
        #general exception handling, finer details will be implemented as needed
        try:
            self.fname = filedialog.askopenfilename()
            self.plot_pressure()
            
            #enable the export button once a file is selected
            #then force focus back on the gui
            self.b['state'] = 'normal'
            self.root.focus_force()
        except:
            easygui.msgbox("Could not open file, check file type.", "Error")
             
    def format_date(self,x,arb=None):
        '''Format dates so that they are padded away from the x-axis'''
        tz = timezone(self.tzstringvar.get())
        date_str = mdates.num2date(x,tz=tz).strftime('%b-%d-%Y \n %H:%M')
        return ''.join([' ','\n',date_str])
            

if __name__ == '__main__':
    root = Tk.Tk()
    gui = Chopper(root)
    root.mainloop()
