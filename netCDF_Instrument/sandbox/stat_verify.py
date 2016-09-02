import jdcal
from datetime import datetime
import unit_conversion as uc
import netCDF_Utils.nc as nc
import netCDF4
import pytz
from tools.storm_options import StormOptions
import numpy as np
import matplotlib.pyplot as plt
import pressure_to_depth as p2d
from stats import Stats
from scipy.signal import welch, detrend

fname = 'stat_calc.nc'
fname2 = 'stat_a.nc'
 
sea_fname = 'true.nc' 
air_fname = 'bp.nc'
 
def run_wave_stats(p_window):
    sea_pressure = nc.get_variable_data(sea_fname, 'sea_pressure')
    sea_time = nc.get_variable_data(sea_fname, 'time')
    air_pressure = nc.get_variable_data(air_fname, 'air_pressure')
    air_time = nc.get_variable_data(air_fname, 'time' )
    
    c_pressure = sea_pressure - np.interp(sea_time,air_time,air_pressure)
    start_index, end_index, step = 0, 4096, 2048
    
    corrected_pressure = []
    while end_index < len(c_pressure):
        corrected_pressure.append(c_pressure[start_index:end_index])
        start_index += step
        end_index += step
        
    corrected_pressure = np.array(corrected_pressure)
    # time2 = nc.get_variable_data(fname, 'time2')
    # corrected_pressure = nc.get_variable_data(fname,'P_1ac')
    # depth = float(nc.get_variable_data(fname, 'depth'))
    pspec = nc.get_variable_data(fname2, 'pspec')
    file_freq = nc.get_variable_data(fname2, 'frequency')
     
    sig_height = nc.get_variable_data(fname2,'wh_4061')
    average_period = nc.get_variable_data(fname2,'wp_4060')

    stat_o = Stats()
    
    our_sig_wave_height = []
    our_avg_period = []
    
    get_index = []
     
    fs = 4.0
    for x in range(0, len(corrected_pressure)):
        
        get_index.append(x)
        ms = np.array([1430049600000.0 + (y * 166.66667) for y in range(0,len(corrected_pressure))])
        final_pressure = corrected_pressure[x]
        
    #     coeff = np.polyfit(ms, final_pressure, 1)
    #     lin_trend = coeff[1] + coeff[0]*ms
    #     detrended_pressure = detrend(final_pressure, type='linear', axis=-1)
    # #     final_pressure - lin_trend
    #
        window = np.hanning(p_window)
    # #     window = window ** 2
    #     windowed_pressure = detrended_pressure 
        #perform real fourier function on the scaled pressure and get the frequencies
    
        
        amps = []
        freqs= np.fft.rfftfreq(p_window, d=1/fs)
         
        final_pressure -= np.mean(final_pressure)
        final_pressure = detrend(final_pressure, type='linear', axis=-1) 
        
        for y in range(0, int(4096/p_window)):
            p = final_pressure[y * p_window:y * p_window + p_window]
            
            p *= window
             
             
            amps.append(np.fft.rfft(p))
            
           
        if p_window == 4096:
            print('4096!!')
            amp_sum = amps[0]
        else: 
            amp_sum = np.array(amps).sum(axis=0)
        
        amp_sum *= np.conjugate(amp_sum)
        scale = 1.0 / (fs * (window**2).sum())      
        amps = amp_sum * scale
        amps = amps.real 
    #     print(amps)
        freqs,amps = welch(final_pressure, 6, window = window, nperseg=256, noverlap=0, detrend='linear')
        
        amps = np.array(amps,dtype=np.float64)
        freqs, amps = freqs[1:], amps[1:]
        
        cut_off = np.where(freqs<=1.0)
        
        freqs = freqs[cut_off]
        amps = amps[cut_off]
        
        if x == 0:
            plt.plot(freqs,amps)
            plt.show()
    
        amps2 = np.array([pspec[x][p][0][0] for p in range(0,len(pspec[x]))], dtype=np.float64)
        freqs2 = file_freq
        
        #get the approximate depth
        approx_depth = 0.2926
        
    #     step = float(len(freqs)/float(len(freqs2)))
    #     freqs = freqs[step::step]  
          
        #get the wave numbers
        k = p2d.echart_omega_to_k(freqs * 2.0 * np.pi, np.repeat(approx_depth,len(freqs)))
        kz = np.array(np.cosh(0.1829*k)/np.cosh(approx_depth*k))
        
#         print('kz',kz)
         
    #     query = np.where(kz < 0.45)
    # #      
    # # #     if len(query[0]) > 0:
    # #     print('cut')
    #     cut = query[0][0]
    #     lin_trans1 = amps[0:cut]/(kz[0:cut]**2)
    #       
    #     #this adds the f^-4 tail to the end of the spectrum
    #     lin_trans2 = (lin_trans1[cut-1] * (freqs[cut-1:]**-4)) \
    #     * ( 1 /  (freqs[cut-1]**-4))
    #       
    #     lin_transform = np.concatenate((  
    #                                     lin_trans1[:len(lin_trans1)-1],
    #                                     lin_trans2
    #                                     ))
    #        
           
              
    #     else:
    #         print('no cut')
        lin_transform = amps/(kz**2) 
         
    #     freqs = np.fft.rfftfreq(len(lin_transform), d=1/6)
    #     print(len(amps))
    # #     step = float(len(freqs)/float(len(freqs2)))
    # #     freqs = freqs[step::step]  
    #     print('freqs1',freqs)
    #     print('freqs2', freqs2)
    #     fig = plt.figure()
    #     ax = fig.add_subplot('211')
    #     ax2 = fig.add_subplot('212')   
    #     ax.plot(freqs2,amps2)
    # #     stat_o.power_spectrum(detre, tstep)
    # #     divide = []
    # #     for x in range(0,len(amps2)):
    # #         print(freqs[x], amps2[x],amps[x], amps2[x]/amps[x])
    # #         divide.append(amps2[x]/amps[x])
    #     
    #     ax2.plot(freqs,amps) 
    #     plt.show()
    #      
        our_sig_wave_height.append(stat_o.significant_wave_height(lin_transform, freqs, \
                                                            None, None))
        our_avg_period.append(stat_o.mean_wave_period(lin_transform, freqs, \
                                                            None, None))
     
    
      
    diff = []
#     for x in range(0,len(corrected_pressure)):#len(end_time)):
#          
#         print(' ')
#         print('H1/3: ', sig_height[get_index[x]])
#         print('avg period: ', average_period[get_index[x]])
#              
#         print('H1/3 ours', our_sig_wave_height[x])
#         print('Avg Period ours', our_avg_period[x])
#              
#         diff.append(np.abs(sig_height[get_index[x]][0][0] - our_sig_wave_height[x]))  
#           
#                
#     
#     print(np.array(diff).sum()/len(corrected_pressure))
    
    plt.plot(range(0,len(our_sig_wave_height)),our_sig_wave_height)
    plt.show()
    
    plt.plot(range(0,len(our_sig_wave_height)),our_avg_period)
    plt.show()
     
    
   
if __name__ == '__main__':
    run_wave_stats(4096)
    run_wave_stats(2048)
    run_wave_stats(1024)
    run_wave_stats(512)
    run_wave_stats(256)
    
    