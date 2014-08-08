# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 08:48:12 2014

@author: Chris Mazzullo
"""
import numpy as np
from scipy.optimize import newton

# Constants
g = 9.8  # gravity (m / s**2)
rho = 1030  # density of seawater (kg / m**3)

      
def pressure_to_depth(t, p_dbar, z, H, timestep, gate=0, window=False, 
                      cutoff=-1):
    """Takes an array of pressure readings and creates wave height data.
    
    t -- the time array
    p -- an array of pressure readings such that len(t) == len(p)
    timestep -- the time interval in between pressure readings
    amp_cutoff -- any fluctuations in the pressure that are less than this
                  threshold won't be used in the height data. 
    """
    # Put the pressure data into frequency space
    p = p_dbar * 1e4
    n = len(p)
    
    if window:
        window_func = np.hamming(n)
        scaled_p = p * window_func  # scale by a hamming window function
    else:
        scaled_p = p
        
    amps = np.fft.rfft(scaled_p)
    freqs = np.fft.rfftfreq(n, d=timestep)
    new_amps = np.zeros_like(amps)
    
    for i in range(len(amps)):
        # Filter out the noise with amp_cutoff
        if np.absolute(amps[i] / n) >= gate:
            if cutoff == -1 or freqs[i] < cutoff:
                k = omega_to_k(freqs[i] * 2 * np.pi, H)
                # Scale, applying the diffusion relation
                a = pressure_to_eta(amps[i], k, z, H)
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