# -*- coding: utf-8 -*-
"""
Created on Thu Aug  7 08:20:07 2014

@author: cmazzullo

Inputs: One netCDF file containing water pressure and one containing
air pressure.

Outputs: One netCDF file containing water pressure, interpolated air
pressure, and water level.
"""


import SpectralAnalysis.nc as nc
import shutil
import DepthCalculation.pressure_to_depth as p2d
import numpy as np

def make_depth_file(water_fname, air_fname, out_fname, depth_method='fft'):
    # get time series for air and water pressure
    device_depth = -1 * nc.get_device_depth(water_fname)
    water_depth = nc.get_water_depth(water_fname)
    timestep = 1 / nc.get_frequency(water_fname)
    sea_pressure = nc.get_pressure(water_fname)
    sea_time = nc.get_time(water_fname)
    raw_air_pressure = nc.get_air_pressure(air_fname)
    air_time = nc.get_time(air_fname)

    air_pressure = np.interp(sea_time, air_time, raw_air_pressure)
    corrected_pressure = sea_pressure - air_pressure

    if depth_method == 'fft':
        depth = p2d.fft_method(sea_time, corrected_pressure,
                               device_depth, water_depth, timestep)
    elif depth_method == 'method2':
        depth = p2d.method2(sea_pressure)
    elif depth_method == 'naive':
        depth = p2d.hydrostatic_method(sea_pressure)
    else:
        raise TypeError('Accepted values for depth_method are: fft, '
                        'method2 and naive.')
    print(len(sea_pressure), len(depth))
    shutil.copy(water_fname, out_fname)
    nc.append_air_pressure(out_fname, air_pressure)
    nc.append_corrected_water_pressure(out_fname, corrected_pressure)
    nc.append_depth(out_fname, depth)
    print('Success!')


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import netCDF4
    # testing
    sea_fname = ('C:\\Users\\cmazzullo\\wave-sensor-test-data\\test-ncs\\'
                 'logger3.csv.nc')
    air_fname = ('C:\\Users\\cmazzullo\\wave-sensor-test-data\\test-ncs\\'
                 'logger3_air.nc')
    out_fname = 'C:\\Users\\cmazzullo\\Desktop\\script2_output.nc'
    import os
    if os.path.exists(out_fname):
        os.remove(out_fname)

    make_depth_file(sea_fname, air_fname, out_fname, depth_method='naive')

    depth = nc.get_depth(out_fname)
    air_p = nc.get_air_pressure(out_fname)
    sea_p = nc.get_pressure(out_fname)
    corrected_p = nc.get_corrected_pressure(out_fname)
    time = nc.get_time(out_fname)

    plt.plot(time, air_p, color='y', label='Air pressure')
    plt.plot(time, sea_p, color='b', label='Water pressure')
    plt.plot(time, depth, color='r', label='Depth')
    #plt.plot(time, corrected_p, color='r', label='Corrected water pressure')
    plt.legend()
    plt.show()

    f = netCDF4.Dataset(out_fname, 'r', format='NETCDF4_CLASSIC')
    print(f.variables['air_pressure'])
    print(f.variables['sea_water_pressure'])
    print(f.variables['sea_water_pressure_due_to_sea_water'])
    print(f.variables['depth'])
    print(f.device_depth)
    f.close()
