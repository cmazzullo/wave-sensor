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


def hydrostatic_method(p):
    print(p, 1e4, rho, g)
    return (p *  1e4) / (rho * g)


def fft_method(t, p_dbar, z, H, timestep, gate=0, window=True,
                      cutoff=-1):
    """Takes an array of pressure readings and creates wave height data.

    t -- the time array
    p_dbar -- an array of pressure readings such that len(t) == len(p)
    z -- the depth of the sensor
    H -- the water depth (array)
    timestep -- the time interval in between pressure readings
    amp_cutoff -- any fluctuations in the pressure that are less than this
                  threshold won't be used in the height data.
    """
    print('Calculating depth...')
    # Put the pressure data into frequency space
    p = p_dbar * 1e4
    n = len(p)
    raw_gate_array = np.ones_like(p) * gate

    if window:
        window_func = np.hamming(n)
        scaled_p = p * window_func  # scale by a hamming window
        gate_array = raw_gate_array * window_func
    else:
        scaled_p = p
        gate_array = raw_gate_array

    amps = np.fft.rfft(scaled_p)
    freqs = np.fft.rfftfreq(n, d=timestep)
    new_amps = np.zeros_like(amps)

    for i in range(len(amps)):
        # Filter out the noise with amp_cutoff
        if np.absolute(amps[i] / n) >= gate_array[i]:
            if cutoff == -1 or freqs[i] < cutoff:
                k = omega_to_k(freqs[i] * 2 * np.pi, H[i])
                # Scale, applying the diffusion relation
                a = pressure_to_eta(amps[i], k, z, H[i])
                new_amps[i] = a
    # Convert back to time space
    eta = np.fft.irfft(new_amps)
    if window:
        eta = eta / window_func
    return eta


def _frequency_to_index(f, n, timestep):
    """Gets the index of a frequency in np.fftfreq.

    f -- the desired frequency
    n -- the length given to fftfreq
    sample_freq -- the sampling frequency
    """
    return np.round(n * f * timestep)


def omega_to_k(omega, H):
    """Gets the wave number from the angular frequency using the dispersion
    relation for water waves and Newton's method."""
    f = lambda k: omega**2 - k * g * np.tanh(k * H)
    return newton(f, 0)


def k_to_omega(k, H):
    """Takes the wave number and water depth as arguments, returns the
    angular frequency."""
    return np.sqrt(k * g * np.tanh(k * H))


def pressure_to_eta(del_p, k, z, H):
    """Converts the non-hydrostatic pressure to height above z=0."""
    c = _coefficient(k, z, H)
    return del_p / c


def eta_to_pressure(eta, k, z, H):
    c = _coefficient(k, z, H)
    return eta * c


def _coefficient(k, z, H):
    """Returns C, a coefficient to transform pressure to eta and vice versa."""
    return rho * g * np.cosh(k * (H + z)) / np.cosh(k * H)

def method2(p_dbar):
    """Downward crossing method: if the function crosses the x axis in
    an interval and if its endpoint is below the x axis, we've found
    a new wave."""
    p = p_dbar * 1e4            # convert to Pascals
    Pstatic = make_pstatic(p)
    Pwave = p - Pstatic
    depth = Pstatic / (rho * g)
    start = period = counter = Pmin = Pmax = 0
    periods = []  # periods of found waves
    eta = np.zeros(len(Pwave))
    interval = 1 / 4
    steepness = 0.03
    Hminimum = 0.10
    H = []

    for i in range(len(Pwave) - 1):
        if Pwave[i] > 0 and Pwave[i+1] < 0:
            periods.append(period)
            # w**2 = g * k, the dispersion relation for deep water
            wavelength = g * period**2 / (2 * np.pi)
            # if the water is too shallow
            if depth[i] / wavelength < 0.36:
                wavelength = ((g * depth[i])**(1/2) *
                              (1 - depth[i] / wavelength) *
                              period)
                height = (((Pmax - Pmin) / (rho * g)) *
                          np.cosh(2 * np.pi * depth[i] /
                                  wavelength))
            H.append(height)
            Hunreduced = Hreduced = height
            if height / wavelength > steepness:
                Hreduced = steepness * wavelength
                H.append(Hreduced)
            if height < Hminimum:
                H.pop()
                Hreduced = Hminimum
                counter -= 1
            if str(wavelength) == 'nan':
                H.pop()
            reduction = Hreduced / Hunreduced
            for j in range(start, i):
                eta[j] = ((Pwave[j] * reduction) / (rho * g)) * \
                         np.cosh(2 * np.pi * depth[j] / wavelength)
            start = i + 1
            period = Pmax = Pmin = 0
            counter += 1
        period = period + interval
        if Pwave[i] > Pmax:
            Pmax = Pwave[i]
        if Pwave[i] < Pmin:
            Pmin = Pwave[i]

    return eta + depth


def make_pstatic(p):
    x = np.arange(len(p))
    slope, intercept = np.polyfit(x, p, 1)
    pwave = slope * x + intercept
    return pwave

# Constant

fill_value = -1e10

# Utility methods

def parse_time(fname, time_name):
    """Convert a UTC offset in attribute "time_name" to a datetime."""
    tz = pytz.timezone(_get_global_attribute(fname, 'time_zone'))
    time_str = _get_global_attribute(fname, time_name)
    fmt = '%Y%m%d %H%M'
    time = tz.localize(datetime.strptime(time_str, fmt))
    epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
    time_ms = (time - epoch_start).total_seconds() * 1000
    return time_ms

# Append new variables

def append_air_pressure(fname, p):
    """Insert air pressure array p into the netCDF file fname"""
    name = 'air_pressure'
    long_name = 'air pressure record'
    _append_variable(fname, name, p, '', standard_name=name,
                    short_name=name, long_name=long_name)


def append_depth(fname, depth):
    """Insert depth array into the netCDF file at fname"""
    comment = ('The depth, computed using the variable "corrected '
               'water pressure".')
    name = 'depth'
    _append_variable(fname, name, depth, comment, standard_name=name,
                    short_name=name, long_name=name, depth=True)

# Get variable data

def get_water_depth(in_fname):
    """Get the static water depth from the netCDF at fname"""
    H0 = get_initial_water_depth(in_fname)
    Hf = get_final_water_depth(in_fname)
    t0 = get_deployment_time(in_fname)
    tf = get_retrieval_time(in_fname)
    time = get_time(in_fname)
    m = (Hf - H0) / (tf - t0)
    H = m * time + H0 - m * t0
    return H


def get_depth(fname):
    """Get the wave height array from the netCDF at fname"""
    return _get_variable_data(fname, 'depth')


def get_time(fname):
    """Get the time array from the netCDF at fname"""
    return _get_variable_data(fname, 'time')


def get_air_pressure(fname):
    """Get the air pressure array from the netCDF at fname"""
    return _get_variable_data(fname, 'air_pressure')


def get_pressure(fname):
    """Get the water pressure array from the netCDF at fname"""
    return _get_variable_data(fname, 'sea_water_pressure')

# Get global data

def get_frequency(fname):
    """Get the frequency of the data in the netCDF at fname"""
    freq_string = _get_global_attribute(fname, 'time_coverage_resolution')
    return float(freq_string[1:-1])


def get_initial_water_depth(fname):
    """Get the initial water depth from the netCDF at fname"""
    return _get_global_attribute(fname, 'initial_water_depth')


def get_final_water_depth(fname):
    """Get the final water depth from the netCDF at fname"""
    return _get_global_attribute(fname, 'final_water_depth')


def get_deployment_time(fname):
    """Get the deployment time from the netCDF at fname"""
    return parse_time(fname, 'deployment_time')


def get_retrieval_time(fname):
    """Get the retrieval time from the netCDF at fname"""
    return parse_time(fname, 'retrieval_time')



def get_device_depth(fname):
    """Get the retrieval time from the netCDF at fname"""
    return _get_global_attribute(fname, 'device_depth')


def _get_variable_data(fname, variable_name):
    """Get the values of a variable from a netCDF file."""
    nc = netCDF4.Dataset(fname)
    var = nc.variables[variable_name]
    v = var[:]
    nc.close()
    return v

# Private methods

def _get_global_attribute(fname, name):
    """Get the value of a global attibute from a netCDF file."""
    nc = netCDF4.Dataset(fname)
    attr = getattr(nc, name)
    nc.close()
    return attr


def _append_variable(fname, name, p, comment='', standard_name='',
                     short_name='', long_name='', depth=False):
    """Append a new variable to an existing netCDF."""
    nc = netCDF4.Dataset(fname, 'a', format='NETCDF4_CLASSIC')
    pvar = nc.createVariable(name, 'f8', ('time',))
    pvar.ioos_category = ''
    pvar.comment = comment
    pvar.standard_name = standard_name
    pvar.max = 1000
    pvar.min = -1000
    pvar.short_name = short_name
    pvar.ancillary_variables = ''
    pvar.add_offset = 0.0
    pvar.coordinates = 'time latitude longitude altitude'
    pvar.long_name = long_name
    pvar.scale_factor = 1.0
    if depth:
        units = 'meters'
        pvar.nodc_name = 'WATER DEPTH'
    else:
        units = 'decibars'
        pvar.nodc_name = 'PRESSURE'
    pvar.units = units
    pvar.compression = 'not used at this time'
    pvar[:] = p
    nc.close()

def make_depth_file(water_fname, air_fname, out_fname, method='fft'):
    device_depth = -1 * get_device_depth(water_fname)
    water_depth = get_water_depth(water_fname)
    timestep = 1 / get_frequency(water_fname)
    sea_pressure = get_pressure(water_fname)
    sea_time = get_time(water_fname)
    raw_air_pressure = get_air_pressure(air_fname)
    air_time = get_time(air_fname)

    air_pressure = np.interp(sea_time, air_time, raw_air_pressure,
                             left=fill_value, right=fill_value)
    corrected_pressure = sea_pressure - air_pressure

    if method == 'fft':
        depth = fft_method(sea_time, corrected_pressure,
                               device_depth, water_depth, timestep)
    elif method == 'method2':
        depth = method2(corrected_pressure)
    elif method == 'naive':
        depth = hydrostatic_method(corrected_pressure)
    else:
        raise TypeError('Accepted values for "method" are: fft, '
                        'method2 and naive.')
    shutil.copy(water_fname, out_fname)
    append_air_pressure(out_fname, air_pressure)
    append_depth(out_fname, depth)


def make_frame(frame, header=None):
    """Make a frame with uniform padding."""
    return ttk.Frame(frame, padding="3 3 5 5")

class MessageDialog(tkinter.Toplevel):
    """ A template for nice dialog boxes. """

    def __init__(self, parent, message="", title="", buttons=1,
                 wait=True):
        tkinter.Toplevel.__init__(self, parent)
        body = ttk.Frame(self)
        self.title(title)
        self.boolean = None
        self.parent = parent
        self.transient(parent)
        ttk.Label(body, text=message).pack()
        if buttons == 1:
            b = ttk.Button(body, text="OK", command=self.destroy)
            b.pack(pady=5)
        elif buttons == 2:
            buttonframe = make_frame(body)

            def event(boolean):
                self.boolean = boolean
                self.destroy()

            b1 = ttk.Button(buttonframe, text='YES',
                            command=lambda: event(True))
            b1.grid(row=0, column=0)
            b2 = ttk.Button(buttonframe, text='NO',
                            command=lambda: event(False))
            b2.grid(row=0, column=1)
            buttonframe.pack()

        body.pack()
        self.grab_set()
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        if wait:
            self.wait_window(self)
            
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
        methods = [('Naive', 'naive'),
                   ('Linear Wave', 'fft'),
                   ('Delft Paper', 'method2')]
        self.methodvar = StringVar()

        ttk.Label(root, text='Depth calculation:').pack(anchor=W)
        for name, kwarg in methods:
            Radiobutton(root, text=name, variable=self.methodvar,
                            value=kwarg).pack(anchor=W)
        self.methodvar.set('naive')
        self.sea_fname = None
        self.sea_var = StringVar()
        self.sea_var.set('File containing water pressure...')
        self.air_fname = None
        self.air_var = StringVar()
        self.air_var.set('File containing air pressure...')
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
        stringvar.set(fname)
        setattr(self, varname, fname)
        if self.sea_fname and self.air_fname:
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
        e = ttk.Entry(frame, textvariable=stringvar, justify=LEFT,
                      width=32)
        e.grid(row=0, column=1, sticky=(W, E))
        frame.pack(anchor=W, fill=BOTH)

    def select_output_file(self, root):
        output_fname = filedialog.asksaveasfilename()
        method = self.methodvar.get()
        sea_t = get_time(self.sea_fname)
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
            "set to the fill value:%d" % fill_value)
            MessageDialog(root, message=message, title='Warning')
        make_depth_file(self.sea_fname, self.air_fname,
                                output_fname, method=method)
        MessageDialog(root, message="Success! Files saved.",
                         title='Success!')
        # root.destroy()


if __name__ == '__main__':
    root = Tk()
    g2 = Script2gui(root)
    root.mainloop()
