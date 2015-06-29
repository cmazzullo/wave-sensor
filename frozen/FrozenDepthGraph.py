#!/usr/bin/env python3
import scipy
from scipy.integrate.lsoda import *
import scipy.integrate.vode
import scipy.special._ufuncs_cxx
import scipy.sparse.csgraph._validation
from scipy.integrate import *

import tkinter as Tk
from tkinter import filedialog
from tkinter import ttk
from tkinter.constants import W

import tools.depth_grapher
from tools.depth_grapher import make_depth_graph



class DepthGui:
    def __init__(self, root):
       
        self.in_file_name = ''
        self.root = root
        self.root.title('Water Level vs. Pressure Grapher')
        self.Label = Tk.Label(self.root, text='Averaged Points:')
        self.Label.pack(anchor=W,padx = 15,pady = 2)
        self.AveragedPoints = Tk.Entry(self.root)
        self.AveragedPoints.pack(anchor=W,padx = 15,pady = 2)
        self.b1 = Tk.Button(self.root, text='Select File', command=self.select_input)
        self.b1.pack(anchor=W,padx = 15,pady = 2)
        
    def select_input(self):
        self.in_file_name = filedialog.askopenfilename()
        make_depth_graph(int(self.AveragedPoints.get()), self.in_file_name)

class Variable:
    """
    Stores data about each attribute to be added to the netCDF file.

    Also contains metadata that allows the GUI to build widgets from
    the Variable and use the data inside it in the csv-to-netCDF
    converters.
    """
    def __init__(self, name_in_device=None, label=None, doc=None,
                 options=None, filename=False, autosave=False,
                 in_air_pressure=True, in_water_pressure=True):
        self.name_in_device = name_in_device
        self.label = label
        self.doc = doc
        self.options = options
        self.stringvar = Tk.StringVar()
        self.stringvar.set('')
        self.filename = filename
        self.autosave = autosave
        self.in_air_pressure = in_air_pressure
        self.in_water_pressure = in_water_pressure
        
root = Tk.Tk()
gui = DepthGui(root)
root.mainloop()