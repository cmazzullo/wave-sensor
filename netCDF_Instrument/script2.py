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

in_fname = ('C:\\Users\\cmazzullo\\wave-sensor-test-data\\'
         'logger3.csv.nc')
out_fname = 'C:\\Users\\cmazzullo\\Desktop\\script2_output.nc'
station = 8454000


shutil.copy(in_fname, out_fname)

air_pressure, lat, lon = slurp.get_air_pressure(in_fname, station)

sea_pressure = nc.get_pressure(out_fname)
corrected_pressure = sea_pressure - air_pressure

nc.append_air_pressure(out_fname, air_pressure, station, lat, lon)
nc.append_corrected_water_pressure(out_fname, corrected_pressure)
print('Success!')

air_p = nc.get_air_pressure(out_fname)
sea_p = nc.get_pressure(out_fname)
corrected_p = nc.get_corrected_pressure(out_fname)
time = nc.get_time(out_fname)


# testing

plt.plot(time, air_p, color='y', label='Air pressure')
plt.plot(time, sea_p, color='b', label='Water pressure')
plt.plot(time, corrected_p, color='r', label='Corrected water pressure')
plt.legend()
plt.show()

f = netCDF4.Dataset(out_fname, 'r', format='NETCDF4_CLASSIC')
print(f.variables['air_pressure'])
print(f.variables['sea_water_pressure'])
print(f.variables['sea_water_pressure_due_to_sea_water'])
f.close()