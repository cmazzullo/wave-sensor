import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import math
import array_compare
from scipy.optimize import curve_fit

instr_min = []
instr_max = []
instr_std_dev = []
wire_min = []
wire_max = []
wire_std_dev = []
total_average_distance = []
fit_amplitude = []
fit_stevens_amplitude = []
# stevens_file_names = ['A5763.0%s' % x for x in range(15,22)]
stevens_file_names = ['A5763.006','A5763.007','A5763.008','A5763.009','A5763.010','A5763.011']
trial_file = stevens_file_names

def WaveDetection(file_name, ax):
    '''Gets full wave data from Stevens and extracts a time series of same length
    from the instrument file to find a best fit'''
    initialize()
    
    interp_depth = get_netCDF(file_name)
    plot_numbers(np.arange(0,len(interp_depth)),interp_depth, 'Ins', ax)
    
    for x in range(0,len(stevens_file_names)):
        
        #READ IN STEVENS FILE NAME
        sdf = pd.read_table(stevens_file_names[x], header=None, skiprows=1, engine='python',  sep='\t')
        sdf.columns = ['index','timestep','channel1','channel2','']
        
        #CONVERT UNITS TO METERS may change this in the future
        sdf.channel1 = np.multiply(.305,np.divide(sdf.channel1,12))
       
        if stevens_file_names[x] == 'A5763.008':
            final_start, final_finish, final_min = array_compare.array_compare(sdf.channel1.values.astype(np.double),interp_depth[30000:].astype(np.double))
            final_start += 30000
            final_finish += 30000
        else:
            #GET INDICES AND ECUCLIDEAN DISTANCE FOR STEVENS WAVE FILE AND INSTRUMENT DATA
            final_start, final_finish, final_min = array_compare.array_compare(sdf.channel1.values.astype(np.double),interp_depth.astype(np.double))
       
        amp = fit_curve(interp_depth[final_start:final_finish])
        fit_amplitude.append(np.abs(amp) * 100)
        
        stevens_amp = fit_curve(sdf.channel1)
        fit_stevens_amplitude.append(np.abs(stevens_amp) * 100)
#         print(amp, stevens_amp)
        #ADD DATA TO ARRAYS FOR WRITING TO EXCEL FILE
        print('pts', final_start, final_finish)
        wire_min.append(np.min(sdf.channel1) * 100)
        wire_max.append(np.max(sdf.channel1) * 100)
        wire_std_dev.append(np.std(sdf.channel1) * 100)
#         wire_significant  = wire_std_dev * 4
        total_average_distance.append(final_min * 100)
        instr_min.append(np.min(interp_depth[final_start:final_finish]) * 100)
        instr_max.append(np.max(interp_depth[final_start:final_finish]) * 100)
        
        std_dev = np.std(interp_depth[final_start:final_finish]) * 100
        instr_std_dev.append(std_dev)
#         instr_significant.append(std_dev * 4)
        
        #MAKE PLOT
        plot_numbers(np.arange(final_start,final_finish), sdf.channel1, x + 3, ax)
       
        ax.text(final_start, np.max(sdf.channel1), x + 3)
    
    #WRITE EXCEL FILE AND SHOW PLOT
    write_excel_file(''.join(['Metrics', file_name, '.csv']))
#     plt.title('Stevens Test Data over Instrument Data')
#     plt.xlabel('Time in milliseconds')
#     plt.ylabel('Water Level in meters')
#     plt.legend(bbox_to_anchor=(1.10, 1.0))   
#     plt.show()
    
def get_netCDF(infile_name): 
    '''Gets netCDF properties and interpolates them over the frequency of Stevens data'''
    ds = Dataset(infile_name)
#     time = netCDF4.num2date(ds.variables['time'][:],ds.variables['time'].units)
    depth = ds.variables['depth'][:-1]
    ds.close()
    interp_depth = np.interp(np.arange(0,len(depth)/4,.02),np.arange(0,len(depth)/4,.25),depth)
    interp_depth = np.subtract(interp_depth,np.average(interp_depth))
    return interp_depth
    
def write_excel_file(file_name):
    
    df = pd.DataFrame({"Instr_Min": instr_min, 
                        "Instr_Max": instr_max, 
                        "Instr_Std_Dev": instr_std_dev, 
                        "Wire_Min": wire_min,
                        "Wire_Max": wire_max, 
                        "Wire_Std_Dev": wire_std_dev,
                        "Euclidean_Distance": total_average_distance,
                        "Instr_Fit Amplitude": fit_amplitude,
                        "Wire_Fit_Amplitude": fit_stevens_amplitude,
                        "File": trial_file});
    df = df.set_index('File')
                        
    df.to_csv(path_or_buf=file_name)
    
def fit_curve(depth_data):
#     plt.cla()
    n = len(depth_data)
    x = np.arange(0.0,len(depth_data))
    depth = pd.Series(depth_data,x)
    fourier = np.fft.rfft(depth)
    maxFour = (fourier).argmax()
    freq = np.fft.rfftfreq(len(depth), d = x[1] - x[0])
    
    frequency_guess = freq[maxFour]
    amplitude_guess = depth.max()
    phase_guess = 1
    
    f = lambda t, amp, freq, phase: amp * np.sin(2*np.pi*freq*t - phase)
    
    popt, pcov = curve_fit(f,x,depth,
                           p0=(amplitude_guess, frequency_guess, phase_guess))
    
    amp, freq, phase = popt
    
    y = amp * np.sin(2*np.pi*freq*x - phase)
    
#     plt.plot(x,depth_data,color="blue", alpha=0.5)
#     plt.plot(x,y, color="purple", alpha=0.5)
#     plt.show()
#     
    return amp
                        
def initialize():
    instr_min[:] = []
    instr_max[:] = []
    instr_std_dev[:] = []
    wire_min[:] = []
    wire_max[:] = []
    wire_std_dev[:] = []
    total_average_distance[:] = []
    fit_amplitude[:] = []
    fit_stevens_amplitude[:] = []
    
def plot_numbers(x,y,label, ax):
    ax.plot(x,y,alpha=.5, label = label)

# def fit_sin_wave():
#     datax = np.sin(np.pi * 2)
    

if __name__ == '__main__':
    fig = plt.figure(figsize=(16,8))
    ax = fig.add_subplot(111)
#     ax2 = fig.add_subplot(212)
#     file_names = ['hydro_hb.nc', 'hydro_rbr.nc', 'hydro_lt.nc','hydro_ms.nc']
#                   #'leveltest.nc']
#     
    interp_depth = get_netCDF('hydro_lt.nc')
#     interp_depth2 = get_netCDF('hydro_lt.nc')
    plot_numbers(np.arange(0,len(interp_depth)),interp_depth, 'ins lw',ax)
#     plot_numbers(np.arange(0,len(interp_depth2)),interp_depth2, 'ins hydro',ax)
#     WaveDetection('leveltest.nc', ax)
    WaveDetection('leveltest.nc', ax)
    
    ax.set_title('Linear Wave Theory vs. Hydrostatic')
    ax.set_ylabel('Water Level in meters')
#    ax.set_xlabel('Time in milliseconds') 
#     ax2.set_title('Hydrostatic Method')
#     ax2.set_ylabel('Water Level in meters')
#     ax2.set_xlabel('Time in milliseconds')
    
    ax.legend()
#     ax2.legend()
    plt.show()
#        
    
     
   
            
        
        
        
        
        
        
    

    
    