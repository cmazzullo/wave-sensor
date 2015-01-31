"""This needs to read in a netCDF file containing pressure and get the
water depth using fft and hydrostatic methods"""

from pressure_to_depth import combo_method, hydrostatic_method, trim_to_even
import NetCDF_Utils.nc as nc
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#f = '/home/chris/work/wave-sensor/data_files/logger1.csv.nc'
f = '/home/chris/testfile.nc'
t = trim_to_even(nc.get_time(f))
timestep = t[1] - t[0]
p = trim_to_even(nc.get_pressure(f))
H = nc.get_water_depth(f)
z = nc.get_device_depth(f)

combo_y = combo_method(t, p, z, H, timestep, window_func=np.hamming)
static_y = hydrostatic_method(p)


plt.plot(t, static_y, label='Hydrostatic method')
plt.plot(t, combo_y, label='LWT method')
# plt.plot(t, np.ones_like(t), label='ones')
plt.legend()
plt.show()
