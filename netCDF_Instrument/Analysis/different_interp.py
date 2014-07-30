#!/usr/bin/env python3
'''This module interpolates wave data with a sin wave using nonlinear least
squares. If you do this and subtract the best-fit sin wave, you can get the
water level independent of tides.'''

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
from scipy.optimize import curve_fit
def create_data(t):
    '''Fabricates some pressure data covering time array t'''
    #   r = np.random.normal(scale=.2, size=len(t))
    r = 0
    amplitude = 1
    phase = 2
    angfreq =.05
    p = amplitude * np.sin(angfreq * t + phase) + r
    return p


def residual(params, t, data):
    '''Defines a residual between a sin wave based model and the real
data. Minimizing this will give the coefficients of the best-fit
sin wave.'''
    phase = params[0]
    freq = params[1]
    model = np.sin(freq * t + phase)
    return abs(data - model)


# Setup, create wave    
T = 300
samfreq = 4  # Samples per second
t = np.arange(0, T, 1 / samfreq)
p = create_data(t)
data = 2 * p / (max(p) - min(p))
params = [.05, 2]
out = leastsq(residual, params, args=(t, data))
freqout = out[0][0]
phaseout = out[0][1]


# def func(t, amp, freq, phase):
#     return amp * np.sin(freq * t + phase)

# y = func(t, 2.5, 1.3, .5)
# ydata = y + .2 * np.random.normal(size=len(t))
# popt, pcov = curve_fit(func, t, ydata)


def func(x, a, b, c):
    return a * np.sin(-b * x) + c
xdata = np.linspace(0, 4, 50)
y = func(xdata, 2.5, 1.3, 0.5)
ydata = y + 0.2 * np.random.normal(size=len(xdata))
popt, pcov = curve_fit(func, xdata, ydata)

plt.plot(func(xdata, *popt))
plt.plot(ydata)
plt.show()
