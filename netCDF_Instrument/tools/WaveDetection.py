import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import netCDF4
from netCDF4 import Dataset
import math

def WaveDetection(stevensFileName, interp_depth, label):
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
        elif (rolling_mean[x] > rolling_mean[x + 1] and rolling_mean[x] >= rolling_mean[x - 1]) or \
            rolling_mean[x] >=  rolling_mean[x + 1] and rolling_mean[x] > rolling_mean[x-1]:
            
            if crest_watch == None:
                crest_watch = True
            
            if crest_watch == True and crests > 0:
                wave_count += 1
            crests += 1
            
        elif (rolling_mean[x] < rolling_mean[x + 1] and rolling_mean[x] <= rolling_mean[x - 1]) or \
            rolling_mean[x] <=  rolling_mean[x + 1] and rolling_mean[x] < rolling_mean[x-1]:
            
            if crest_watch == None:
                crest_watch = False
            
            if crest_watch == False and troughs > 0:
                wave_count += 1
            troughs += 1   
            
    print('stevens: ', crests, ' ', troughs, ' ', wave_count)
    
    #BRUTE FORCE CHECK OF ALL POINTS IN TIME SERIES SLICE
    final_min = 999999
    final_start = 0
    final_finish = 0
    start = 0;
    endrange = sdf.shape[0]
    
    while endrange < len(interp_depth):
        min_array = np.sum(np.abs(np.subtract(interp_depth[start:endrange],sdf.channel1)))
        if min_array < final_min:
            final_min = min_array
            final_start = start;
            final_finish = endrange;
            
        start += 1
        endrange += 1
     
    
#     plt.plot(rolling_mean2.index[final_start:final_finish],depth[final_start:final_finish])
    
    plt.plot(np.arange(final_start,final_finish), sdf.channel1, label = label)
    
#     plt.plot(np.arange(0,len(interp_pressure)),sea_pressure)
def get_netCDF(infile_name): 
    ds = Dataset(infile_name)
    time = netCDF4.num2date(ds.variables['time'][:],ds.variables['time'].units)
    depth = ds.variables['depth'][:-1]
    ds.close();
    interp_depth = np.interp(np.arange(0,len(depth)/4,.02),np.arange(0,len(depth)/4,.25),depth)
    interp_depth = np.subtract(interp_depth,np.average(interp_depth))
    
    plt.plot(np.arange(len(interp_depth)),interp_depth, color="grey")
    return interp_depth
    
    
if __name__ == '__main__':
    
    interp_depth = get_netCDF('RBR2Final1.nc')
    for x in range(14,16):
        WaveDetection('A5763.0%s' % x,interp_depth,x)
        
#     for x in range(10,12):
#         WaveDetection('A5763.0%s' % x,interp_depth,x)
#     
    plt.legend()
    plt.show()
            
        
        
        
        
        
        
    

    
    