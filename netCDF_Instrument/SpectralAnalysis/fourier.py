#!/usr/bin/env python3
"""
This module does frequency analysis and plotting.

Typical usage:

p = pressure_readings
sample_f = 4  # Hz
freqs, fft_data = fourier.transform(p, sample_f)
fourier.plot_freq(freqs, fft_data)
plt.show()
fourier.quickplot(p, sample_f)
plt.show()
"""

import sys
import matplotlib.pyplot as plt
import numpy as np
from numpy import fft
from numpy.random import randn
import netCDF4


def transform(p, sample_f):
    '''Runs a fast fourier transform on p.

    Returns a power spectrum of p in units (unit of p)**2 / Hz, along
    with the frequency bins that the x-coordinate in the transformed
    data correspond to.

    Arguments:
    p -- the pressure array
    sample_f -- the frequency that the data was sampled at (in Hz)
    '''
    y = fft.fft(p) / len(p)  # fourier transform of p
    # THIS SCALING MIGHT BE WRONG, NEED TO CHECK:
    Y = np.absolute(2 * y)**2  # power spectrum of p
    nu = fft.fftfreq(len(p), 1 / sample_f)  # frequency bins
    return nu, Y
    

def quickplot(p, sample_f):
    nu, Y = transform(p, sample_f)
    plot_time_and_freq(p, nu, Y)

# These methods fabricate data for testing purposes.

def get_pressure_array(fname):
    f = netCDF4.Dataset(fname, 'r', format='NETCDF4_CLASSIC')
    v = f.variables
    P = v['sea_water_pressure'][:]
    return P


def create_data(t):
    """Fabricates some pressure data covering time array t"""
    r = np.random.normal(scale=1, size=len(t))
    p = (1 * np.sin(2 * np.pi * .01 * t) +
         1 * np.sin(2 * np.pi * .05 * t) +
         .3 * np.sin(2 * np.pi * .1 * t) +
         .2 * np.sin(2 * np.pi * .2 * t) + 10 + r)
    return p


# Plotting utilities

def compress(arr, points=1000):
    """Compresses an array down to the given number of points by
    averaging."""
    c = np.ceil(len(arr) / points)
    final = np.zeros(np.floor(len(arr) / c))
    summed = 0
    for i, e in enumerate(arr):
        summed += np.float64(e)
        if i % c == c - 1:
            final[np.floor(i / c)] = summed / c
            summed = 0
    return final


def plot_freq(nu, Y):
    cutoff = len(nu) / 4
    plt.plot(nu[1:cutoff], Y[1:cutoff], linewidth=2, color='r')
    plt.title('Power spectrum')
    plt.ylabel('Power (Pa**2 / Hz)')
    plt.xlabel('Frequency (Hz)')


def plot_pressure(t, p):
    '''Plots the raw pressure readings'''
    plt.plot(t, p)
    plt.title('Pressure readings')
    plt.ylabel('Pressure (bar)')
    plt.xlabel('Time (hours)')


def plot_time_and_freq(p, nu, Y):
    # Make a nice plot
    plt.title('Time space and frequency space')
    plt.subplot(2, 1, 1)
    plot_pressure(t, p)
    plt.subplot(2, 1, 2)
    plot_freq(nu, Y)


if __name__ == '__main__':

    sample_f = 10  # sampling frequency (Hz)
    total_time = 300  # total seconds
    
    # Fabricate some data
    t = np.arange(0, total_time, 1 / sample_f)
    p = create_data(t)

    # Transform to frequency space
    quickplot(p, sample_f)
    plt.show()
