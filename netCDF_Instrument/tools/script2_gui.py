#!/usr/bin/env python3
"""
Created on Thu Aug  7 2014

@author: cmazzullo

A frontend for script2, which takes one water pressure and one air
pressure file and outputs a file containing water pressure, air
pressure and depth.
"""

import tkinter as tk
from tkinter import filedialog
import NetCDF_Utils.nc as nc
import tools.script2 as script2
import tools.script1_gui as gc

BUTTONWIDTH = 10

class Script2gui:
    """Add depth information to a NetCDF containing pressure."""
    def __init__(self, parent):
        """Make the radio buttons and file selection buttons."""
        parent.title('Pressure -> Water Height')
        methods = [('Hydrostatic', 'naive'),
                   ('Linear Wave', 'combo')]
        self.methodvar = tk.StringVar()
        self.methodvar.set('combo')
        tk.Label(parent, text='Depth calculation:').pack(anchor='w')
        for name, kwarg in methods:
            tk.Radiobutton(parent, text=name, variable=self.methodvar,
                           value=kwarg).pack(anchor='w')
        self.sea_fname = None
        self.sea_var = tk.StringVar()
        self.sea_var.set('File containing water pressure...')
        self.air_fname = ''
        self.air_var = tk.StringVar()
        self.air_var.set('File containing air pressure (optional)...')
        self.make_fileselect(parent, 'Water file:', self.sea_var,
                             'sea_fname').pack(anchor='w', fill='both')
        self.make_fileselect(parent, 'Air file:', self.air_var,
                             'air_fname').pack(anchor='w', fill='both')
        export_command = lambda: self.select_output_file(parent)
        self.export_button = tk.Button(parent, text="Export to File", command=export_command,
                                       state='disabled', width=BUTTONWIDTH)
        self.export_button.pack(anchor='w', fill='both')

    def select_file(self, varname, stringvar):
        """Prompt for an input file and activate the "Export" button."""
        fname = filedialog.askopenfilename()
        stringvar.set(fname)
        setattr(self, varname, fname)
        if self.sea_fname:
            self.export_button['state'] = 'active'

    def make_fileselect(self, parent, labeltext, stringvar, varname):
        """Make a widget with a button to select a file and labels."""
        command = lambda: self.select_file(varname, stringvar)
        frame = tk.Frame(parent)
        tk.Label(frame, justify='left', text=labeltext,
                 width=BUTTONWIDTH).grid(row=0, column=0, sticky='w')
        tk.Button(frame, text='Browse', command=command,
                  width=BUTTONWIDTH).grid(row=0, column=2, sticky='w')
        tk.Label(frame, textvariable=stringvar, justify='left',
                 width=32).grid(row=0, column=1, sticky=('w', 'e'))
        return frame

    def select_output_file(self, parent):
        """Select a file to export to and write depth data to it."""
        output_fname = filedialog.asksaveasfilename()
        method = self.methodvar.get()
        sea_t = nc.get_time(self.sea_fname)
        if self.air_fname:
            air_t = nc.get_time(self.air_fname)
            if (air_t[-1] < sea_t[0]) or (air_t[0] > sea_t[-1]):
                message = ("Air pressure and water pressure files don't "
                           "cover the same time period!\nPlease choose "
                           "other files.")
                gc.MessageDialog(parent, message=message, title='Error!')
                return
            elif air_t[0] > sea_t[0] or air_t[-1] < sea_t[-1]:
                message = ("The air pressure file doesn't span the "
                           "entire time period covered by the water pressure "
                           "file.\nThe period not covered by both files will be"
                           " set to the fill value:%d" % nc.FILL_VALUE)
                gc.MessageDialog(parent, message=message, title='Warning')
        timestep = 1 / nc.get_frequency(self.sea_fname)
        if method == "combo" and timestep > .5:
            method = "naive"
            message = ("Time resolution too small to run Linear Wave method. "
                       "Will run hydrostatic...")
            gc.MessageDialog(parent, message=message, title='Success!')
        script2.make_depth_file(self.sea_fname, self.air_fname,
                                output_fname, method=method)
        gc.MessageDialog(parent, message="Success! Files saved.",
                         title='Success!')


if __name__ == '__main__':
    root = tk.Tk()
    Script2gui(root)
    root.mainloop()
