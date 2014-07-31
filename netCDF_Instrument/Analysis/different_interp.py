#!/usr/bin/env python3
"""
Find tides by interpolation

This module interpolates wave data with a sin wave using nonlinear least
squares. If you do this and subtract the best-fit sin wave, you can get the
water level independent of tides.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
from scipy.optimize import curve_fit
from scipy.optimize import brute
import numpy.fft as fft

def create_data(t):
    """Fabricates some pressure data covering time array t"""
    r = np.random.normal(scale=.4, size=len(t))
    p = (1 * np.sin(2 * np.pi * .01 * t) + 
         .5 * np.sin(2 * np.pi * .05 * t) +
         .3 * np.sin(2 * np.pi * .1 * t) +
         .2 * np.sin(2 * np.pi * .2 * t) + 10 + r)

    return p


def residual(params, t, data):
    """Residual between sin and data.

    Defines a residual between a sin wave based model and the real
    data. Minimizing this will give the coefficients of the best-fit
    sin wave."""
    phase = params[0]
    freq = params[1]
    model = np.sin(freq * t + phase)
    return abs(data - model)


T = 300
samfreq = 4  # Samples per second
t = np.arange(0, T, 1 / samfreq)
p = create_data(t)
# Massage data
clean_p = (p - np.average(p)) / (max(p) - min(p))
Y = np.absolute(fft.fft(clean_p) / len(clean_p))**2
nu = fft.fftfreq(len(clean_p), 1 / samfreq)
max_freq = nu[np.argmax(Y[0:len(Y) / 2])]

tide = np.average(p) + (max(p) - min(p)) * np.sin(2 * np.pi * max_freq * t) / 2
print(max_freq)
#plt.plot(nu, Y)
plt.plot(p, label='Pressure data')
#plt.plot(p - tide)
plt.plot(tide, linewidth=1, color='r', label='Calculated tide')
plt.legend()
plt.show()
