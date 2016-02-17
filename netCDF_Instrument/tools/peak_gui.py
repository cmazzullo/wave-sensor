#!/usr/bin/env python3
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

import NetCDF_Utils.nc as nc
import tools.script2 as script2
import tools.script1_gui as gc
import os
from tools.depth_grapher import make_depth_graph
import unit_conversion
import pytz

class PeakGui:
    def __init__(self, root):
        
        #root and selection dialogs for sea and air netCDF files
        self.root = root
        root.title('Peak GUI')
        self.root.focus_force()
        
#        
        self.sea_fname = ''
        self.sea_var = StringVar()
        self.sea_var.set('File containing water pressure...')
        self.air_fname = ''
        self.air_var = StringVar()
        self.air_var.set('File containing air pressure...')
        self.make_fileselect(root, 'Water file:',
                             self.sea_var, 'sea_fname')
        self.make_fileselect(root, 'Air file:',
                             self.air_var, 'air_fname')
        c3 = lambda: self.select_output_file(root)
        
        
        #Frame for graph options (will hide unless graph output is selected)
        self.graphOptions = Frame(root)
        
        self.TzLabel = Label(self.root, text='Time zone to display date in:')
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
        
        #tkinter spacing
        self.emptyLabel4 = Label(self.graphOptions, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W,padx = 15,pady = 0)
        
        
        self.b3 = self.make_button(root, "Process Files", c3,
                                   state=DISABLED)
        
        self.b3.pack(anchor=W, fill=BOTH)
        
        self.justMax = True
    
    def hide_options(self, event, arb1, arb2):
        '''Checks whether the graph option is selected to show options and whether files and one
        output is selected to enable the process files button'''
        if (self.sea_fname != '' and self.air_fname != '') and (self.graphOutput.get() or self.csvOutput.get() or self.netOutput.get()):
            self.b3['state'] = 'ENABLED'
        else:
            self.b3.config(state=DISABLED)
            
        if self.graphOutput.get() == True:
            self.b3.pack_forget()
            self.graphOptions.pack(anchor=W, padx = 2)
            self.b3.pack(anchor=W, fill=BOTH)
        else:
            self.graphOptions.pack_forget()
    
    def button_state(self, event, arb1, arb2):
        '''Checks whether files and one output is selected to enable the process files button'''
        if (self.sea_fname != '' and self.air_fname != '') and (self.graphOutput.get() or self.csvOutput.get() or self.netOutput.get()):
            self.b3['state'] = 'ENABLED'
        else:
            self.b3.config(state=DISABLED)

    def select_file(self, varname, stringvar):
        fname = filedialog.askopenfilename()
        if fname != '':
            stringvar.set(fname)
            setattr(self, varname, fname)
            if not self.justMax:
                if(self.sea_fname != '' and self.air_fname != '') and (self.graphOutput.get() or self.csvOutput.get() or self.netOutput.get()):
                    self.b3['state'] = 'ENABLED'
            else:
                if(self.sea_fname != '' and self.air_fname != ''):
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
        
        try:
            #Format the name properly based on the input of the user
            sea_t = nc.get_time(self.sea_fname)
            if self.air_fname != '':
                air_t = nc.get_time(self.air_fname)
                if (air_t[-1] < sea_t[0]) or (air_t[0] > sea_t[-1]):
                    message = ("Air pressure and water pressure files don't "
                               "cover the same time period!\nPlease choose "
                               "other files.")
                    gc.MessageDialog(root, message=message, title='Error!')
                    return
                elif (air_t[0] > sea_t[0] or air_t[-1] < sea_t[-1]):
                    message = ("The air pressure file doesn't span the "
                    "entire time period covered by the water pressure "
                    "file.\nThe period not covered by both files will be "
                    "chopped")
                    gc.MessageDialog(root, message=message, title='Warning')
            
            #This creates the depth file/s for storage or use in the graph
                final_depth, final_date = script2.make_depth_file(self.sea_fname, self.air_fname,
                                    'arb', method='naive', purpose='get_max', \
                                    csv= False, step=1)
                
                final_depth = final_depth * unit_conversion.METER_TO_FEET
                
                formatted_date = unit_conversion.convert_ms_to_date(final_date, pytz.utc)
                formatted_date = unit_conversion.adjust_from_gmt([formatted_date], \
                                                                 self.tzstringvar.get(), self.daylightSavings.get())
                
                formatted_date = formatted_date[0].strftime('%m/%d/%y %H:%M:%S')
                
                message = 'The max water level in feet is: %.4f\n' \
                    'The time is: %s' % (final_depth, formatted_date)
                gc.MessageDialog(root, message=message, title='Success!')
        except:
          
                gc.MessageDialog(root, message="Could not process file/s, please check file type.",
                                 title='Error')

def make_frame(frame, header=None):
    """Make a frame with uniform padding."""
    return ttk.Frame(frame, padding="3 3 5 5")

 
if __name__ == '__main__':
    root = Tk()
    gui = PeakGui(root)
    root.mainloop()
