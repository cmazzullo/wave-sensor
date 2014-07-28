#!/usr/bin/env python3
import sys
sys.path.append('..')
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import NetCDF_Utils.slurp as slurp
import math
import numpy as np
from numpy import fft
from numpy.random import randn


def get_pressure_array(fname):
    f = Dataset(fname, 'r', format='NETCDF4_CLASSIC')
    v = f.variables
    P = v['sea_water_pressure'][:]
    return P


def draw_nc(fname):
    P = get_pressure_array(fname)
    # max number of points that Cairo can draw
    pl(p)


def compress(P):
    M = 500
    c = math.ceil(len(P) / M)
    p = slurp.compress_np(P, c)
    return p


def pl(P):
    p = compress(P)
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
    plt.vlines(nu, [0], Y)
    plt.ylabel('Magnitude')
    plt.xlabel('Frequency (Hz)')

    plt.show()

def semilog_vlines(Y, nu, nq, label='', xlim=1000):
    plt.vlines(nu[1:nq], [0],
               np.log(Y[1:nq]),
               colors='r')
#    plt.xticks(np.arange(0, 1, .1), rotation=30, size='small')
    plt.xlim((0, xlim))
    plt.grid()
    plt.ylabel(label)
    plt.xlabel('Frequency (1/hour)')

def semilog(Y, nu, nq, label='', xlim=1000):
    plt.plot(nu[0:nq], np.log(Y[0:nq]))
#    plt.xticks(np.arange(0, 1, .1), rotation=30, size='small')
    plt.xlim((0, xlim))
    plt.grid()
    plt.ylabel(label)
    plt.xlabel('Frequency (1/hour)')

def linear_vlines(Y, nu, nq, label='', xlim=1):
    plt.vlines(nu[0:nq], [0], Y[0:nq], colors='r')
#    plt.xticks(np.arange(0, 1, .1), rotation=30, size='small')
    plt.xlim((0, xlim))
    plt.grid()
    plt.ylabel(label)
    plt.xlabel('Frequency (1/hour)')



def plot_pressure(time, y):
    plt.plot(compress(time), compress(y))
    plt.title('Hurricane pressure readings')
    plt.ylabel('Pressure (bar)')
    plt.xlabel('Time (hours)')

        
def plot_storm():
    fname = '/home/chris/measurement-systems.nc'
    y = get_pressure_array(fname)
    L = len(y)
    print(L)
    Fs = 3                          # sampling frequency (Hz)
    total_time = L / Fs             # total seconds
    T = 1 / Fs                      # sample time
    t = np.arange(0, total_time + T, T)      # time vector

    nyquist = Fs / 2                # highest representable frequency
    Y = fft.fft(y)
    Y = np.absolute(Y)**2
    Y = Y[:len(Y) / 2]
    nu = fft.fftfreq(L, T)
    nu = nu * 60  # turns Hz frequency into minute^-1 frequency
    nu = nu[:len(nu) / 2]
    time = np.arange(0, L + 1) / (Fs * 60)

    nq_hours = 60 * nyquist # nyquist in minute**-1
    
    plt.subplot(2, 1, 1)
    plot_pressure(time, y)

    plt.subplot(2, 1, 2)
    # Compressed
    semilog(compress(Y), compress(nu), nq_hours, 
            label='ln(F(m)**2)', xlim=nq_hours)

    plt.show()
    return Y, nu

Y, nu = plot_storm()
print('done')
