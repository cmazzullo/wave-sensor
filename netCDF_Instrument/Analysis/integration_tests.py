# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 08:48:12 2014

@author: Chris Mazzullo
"""
import numpy as np
import matplotlib.pyplot as plt
import Analysis.nc as nc
import DepthCalculation.pressure_to_depth as p2d
import netCDF4
import shutil


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
        omega = p2d.k_to_omega(k, H)
        eta = A * np.cos(omega * t + phase)
        p += p2d.eta_to_pressure(eta, k, z, H)
    return p - rho * g * z


def make_test_height(t, H, *args):
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
        omega = p2d.k_to_omega(k, H)
        eta = A * np.cos(omega * t + phase)
        total += eta
    return total


def make_test_netcdf(fname, t, z, H, waves):
    p = make_test_pressure(z, t, *waves)
    nc.write(fname, t, p)


def rmse_by_amp_cutoff(amp_cutoff, z, H, timestep, t, waves):
    real_eta = make_test_height(t, *waves)
    p = make_test_pressure(z, H, t, *waves)
    rmse_array = []
    for c in amp_cutoff:
        calc_wave_height = p2d.pressure_to_depth(t, p, z, H, timestep, c)
        calc_eta = calc_wave_height + z
        error = abs(real_eta - calc_eta)
        rmse = np.sqrt(sum(error**2) / len(error))
        rmse_array.append(rmse)
    return rmse_array
        
        
def plot_rmse_by_cutoff(z, H, timestep, t, waves):
    x = np.arange(1, 1000, 1)
    rmse = rmse_by_amp_cutoff(x, z, H, timestep, t, waves)
    return rmse
    
    
def run_test():
    # Constants
    z = -10  # depth of the sensor in meters
    H = 30  # water depth in meters
    timestep = .25
    amp_cutoff = 40  # helps reduce the tearing at the edges of the interval
    t = np.arange(0, 300, timestep)  # time in seconds
    # tuple containing wave coefficients
    waves = ((1, .001, 0), (.5, .01, 1), (.3, .1, 0), (1, .0001, 1))  

    real_eta = make_test_height(t, H, *waves)  # Hopefully our script can get 
                                               # this from the netCDF

    p = make_test_pressure(z, H, t, *waves)

    fname = 'integration_test_output.nc'
    nc.write(fname, t, p)  # saves 'known' pressure data
    
    # Now we need to compare real_z and what our program thinks z is
    out_p = nc.get_pressure(fname)
    calc_wave_height = p2d.pressure_to_depth(t, out_p, z, H, timestep, amp_cutoff)
    calc_eta = calc_wave_height + z
    
    error = abs(real_eta - calc_eta)
    rmse = np.sqrt(sum(error**2) / len(error))
    print('RMSE =', rmse)

    plt.plot(t, real_eta, color='b', label='Real eta')
    plt.plot(t, calc_eta, color='g', label='Calculated eta')
    plt.plot(t, error, color='r', label='Error')
    plt.legend()


def dbar_to_pascals(p):
    return p * 1e4
    
    
if __name__ == '__main__':
    in_fname = ('C:\\Users\\cmazzullo\\wave-sensor-test-data\\'
             'height.nc')
    out_fname = ('C:\\Users\\cmazzullo\\wave-sensor-test-data\\'
             'logger3_height.csv.nc')
             
    shutil.copy(in_fname, out_fname)    
    data = netCDF4.Dataset(in_fname, 'r', format="NETCDF4_CLASSIC")
    p = dbar_to_pascals(data.variables['sea_water_pressure'][:])
    t = data.variables['time'][:]
    
    
    # Analysis

    z = -5
    timestep = .25
    H = 20
    cutoff = 3
    data.close()
    

    writer = netCDF4.Dataset(in_fname, 'a', format='NETCDF4_CLASSIC')
    wave_height = writer.createVariable('wave_height','f4',('time',))
    wave_height.units = 'meters'
    cutoff = 3
    height = p2d.pressure_to_depth(t, p, z, H, timestep, cutoff)
    wave_height[:] = height
    writer.close()
    #plt.plot(t, p)
    #plt.plot(t, height, color='y')
#    plt.plot(t, height, color='r')