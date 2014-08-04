# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 08:48:12 2014

@author: Chris Mazzullo
"""
import numpy as np
import matplotlib.pyplot as plt
import Analysis.nc as nc

g = 9.8  # gravity (m / s**2)
rho = 1030  # density of seawater (kg / m**3)



def make_test_pressure(z, t, *args):
    """Takes time array t and any number of wave arguments.
    
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
        omega = get_frequency(k, H)
        
        p += ((rho * A * omega**2 / k) * 
        (np.cosh(k * (z + H)) / np.sinh(k * H)) * 
        np.cos(omega * t + phase) - rho * g * z)
    return p


def make_test_height(t, *args):
    """Takes an arbitary number of arguments, one for each wave. 
    
    Arguments are tuples of the form: 
    
        (A, k, phase)
        
    where A is the amplitude, k is the wave number and phase is the phase 
    shift. The output will be the sum of all of the waves."""
    result = np.zeros_like(t)
    print(args)
    print(*args)
    for arg in args:
        A = arg[0]
        k = arg[1]
        phase = arg[2]
        omega = get_frequency(k, H)
        result += A * np.sin(omega * t + phase)
    return result
        
        
def eta_to_pressure(eta, k, z, H):
    """Converts eta, the height above the baseline water height, to pressure.
    
    Note: This is just the pressure caused by the wave, and doesn't take into
    account the hydrostatic pressure given by -rho*g*z."""
    return rho * g * eta * np.cosh(k * (H * z)) / np.cosh(k * H)
    
    
def pressure_to_eta(del_p, k, z, H):
    """Converts the non-hydrostatic pressure to height above z=0."""
    return (del_p / rho * g) * np.cosh(k * H) / np.cosh(k * (H + z))
    
    
def k_to_omega(k, H):
    """Takes the wave number and water depth as arguments, returns the 
    angular frequency."""
    return np.sqrt(k * g * np.tanh(k * H))


def make_test_netcdf(fname, t, z, H, waves):
    p = make_test_pressure(z, t, *waves)
    nc.write(fname, t, p)


if __name__ == '__main__':
    H = 30  # water depth in meters
    z = -10  # depth of the sensor in meters
    t = np.arange(0, 300, .5)  # time in seconds
    waves = ((2, .01, 0), (1, .05, 1))  # tuple containing wave coefficients

    real_z = make_test_height(t, *waves)  # Hopefully our script can get 
                                          # this from the netCDF
    
    p = make_test_pressure(z, t, *waves)
    
    fname = 'integration_test_output.nc'
    nc.write(fname, t, p)  # saves 'known' pressure data
    
    # Now we need to compare real_z and what our program thinks z is

    out_p = nc.read(fname)