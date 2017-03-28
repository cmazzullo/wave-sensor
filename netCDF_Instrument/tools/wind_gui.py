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
from netCDF_Utils import nc
from netCDF_Utils.nc import chop_netcdf
from datetime import datetime
# from datetime import timedelta
# from pytz import timezone
import easygui
import numpy
import unit_conversion as uc
from tools.wind_script import get_wind_data
# import traceback
# import sys


def find_index(array, value):
    
    array = numpy.array(array)
    idx = (np.abs(array-value)).argmin()
    
    return idx

    

class WindGUI:
    def __init__(self, root):
        
        #file name and title
        self.fname = ''
        self.root = root
        self.root.focus_force()
        self.root.title("Wind GUI")
        self.canvas = None
        self.toolbar = None
        self.frame = Tk.Frame(root)
        
        #used for spacing
        self.emptyLabel1 = Tk.Label(self.frame, text='', font=("Helvetica", 2))
        self.emptyLabel1.pack(anchor=W, padx=15, pady=0)
        
        Tk.Label(self.frame, text='Station Id:').pack(anchor=W, pady=2, padx=15)
        self.station_id = Tk.StringVar()
      
        self.textEntry = Tk.Entry(self.frame, width=30, textvariable=self.station_id).pack(anchor=W, pady=2, padx=15)

        self.emptyLabel1 = Tk.Label(self.frame, text='', font=("Helvetica", 2))
        self.emptyLabel1.pack(anchor=W, padx=15, pady=0)
        
        # Date time options
        Tk.Label(self.frame, text='Time zone of date parameters:').pack(anchor=W, pady=2, padx=15)
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
        
        # select file button
        
        
        # more spacing, tkinter spacing, this should be remedied some other way
        self.emptyLabel2 = Tk.Label(self.frame, text='', font=("Helvetica", 2))
        self.emptyLabel2.pack(anchor=W, padx=15, pady=0)
        
        # Start Date
        Tk.Label(self.frame, text='Start date (yyyy-mm-dd HH:MM) 24 hour clock:').pack(anchor=W, pady=2, padx=15)
        self.date1 = Tk.StringVar()
      
        self.textEntry = Tk.Entry(self.frame, width=30, textvariable=self.date1).pack(anchor=W, pady=2, padx=15)
        
        # End Date
        Tk.Label(self.frame, text='End date (yyyy-mm-dd HH:MM) 24 hour clock:').pack(anchor=W, pady=2, padx=15)
        self.date2 = Tk.StringVar()
        self.textEntry2 = Tk.Entry(self.frame, width=30, textvariable=self.date2).pack(anchor=W, pady=2, padx=15)
        
        # tkinter spacing
        self.emptyLabel3 = Tk.Label(self.frame, text='', font=("Helvetica", 2))
        self.emptyLabel3.pack(anchor=W, padx=15, pady=0)
        
        # Export the selected time series
        self.b = Tk.Button(self.frame, text='Get Wind Data', command=self.process_file)
        self.b.pack(anchor=W, pady=2, padx=15)
        self.emptyLabel4 = Tk.Label(self.frame, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W, padx=15, pady=0)
        
        self.frame.pack(side=Tk.LEFT)
        
    
        
        
    def process_file(self):
        
        if self.station_id is None or self.station_id == '':
            easygui.msgbox("Please fill in a site id", "Error")
            return
        
       
        #exception handling for the export process
#         try:
        out_fname = filedialog.asksaveasfilename()
        if out_fname == '':
            return
#           #get the beginning and end of the selection
        site = self.station_id.get()
        date1 = self.date1.get()
        date2 = self.date2.get()
        tz = self.tzstringvar.get()
        daylight_savings = self.daylightSavings.get()
       
        get_wind_data(out_fname, site, date1, date2, tz, daylight_savings)         
        #convert string to date time, then convert to matplotlib number
        #tz = pytz.timezone(str(self.tzstringvar.get()))
        
        easygui.msgbox("Success grabbing file!", "Success")
#         except:
#             easygui.msgbox("Could not process file, please check station id and date time entries.", "Error")

    
             
            

if __name__ == '__main__':
    root = Tk.Tk()
    gui = WindGUI(root)
    root.mainloop()
