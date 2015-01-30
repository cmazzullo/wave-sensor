"""This needs to read in a netCDF file containing pressure and get the
water depth using fft and hydrostatic methods"""

from pressure_to_depth import combo_method, hydrostatic_method
import NetCDF_Utils.nc as nc

f = '/home/chris/work/wave-sensor/data_files/logger3.csv.nc'
t = nc.get_time(f)
p = nc.get_pressure(f)

combo_y = combo_method(t, p, z, H, timestep, window_func=np.hamming)
