# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 08:48:12 2014

@author: Chris Mazzullo
"""
import numpy as np
import matplotlib.pyplot as plt
import Analysis.nc as nc
from scipy.optimize import newton
from Analysis.method2 import get_wave_data_method2


# Constants
g = 9.8  # gravity (m / s**2)
rho = 1030  # density of seawater (kg / m**3)


def make_test_pressure(z, H, t, *args):
    """Takes time array t and any number of wave arguments. Eta is wave height.
    
    Wave arguments are tuples of the form:
    
            (A, k, phase)
        
    where A is the amplitude, k is the wave number and phase is the phase 
    shift. The output will be the sum of all of the waves.
    
    Returns the pressure at elevation z: 0 is at the water's surface, -H is on
    the ocean floor.
    """
    p = np.zeros_like(t)
    for arg in args:
        A = arg[0]
        k = arg[1]
        phase = arg[2]
        omega = k_to_omega(k, H)
        eta = A * np.cos(omega * t + phase)
        p += eta_to_pressure(eta, k, z, H)
    return p + hydrostatic_pressure(z)


def make_test_height(t, *args):
    """Takes an arbitary number of arguments, one for each wave. 
    
    Arguments are tuples of the form: 
    
        (A, k, phase)
        
    where A is the amplitude, k is the wave number and phase is the phase 
    shift. The output will be the sum of all of the waves.
    
    The equation used to make waves is:
    
        A * np.cos(omega * t + phase)
    """
    total = np.zeros_like(t)

    for arg in args:
        A = arg[0]
        k = arg[1]
        phase = arg[2]
        omega = k_to_omega(k, H)
        eta = A * np.cos(omega * t + phase)
        total += eta
    return total
        
        
def eta_to_pressure(eta, k, z, H):
    """Converts eta, the height above the baseline water height, to pressure.
    
    Note: This is just the pressure caused by the wave, and doesn't take into
    account the hydrostatic pressure given by -rho*g*z.
    """
    c = coefficient(k, z, H)
    return eta * c
    
    
def pressure_to_eta(del_p, k, z, H):
    """Converts the non-hydrostatic pressure to height above z=0."""
    c = coefficient(k, z, H)
    return del_p / c
    
    
def coefficient(k, z, H):
    """Returns C, a coefficient to transform pressure to eta and vice versa."""
    return rho * g * np.cosh(k * (H + z)) / np.cosh(k * H)
    

def hydrostatic_pressure(z):
    return rho * g * z * (-1)
    
    
def k_to_omega(k, H):
    """Takes the wave number and water depth as arguments, returns the 
    angular frequency."""
    return np.sqrt(k * g * np.tanh(k * H))


def omega_to_k(omega, H):
    """Gets the wave number from the angular frequency using the dispersion 
    relation for water waves and Newton's method."""
    f = lambda k: omega**2 - k * g * np.tanh(k * H)
    return newton(f, 0)
 
    
def make_test_netcdf(fname, t, z, H, waves):
    p = make_test_pressure(z, t, *waves)
    nc.write(fname, t, p)


# This is maybe a bad idea
def make_height_data(t, p, z, H, timestep, amp_cutoff):
    """Takes an array of pressure readings and creates wave height data.
    
    t -- the time array
    p -- an array of pressure readings such that len(t) == len(p)
    timestep -- the time interval in between pressure readings
    amp_cutoff -- any fluctuations in the pressure that are less than this
                  threshold won't be used in the height data. 
    """
    sample_freq = 1 / timestep
    nyquist = sample_freq / 2
    amps = np.fft.rfft(p)
    freqs = np.fft.rfftfreq(len(p), d=timestep)
    newamps = np.zeros_like(amps)
    ks = []
    for i in range(len(amps)):
        if np.absolute(amps[i] / len(p)) < amp_cutoff:
            newamps[i] = 0
        else:
            k = omega_to_k(freqs[i] * 2 * np.pi, H)
            ks.append(coefficient(k, z, H))
            newamps[i] = pressure_to_eta(amps[i], k, z, H)

    eta = np.fft.irfft(newamps)    
    return eta


# This doesn't work right now
def make_height_data_zero_crossings(t, p, z, H, timestep):
    """Calculates eta using zero crossings and the dispersion relation."""
    zero_crossings = [i for i in range(len(p) - 1) 
                      if p[i] > 0 and p[i + 1] < 0]
    eta = np.zeros_like(t)
    for start, end in zip(zero_crossings[:-1], zero_crossings[1:]):
        period = (end - start) * timestep
        omega = 2 * np.pi / period
        k = omega_to_k(omega, H)
    return eta
    

def rmse_by_amp_cutoff(amp_cutoff, z, H, timestep, t, waves):
    real_eta = make_test_height(t, *waves)
    p = make_test_pressure(z, H, t, *waves)
    rmse_array = []
    for c in amp_cutoff:
        calc_wave_height = make_height_data(t, p, z, H, timestep, c)
        calc_eta = calc_wave_height + z
        error = abs(real_eta - calc_eta)
        rmse = np.sqrt(sum(error**2) / len(error))
        rmse_array.append(rmse)
    return rmse_array
        
        
def plot_rmse_by_cutoff(z, H, timestep, t, waves):
    x = np.arange(1, 1000, 1)
    rmse = rmse_by_amp_cutoff(x, z, H, timestep, t, waves)
    return rmse
    
    
if __name__ == '__main__':
    # Constants
    z = -10  # depth of the sensor in meters
    H = 30  # water depth in meters
    timestep = .25
    amp_cutoff = 3  # helps reduce the tearing at the edges of the interval
    t = np.arange(0, 3000, timestep)  # time in seconds
    waves = ((1, .001, 0),(.5, .01, 1))  # tuple containing wave coefficients


    real_eta = make_test_height(t, *waves)  # Hopefully our script can get 
                                            # this from the netCDF
    
    p = make_test_pressure(z, H, t, *waves)

    fname = 'integration_test_output.nc'
    nc.write(fname, t, p)  # saves 'known' pressure data
    
    # Now we need to compare real_z and what our program thinks z is

    out_p = nc.read(fname)
    
    calc_wave_height = make_height_data(t, p, z, H, timestep, amp_cutoff)
    calc_eta = calc_wave_height + z
    
    error = abs(real_eta - calc_eta)
    rmse = np.sqrt(sum(error**2) / len(error))
    print('RMSE =', rmse)

    # Plotting
    plot = True
#    plt.plot(real_eta - z)
#    plt.title('Real wave height')
#    plt.show()
#    plt.plot(out_p)
#    plt.title('Real wave pressure')
#    plt.show()
#    plt.plot(t, calc_eta)
#    plt.title('Calculated wave height')
#    plt.show()
    if plot:
        plt.plot(t, real_eta, color='b', label='Real eta')
        plt.plot(t, calc_eta, color='g', label='Calculated eta')
        plt.plot(t, error, color='r', label='Error')
        plt.legend()
    #rmse_array = plot_rmse_by_cutoff(z, H, timestep, t, waves)
