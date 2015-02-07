"""This needs to read in a netCDF file containing pressure and get the
water depth using fft and hydrostatic methods"""

from pressure_to_depth import combo_method, hydrostatic_method
from tests.pressure_to_depth_tests import random_waves

import numpy as np
from tkinter import *

### stuff to make cx_freeze work
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.backends.backend_qt4agg, matplotlib.backends.backend_tkagg
### end

import matplotlib.pyplot as plt


# This stuff will be useful when we get proper .nc test files full of
# known waves
# from NetCDF_Utils.make_default import make_default_netcdf
# f = '/home/chris/testfile.nc'
# t = trim_to_even(nc.get_time(f))
# timestep = t[1] - t[0]
# p = trim_to_even(nc.get_pressure(f))
# H = nc.get_water_depth(f)
# z = nc.get_device_depth(f)

def plot_depth(length, h, z, n_waves, max_f, max_a):
    time, y, pressure = random_waves(length, 4, h, z, max_f, max_a, n_waves)
    combo_y = combo_method(time, pressure/1e4, z, np.ones_like(time)*h, time[1] - time[0])
    static_y = hydrostatic_method(pressure/1e4)

    plt.clf()
    plt.plot(time, y, label='Real y')
    plt.plot(time, combo_y, label='FFT y')
    plt.plot(time, static_y, label='Hydrostatic y')
    plt.xlabel('Time (ms)')
    plt.ylabel('Wave Height (m)')
    plt.legend()
    plt.show()

fields = 'Time series length (s)', 'Water depth (m)', 'Device depth (m)', 'Number of waves to generate', 'Max frequency of random waves (Hz)', 'Max amplitude of random waves (m)'


def fetch(entries):
    inputs = [entry[1].get() for entry in entries]
    length = int(inputs[0])
    h = float(inputs[1])
    z = -float(inputs[2])
    n_waves = int(inputs[3])
    max_f = float(inputs[4])
    max_a = float(inputs[5])
    plot_depth(length, h, z, n_waves, max_f, max_a)

def makeform(root, fields):
   entries = []
   for field in fields:
      row = Frame(root)
      lab = Label(row, width=30, text=field, anchor='w')
      ent = Entry(row)
      row.pack(side=TOP, fill=X, padx=5, pady=5)
      lab.pack(side=LEFT)
      ent.pack(side=RIGHT, expand=YES, fill=X)
      entries.append((field, ent))
   return entries


def set_defaults(entries):
    entries[0][1].insert(0, '100')
    entries[1][1].insert(0, '10.5')
    entries[2][1].insert(0, '10.1')
    entries[3][1].insert(0, '10')
    entries[4][1].insert(0, '.5')
    entries[5][1].insert(0, '1.2')


if __name__ == '__main__':
   root = Tk()
   ents = makeform(root, fields)
   set_defaults(ents)
   root.bind('<Return>', (lambda event, e=ents: fetch(e)))
   b1 = Button(root, text='Show',
          command=(lambda e=ents: fetch(e)))
   b1.pack(side=LEFT, padx=5, pady=5)
   b2 = Button(root, text='Quit', command=root.destroy)
   b2.pack(side=LEFT, padx=5, pady=5)
   root.title('Compare Depth Calculation Methods')

   root.mainloop()
