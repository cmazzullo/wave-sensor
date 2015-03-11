#!/usr/bin/env python3
from numpy import sin, cos, pi, array
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import tkinter as Tk
from tkinter import filedialog

from NetCDF_Utils import nc
from netCDF4 import Dataset
from NetCDF_Utils.nc import chop_netcdf


root = Tk.Tk()
fname = filedialog.askopenfilename(parent=root)

## get data from nc file
t = nc.get_time(fname) / 1000
p = nc.get_pressure(fname)
qc = nc.get_flags(fname)

## make plot
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title('Chop Pressure File')
line = plt.plot(t, p, color='blue')
plt.xlabel('Time (s)')
plt.ylabel('Pressure (dBar)')
for i, flag in enumerate(qc):
    if flag != 1111:
        plt.axvspan(t[i], t[i+1], alpha=0.5, color='red', linewidth=0)

x1 = t[0]
x2 = t[-1]

left = ax.axvline(x1, color='black')
right = ax.axvline(x2, color='black')
patch = ax.axvspan(x1, x2, alpha=0.5, color='yellow', linewidth=0)

## process clicks
def find_index(array, value):
    return (np.abs(array - value)).argmin()
events = []
def on_click(event):
    events.append(event)
    if event.button == 1:
        l = left
    elif event.button == 3:
        l = right
    l.set_xdata([event.xdata, event.xdata])
    l.figure.canvas.draw()
    x1 = left.get_xdata()[0]
    x2 = right.get_xdata()[0]
    xy = [[x1, 0], [x1, 1], [x2, 1], [x2, 0], [x1, 0]]
    patch.set_xy(xy)
    patch.figure.canvas.draw()

canvas = FigureCanvasTkAgg(fig, master=root)
cid_up = canvas.mpl_connect('button_press_event', on_click)
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
canvas.show()
toolbar = NavigationToolbar2TkAgg( canvas, root )
toolbar.update()
canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

def export():
    i1 = find_index(t, left.get_xdata()[0])
    i2 = find_index(t, right.get_xdata()[0])
    print(i1, i2)
    chop_netcdf(fname, 'output.nc', i1, i2)

b = Tk.Button(root, text='Export Selection', command=export)
b.pack()
