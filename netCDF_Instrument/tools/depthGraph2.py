'''
Created on Nov 20, 2015

@author: Gregory
'''
import NetCDF_Utils.nc as nc
import numpy as np
from matplotlib import pyplot as plt

file_name = "depth4.nc"

time = nc.get_time(file_name)
sea_pressure = nc.get_pressure(file_name)
air_pressure = nc.get_air_pressure(file_name)

plt.plot(time,sea_pressure)
plt.plot(time,air_pressure)
plt.show()

new_series = np.subtract(sea_pressure,air_pressure)
print(new_series[new_series.argmin()])