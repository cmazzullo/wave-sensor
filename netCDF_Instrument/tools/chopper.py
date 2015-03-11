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

def find_index(array, value):
    return (np.abs(array - value)).argmin()

class Chopper:
    def __init__(self, root):
        self.fname = ''
        self.root = root
        self.b1 = Tk.Button(self.root, text='Select File', command=self.select_input)
        self.b1.pack()

    def plot_pressure(self):
        self.t = t = nc.get_time(self.fname) / 1000
        p = nc.get_pressure(self.fname)
        qc = nc.get_flags(self.fname)
        self.fig = fig = plt.figure()
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
        self.left = ax.axvline(x1, color='black')
        self.right = ax.axvline(x2, color='black')
        patch = ax.axvspan(x1, x2, alpha=0.5, color='yellow', linewidth=0)
        events = []

        def on_click(event):
            events.append(event)
            if event.button == 1:
                l = self.left
            elif event.button == 3:
                l = self.right
            l.set_xdata([event.xdata, event.xdata])
            l.figure.canvas.draw()
            x1 = self.left.get_xdata()[0]
            x2 = self.right.get_xdata()[0]
            xy = [[x1, 0], [x1, 1], [x2, 1], [x2, 0], [x1, 0]]
            patch.set_xy(xy)
            patch.figure.canvas.draw()

        self.canvas = canvas = FigureCanvasTkAgg(fig, master=self.root)
        cid_up = canvas.mpl_connect('button_press_event', on_click)
        canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        canvas.show()
        toolbar = NavigationToolbar2TkAgg( canvas, self.root )
        toolbar.update()
        canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        b = Tk.Button(self.root, text='Export Selection', command=self.export)
        b.pack()

    def export(self):
        out_fname = filedialog.asksaveasfilename()
        if out_fname != '':
            points = (self.left.get_xdata()[0], self.right.get_xdata()[0])
            lpoint = min(points)
            rpoint = max(points)
            i1 = find_index(self.t, lpoint)
            i2 = find_index(self.t, rpoint)
            print('self.fname = ', self.fname)
            chop_netcdf(self.fname, out_fname, i1, i2)
            #plt.close('all')
            self.root.quit()
            self.root.destroy()

    def select_input(self):
        self.fname = filedialog.askopenfilename()
        self.b1.destroy()
        self.plot_pressure()

root = Tk.Tk()
gui = Chopper(root)
root.mainloop()
# plt.close('all')
