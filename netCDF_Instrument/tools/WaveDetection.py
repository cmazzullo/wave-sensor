import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import netCDF4
from netCDF4 import Dataset
import math

instr_min = []
instr_max = []
instr_std_dev = []
wire_min = []
wire_max = []
wire_std_dev = []
total_average_distance = []

def WaveDetection(stevensFileName, interp_depth, label):
    '''Gets full wave data from Stevens and extracts a time series of same length
    from the instrument file to find a best fit'''
    
    #Read in stevens file name
  
    sdf = pd.read_table(stevensFileName, header=None, skiprows=1, engine='python',  sep='\t')
    sdf.columns = ['index','timestep','channel1','channel2','']
    
    sdf.channel1 = np.multiply(.305,np.divide(sdf.channel1,12))
    window_seconds = sdf.timestep[sdf.shape[0] - 1]
    
    #BRUTE FORCE CHECK OF ALL POINTS IN TIME SERIES SLICE
    final_min = 999999
    final_start = 0
    final_finish = 0
    start = 0;
    endrange = sdf.shape[0]
    
    while endrange < len(interp_depth):
        
        min_array = np.sum(np.square(np.subtract(interp_depth[start:endrange],sdf.channel1)))
#         min_sum = np.sqrt(min_array/sdf.shape[0])
        if min_array < final_min:
            final_min = min_array
            final_start = start;
            final_finish = endrange;
            
        start += 1
        endrange += 1
     
#     print('From ', final_min, 'Average Distance for ', label, ' :', np.sqrt(final_min/sdf.shape[0]))
    print('Points: ', final_start, final_finish)
    total_average_distance.append(np.sqrt(final_min/sdf.shape[0]))
    

    
    instr_min.append(np.min(interp_depth[final_start:final_finish]))
    instr_max.append(np.max(interp_depth[final_start:final_finish]))
    instr_std_dev.append(np.std(interp_depth[final_start:final_finish]))
    instr_significant = instr_std_dev * 4
    
    wire_min.append(np.min(sdf.channel1))
    wire_max.append(np.max(sdf.channel1))
    wire_std_dev.append(np.std(sdf.channel1))
    wire_significant  = wire_std_dev * 4
    
    plt.plot(np.arange(final_start,final_finish), sdf.channel1, label = label, alpha=.70)
    plt.plot(np.arange(final_start,final_finish), interp_depth[final_start:final_finish])
    
    plt.legend()
    plt.show()
    
#     plt.plot(np.arange(0,len(interp_pressure)),sea_pressure)
def get_netCDF(infile_name): 
    ds = Dataset(infile_name)
    time = netCDF4.num2date(ds.variables['time'][:],ds.variables['time'].units)
    depth = ds.variables['depth'][:-1]
    ds.close();
    interp_depth = np.interp(np.arange(0,len(depth)/4,.02),np.arange(0,len(depth)/4,.25),depth)
    interp_depth = np.subtract(interp_depth,np.average(interp_depth))
    
    
#    plt.plot(np.arange(len(interp_depth)),interp_depth, color="grey")
    return interp_depth

# def fit_sin_wave():
#     datax = np.sin(np.pi * 2)
    
    
    
    
    
if __name__ == '__main__':
    
    interp_depth = get_netCDF('HB_day2_1f.nc')
       
   
    for x in range(15,22):
        WaveDetection('A5763.0%s' % x,interp_depth,x)
         
    df = pd.DataFrame({"Instr_Min": instr_min, 
                       "Instr_Max": instr_max, 
                       "Instr_Std_Dev": instr_std_dev, 
                       "Wire_Min": wire_min,
                       "Wire_Max": wire_max, 
                       "Wire_Std_Dev": wire_std_dev,
                       "Total_Average_Distance": total_average_distance});
                        
    df.to_csv(path_or_buf="Metrics.csv")
    
     
   
            
        
        
        
        
        
        
    

    
    