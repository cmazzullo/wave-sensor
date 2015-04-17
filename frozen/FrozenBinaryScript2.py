import tkinter
from tkinter import ttk
from pytz import timezone
import os
import numpy as np

import shutil
from numpy import arange

from datetime import datetime, timedelta
import netCDF4
import netCDF4_utils
import netcdftime
import pytz

from scipy.optimize import newton
import scipy.sparse.csgraph._validation
import scipy.special._ufuncs_cxx

# Constants
g = 9.8  # gravity (m / s**2)
rho = 1030  # density of seawater (kg / m**3)
min_coeff = 1/15
FILL_VALUE = -1e10


            
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



class Script2gui:
    def __init__(self, root):
        root.title('Pressure -> Water Height')

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
        self.air_var.set('File containing air pressure (optional)...')
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
            if self.sea_fname:
                self.b3['state'] = 'ENABLED'

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
        sea_t = get_time(self.sea_fname)
        if self.air_fname != '':
            air_t = get_time(self.air_fname)
            if (air_t[-1] < sea_t[0]) or (air_t[0] > sea_t[-1]):
                message = ("Air pressure and water pressure files don't "
                           "cover the same time period!\nPlease choose "
                           "other files.")
                MessageDialog(root, message=message, title='Error!')
                return
            elif (air_t[0] > sea_t[0] or air_t[-1] < sea_t[-1]):
                message = ("The air pressure file doesn't span the "
                "entire time period covered by the water pressure "
                "file.\nThe period not covered by both files will be "
                "set to the fill value:%d" % FILL_VALUE)
                MessageDialog(root, message=message, title='Warning')

        make_depth_file(self.sea_fname, self.air_fname,
                                output_fname, method=method)
        MessageDialog(root, message="Success! Files saved.",
                         title='Success!')


if __name__ == '__main__':
    root = Tk()
    g2 = Script2gui(root)
    root.mainloop()
