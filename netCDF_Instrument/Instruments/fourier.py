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

fname = '/home/chris/measurement-systems.nc'
Fs = 1000                       # sampling frequency
T = 1 / Fs                      # sample time
total_time = 1                  # total seconds
L = Fs * total_time + 1
t = np.arange(0, total_time + T, T)      # time vector
f = 10                          # frequency in Hz
y = [ 2 * math.sin(f * 2 * math.pi * e) +
     math.sin(2 * f * 2 * math.pi * e) +
     math.sin(5 * f * 2 * math.pi * e) +
     math.sin(6 * f * 2 * math.pi * e)
      for e in t]
rand = randn(L)
y = y + rand

nyquist = Fs / 2                # highest representable frequency

Y = fft.fft(y) / L
Y = np.absolute(Y)**2
#Y = Y.real
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
# f = fft.fft(signal) / N # fourier coefficients
# f = fft.fftshift(f) # shift zero freq to center
# nu = fft.fftfreq(N, dx) # natural frequencies
# nu = fft.fftshift(nu) # shift zero freq to center
# power = np.absolute(f)**2 / 2
# #plt.plot(signal)
# plt.plot(nu, power)
# plt.show()





