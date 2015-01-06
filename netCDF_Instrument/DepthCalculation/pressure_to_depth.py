#!/usr/bin/env python3
"""
Created on Mon Aug  4 08:48:12 2014

@author: Chris Mazzullo

Provides methods to convert water pressure into water depth.
"""

import numpy as np
from scipy.optimize import newton

# Constants
g = 9.8  # gravity (m / s**2)
rho = 1030  # density of seawater (kg / m**3)
min_coeff = 1/15


def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n-1:]/n


def combo_method(t, p_dbar, z, H, timestep, max_coeff=12):
    coeff = np.polyfit(t, p_dbar, 1)
    static_p = coeff[1] + coeff[0]*t
    static_y = 10000*static_p/rho/g
    wave_p = p_dbar - static_p
    wave_y = fft_method(t, wave_p, z, H, timestep, max_coeff=max_coeff,
                        auto_cutoff=True)
    return static_y + wave_y


# def cutoff_freq(min_coeff, h, z): # this is wrong i think
#     k = sqrt(2*(min_coeff-1)/(z*(z + 2*h)))
#     return sqrt(g*k*tanh(k*h))/2/pi

def cutoff_freq(min_coeff, h, z): # the cutoffs seem too low...
    a = min_coeff
    k = np.sqrt(2 * (a - 1) / (h**2 * (1 - a) + z**2 + 2*h*z))
    return np.sqrt(g*k*np.tanh(k*h))/2/np.pi # convert wavenumber to frequency

def hydrostatic_method(pressure):
    """Return the depth corresponding to a hydrostatic pressure."""
    return (pressure *  1e4) / (rho * g)


def fft_method(t, p_dbar, z, H, timestep, gate=0, window=False,
               lo_cut=-1, hi_cut=float('inf'), auto_cutoff=True,
               max_coeff=float('inf')):
    """
    Create wave height data from an array of pressure readings.

    t             the time array
    p_dbar        an array of pressure readings
    z             the depth of the sensor
    H             the water depth (array)
    timestep      the time interval in between pressure readings
    gate          any fluctuations in the pressure that are less than
                  this threshold won't be used in the height data.
    window        whether or not to use a window function
    lo_cut        minimum frequency data to include, exclusive
    hi_cut        maximum frequency data to include, exclusive (1Hz
                    seems sane)
    """
    # Put the pressure data into frequency space
    n = len(p_dbar) - len(p_dbar) % 2
    p = p_dbar[:n] * 1e4
    raw_gate_array = np.ones_like(p) * gate

    if window:
        window_func = np.hamming(n)
        scaled_p = p * window_func  # scale by a hamming window
        gate_array = raw_gate_array * window_func
    else:
        scaled_p = p
        gate_array = raw_gate_array

    if auto_cutoff:
        #hi_cut = cutoff_freq(min_coeff, np.average(H), z)
        hi_cut=.9/np.sqrt(np.average(H))
        print('hi_cut = ', hi_cut)

    amps = np.fft.rfft(scaled_p)
    freqs = np.fft.rfftfreq(n, d=timestep)
    new_amps = np.zeros_like(amps)

    for i in range(len(amps)):
        # Filter out the noise with the gate
        if ((np.absolute(amps[i] / n) >= gate_array[i])
            and (lo_cut < freqs[i] < hi_cut)):
                k = omega_to_k(freqs[i] * 2 * np.pi, H[i])
                # Scale, applying the diffusion relation
                a = pressure_to_eta(amps[i], k, z, H[i])

                # experimental
                c = 1/_coefficient(k, z, H[i])
                if c <= max_coeff:
                    a = amps[i] * (1 / _coefficient(k, z, H[i]))
                else:
                    a = 0
                    break
                new_amps[i] = a
        else:
            new_amps[i] = 0

    # Convert back to time space
    eta = np.fft.irfft(new_amps)
    if window:
        eta = eta / window_func
    return eta


def _frequency_to_index(f, n, timestep):
    """
    Gets the index of a frequency in np.fftfreq.

    f -- the desired frequency
    n -- the length given to fftfreq
    sample_freq -- the sampling frequency
    """
    return np.round(n * f * timestep)


def omega_to_k(omega, H):
    """
    Gets the wave number from the angular frequency using the
    dispersion relation for water waves and Newton's method.
    """
    f = lambda k: omega**2 - k * g * np.tanh(k * H)
    return newton(f, 0)


def k_to_omega(k, H):
    """Takes the wave number and water depth as arguments, returns the
    angular frequency."""
    return np.sqrt(k * g * np.tanh(k * H))


def pressure_to_eta(del_p, k, z, H):
    """Convert the non-hydrostatic pressure to height above z=0."""
    c = _coefficient(k, z, H)
    return del_p / c


def eta_to_pressure(eta, k, z, H):
    """Convert wave height to pressure using linear wave theory."""
    c = _coefficient(k, z, H)
    return eta * c


def _coefficient(k, z, H):
    """Return a conversion factor for pressure and wave height."""
    return rho * g * np.cosh(k * (H + z)) / np.cosh(k * H)

def make_pstatic(pressure):
    """Extract hydrostatic pressure from a pressure array."""
    x = np.arange(len(pressure))
    slope, intercept = np.polyfit(x, pressure, 1)
    pwave = slope * x + intercept
    return pwave

if __name__ == '__main__':
    from DepthCalculation.testing import easy_waves, print_rmse
    from numpy import *
    from matplotlib.pyplot import *
    ion()

    max_f = .2
    max_a = 10
    max_phase = 10
    length = 6000 # length of the time series in seconds
    h = 30
    z = -.1
    t, actual_y, p = easy_waves(length, h, z, 10)
    sample_frequency = 4
    computed_y = fft_method(t, p/10000, z, np.ones_like(t)*h, \
                            1/sample_frequency)
    static_y = p/rho/g
    clf()

    combo_y = combo_method(t, p/10000, z, np.ones_like(t)*h, 1/sample_frequency,
                           max_coeff=12)

    plot(t, actual_y, 'b')
    plot(t, computed_y, 'g')
    plot(t, combo_y, 'r')
    print_rmse(actual_y, static_y, computed_y)
