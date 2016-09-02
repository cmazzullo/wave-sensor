'''
Created on Mar 29, 2016

@author: chogg
'''


import unit_conversion as uc
import numpy as np
import matplotlib.pyplot as plt
import random
import stats
import netCDF4

    
g = uc.GRAVITY
g_sq = g**2
st = stats.Stats()

def get_data():
    '''initialize the data'''
    air_fname = './data/bp.nc'
    air_time, air_pressure = None, None

    with netCDF4.Dataset(air_fname, 'a') as nc_file:
        air_time = nc_file.variables['time'][:]
        air_pressure = nc_file.variables['air_pressure'][:]
        
    sea_fname = './data/true.nc'
    sea_time, sea_pressure = None, None
    
    sensor_orifice1 = None
    sensor_orifice2 = None
    
    with netCDF4.Dataset(sea_fname, 'a') as nc_file:
        sea_time = nc_file.variables['time'][:]
        sea_pressure = nc_file.variables['sea_pressure'][:]
        sensor_orifice1 = nc_file.sensor_orifice_elevation_at_deployment_time
        sensor_orifice2 = nc_file.sensor_orifice_elevation_at_retrieval_time
        land_surface1 = nc_file.initial_land_surface_elevation
        land_surface2 = nc_file.final_land_surface_elevation
        
        water_depth = np.abs(np.mean(np.linspace(land_surface1,land_surface2,len(sea_pressure))))
        instrument_height = water_depth - \
        np.abs(np.mean(np.linspace(sensor_orifice1,sensor_orifice2,len(sea_pressure))))
        
def derive_spectra(ts, tstep, h, d):
    
    wl_psd = np.fft.rfft(ts)
    phase_angles = [np.tan(wl_psd[x].imag/wl_psd[x].real) for x in wl_psd]
    
    freq, spec = st.power_spectrum(ts, tstep, h, d)
    
    return



class wave(object):
    def __init__(self, name, freq_in_hours, amp, phase):
        self.name = name
        self.freq = float(2*np.pi) / freq_in_hours
        self.amplitude = amp
        self.phase = phase
        
    def get_calculation(self, t):
        return self.amplitude * np.sin(self.freq*t + self.phase)
        
    def get_description(self):
        return self.name


def final_answer(waves, series_length, time_delta, add_noise = False, noise_level = 1):
    
    water_level = []
    interval = 3600000 * time_delta
    time_data = [(x * interval) + 1404647999870 for x in range(0,series_length)]
    for x in range(0,series_length):
        wl_point = 0
        
        next_point = x * time_delta
        
        for p in waves:
            wl_point += p.get_calculation(next_point)
        
        if(add_noise):
                rand_inverse = random.randint(0,1)
                
                if rand_inverse == 0:
                    rand_inverse = -1
                
                rand_int = float( random.randint(0,noise_level * 100.0)/100.0 * rand_inverse )
#                 print rand_int
                
                wl_point += rand_int
         
        water_level.append(wl_point)
            
    return (water_level, time_data)

Hs = 10 #meters
Tz = 1 #average zero crossings is this multiplied by peak frequency

def compute_time_series(freqs, spectrum, calc=True, scale_factor = None):
  
    # a time delta of 4hz in respect to an hour
    t_delta = .00006944444444
    total_energy = 0
    series_length = 4096
    total_amp = 0
    
    if calc == True:
        print('calc')
#         print('scale factor',scale_factor)
        for x in range(0, len(freqs)):
            if spectrum[x] != 0:
                total_energy += (spectrum[x]* 2048 * 4)**.5
         
        waves = []   
        for x in range(0, len(freqs)):
    #         print('spec',spectrum[x],total_energy)
            
            if spectrum[x] != 0:
                amp =  Hs * (1/scale_factor) * \
                ((spectrum[x]* 2048 * 4)**.5/ total_energy)
            else:
                amp = 0
                
            total_amp += amp
    #         print('total amp', total_amp)
            new_freq = 1 / float((freqs[x] * 3600.0))
    #         print('freqs',freqs[x],new_freq)
            phase = random.randint(1,35999) / 100.0
            waves.append(wave("wave1",new_freq,amp,phase))
    else:
        print('fit')
       
        for x in range(0, len(freqs)):
            total_energy += np.sqrt(spectrum[x])
         
        waves = []   
        for x in range(0, len(freqs)):
    #         print('spec',spectrum[x],total_energy)
            amp = (spectrum[x]**(.5)/ total_energy)
            total_amp += amp
           
            new_freq = 1 / float((freqs[x] * 3600.0))
    #         print('freqs',freqs[x],new_freq)
            phase = random.randint(1,35999) / 100.0
            waves.append(wave("wave1",new_freq,amp,phase))
    
#     print('total amp', total_amp)
    wl, time = final_answer(waves, series_length, t_delta, False, 1)
#     
#     plt.plot(time,wl)
#     plt.show()
    
    stats.std_dev = True
    stat_o = stats.Stats()
    
    ht = stat_o.significant_wave_height([x/1000.0 for x in time], wl)
    azc = stat_o.average_zero_crossing_period([x/1000.0 for x in time], wl)
    
    print('computed significant wave height',ht)
    print('computed significant avzcp',azc)
    
#     stats.std_dev = False
#     ht = stats.significant_wave_height([x/1000.0 for x in time], wl)
#     azc = stats.average_zero_crossing_period([x/1000.0 for x in time], wl)
#     
#     print('computed significant wave height',ht)
#     print('computed significant avzcp',azc)
    print('')
    return ht
    


if __name__ == '__main__':
    freqs = np.linspace(.001, 2, 200)
    heights = []
    height_diff = []
    
     
        
    