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

def make_depth_file(water_fname, air_fname, out_fname, method='fft'):
    device_d = -1 * nc.get_device_depth(water_fname)
    water_d = nc.get_water_depth(water_fname)
    timestep = 1 / nc.get_frequency(water_fname)
    sea_p = nc.get_pressure(water_fname)
    sea_t = nc.get_time(water_fname)
    raw_air_p = nc.get_air_p(air_fname)
    air_t = nc.get_time(air_fname)

    air_p = np.interp(sea_t, air_t, raw_air_p,
                             left=nc.FILL_VALUE, right=nc.FILL_VALUE)
    corrected_pressure = sea_p - air_p

    if method == 'fft':
        depth = p2d.fft_method(sea_t, corrected_pressure,
                               device_d, water_d, timestep)
    elif method == 'method2':
        depth = p2d.method2(corrected_pressure)
    elif method == 'naive':
        depth = p2d.hydrostatic_method(corrected_pressure)
    else:
        raise TypeError('Accepted values for "method" are: fft, '
                        'method2 and naive.')
    shutil.copy(water_fname, out_fname)
    nc.append_air_p(out_fname, air_p)
    nc.append_depth(out_fname, depth)


def moving_average(a, n=3):
    """Perform a moving average on an array"""
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def apply_method(method, *args):
    return np.array(list(map(method, *args)))

# NOTE: RIGHT NOW THIS DOESNT HAVE THE CORRECTED PRESSURE
def chunked_p2d(water_fname, air_fname, method, chunk_size=100,
                lo_cut=-1, hi_cut=20, avg_len=-1, noise_gate=0):
    device_d, water_d, ts, sea_p, sea_t = get_file_info(water_fname)

    # MOVING AVG
    if avg_len != -1:
        sea_p = remove_avg(sea_p, avg_len)
        sea_t = sea_t[avg_len - 1:]

    # SPLIT INTO CHUNKS
    chunked_pressure = split_into_chunks(sea_p, chunk_size)
    chunked_time = split_into_chunks(sea_t, chunk_size)
    chunked_pressure = remove_chunk_mean(chunked_pressure)

    def get_depth(time_chunk, pressure_chunk):
        if method == 'fft':
            return p2d.fft_method(time_chunk, pressure_chunk,
                                  device_d, water_d, ts,
                                  gate=noise_gate, hi_cut=hi_cut,
                                  lo_cut=lo_cut)
        elif method == 'hydrostatic':
            return p2d.hydrostatic_method(pressure_chunk)

    chunked_d = apply_method(get_depth, chunked_time,
                                 chunked_pressure)
    return flatten(chunked_time), flatten(chunked_d)


def get_file_info(fname):
    device_d = -1 * nc.get_device_depth(water_fname)
    water_d = nc.get_water_depth(water_fname)
    timestep = 1 / nc.get_frequency(water_fname)
    sea_p = nc.get_pressure(water_fname)
    sea_t = nc.get_time(water_fname)
    return device_d, water_d, timestep, sea_p, sea_t


def split_into_chunks(array, chunk_size):
    """Trim the array to size, then split it evenly into chunks"""
    # Trim the array so its length is evenly divisible by chunk_size
    remainder = len(array) % chunk_size
    trimmed = array[:-remainder]
    # Then split it into chunks with np.reshape
    return trimmed.reshape(len(array) / chunk_size, chunk_size)


def remove_avg(a, n=3):
    return a[n-1:] - moving_average(a, n)


def flatten(chunks):
    """Unchunk an array"""
    return chunks.reshape(np.size(chunks))


def remove_chunk_mean(chunks):
    result = []
    for chunk in chunks:
        result.append(chunk - np.average(chunk))
    return np.array(result)

def fft(array, timestep):
    amps = np.fft.rfft(array)
    freqs = np.fft.rfftfreq(array, d=timestep)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    water_fname = '/home/chris/test-data/ncs/logger3.csv.nc'

    time1, depth_fft = chunked_p2d(water_fname, '', 'fft', chunk_size=10000,
                                   lo_cut=-1, hi_cut=10, noise_gate=0, avg_len=-1)
    time2, depth_static = chunked_p2d(water_fname, '', 'hydrostatic', chunk_size=10000,
                                      lo_cut=-1, hi_cut=10, noise_gate=0, avg_len=-1)

    plt.plot(time1 / 1e3, depth_fft + .001, 'b', label='Chunked spectral')
    plt.plot(time2 / 1e3, depth_static, 'm', label='Hydrostatic')

    error = np.absolute(depth_fft - depth_static)
    rmsd = np.sqrt(np.average(error**2))

    plt.plot(time1/1e3, depth_fft - depth_static, 'r', label='Difference')

    plt.plot(sea_t / (1000 * 60* 60), sea_p, label='Pressure (dbar)')
    plt.legend()
#    plt.ylabel('water height (m)')
    plt.ylabel('pressure (dbar)')
    plt.xlabel('time (hours)')
    plt.grid(which='both')
    plt.show()
