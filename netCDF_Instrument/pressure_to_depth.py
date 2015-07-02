#!/usr/bin/env python3
"""
Created on Mon Aug  4 08:48:12 2014

@author: Chris Mazzullo

Provides methods to convert water pressure into water depth.
"""

import numpy as np
from NetCDF_Utils.nc import FILL_VALUE

# Constants
g = 9.8  # gravity (m / s**2)
rho = 1030  # density of seawater (kg / m**3)


def combo_method(t, p, z, H, timestep):
    fill = FILL_VALUE
    f = (p == fill)
    idx = np.where(f[1:] ^ f[:-1])[0] + 1
    tchunk = np.split(t, idx)
    pchunk = np.split(p, idx)
    Hchunk = np.split(H, idx)
    dchunks = []
    for pc, tc, Hc in zip(pchunk, tchunk, Hchunk):
        if pc[0] == fill:
            dchunks.append(pc)
            continue
        dc = combo_backend(tc, pc, z, Hc, timestep)
        dchunks.append(dc)
    return np.concatenate(dchunks)


def combo_backend(t, p_dbar, z, H, timestep):
    coeff = np.polyfit(t, p_dbar, 1)
    static_p = coeff[1] + coeff[0]*t
    static_y = hydrostatic_method(static_p)
    wave_p = p_dbar - static_p
    cutoff = auto_cutoff(np.average(H))
    wave_y = fft_method(wave_p, z, H, timestep, hi_cut=cutoff)
    wave_y = np.pad(wave_y, (0, len(t) - len(wave_y)), mode='edge')
    return static_y + wave_y


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


def k_to_omega(k, H):
    """Takes the wave number and water depth as arguments, returns the
    angular frequency."""
    return np.sqrt(k * g * np.tanh(k * H))


def omega_to_k(omega, H):
    k = np.arange(0, 10, .01)
    w = k_to_omega(k, H)
    deg = 10
    p = np.polyfit(w, k, deg)
    return sum(p[i] * omega**(deg - i) for i in range(deg + 1))


def fft_method(p_dbar, z, H, timestep, gate=0, window_func=np.hamming,
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


def pressure_to_eta(del_p, k, z, H):
    """Convert the non-hydrostatic pressure to height above z=0."""
    c = _coefficient(k, z, H)
    return del_p / c


def _coefficient(k, z, H):
    """Return a conversion factor for pressure and wave height."""
    return rho * g * np.cosh(k * (H + z)) / np.cosh(k * H)
