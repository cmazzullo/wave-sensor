#!/usr/bin/env python3
"""
Created on Mon Aug  4 08:48:12 2014

@author: Chris Mazzullo

Provides methods to convert water pressure into water depth.
"""

import numpy as np
from NetCDF_Utils.nc import FILL_VALUE

# Constants
GRAVITY = 9.8  # (m / s**2)
WATER_DENSITY = 1030  # density of seawater (kg / m**3)


def combo_method(time, pressure, device_d, water_d, tstep):
    """Convert pressure series into depth series using fft method."""
    split_idx = (pressure == FILL_VALUE)
    idx = np.where(split_idx[1:] ^ split_idx[:-1])[0] + 1
    dchunks = []
    for p_chunk, t_chunk, h_chunk in zip(np.split(pressure, idx),
                                         np.split(time, idx),
                                         np.split(water_d, idx)):
        if p_chunk[0] == FILL_VALUE:
            dchunks.append(p_chunk)
            continue
        coeff = np.polyfit(t_chunk, p_chunk, 1)
        static_p = coeff[1] + coeff[0]*t_chunk
        wave_p = p_chunk - static_p
        wave_y = pressure_to_depth_lwt(wave_p, device_d, h_chunk, tstep)
        wave_y = np.pad(wave_y, (0, len(t_chunk) - len(wave_y)), mode='edge')
        dchunks.append(hydrostatic_method(static_p) + wave_y)
    return np.concatenate(dchunks)


def hydrostatic_method(pressure):
    """Return the depth corresponding to a hydrostatic pressure."""
    return (pressure *  1e4) / (WATER_DENSITY * GRAVITY)


def auto_cutoff(water_d):
    """Return a sensible frequency to cut off for a certain water depth"""
    return .9/np.sqrt(np.average(water_d))


def trim_to_even(seq):
    """Trim a sequence to make it have an even number of elements"""
    if len(seq) % 2 == 0:
        return seq
    else:
        return seq[:-1]


def k_to_omega(wavenumber, water_d):
    """Converts wavenumber to angular frequency for water waves"""
    return np.sqrt(wavenumber * GRAVITY * np.tanh(wavenumber * water_d))


def omega_to_k(omega, water_d):
    """Converts angular frequency to wavenumber for water waves"""
    wavenumber = np.arange(0, 10, .01)
    deg = 10
    pressure = np.polyfit(k_to_omega(wavenumber, water_d), wavenumber, deg)
    return sum(pressure[i] * omega**(deg - i) for i in range(deg + 1))


def pressure_to_depth_lwt(p_dbar, device_d, water_d, tstep, hi_cut='auto'):
    """Create wave height data from an array of pressure readings.

    WARNING: FFT will truncate the last element of an array if it has
    an odd number of elements!
    """
    if hi_cut == 'auto':
        hi_cut = auto_cutoff(water_d)
    water_d = np.average(water_d)
    p_dbar = trim_to_even(p_dbar)
    window = np.hamming(len(p_dbar))
    scaled_p = p_dbar * 1e4 * window
    p_amps = np.fft.rfft(scaled_p)
    freqs = np.fft.rfftfreq(len(p_dbar), d=tstep)
    wavenumber = omega_to_k(2 * np.pi * freqs, water_d)
    d_amps = pressure_to_eta(p_amps, wavenumber, device_d, water_d)
    d_amps[np.where(freqs >= hi_cut)] = 0
    eta = np.fft.irfft(d_amps) # reverse FFT
    eta = eta / window
    return eta


def pressure_to_eta(del_p, wavenumber, device_d, water_d):
    """Convert the non-hydrostatic pressure to height above device_d=0."""
    return del_p / _coefficient(wavenumber, device_d, water_d)


def _coefficient(wavenumber, device_d, water_d):
    """Return a conversion factor for pressure and wave height."""
    if device_d > 0:
        raise ValueError("Device depth > 0, it should be negative.")
    if water_d < 0:
        raise ValueError("Water depth < 0, it should be positive.")
    if -device_d > water_d:
        raise ValueError("Device depth > water depth.")
    return WATER_DENSITY * GRAVITY * (np.cosh(wavenumber * (water_d + device_d)) /
                                      np.cosh(wavenumber * water_d))
