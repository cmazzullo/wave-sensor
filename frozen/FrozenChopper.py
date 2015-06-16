#!/usr/bin/env python3
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from matplotlib.backends import backend_qt4agg

import tkinter as Tk
from tkinter import filedialog

import pytz
import netCDF4
import netCDF4_utils
import netcdftime
from netCDF4 import Dataset
from dateutil import parser
from datetime import datetime
from pytz import timezone

def find_index(array, value):
    return (np.abs(array - value)).argmin()

class Chopper:
    def __init__(self, root):
        self.fname = ''
        self.root = root
        self.b1 = Tk.Button(self.root, text='Select File', command=self.select_input)
        self.b1.pack()

    def plot_pressure(self):
        self.t = t = get_time(self.fname) / 1000
        p = get_pressure(self.fname)
        qc = get_flags(self.fname)
        self.fig = fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title('Chop Pressure File')
        line = plt.plot(t, p, color='blue')
        plt.xlabel('Time (s)')
        plt.ylabel('Pressure (dBar)')
        bad_points = p[np.where(qc != 11110111)]
        bad_times = t[np.where(qc != 11110111)]
        plt.plot(bad_times, bad_points, 'rx')
        x1 = t[0]
        x2 = t[-1]
        self.left = ax.axvline(x1, color='black')
        self.right = ax.axvline(x2, color='black')
        patch = ax.axvspan(x1, x2, alpha=0.25, color='yellow', linewidth=0)
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

        def resizing(event):
            print('resizing')
        self.canvas = canvas = self.fig.canvas
        cid_up = canvas.mpl_connect('button_press_event', on_click)
        # canvas.show()
        # fig.show()
        # plt.show(block=False)
        plt.draw()
        Tk.Label(text='Start date (MM/DD/YY HH:MM):').pack()
        self.date1 = Tk.StringVar()
        Tk.Entry(width=30, textvariable=self.date1).pack()
        Tk.Label(text='End date (MM/DD/YY HH:MM):').pack()
        self.date2 = Tk.StringVar()
        Tk.Entry(width=30, textvariable=self.date2).pack()
        options=("US/Central", "US/Eastern")
        self.tzstringvar = Tk.StringVar()
        self.tzstringvar.set(options[0])
        Tk.OptionMenu(self.root, self.tzstringvar, *options).pack()
        b = Tk.Button(self.root, text='Export Selection', command=self.export)
        b.pack()
        plt.show()


    def export(self):
        date1 = self.date1.get()
        date2 = self.date2.get()
        out_fname = filedialog.asksaveasfilename()
        if out_fname == '':
            return
        if date1 != '' and date2 != '':
            tz = timezone(self.tzstringvar.get())
            d1 = parser.parse(date1).replace(tzinfo=tz)
            d2 = parser.parse(date2).replace(tzinfo=tz)
            t1 = convert_date_to_milliseconds('', '', d1)
            t2 = convert_date_to_milliseconds('', '', d2)
            i1 = find_index(self.t, t1)
            i2 = find_index(self.t, t2)
        else:
            points = (self.left.get_xdata()[0], self.right.get_xdata()[0])
            lpoint = min(points)
            rpoint = max(points)
            i1 = find_index(self.t, lpoint)
            i2 = find_index(self.t, rpoint)
        print('self.fname = ', self.fname)
        chop_netcdf(self.fname, out_fname, i1, i2)
        plt.close('all')
        self.root.quit()
        self.root.destroy()

    def select_input(self):
        self.fname = filedialog.askopenfilename()
        self.b1.destroy()
        self.plot_pressure()
        
"""
A few convenience methods for quickly extracting/changing data in
netCDFs
"""
import numpy as np
import os
from datetime import datetime
from netCDF4 import Dataset
import netCDF4_utils, netcdftime # these make cx_freeze work
import pytz
from bitarray import bitarray as bit
# Constant

FILL_VALUE = -1e10

# Utility methods

def chop_netcdf(fname, out_fname, begin, end):
    """Truncate the data in a netCDF file between two indices"""
    if os.path.exists(out_fname):
        os.remove(out_fname)
    length = end - begin
    p = get_pressure(fname)[begin:end]
    t = get_time(fname)[begin:end]
    flags = get_flags(fname)[begin:end]
    alt = get_variable_data(fname, 'altitude')
    lat = get_variable_data(fname, 'latitude')
    long = get_variable_data(fname, 'longitude')
    d = Dataset(fname)
    output = Dataset(out_fname, 'w', format='NETCDF4_CLASSIC')
    output.createDimension('time', length)
    # copy globals
    for att in d.ncattrs():
        setattr(output, att, d.__dict__[att])
    # copy variables
    for key in d.variables:
        name = key
        # datatype = d.variables[key].datatype
        datatype = np.dtype('float64')
        dim = d.variables[key].dimensions
        var = output.createVariable(name, datatype, dim, fill_value=FILL_VALUE)
        for att in d.variables[key].ncattrs():
            if att != '_FillValue':
                setattr(var, att, d.variables[key].__dict__[att])
    output.variables['time'][:] = t
    output.variables['sea_water_pressure'][:] = p
    output.variables['pressure_qc'][:] = flags
    output.variables['altitude'][:] = alt
    output.variables['longitude'][:] = long
    output.variables['latitude'][:] = lat
    d.close()
    output.close()

def parse_time(fname, time_name):
    """Convert a UTC offset in attribute "time_name" to a datetime."""
    timezone_str = get_global_attribute(fname, 'time_zone')
    timezone = pytz.timezone(timezone_str)
    time_str = get_global_attribute(fname, time_name)
    fmt = '%Y%m%d %H%M'
    time = timezone.localize(datetime.strptime(time_str, fmt))
    epoch_start = datetime(year=1970, month=1, day=1, tzinfo=pytz.utc)
    time_ms = (time - epoch_start).total_seconds() * 1000
    return time_ms

# Append new variables

def append_air_pressure(fname, pressure):
    """Insert air pressure array into the netCDF file fname"""
    name = 'air_pressure'
    long_name = 'air pressure record'
    append_variable(fname, name, pressure, comment='',
                     long_name=long_name)


def append_depth(fname, depth):
    """Insert depth array into the netCDF file at fname"""
    comment = ('The depth, computed using the variable "corrected '
               'water pressure".')
    name = 'depth'
    print('len(depth) = ' + str(len(depth)))
    append_variable(fname, name, depth, comment=comment,
                     long_name=name)

def append_depth_qc(fname, sea_qc, air_qc):
    """Insert depth qc array"""
    depth_name = 'depth_qc'
    air_name = "air_qc"
    air_comment = 'The air_qc is a binary and of the (sea)pressure_qc and air_pressure_qc if an air file is used to calculate depth'
    depth_comment = 'The depth_qc is a binary and of the (sea)pressure_qc and air_pressure_qc'
    flag_masks = '11111111 11111110 11111101 11111011 11110111'
    flag_meanings =  "no_bad_data last_five_vals_identical, outside_valid_range, invalid_rate_of_change, interpolated_data"

    if air_qc != None:
        air_qc = [bit(x) for x in air_qc]
        sea_qc = [bit(str(x)) for x in sea_qc]

        depth_qc = [(air_qc[x] & sea_qc[x]).to01() for x in range(0,len(sea_qc))]
        append_variable(fname, air_name, [x.to01() for x in air_qc], comment=air_comment, long_name=air_name,
                        flag_masks = flag_masks, flag_meanings= flag_meanings)
        append_variable(fname, depth_name, depth_qc, comment=depth_comment, long_name=depth_name,
                         flag_masks = flag_masks, flag_meanings= flag_meanings)
    else:
        append_variable(fname, depth_name, sea_qc, comment=depth_comment, long_name=depth_name,
                         flag_masks = flag_masks, flag_meanings= flag_meanings)


# Get variable data

def get_water_depth(in_fname):
    """Get the static water depth from the netCDF at fname"""
    initial_depth = get_initial_water_depth(in_fname)
    final_depth = get_final_water_depth(in_fname)
    initial_time = get_deployment_time(in_fname)
    final_time = get_retrieval_time(in_fname)
    time = get_time(in_fname)
    slope = (final_depth - initial_depth) / (final_time - initial_time)
    depth_approx = slope * (time - initial_time) + initial_depth
    return depth_approx


def get_depth(fname):
    """Get the wave height array from the netCDF at fname"""
    return get_variable_data(fname, 'depth')


def get_flags(fname):
    """Get the time array from the netCDF at fname"""
    return get_variable_data(fname, 'pressure_qc')

def get_time(fname):
    """Get the time array from the netCDF at fname"""
    return get_variable_data(fname, 'time')


def get_air_pressure(fname):
    """Get the air pressure array from the netCDF at fname"""
    return get_variable_data(fname, 'air_pressure')


def get_pressure(fname):
    """Get the water pressure array from the netCDF at fname"""
    return get_variable_data(fname, 'sea_water_pressure')

def get_pressure_qc(fname):
    return get_variable_data(fname, 'pressure_qc')

# Get global data

def get_frequency(fname):
    """Get the frequency of the data in the netCDF at fname"""
    freq_string = get_global_attribute(fname, 'time_coverage_resolution')
    return 1 / float(freq_string[1:-1])


def get_initial_water_depth(fname):
    """Get the initial water depth from the netCDF at fname"""
    return get_global_attribute(fname, 'initial_water_depth')


def get_final_water_depth(fname):
    """Get the final water depth from the netCDF at fname"""
    return get_global_attribute(fname, 'final_water_depth')


def get_deployment_time(fname):
    """Get the deployment time from the netCDF at fname"""
    return parse_time(fname, 'deployment_time')


def get_retrieval_time(fname):
    """Get the retrieval time from the netCDF at fname"""
    return parse_time(fname, 'retrieval_time')


def get_device_depth(fname):
    """Get the retrieval time from the netCDF at fname"""
    return get_global_attribute(fname, 'device_depth')


def get_variable_data(fname, variable_name):
    """Get the values of a variable from a netCDF file."""
    with Dataset(fname) as nc_file:
        var = nc_file.variables[variable_name]
        var_data = var[:]
        return var_data

# Backend

def get_global_attribute(fname, name):
    """Get the value of a global attibute from a netCDF file."""
    with Dataset(fname) as nc_file:
        attr = getattr(nc_file, name)
        return attr


def append_variable(fname, standard_name, data, comment='',
                     long_name='', flag_masks = None, flag_meanings = None):
    """Append a new variable to an existing netCDF."""
    with Dataset(fname, 'a', format='NETCDF4_CLASSIC') as nc_file:
        pvar = nc_file.createVariable(standard_name, 'f8', ('time',))
        pvar.ioos_category = ''
        pvar.comment = comment
        pvar.standard_name = standard_name
        pvar.max = 1000
        pvar.min = -1000
        pvar.short_name = standard_name
        pvar.ancillary_variables = ''
        pvar.add_offset = 0.0
        pvar.coordinates = 'time latitude longitude altitude'
        pvar.long_name = long_name
        pvar.scale_factor = 1.0
        if flag_masks != None:
            pvar.flags_masks = flag_masks
            pvar.flag_meanings = flag_meanings
        if standard_name == 'depth':
            pvar.units = 'meters'
            pvar.nodc_name = 'WATER DEPTH'
        else:
            pvar.units = 'decibars'
            pvar.nodc_name = 'PRESSURE'
        pvar.compression = 'not used at this time'
        pvar[:] = data

def ncdump(fname):
    """Dump all attributes and variables in a netCDF to stdout"""
    f = Dataset(fname)
    print('\nDimensions:\n')
    for dim in f.dimensions:
        print(dim, ':\t\t', len(f.dimensions[dim]))
    print('\n\nAttributes:\n\n')
    for att in f.__dict__:
        name = (att + ':').ljust(35)
        value = str(f.__dict__[att]).ljust(50)
        print(name, value)
    print('\n\nVariables:\n\n')
    for att in f.variables:
        name = (att + ':').ljust(35)
        value = str(f.variables[att]).ljust(50)
        print(name, value)
    f.close()
   
epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc) 
def convert_date_to_milliseconds(datestring, date_format_string, date_time = None):
        if date_time == None:
            first_date = pytz.utc.localize(datetime.strptime(datestring, date_format_string))
            return (first_date - epoch_start).total_seconds() * 1000
        else:
            #pandas index will not take a long so I cannot multiply by 1000
            first_date = date_time
            return (first_date - epoch_start).total_seconds()


root = Tk.Tk()
gui = Chopper(root)
root.mainloop()
