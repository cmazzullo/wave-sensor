# -*- coding: utf-8 -*-
"""
Created on Thu Aug  7 08:20:07 2014

@author: cmazzullo

Inputs: One netCDF file containing water pressure and one containing
air pressure.

Outputs: One netCDF file containing water pressure, interpolated air
pressure, and water level.
"""

import NetCDF_Utils.slurp as slurp
import numpy as np
import matplotlib.pyplot as plt
import SpectralAnalysis.nc as nc
import shutil
import netCDF4
from TimeDomainAnalysis.time_domain import Time_Domain_Analysis
import DepthCalculation.pressure_to_depth as p2d


def make_depth_file(in_fname, out_fname, station, depth_method='crossings'):
    shutil.copy(in_fname, out_fname)
    
    initial_pressure = nc.get_initial_pressure(in_fname)  # pressure inside the device
    water_depth = nc.get_water_depth(in_fname)
    # Watch out for this negative sign!:
    device_depth = nc.get_device_depth(in_fname) * -1
    
    air_pressure, lat, lon = slurp.get_air_pressure(in_fname, station)
    time = nc.get_time(in_fname)
    sea_pressure = nc.get_pressure(out_fname)
    corrected_pressure = sea_pressure + initial_pressure - air_pressure
    
    # DOESN'T WORK YET!    
    if depth_method == 'crossings':
        td = Time_Domain_Analysis()
        depth = td.method2()
    elif depth_method == 'fft':
        timestep = 1 / nc.get_frequency(in_fname)
        depth = p2d.pressure_to_depth(time, corrected_pressure, device_depth, 
                                  water_depth, timestep, gate=.025, window=True)
    
    
    nc.append_air_pressure(out_fname, air_pressure, station, lat, lon)
    nc.append_corrected_water_pressure(out_fname, corrected_pressure)
    nc.append_depth(out_fname, depth)
    print('Success!')


if __name__ == '__main__':
    # testing
    in_fname = ('C:\\Users\\cmazzullo\\wave-sensor-test-data\\'
         'logger3.csv.nc')
    out_fname = 'C:\\Users\\cmazzullo\\Desktop\\script2_output.nc'
    station = 8454000
    depth_method='fft'

    make_depth_file(in_fname, out_fname, station, depth_method=depth_method)
    
    depth = nc.get_depth(out_fname)
    air_p = nc.get_air_pressure(out_fname)
    sea_p = nc.get_pressure(out_fname)
    corrected_p = nc.get_corrected_pressure(out_fname)
    time = nc.get_time(out_fname)
    
    plt.plot(time, air_p, color='y', label='Air pressure')
    plt.plot(time, sea_p, color='b', label='Water pressure')
    plt.plot(time, depth, color='purple', label='Depth')
    plt.plot(time, corrected_p, color='r', label='Corrected water pressure')
    plt.legend()
    plt.show()
    
    f = netCDF4.Dataset(out_fname, 'r', format='NETCDF4_CLASSIC')
    print(f.variables['air_pressure'])
    print(f.variables['sea_water_pressure'])
    print(f.variables['sea_water_pressure_due_to_sea_water'])
    print(f.variables['depth'])

    print(f.water_depth)
    print(f.device_depth)
    print(f.initial_pressure)
    f.close()