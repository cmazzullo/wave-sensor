import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import netCDF4
from netCDF4 import Dataset
import math

def WaveDetection(stevensFileName, depthFileName, frequency):
    '''Gets full wave data from Stevens and extracts a time series of same length
    from the instrumen file to find a best fit'''
    
    #Read in stevens file name
    sdf = pd.read_table(stevensFileName, header=None, skiprows=1, engine='python', sep='   ')
    sdf.columns = ['index','timestep','channel1','channel2']
    
    sdf.channel1 = np.multiply(.38,np.divide(sdf.channel1,12))
    window_seconds = sdf.timestep[sdf.shape[0] - 1]
#     window_size = window_seconds / frequency
#     min_periods = int(math.ceil(window_size * .9))
    rolling_mean = pd.rolling_mean(sdf.channel1, 25, center=True)
    
    crests = 0
    troughs = 0
    crest_watch = None
    wave_count = 0
   
    for x in range(0,len(rolling_mean)):
        if x == 0:
            continue
        if x == (len(rolling_mean) - 1):
            continue
        elif rolling_mean[x] > rolling_mean[x + 1] and rolling_mean[x] >= rolling_mean[x - 1]:
#             print('crest Point:', x)
            if crest_watch == None:
                crest_watch = True
            
            if crest_watch == True and crests > 0:
                wave_count += 1
            crests += 1
            
        elif rolling_mean[x] < rolling_mean[x + 1] and rolling_mean[x] <= rolling_mean[x - 1]:
#             print('trough Point:', x)
            if crest_watch == None:
                crest_watch = False
            
            if crest_watch == False and troughs > 0:
                wave_count += 1
            troughs += 1   
            
    print('stevens: ', crests, ' ', troughs, ' ', wave_count)
    
    #Read in sliced Sensor Data
    ds = Dataset(depthFileName)
    time = netCDF4.num2date(ds.variables['time'][:],ds.variables['time'].units)
    depth = ds.variables['depth'][:-1]
    ds.close();
    #PRESSURE READINGS
#     ds2 = Dataset('Wave1.nc')
#     sea_pressure = ds2.variables['sea_water_pressure'][:]
#     ds2.close();
#     
#     interp_pressure = np.interp(np.arange(0,len(sea_pressure)/4,.02),np.arange(0,len(sea_pressure)/4,.25),sea_pressure)
#     interp_pressure = np.subtract(interp_pressure,np.average(interp_pressure))
    interp_depth = np.interp(np.arange(0,len(depth)/4,.02),np.arange(0,len(depth)/4,.25),depth)
    interp_depth = np.subtract(interp_depth,np.average(interp_depth))
    wave_series = pd.Series(interp_depth, index = np.arange(0,len(depth) * 12.5))
    
    rolling_mean2 = pd.rolling_mean(wave_series,5,center=True)
    
    #ORIGINALLY GETTING ONLY PERFECT WAVES
#     print(len(rolling_mean2), sdf.shape[0])
#     begin_slice = 0;
#     end_slice = 0;
#     final_slice_s = 0
#     final_slice_t = 0
#     crest_watch = None
#     wave2_count = 0
#     over = False
#     min_avg = 9999
#     while(over == False):
#         for x in range(begin_slice, len(rolling_mean2)):
#             print(x)
#             if x == 0:
#                 continue
#             elif x == (len(rolling_mean2) - 1):
#                 over = True;
#             elif rolling_mean2[x] > rolling_mean2[x + 1] and rolling_mean2[x] >= rolling_mean2[x - 1]:
#     #             print('crest Point:', x)
#                 if crest_watch == None:
#                     crest_watch = True
#                     begin_slice = x
#                 
#                 if crest_watch == True and crests > 0:
#                     wave2_count += 1
#                     if wave2_count == wave_count:
#                         end_slice = x
#                         break
#                 crests += 1
#                 
#             elif rolling_mean2[x] < rolling_mean2[x + 1] and rolling_mean2[x] <= rolling_mean2[x - 1]:
#     #             print('trough Point:', x)
#                 if crest_watch == None:
#                     crest_watch = False
#                     begin_slice = x
#                 
#                 if crest_watch == False and troughs > 0:
#                     wave2_count += 1
#                     if wave2_count == wave_count:
#                         end_slice = x
#                         break
#                 troughs += 1   
#     
#         if over == True:
#             break
#         
#         print(begin_slice, end_slice)

    #BRUTE FORCE CHECK OF ALL POINTS IN TIME SERIES SLICE
    final_min = 999999
    final_start = 0
    final_finish = 0
    start = 0;
    endrange = sdf.shape[0]
    
    while endrange < len(rolling_mean2):
        min_array = np.mean(np.subtract(interp_depth[start:endrange],sdf.channel1))
        if np.sum(min_array) < final_min:
            final_min = np.mean(min_array)
            final_start = start;
            final_finish = endrange;
            
        start += 1
        endrange += 1
     
    
#     plt.plot(rolling_mean2.index[final_start:final_finish],depth[final_start:final_finish])
    plt.plot(rolling_mean2.index,interp_depth)
    plt.plot(np.arange(final_start,final_finish), sdf.channel1)
#     plt.plot(np.arange(0,len(interp_pressure)),sea_pressure)
    plt.show()

    
    
if __name__ == '__main__':
    WaveDetection('A5763.006','ltroll_day6depth.nc',2)
    WaveDetection('A5763.004','rbr_wave4.nc',2)
    WaveDetection('A5763.004','ltroll_final.nc',2)
        
            
        
        
        
        
        
        
    

    
    