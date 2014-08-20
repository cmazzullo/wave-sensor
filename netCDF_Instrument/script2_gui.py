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

import SpectralAnalysis.nc as nc
import script2
import Instruments.guicore as gc


class Script2gui:
    def __init__(self, root):
        methods = [('Naive', 'naive'),
                   ('Linear Wave', 'fft'),
                   ('Delft Paper', 'method2')]
        self.v = StringVar()

        ttk.Label(root, text='Depth calculation:').pack(anchor=W)
        for name, kwarg in methods:
            Radiobutton(root, text=name, variable=self.v,
                            value=kwarg).pack(anchor=W)
        self.v.set('naive')
        self.sea_fname = None
        self.sea_var = StringVar()
        self.air_fname = None
        self.air_var = StringVar()
        self.make_fileselect(root, "Open Water Pressure File",
                             self.sea_var, 'sea_fname')
        self.make_fileselect(root, "Open Air Pressure File",
                             self.air_var, 'air_fname')
        c3 = lambda: self.select_output_file(root)
        self.b3 = self.make_button(root, "Export to File", c3,
                                   state=DISABLED)
        self.b3.pack(anchor=W, fill=BOTH)


    def select_file(self, varname, stringvar):
        fname = filedialog.askopenfilename()
        stringvar.set(fname)
        setattr(self, varname, fname)
        if self.sea_fname and self.air_fname:
            self.b3['state'] = 'ENABLED'

    def make_button(self, root, text, command, state=None):
        b = ttk.Button(root, text=text, command=command, state=state)
        return b

    def make_fileselect(self, root, buttontext, stringvar, varname):
        command = lambda: self.select_file(varname, stringvar)
        frame = gc.make_frame(root)
        b = self.make_button(frame, buttontext, command)
        b.grid(row=0, column=0, sticky=W)
        l = ttk.Label(frame, textvariable=stringvar, justify=RIGHT)
        l.grid(row=0, column=1, sticky=W)
        frame.pack(anchor=W, fill=BOTH)

    def select_output_file(self, root):
        output_fname = filedialog.asksaveasfilename()
        m = self.v.get()
        sea_t = nc.get_time(self.sea_fname)
        air_t = nc.get_time(self.air_fname)
        air_t[0] = 1; sea_t[0] = 0
        if (air_t[-1] < sea_t[0]) or (air_t[0] > sea_t[-1]):
            message = ("Air pressure and water pressure files don't "
                       "cover the same time period!\nPlease choose "
                       "other files.")
            gc.MessageDialog(root, message=message, title='Error!')
        elif (air_t[0] > sea_t[0] or air_t[-1] < sea_t[-1]):
            message = ("The air pressure file doesn't span the "
            "entire time period covered by the water pressure "
            "file.\nThe period not covered by both files will be "
            "set to the fill value:%d" % nc.fill_value)
            gc.MessageDialog(root, message=message, title='Warning')
        else:
            script2.make_depth_file(self.sea_fname, self.air_fname,
                                    output_fname, method=m)
        root.destroy()


if __name__ == '__main__':
    root = Tk()
    g = Script2gui(root)
    root.mainloop()
