#!/usr/bin/env python3
import sys
sys.path.append('.')
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import slurp
import math
import numpy as np
from numpy import fft
from numpy.random import randn

def get_pressure_array(fname):
    f = Dataset(filename,'r',format='NETCDF4_CLASSIC')
    v = f.variables
    P = v['sea_water_pressure'][:]
    return P

def draw_nc(fname):
    P = get_pressure_array(fname)
    # max number of points that Cairo can draw
    pl(p)

def pl(P):
    M = 18000
    c = math.ceil(len(P) / M)
    p = slurp.compress_np(P, c)
    plt.plot(p)
    plt.show()

def make_signal(sample_rate, total_time):
    f = 10
    t = np.arange(0, total_time + T, T)      # time vector
    y = [2 * math.sin(f * 2 * math.pi * e) +
         math.sin(2 * f * 2 * math.pi * e) +
         math.sin(5 * f * 2 * math.pi * e) +
         math.sin(6 * f * 2 * math.pi * e)
         for e in t]
    rand = randn(L)
    y = y + rand
    return y

def plot_fourier():
    Fs = 1000                       # sampling frequency (Hz)
    total_time = 1                  # total seconds
    #y = make_signal(Fs, total_time)
    fname = '/home/chris/measurement-systems.nc'
    y = get_pressure_array(fname)
    T = 1 / Fs                      # sample time
    L = Fs * total_time + 1
    t = np.arange(0, total_time + T, T)      # time vector
    f = 10                          # frequency in Hz

    nyquist = Fs / 2                # highest representable frequency

    Y = fft.fft(y) / L
    Y = np.absolute(Y)**2
    Y = Y[0:nyquist]
    nu = fft.fftfreq(L + 1, T)
    nu = nu[0:nyquist]


    plt.subplot(2, 1, 1)
    plt.plot(y)
    plt.title('Time space and frequency space')
    plt.ylabel('Amplitude')
    plt.xlabel('Time (s)')

    plt.subplot(2, 1, 2)
    #plt.plot(nu, Y)
    plt.vlines(nu, [0], Y)
    plt.ylabel('Magnitude')
    plt.xlabel('Frequency (Hz)')

    plt.show()

def plot_storm():
    fname = '/home/chris/measurement-systems.nc'
    y = get_pressure_array(fname)
    Fs = 3                          # sampling frequency (Hz)
    L = len(y)
    total_time = L / Fs             # total seconds
    T = 1 / Fs                      # sample time
    t = np.arange(0, total_time + T, T)      # time vector

    nyquist = Fs / 2                # highest representable frequency

    Y = fft.fft(y) / L
    Y = np.absolute(Y)**2
    Y = Y[0:nyquist]
    nu = fft.fftfreq(L + 1, T)
    nu = nu[0:nyquist]
    
    plt.subplot(2, 1, 1)
    plt.plot(y)
    plt.title('Time space and frequency space')
    plt.ylabel('Amplitude')
    plt.xlabel('Time (s)')

    plt.subplot(2, 1, 2)
    #plt.plot(nu, Y)
    plt.vlines(nu, [0], Y)
    plt.ylabel('Magnitude')
    plt.xlabel('Frequency (Hz)')

    plt.show()
