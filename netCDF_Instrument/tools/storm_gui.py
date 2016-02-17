#!/usr/bin/env python3
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

import NetCDF_Utils.nc as nc
import tools.script2 as script2
import tools.script1_gui as gc
import os
from tools.storm_options import StormOptions
from tools.storm_graph import StormGraph
from tools.storm_csv import StormCSV
from tools.storm_netCDF import Storm_netCDF
import traceback


class StormGui:
    def __init__(self, root):
        
        #root and selection dialogs for sea and air netCDF files
        self.root = root
        root.title('Storm Surge GUI (Pressure -> Water Level)')
        self.root.focus_force()
        
        self.chopperLabel = Label(root, text='(Please make sure Chopper is closed before making a graph)')
        self.chopperLabel.pack(anchor=W,padx = 15,pady = 2)
        
        self.sea_fname = ''
        self.sea_var = StringVar()
        self.sea_var.set('File containing water pressure...')
        self.air_fname = ''
        self.air_var = StringVar()
        self.air_var.set('File containing air pressure...')
        self.wind_fname = ''
        self.wind_var = StringVar()
        self.wind_var.set('File containing wind data...')
        
        self.make_fileselect(root, 'Water file:',
                             self.sea_var, 'sea_fname')
        self.make_fileselect(root, 'Air file:',
                             self.air_var, 'air_fname')
        self.make_fileselect(root, 'Wind file:',
                             self.wind_var, 'wind_fname')
        c3 = lambda: self.select_output_file(root)
        
        self.so = StormOptions()
        
        #Check boxes for output variables
        self.netCDFLabel = Label(self.root, text='netCDF Options:')
        self.netCDFLabel.pack(anchor=W,padx = 2,pady = 2)
        
        for x in sorted(self.so.netCDF):
            self.so.netCDF[x] = BooleanVar()
            button = Checkbutton(root, text=x, variable=self.so.netCDF[x])
            button.pack(anchor=W,padx = 15,pady = 2)
        
        self.csvLabel = Label(self.root, text='CSV Options:')
        self.csvLabel.pack(anchor=W,padx = 2,pady = 2)
        
        for x in sorted(self.so.csv):
            self.so.csv[x] = BooleanVar()
            button = Checkbutton(root, text=x, variable=self.so.csv[x])
            button.pack(anchor=W,padx = 15,pady = 2)
            
        self.graphLabel = Label(self.root, text='Graph Options:')
        self.graphLabel.pack(anchor=W,padx = 2,pady = 2)
        
        for x in sorted(self.so.graph):
            self.so.graph[x] = BooleanVar()
            button = Checkbutton(root, text=x, variable=self.so.graph[x])
            button.pack(anchor=W,padx = 15,pady = 2)
        
        self.TzLabel = Label(self.root, text='Time zone to display dates in:')
        self.TzLabel.pack(anchor=W,padx = 2,pady = 2)
        
        options=('GMT',
                'US/Aleutian',
                'US/Central',
                'US/Eastern',
                'US/Hawaii',
                'US/Mountain',
                'US/Pacific')
        self.tzstringvar = StringVar()
        self.tzstringvar.set(options[0])

        self.datePickFrame = Frame(self.root)
        
        OptionMenu(self.datePickFrame, self.tzstringvar, *options).pack(side=LEFT, pady=2, padx=15)
        self.daylightSavings = BooleanVar()
        Checkbutton(self.datePickFrame, text="Daylight Savings", variable=self.daylightSavings).pack(side=RIGHT)
        self.datePickFrame.pack(anchor=W)
        
        self.emptyLabel4 = Label(self.root, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W,padx = 15,pady = 0)
        
        #variables and text boxes for air pressure limits
        self.BaroPickLabel = Label(self.root, text='Barometric Pressure Y Axis Limits: (optional)')
        self.BaroPickLabel.pack(anchor=W,padx = 15,pady = 0)
        
        self.baroPickFrame = Frame(self.root)
        self.bLowerLabel = Label(self.baroPickFrame, text="lower:").pack(side=LEFT, pady=10, padx=2)
        self.baroYlim1 = Entry(self.baroPickFrame, width=5)
        self.baroYlim1.pack(side=LEFT, pady=2, padx=15)
        self.baroYlim2 = Entry(self.baroPickFrame, width=5)
        self.baroYlim2.pack(side=RIGHT, pady=2, padx=15)
        self.bUpperLabel = Label(self.baroPickFrame, text="upper:").pack(side=RIGHT, pady=10, padx=2)
        self.baroPickFrame.pack(anchor=W, padx = 15)
        
        #tkinter spacing
        self.emptyLabel4 = Label(self.root, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W,padx = 15,pady = 0)
        
        #variables and textboxes for water level limits
        self.WaterLevelLabel = Label(self.root, text='Water Level Y Axis Limits: (optional)')
        self.WaterLevelLabel.pack(anchor=W,padx = 15,pady = 0)
        
        self.wlPickFrame = Frame(self.root)
        self.wlLowerLabel = Label(self.wlPickFrame, text="lower:").pack(side=LEFT, pady=10, padx=2)
        self.wlYlim1 = Entry(self.wlPickFrame, width=5)
        self.wlYlim1.pack(side=LEFT, pady=2, padx=15)
        self.wlYlim2 = Entry(self.wlPickFrame, width=5)
        self.wlYlim2.pack(side=RIGHT, pady=2, padx=15)
        self.wlUpperLabel = Label(self.wlPickFrame, text="upper:").pack(side=RIGHT, pady=10, padx=2)
        self.wlPickFrame.pack(anchor=W, padx = 15)
        
        self.b3 = self.make_button(root, "Process Files", c3,
                                   state=DISABLED)
        
        self.b3.pack(anchor=W, fill=BOTH)
    

    def select_file(self, varname, stringvar):
        fname = filedialog.askopenfilename()
        if fname != '':
            stringvar.set(fname)
            setattr(self, varname, fname)
            if(self.air_fname != ''):
                self.b3['state'] = 'ENABLED'
        self.root.focus_force()

    def make_button(self, root, text, command, state=None):
        '''Creates a new button'''
        b = ttk.Button(root, text=text, command=command, state=state,
                       width=10)
        return b

    def make_fileselect(self, root, labeltext, stringvar, varname):
        '''Creates a file selection menu'''
        command = lambda: self.select_file(varname, stringvar)
        frame = make_frame(root)
        l = ttk.Label(frame, justify=LEFT, text=labeltext, width=10)
        l.grid(row=0, column=0, sticky=W)
        b = self.make_button(frame, 'Browse', command)
        b.grid(row=0, column=2, sticky=W)
        e = ttk.Label(frame, textvariable=stringvar, justify=LEFT,
                      width=32)
        e.grid(row=0, column=1, sticky=(W, E))
        frame.pack(anchor=W, fill=BOTH)

    def select_output_file(self, root):
        '''Processes the selected afiles and outputs in format selected'''
        
        #Format the name properly based on the input of the user
        if self.sea_fname is None or self.sea_fname == '':
            if self.so.air_check_selected() == True:
                message = ("Please upload a water netCDF file or uncheck options that require it")
                gc.MessageDialog(root, message=message, title='Error!')
                return
            
        if self.so.check_selected() == False:
            message = ("Please select at least one option")
            gc.MessageDialog(root, message=message, title='Error!')
            return
        
        self.so.clear_data()
        og_fname = filedialog.asksaveasfilename()
        
        if og_fname is None or og_fname == '':
            self.root.focus_force()
            return
        
        try:
            self.so.air_fname = self.air_fname
            self.so.sea_fname = self.sea_fname
            self.so.wind_fname = self.wind_fname
            self.so.format_output_fname(og_fname)
            self.so.timezone = self.tzstringvar.get()
            self.so.daylight_savings = self.daylightSavings.get()
            
            self.so.baroYLims = []
            try:
                self.so.baroYLims.append(float(self.baroYlim1.get()))
                self.so.baroYLims.append(float(self.baroYlim2.get()))
            except:
                self.so.baroYLims = None
                
            self.so.wlYLims = []
            try:
                self.so.wlYLims.append(float(self.wlYlim1.get()))
                self.so.wlYLims.append(float(self.wlYlim2.get()))
            except:
                self.so.wlYLims = None
            
            if self.sea_fname != None and self.sea_fname != '':
                
                overlap = self.so.time_comparison()
                    
                if overlap == 2:
                    message = ("Air pressure and water pressure files don't "
                               "cover the same time period!\nPlease choose "
                               "other files.")
                    gc.MessageDialog(root, message=message, title='Error!')
                    return
                elif overlap == 1:
                    message = ("The air pressure file doesn't span the "
                    "entire time period covered by the water pressure "
                    "file.\nThe period not covered by both files will be "
                    "chopped")
                    gc.MessageDialog(root, message=message, title='Warning')
                
            
            snc = Storm_netCDF()
            snc.process_netCDFs(self.so)
            
            scv = StormCSV()
            scv.process_csv(self.so)
            
            sg = StormGraph()
            sg.process_graphs(self.so) 
            
            gc.MessageDialog(root, message="Success! Files processed.",
                                     title='Success!')
                
        except:
#             exc_type, exc_value, exc_traceback = sys.exc_info()
    
#             message = traceback.format_exception(exc_type, exc_value,
#                                           exc_traceback)
            message = 'Could not process files, please check file type.'
            gc.MessageDialog(root, message=message,
                             title='Error')

def make_frame(frame, header=None):
    """Make a frame with uniform padding."""
    return ttk.Frame(frame, padding="3 3 5 5")

 
if __name__ == '__main__':
    root = Tk()
    gui = StormGui(root)
    root.mainloop()
