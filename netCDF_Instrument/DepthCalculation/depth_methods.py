#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: cmazzullo

This is a version of Script 2 for testing different pressure to depth
conversion methods.
"""


import numpy as np
import shutil
from numpy import arange
import DepthCalculation.pressure_to_depth as p2d
import NetCDF_Utils.nc as nc


# Strategy:
# 1. Split the file into chunks
# 2. Subtract out tide and avg. water level to get just the waves
# 3. Apply linear wave theory to get water level
# 4. Plot the water level

def split_into_chunks(array, chunk_length):
    # Trim the array so its length is evenly divisible by chunk_length
    remainder = len(array) % chunk_length
    trimmed = array[:-remainder]
    # Then split it into chunks with np.reshape
    return trimmed.reshape(len(array) / chunk_length, chunk_length) 

def make_depth_file(water_fname, air_fname, out_fname, method='fft'):
    device_depth = -1 * nc.get_device_depth(water_fname)
    water_depth = nc.get_water_depth(water_fname)
    timestep = 1 / nc.get_frequency(water_fname)
    sea_pressure = nc.get_pressure(water_fname)
    sea_time = nc.get_time(water_fname)
    raw_air_pressure = nc.get_air_pressure(air_fname)
    air_time = nc.get_time(air_fname)

    air_pressure = np.interp(sea_time, air_time, raw_air_pressure,
                             left=nc.FILL_VALUE, right=nc.FILL_VALUE)
    corrected_pressure = sea_pressure - air_pressure

    if method == 'fft':
        depth = p2d.fft_method(sea_time, corrected_pressure,
                               device_depth, water_depth, timestep)
    elif method == 'method2':
        depth = p2d.method2(corrected_pressure)
    elif method == 'naive':
        depth = p2d.hydrostatic_method(corrected_pressure)
    else:
        raise TypeError('Accepted values for "method" are: fft, '
                        'method2 and naive.')
    shutil.copy(water_fname, out_fname)
    nc.append_air_pressure(out_fname, air_pressure)
    nc.append_depth(out_fname, depth)

