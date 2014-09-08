#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: cmazzullo

This is a version of Script 2 for testing different pressure to depth
conversion methods.
"""


import numpy as np
import timeit
import shutil
from numpy import arange
import DepthCalculation.pressure_to_depth as p2d
import NetCDF_Utils.nc as nc
from functools import partial

# Strategy:
# 1. Split the file into chunks
# 2. Subtract out tide and avg. water level to get just the waves
# 3. Apply linear wave theory to get water level
# 4. Plot the water level

def split_into_chunks(array, chunk_size):
    """Trim the array to size, then split it evenly into chunks"""
    # Trim the array so its length is evenly divisible by chunk_size
    remainder = len(array) % chunk_size
    trimmed = array[:-remainder]
    # Then split it into chunks with np.reshape
    return trimmed.reshape(len(array) / chunk_size, chunk_size)


def flatten(chunks):
    """Unchunk an array"""
    return chunks.reshape(np.size(chunks))


def remove_chunk_mean(chunks):
    result = []
    for chunk in chunks:
        result.append(remove_mean(chunk))
    return np.array(result)


def remove_mean(array):
    return array - np.average(array)


def fft(array, timestep):
    amps = np.fft.rfft(array)
    freqs = np.fft.rfftfreq(array, d=timestep)


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


def moving_average(a, n=3):
    """Perform a moving average on an array"""
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def remove_avg(a, n=3):
    return a[n-1:] - moving_average(a, n)

def get_sea_data(fname):
    data = dict()
    data['device_depth'] = -1 * nc.get_device_depth(water_fname)
    data['water_depth'] = nc.get_water_depth(water_fname)
    data['timestep'] = 1 / nc.get_frequency(water_fname)
    data['sea_pressure'] = nc.get_pressure(water_fname)
    data['sea_time'] = nc.get_time(water_fname)

# NOTE: RIGHT NOW THIS DOESNT HAVE THE CORRECTED PRESSURE
def chunked_p2d(water_fname, air_fname, chunk_size=100, lo_cut=-1,
                hi_cut=20, rolling_avg_len=-1, noise_gate=0):
    device_depth = -1 * nc.get_device_depth(water_fname)
    water_depth = nc.get_water_depth(water_fname)
    timestep = 1 / nc.get_frequency(water_fname)
    sea_pressure = nc.get_pressure(water_fname)
    sea_time = nc.get_time(water_fname)

    # MOVING AVG
    if rolling_avg_len != -1:
        sea_pressure = remove_avg(sea_pressure, rolling_avg_len)
        sea_time = sea_time[rolling_avg_len - 1:]

    # SPLIT INTO CHUNKS
    chunked_pressure = split_into_chunks(sea_pressure, chunk_size)
    chunked_time = split_into_chunks(sea_time, chunk_size)
    chunked_pressure = remove_chunk_mean(chunked_pressure)

    def get_depth(time_chunk, pressure_chunk):
        return p2d.fft_method(time_chunk, pressure_chunk,
                              device_depth, water_depth, timestep,
                              gate=noise_gate, hi_cut=hi_cut,
                              lo_cut=lo_cut)

    chunked_depth = apply_method(get_depth, chunked_time,
                                 chunked_pressure)
    return flatten(chunked_depth)

def apply_method(method, *args):
    return np.array(list(map(method, *args)))

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    water_fname = '/home/chris/test-data/ncs/logger3.csv.nc'
    depth = chunked_p2d(water_fname, '', chunk_size=1000,
                        lo_cut=-1, hi_cut=1, noise_gate=0, rolling_avg_len=(60*15))

    hydrostatic_depth = flatten(apply_method(p2d.hydrostatic_method,
                                             chunked_pressure))

    plt.plot(depth, 'b', label='Chunked spectral')
    plt.plot(hydrostatic_depth + .001, 'm', label='Hydrostatic')
    #error = np.absolute(depth - hydrostatic_depth)
    #rmsd = np.sqrt(np.average(error**2))
    #plt.plot(depth - hydrostatic_depth, 'r', label='Difference')
    plt.legend()
    plt.grid(which='both')
    plt.show()
