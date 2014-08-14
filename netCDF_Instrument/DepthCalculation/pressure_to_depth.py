# -*- coding: utf-8 -*-
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


def hydrostatic_method(p):
    return (p *  1e4) / (rho * g)


def fft_method(t, p_dbar, z, H, timestep, gate=0, window=True,
                      cutoff=-1):
    """Takes an array of pressure readings and creates wave height data.

    t -- the time array
    p_dbar -- an array of pressure readings such that len(t) == len(p)
    z -- the depth of the sensor
    H -- the water depth (array)
    timestep -- the time interval in between pressure readings
    amp_cutoff -- any fluctuations in the pressure that are less than this
                  threshold won't be used in the height data.
    """
    print('Calculating depth...')
    # Put the pressure data into frequency space
    p = p_dbar * 1e4
    n = len(p)
    raw_gate_array = np.ones_like(p) * gate

    if window:
        window_func = np.hamming(n)
        scaled_p = p * window_func  # scale by a hamming window
        gate_array = raw_gate_array * window_func
    else:
        scaled_p = p
        gate_array = raw_gate_array

    amps = np.fft.rfft(scaled_p)
    freqs = np.fft.rfftfreq(n, d=timestep)
    new_amps = np.zeros_like(amps)

    for i in range(len(amps)):
        # Filter out the noise with amp_cutoff
        if np.absolute(amps[i] / n) >= gate_array[i]:
            if cutoff == -1 or freqs[i] < cutoff:
                k = omega_to_k(freqs[i] * 2 * np.pi, H[i])
                # Scale, applying the diffusion relation
                a = pressure_to_eta(amps[i], k, z, H[i])
                new_amps[i] = a
    # Convert back to time space
    eta = np.fft.irfft(new_amps)
    if window:
        eta = eta / window_func
    return eta


def _frequency_to_index(f, n, timestep):
    """Gets the index of a frequency in np.fftfreq.

    f -- the desired frequency
    n -- the length given to fftfreq
    sample_freq -- the sampling frequency
    """
    return np.round(n * f * timestep)


def omega_to_k(omega, H):
    """Gets the wave number from the angular frequency using the dispersion
    relation for water waves and Newton's method."""
    f = lambda k: omega**2 - k * g * np.tanh(k * H)
    return newton(f, 0)


def k_to_omega(k, H):
    """Takes the wave number and water depth as arguments, returns the
    angular frequency."""
    return np.sqrt(k * g * np.tanh(k * H))


def pressure_to_eta(del_p, k, z, H):
    """Converts the non-hydrostatic pressure to height above z=0."""
    c = _coefficient(k, z, H)
    return del_p / c


def eta_to_pressure(eta, k, z, H):
    c = _coefficient(k, z, H)
    return eta * c


def _coefficient(k, z, H):
    """Returns C, a coefficient to transform pressure to eta and vice versa."""
    return rho * g * np.cosh(k * (H + z)) / np.cosh(k * H)

def method2(p_dbar):
    """Downward crossing method: if the function crosses the x axis in
    an interval and if its endpoint is below the x axis, we've found
    a new wave."""
    p = p_dbar * 1e4            # convert to Pascals
    Pstatic = make_pstatic(p)
    Pwave = p - Pstatic
    depth = Pstatic / (rho * g)
    start = period = counter = Pmin = Pmax = 0
    periods = []  # periods of found waves
    eta = np.zeros(len(Pwave))
    interval = 1 / 4
    steepness = 0.03
    Hminimum = 0.10
    H = []

    for i in range(len(Pwave) - 1):
        if Pwave[i] > 0 and Pwave[i+1] < 0:
            periods.append(period)
            # w**2 = g * k, the dispersion relation for deep water
            wavelength = g * period**2 / (2 * np.pi)
            # if the water is too shallow
            if depth[i] / wavelength < 0.36:
                wavelength = ((g * depth[i])**(1/2) *
                              (1 - depth[i] / wavelength) *
                              period)
                height = (((Pmax - Pmin) / (rho * g)) *
                          np.cosh(2 * np.pi * depth[i] /
                                  wavelength))
            H.append(height)
            Hunreduced = Hreduced = height
            if height / wavelength > steepness:
                Hreduced = steepness * wavelength
                H.append(Hreduced)
            if height < Hminimum:
                H.pop()
                Hreduced = Hminimum
                counter -= 1
            if str(wavelength) == 'nan':
                H.pop()
            reduction = Hreduced / Hunreduced
            for j in range(start, i):
                eta[j] = ((Pwave[j] * reduction) / (rho * g)) * \
                         np.cosh(2 * np.pi * depth[j] / wavelength)
            start = i + 1
            period = Pmax = Pmin = 0
            counter += 1
        period = period + interval
        if Pwave[i] > Pmax:
            Pmax = Pwave[i]
        if Pwave[i] < Pmin:
            Pmin = Pwave[i]

    return eta + depth


def make_pstatic(p):
    x = np.arange(len(p))
    slope, intercept = np.polyfit(x, p, 1)
    pwave = slope * x + intercept
    return pwave
