#!/usr/bin/env python3
"""
Created on Mon Aug  4 08:48:12 2014

@author: Chris Mazzullo

Provides methods to convert water pressure into water depth.
"""

import numpy as np
import unit_conversion as uc
from scipy import signal

# Constants
GRAVITY = uc.GRAVITY  
WATER_DENSITY = uc.WATER_DENSITY
FILL_VALUE =  uc.FILL_VALUE


def combo_method(time, pressure, device_d, water_d, tstep = 4):
    """Convert pressure series into depth series using fft method."""
    
    #this creates a split for each fill value since the fourier functions
    #handle fill values gracefully
#     split_idx = (pressure == FILL_VALUE)
#     idx = np.where(split_idx[1:] ^ split_idx[:-1])[0] + 1

    #for the purposes of our method we will take windows of every 4096 amounting to 17 minutes and whatever seconds
    #in order to maximize the i utility of the fourier functions
    increment_size = 2048
    current_start_index = 0
    current_end_index = 4096
    series_len = len(time)
    len_finished = False
    dchunks, tchunks = [], []
    
    
    while len_finished == False:

        device_chunk = device_d[current_start_index, current_end_index]
        p_chunk = pressure[current_start_index, current_end_index]
        t_chunk = time[current_start_index, current_end_index]
        h_chunk = water_d[current_start_index, current_end_index]
         
        device_d_average = np.average(device_chunk)
        #removing the linear trend
        coeff = np.polyfit(t_chunk, p_chunk, 1)
        static_p = coeff[1] + coeff[0]*t_chunk
        wave_p = p_chunk - static_p
         
        #applying linear wave theory to the wave and device slices
        wave_y = pressure_to_depth_lwt(wave_p, device_d_average, h_chunk, tstep)
        wave_y = np.pad(wave_y, (0, len(t_chunk) - len(wave_y)), mode='edge')
        dchunks.append(hydrostatic_method(static_p) + wave_y)
        tchunks.append(t_chunk)
        
        if current_end_index >= series_len:
            len_finished = True
            
        current_start_index += increment_size
        current_end_index += increment_size
    return (dchunks,tchunks)


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


def omega_to_k(omega, h):
    """Converts angular frequency to wavenumber for water waves.
    Using Lo approximation
    Approximation to the dispersion relation, Fenton and McKee (1989)."""
    T = 2 * np.pi / omega
    print(T)
    Lo = GRAVITY * T**2 / (2 * np.pi)
    l = Lo * np.tanh(((2 * np.pi)*((np.sqrt( h / GRAVITY))/T))**(3/4))**(2/3)
    
    return np.nan_to_num(2 * np.pi / l) # nan at omega = 0 (low freq limit)

def echart_omega_to_wavenumber(omega, h):
    ke =  omega/(GRAVITY*np.sqrt(np.tanh(h*(omega/GRAVITY))))
    return np.nan_to_num(2 * np.pi / ke)


def pressure_to_depth_lwt(p_dbar, device_d, water_d, tstep, hi_cut='auto'):
    """Create wave height data from an array of pressure readings."""
    if hi_cut == 'auto':
        hi_cut = auto_cutoff(water_d)
        
    #Get the average of the water_d time seires
    #*still need to establish relation to land surface elevation and sensor orifice elevation
    water_d = np.average(water_d)
    surface_height = hydrostatic_method(np.average(p_dbar))
    water_d = water_d - surface_height
    
    #create window to multiply by pressure time series to reduce gibbs effect and other ringing noise artifacts
    trimmed_p = trim_to_even(p_dbar)
    window = np.hamming(len(trimmed_p))
    scaled_p = trimmed_p * 1e4 * window
    
    #perform real fourier function on the scaled pressure and get the frequencies
    p_amps = np.fft.rfft(scaled_p)
    freqs = np.fft.rfftfreq(len(trimmed_p), d=tstep)
    
    #get the wave numbers by applying properties of the dispersion relation
    wavenumbers = omega_to_k(2 * np.pi * freqs, water_d)
    
    #convert scaled pressure to water level and converting any value above the cutoff to zero
    d_amps = pressure_to_eta(p_amps, wavenumbers, device_d, water_d)
    d_amps[np.where(freqs >= hi_cut)] = 0
    return np.fft.irfft(d_amps) / window


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

def eta_to_pressure(a, omega, k, z, H, t): 
    
    return WATER_DENSITY * ((a*omega**2)/k)*(np.cosh(k*(z+H))/np.sinh(k*H)) \
        * (np.cos(omega*t)) - (WATER_DENSITY*GRAVITY*z)
       
def lowpass_filter(data):
    '''Performs a butterworth filter of order 4 with a 1 min cutoff'''
    fs = 4 
    cutoff = .0166666665
#     cutoff = .0001
    
    lowcut = cutoff / (.5 * fs)
        
    b, a = signal.butter(4, [lowcut], btype='lowpass')

    filtered_data = signal.filtfilt(b, a, data)
   
    return filtered_data

    

