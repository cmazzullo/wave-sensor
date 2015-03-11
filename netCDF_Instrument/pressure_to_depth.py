#!/usr/bin/env python3
"""
Created on Mon Aug  4 08:48:12 2014

@author: Chris Mazzullo

Provides methods to convert water pressure into water depth.
"""

import numpy as np

# Constants
g = 9.8  # gravity (m / s**2)
rho = 1030  # density of seawater (kg / m**3)


def combo_method(t, p_dbar, z, H, timestep, window_func=np.hamming):
    coeff = np.polyfit(t, p_dbar, 1)
    static_p = coeff[1] + coeff[0]*t
    static_y = hydrostatic_method(static_p)
    wave_p = p_dbar - static_p
    cutoff = auto_cutoff(np.average(H))
    wave_y = fft_method(wave_p, z, H, timestep, hi_cut=cutoff,
                        window_func=window_func)
    return trim_to_even(static_y) + wave_y


def hydrostatic_method(pressure):
    """Return the depth corresponding to a hydrostatic pressure."""
    return (pressure *  1e4) / (rho * g)


def auto_cutoff(h):
    return .9/np.sqrt(h)


def trim_to_even(seq):
    """Trim a sequence to make it have an even number of elements"""
    if len(seq) % 2 == 0:
        return seq
    else:
        return seq[:-1]

def omega_to_k(omega, H):
    k = np.arange(0, 10, .01)
    w = k_to_omega(k, H)
    deg = 10
    p = np.polyfit(w, k, deg)
    return sum(p[i] * omega**(deg - i) for i in range(deg + 1))


def fft_method(p_dbar, z, H, timestep, gate=0, window_func=np.ones,
               lo_cut=-1, hi_cut=float('inf')):
    """Create wave height data from an array of pressure readings.

    WARNING: FFT will truncate the last element of an array if it has
    an odd number of elements!
    """
    H = np.average(H)
    p_dbar = trim_to_even(p_dbar)
    n = len(p_dbar)
    window = window_func(n)
    scaled_p = p_dbar[:n] * 1e4 * window  # scale by the window

    p_amps = np.fft.rfft(scaled_p)
    freqs = np.fft.rfftfreq(n, d=timestep)
    k = omega_to_k(2 * np.pi * freqs, H)
    d_amps = pressure_to_eta(p_amps, k, z, H)
    d_amps[np.where((freqs <= lo_cut) | (freqs >= hi_cut))] = 0

    eta = np.fft.irfft(d_amps) # reverse FFT
    if window_func:
        eta = eta / window
    return eta


def _frequency_to_index(f, n, timestep):
    """
    Gets the index of a frequency in np.fftfreq.

    f -- the desired frequency
    n -- the length given to fftfreq
    sample_freq -- the sampling frequency
    """
    return np.round(n * f * timestep)


def binary_search(func, x1, x2, tol):
    y1 = func(x1)
    y2 = func(x2)
    x_mid = (x1 + x2) / 2
    y_mid = func(x_mid)
    if abs(y_mid) < tol:
        return x_mid
    elif y1 * y_mid < 0:
        return binary_search(func, x1, x_mid, tol)
    elif y_mid * y2 < 0:
        return binary_search(func, x_mid, x2, tol)
    else:
        print('Binary root finder failed to find a root!')


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


if __name__ == '__main__':
    from tests.pressure_to_depth_tests import easy_waves
    from numpy import *
    from matplotlib.pyplot import *
    # import seaborn as sns
    ion()

    max_f = .2
    max_a = 10
    max_phase = 10
    length = 6000 # length of the time series in seconds
    h = 15
    z = -14.6
    t, actual_y, p = easy_waves(length, h, z, 10)
    sample_frequency = 4
    cutoff = auto_cutoff(h)
    computed_y = fft_method(p/10000, z, np.ones_like(t)*h,
                            1/sample_frequency, hi_cut=cutoff)
    static_y = p/rho/g
    combo_y = combo_method(t, p/10000, z, np.ones_like(t)*h,
                           1/sample_frequency)

    ## plotting
    clf()
    plot(t, actual_y, label='Actual y')
    plot(t, computed_y, label='FFT method y')
    plot(t, combo_y, label='Combo y')
    legend()

    def rmse(a, b):
        return sqrt(average(absolute(a-b)**2))

    print('FFT method: ', rmse(computed_y, actual_y))
    print('Combo method: ', rmse(combo_y, actual_y))