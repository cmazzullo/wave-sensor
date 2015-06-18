#!/usr/bin/env python3
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from NetCDF_Utils import nc
import tools.script1_gui as gc


def plot_variable(fname, varname, label):
    t = nc.get_time(fname) / 1000
    p = nc.get_variable_data(fname, varname)
    # qc = nc.get_flags(fname)
    # bad_points = p[np.where(qc != 11110111)]
    # bad_times = t[np.where(qc != 11110111)]
    plt.plot(t, p, label=label)
    plt.ylim(-10,20)
    # plt.plot(bad_times, bad_points, 'rx', label='Bad data')
    plt.xlabel('Time (s)')
    # plt.legend()
    plt.title('Water Pressure with Bad Data Marked')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("in_filename",
                        help="a netCDF file")
    parser.add_argument("--pressure", "-p",
                        help="plot pressure",
                        action='store_true')
    parser.add_argument("--depth", "-d",
                        help="plot depth",
                        action='store_true')
    args = parser.parse_args()
    if args.depth:
        plot_variable(args.in_filename, 'depth', label='Depth (m)')
    if args.pressure:
        plot_variable(args.in_filename, 'sea_water_pressure',
                      label='Pressure (dbar)')
    plt.legend()
    plt.show()
