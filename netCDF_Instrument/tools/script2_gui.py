#!/usr/bin/env python3
"""
Created on Thu Aug  7 2014

@author: cmazzullo

A frontend for script2, which takes one water pressure and one air
pressure file and outputs a file containing water pressure, air
pressure and depth.
"""

from tkinter import *
from tkinter import filedialog
from tkinter import ttk

import NetCDF_Utils.nc as nc
import tools.script2 as script2
import tools.script1_gui as gc


class Script2gui:
    def __init__(self, root):
        self.root = root
        root.title('Water Level GUI (Pressure -> Water Level)')
        self.root.focus_force()
        methods = [('Hydrostatic', 'naive'),
                   ('Linear Wave', 'combo')]

        self.methodvar = StringVar()
        self.methodvar.set('combo')

        ttk.Label(root, text='Depth calculation:').pack(anchor=W)
        for name, kwarg in methods:
            ttk.Radiobutton(root, text=name, variable=self.methodvar,
                            value=kwarg).pack(anchor=W)

        self.sea_fname = None
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
        self.b3 = self.make_button(root, "Export to File", c3,
                                   state=DISABLED)
        self.b3.pack(anchor=W, fill=BOTH)


    def select_file(self, varname, stringvar):
        fname = filedialog.askopenfilename()
        if fname != '':
            stringvar.set(fname)
            setattr(self, varname, fname)
            if self.sea_fname and self.air_fname:
                self.b3['state'] = 'ENABLED'
        self.root.focus_force()

    def make_button(self, root, text, command, state=None):
        b = ttk.Button(root, text=text, command=command, state=state,
                       width=10)
        return b

    def make_fileselect(self, root, labeltext, stringvar, varname):
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
        output_fname = filedialog.asksaveasfilename()
        method = self.methodvar.get()
        
#         try:
        sea_t = nc.get_time(self.sea_fname)
        print('self.air_fname = ', self.air_fname)
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
                "set to the fill value:%d" % nc.FILL_VALUE)
                gc.MessageDialog(root, message=message, title='Warning')

        #check to see if time coverage resolution is small enough to perform combo
        timestep = 1 / nc.get_frequency(self.sea_fname)
        print(method, timestep)
        if method =="combo" and timestep > .5:
            method = "naive"
            message = "Time resolution too large to run Linear Wave method.  Will run hydrostatic..."
            gc.MessageDialog(root, message=message,
                         title='Success!')
         
        print(method)   
        script2.make_depth_file(self.sea_fname, self.air_fname,
                                output_fname, method=method)
        gc.MessageDialog(root, message="Success! Files saved.",
                         title='Success!')
#         except:
#             gc.MessageDialog(root, message="Could not process file/s, please check file type.",
#                              title='Error')

def make_frame(frame, header=None):
    """Make a frame with uniform padding."""
    return ttk.Frame(frame, padding="3 3 5 5")

if __name__ == '__main__':
    root = Tk()
    g = Script2gui(root)
    root.mainloop()
