#!/usr/bin/env python3
"""
Created on Thu Aug  7 08:20:07 2014

@author: cmazzullo

Inputs: One netCDF file containing water pressure and one containing
air pressure.

Outputs: One netCDF file containing water pressure, interpolated air
pressure, and water level.
"""


import numpy as np
import shutil
import pressure_to_depth as p2d
import NetCDF_Utils.nc as nc
import NetCDF_Utils.Testing as tests

def make_depth_file(water_fname, air_fname, out_fname, method='fft'):
    """Adds depth information to a water pressure file.

    The argument air_fname is optional, when set to '' no air
    pressure is used.
    """
    device_depth = -1 * nc.get_device_depth(water_fname)
    water_depth = nc.get_water_depth(water_fname)
    timestep = 1 / nc.get_frequency(water_fname)
    sea_pressure = nc.get_pressure(water_fname)
    print('sea_pressure len')
    print(len(sea_pressure))
    sea_time = nc.get_time(water_fname)
    sea_qc = nc.get_pressure_qc(water_fname)
    test = tests.DataTests()
    if air_fname != '':
        raw_air_pressure = nc.get_air_pressure(air_fname)
        air_time = nc.get_time(air_fname)
        air_pressure = np.interp(sea_time, air_time, raw_air_pressure,
                                 left=nc.FILL_VALUE, right=nc.FILL_VALUE)
        corrected_pressure = sea_pressure - air_pressure
       
        test.pressure_data = air_pressure
        air_qc = test.select_tests('depth')
        nc.append_depth_qc(out_fname, air_qc)
    else:
        corrected_pressure = sea_pressure

    if method == 'fft':
        depth = p2d.fft_method(corrected_pressure, device_depth,
                               water_depth, timestep)
    elif method == 'combo':
        depth = p2d.combo_method(sea_time, corrected_pressure,
                                 device_depth, water_depth, timestep)
    elif method == 'naive':
        depth = p2d.hydrostatic_method(corrected_pressure)
    else:
        raise TypeError('Accepted values for "method" are: fft, '
                        'method2 and naive.')
    if len(depth) == len(sea_pressure) - 1:
        depth = np.append(depth, np.NaN)

    print('len depth:')
    print(len(depth))

    shutil.copy(water_fname, out_fname)
    if air_fname != '':
        nc.append_air_pressure(out_fname, air_pressure)
        
        #air_qc and depth qc
        air_qc = test.select_tests('')
        nc.append_depth_qc(out_fname, sea_qc, air_qc)
    nc.append_depth(out_fname, depth)
