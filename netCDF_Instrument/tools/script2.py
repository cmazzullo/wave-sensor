# -*- coding: utf-8 -*-
"""
Created on Thu Aug  7 08:20:07 2014

@author: cmazzullo

Inputs: One netCDF file containing water pressure and one containing
air pressure.

Outputs: One netCDF file containing water pressure, interpolated air
pressure, and water level.
"""


import numpy as np
import shutil
from numpy import arange
import pressure_to_depth as p2d
import NetCDF_Utils.nc as nc


def make_depth_file(water_fname, air_fname, out_fname, method='fft'):
    """Adds depth information to a water pressure file.

    The argument air_fname is optional, when set to '' no air
    pressure is used.
    """
    device_depth = -1 * nc.get_device_depth(water_fname)
    water_depth = nc.get_water_depth(water_fname)
    timestep = 1 / nc.get_frequency(water_fname)
    sea_pressure = nc.get_pressure(water_fname)
    sea_time = nc.get_time(water_fname)

    if air_fname != '':
        raw_air_pressure = nc.get_air_pressure(air_fname)
        air_time = nc.get_time(air_fname)
        air_pressure = np.interp(sea_time, air_time, raw_air_pressure,
                                 left=nc.FILL_VALUE, right=nc.FILL_VALUE)
        corrected_pressure = sea_pressure - air_pressure
        nc.append_air_pressure(out_fname, air_pressure)
    else:
        corrected_pressure = sea_pressure

    if method == 'fft':
        depth = p2d.fft_method(sea_time, corrected_pressure,
                               device_depth, water_depth, timestep)
    elif method == 'combo':
        depth = p2d.combo_method(sea_time, corrected_pressure,
                                 device_depth, water_depth, timestep)
    elif method == 'naive':
        depth = p2d.hydrostatic_method(corrected_pressure)
    else:
        raise TypeError('Accepted values for "method" are: fft, '
                        'method2 and naive.')
    shutil.copy(water_fname, out_fname)
    nc.append_depth(out_fname, depth)
