import jdcal
from datetime import datetime
import unit_conversion as uc
import netCDF_Utils.nc as nc
import pytz
from tools.storm_options import StormOptions
import numpy as np
import matplotlib.pyplot as plt

fname = 'stat_calc.nc'
fname2 = 'stat_a.nc'

time = nc.get_variable_data(fname, 'time')
time2 = nc.get_variable_data(fname, 'time2')
corrected_pressure = nc.get_variable_data(fname,'P_1ac')
depth = float(nc.get_variable_data(fname, 'depth'))

end_time = nc.get_variable_data(fname2, 'time')
sig_height = nc.get_variable_data(fname2,'wh_4061')
average_period = nc.get_variable_data(fname2,'wp_4060')
water_depth = nc.get_variable_data(fname2, 'water_depth')

storm_objects = []

for x in range(0, 5):
#     new_times = [jdcal.jd2gcal(y,float(z/86400000)) for y,z in zip(time[x],time[x])]
#     
#     print(new_times[0])
#     dates = [datetime(y[0],y[1],y[2], int(24*y[3]),tzinfo=pytz.UTC) for y in new_times]
    ms = [1430049600000.0 + (y* 166.66667) for y in range(0,len(time[x]))]
    
    so = StormOptions()
    so.sliced = True
    so.sensor_orifice_elevation = np.repeat(0.15, len(time[x]))
    so.sea_time = np.array(ms)
    so.corrected_sea_pressure = corrected_pressure[x]
    so.sea_pressure_mean = np.mean(corrected_pressure[x])
    
    so.get_wave_water_level()
    
    print('wl', np.mean(so.raw_water_level), water_depth[x])
    coeff = np.polyfit(so.sea_time, so.wave_water_level, 1)
    static_wl = coeff[1] + coeff[0]*so.sea_time
    so.wave_water_level = so.wave_water_level - static_wl
    
    
#     plt.plot(so.sea_time,so.wave_water_level)
#     plt.show()
    
    
    so.chunk_data()
    so.get_wave_statistics()
    
    storm_objects.append(so)
    
for x in range(0,5):#len(end_time)):
    for y in range(0,len(storm_objects[x].stat_dictionary['time'])):
        print(' ')
        print('H1/3: ', sig_height[x])
        print('avg period: ', average_period[x])
       
        print('H1/3 ours', np.mean(storm_objects[x].stat_dictionary['H1/3']))
        print('Avg Period ours', np.mean(storm_objects[x].stat_dictionary['Mean Wave Period']))
            
         
    print('')
    
    
    
    
    