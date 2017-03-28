# import netCDF4
# import numpy as np
# import matplotlib.pyplot as plt
# 
# with netCDF4.Dataset('NCCAR00007.nc') as nc_file:
#     sea_time = nc_file.variables['time'][:]
#     sea_pressure = nc_file.variables['sea_pressure'][:]
#     
# with netCDF4.Dataset('NCCAR12248.nc') as nc_file:
#     air_time = nc_file.variables['time'][:]
#     air_pressure = nc_file.variables['air_pressure'][:]
# 
# air_pressure = np.interp(sea_time, air_time, air_pressure)
# sea_pressure = sea_pressure - air_pressure
# 
# plt.plot(sea_time, sea_pressure)
# plt.show()

