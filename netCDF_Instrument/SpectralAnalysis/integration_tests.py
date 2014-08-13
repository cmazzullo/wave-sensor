# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 08:48:12 2014

@author: Chris Mazzullo

Tests for the parts of the project concerned with reading raw pressure from
netCDFs, converting it to water level, and writing the results to netCDF.
"""
import numpy as np
import matplotlib.pyplot as plt
import SpectralAnalysis.nc as nc
import DepthCalculation.pressure_to_depth as p2d


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
    return p #- rho * g * z


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
    """Writes a netCDF file containing pressure data corresponding to a wave
    combination."""
    p = make_test_pressure(z, H, t, *waves)
    nc.write(fname, t, p)


def rmse_by_amp_cutoff(amp_cutoffs, z, H, timestep, t, waves):
    """Makes a plot of the root mean squared error as a function of the
    amp_cutoff variable, which serves as a noise gate."""
    real_eta = make_test_height(t, H, *waves)
    p = make_test_pressure(z, H, t, *waves)
    rmse_array = []
    for c in amp_cutoffs:
        calc_wave_height = p2d.pressure_to_depth(t, p, z, H, timestep, c)
        calc_eta = calc_wave_height + z
        error = abs(real_eta - calc_eta)
        rmse = np.sqrt(sum(error**2) / len(error))
        rmse_array.append(rmse)
    return rmse_array


def compare_methods():
    """Draws a plot comparing downward crossing method and fft method."""
    # Constants
    z = -10  # depth of the sensor in meters
    H = 3  # water depth in meters
    timestep = .25
    amp_cutoff = 50  # helps reduce the tearing at the edges of the interval
    t = np.arange(0, 300, timestep)  # time in seconds
    # tuple containing wave coefficients
    waves = ((1, .001, 0), (.5, .01, 1), (.3, .1, 0), (1, 1, 2))

    real_eta = make_test_height(t, H, *waves)  # Hopefully our script can get
                                               # this from the netCDF

    fname = 'integration_test_output.nc'
    make_test_netcdf(fname, t, z, H, waves)

    # Now we need to compare real_z and what our program thinks z is
    out_p = nc.get_pressure(fname)
    calc_wave_height = p2d.pressure_to_depth(t, out_p, z, H, timestep,
                                             amp_cutoff)
    calc_eta = calc_wave_height + z

    error = abs(real_eta - calc_eta)
    rmse = np.sqrt(sum(error**2) / len(error))
    print('RMSE =', rmse)

    plt.plot(t, real_eta, color='b', label='Real eta')
    plt.plot(t, calc_eta, color='g', label='Calculated eta')
    plt.plot(t, error, color='r', label='Error')
    plt.legend()


def frequency_to_index(f, n, timestep):
    """Gets the index of a frequency in np.fftfreq.

    f -- the desired frequency
    n -- the length given to fftfreq
    sample_freq -- the sampling frequency
    """
    return np.round(n * f * timestep)


def run_test_real_data(fname):
    """Reads pressure data from a netCDF and plots the approximate water
    level."""
    # Constants
    z = -10  # depth of the sensor in meters
    H = 30  # water depth in meters
    timestep = .25
    amp_cutoff = 50  # helps reduce the tearing at the edges of the interval

    t = nc.get_time(fname)

    timestep = (t[1] - t[0]) / 1e3
    print(timestep)
#    p = nc.get_pressure(fname)

    p = make_test_pressure(z, H, t, *waves)
    print(np.shape(p))
    #plt.plot(t, p)
    low = frequency_to_index(.01, len(p), timestep)  # in Hz
    high = frequency_to_index(1, len(p), timestep)  # in Hz

    p_amp = np.fft.rfft(p)[low:high] / len(p)
    freq_bins = np.fft.rfftfreq(len(p), d=timestep)[low:high]
    plt.plot(freq_bins, p_amp)
    plt.show()
    calc_wave_height = p2d.pressure_to_depth_windowing(t, p, z, H, timestep,
                                                       amp_cutoff)
    calc_eta = calc_wave_height + z
#    plt.plot(t, calc_eta, color='g', label='Calculated eta')

def run_test():
    # Constants
    z = -10  # depth of the sensor in meters
    H = 30  # water depth in meters
    timestep = .25
    t = np.arange(0, 600, timestep)  # time in seconds
    # tuple containing wave coefficients (A, k, phase)
    waves = ((1, .005, 0), (.5, .01, 1), (.5, .001, 0), (.5, .08, 2))

    real_eta = make_test_height(t, H, *waves)  # Hopefully our script can get
                                               # this from the netCDF
    p_pascals = make_test_pressure(z, H, t, *waves)
    p = p_pascals / 1e4
    eta_window = p2d.fft_method(t, p, z, H, timestep,
                                       window=True, gate=30, cutoff=1)
    eta = p2d.fft_method(t, p, z, H, timestep, gate=80, cutoff=1)
    n = p2d.hydrostatic_method(p)

    def rmse(real, calc):
        error = abs(real - calc)
        return np.sqrt(sum(error**2) / len(error))

    window_rmse = rmse(real_eta, eta_window)
    nowindow_rmse = rmse(real_eta, eta)
    nrmse = rmse(real_eta, n)

    print('window rmse =', window_rmse)
    print('no window rmse =', nowindow_rmse)
    print('naive rmse =', nrmse)

    plt.plot(t, real_eta, 'b', label='Real eta')
    plt.plot(t, eta_window, 'r', label='Calculated eta with windowing')
    #plt.plot(t, eta, 'y', label='Calculated eta')
    plt.plot(t, n, 'y', label='Naive eta')
    plt.legend()
    plt.show()


def dbar_to_pascals(p):
    return p * 1e4


if __name__ == '__main__':
    run_test()
    fname = ('C:\\Users\\cmazzullo\\wave-sensor-test-data\\'
             'logger3.csv.nc')
    print('hello')
    #run_test_real_data(fname)
