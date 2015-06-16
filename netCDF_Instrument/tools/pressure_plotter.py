#!/usr/bin/env python3
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from NetCDF_Utils import nc
import tools.script1_gui as gc


def plot_variable(fname, varname):
    t = nc.get_time(fname) / 1000
    p = nc.get_variable_data(fname, varname)
    # qc = nc.get_flags(fname)
    # bad_points = p[np.where(qc != 11110111)]
    # bad_times = t[np.where(qc != 11110111)]
    plt.plot(t, p)
    # plt.plot(bad_times, bad_points, 'rx', label='Bad data')
    plt.xlabel('Time (s)')
    plt.ylabel('Pressure (dBar)')
    # plt.legend()
    plt.title('Water Pressure with Bad Data Marked')
    plt.show()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("in_filename",
                        help="a netCDF file")
    parser.add_argument("-p",
                        help="plot pressure",
                        dest='varname',
                        const='sea_water_pressure',
                        default='sea_water_pressure',
                        action='store_const')
    parser.add_argument("-d",
                        help="plot depth",
                        dest='varname',
                        const='depth',
                        default='sea_water_pressure',
                        action='store_const')
    args = parser.parse_args()
    print(args)
    plot_variable(args.in_filename, args.varname)
