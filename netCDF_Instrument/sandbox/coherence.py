'''
Created on Sep 8, 2016

@author: chogg
'''
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
import pressure_to_depth as p2d
import random

class constituent(object):
    
    def __init__(self, name, freq_in_hours, amp, phase):
        self.name = name
        self.freq = (2*np.pi) / freq_in_hours
        self.amplitude = amp
        self.phase = phase
        
    def get_calculation(self, t):
        return self.amplitude * np.sin(self.freq*t + self.phase)
        
    def get_description(self):
        return self.name

def final_answer(waves, series_length, time_delta, time_start, add_noise = False, noise_level = 1):
    water_level = []
    interval = 3600000 * time_delta
    time_data = [(x * interval) + time_start for x in range(0,series_length)]
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
    

with netCDF4.Dataset('true.nc') as nc_file:
    sea_time = nc_file.variables['time'][:]
    sea_pressure = nc_file.variables['sea_pressure'][:]
    
with netCDF4.Dataset('bp.nc') as nc_file:
    air_time = nc_file.variables['time'][:]
    air_pressure = nc_file.variables['air_pressure'][:]

air_pressure = np.interp(sea_time, air_time, air_pressure)
sea_pressure = sea_pressure - air_pressure

co = np.correlate(sea_pressure[0:4096], sea_pressure[0:4096], mode="full")
co = co/np.max(co)
for x in co[co.size/2.0:]:
    print(x) 
    
    
# sea_pressure = sea_pressure[0:4096]  
# air_pressure = air_pressure[0:4096]
# 
# 
# freqs, values = sc.coherence(sea_pressure, air_pressure, fs=4)
# freqs, values =  freqs[0:int(len(freqs)/2)], values[0:int(len(values)/2)]
# 
# 
# # Cxy = np.abs(np.conj(np.fft.fft(sea_pressure)) * np.fft.fft(air_pressure))**2 / (len(sea_pressure)/2) / 4.0
# # print(Cxy)
# 
# stat = stats.Stats()
# scale = (len(sea_pressure)/2) * 4.0
# Pxx = np.fft.fft(sea_pressure)
# Pxx = Pxx * np.conjugate(Pxx) / scale
# freqs_og = np.fft.rfftfreq(4096,d=1/4.0)[1:]
# freqs_X, newPxx = stat.band_average_psd(freqs_og, Pxx[1:], 32)
#  
# Pyy = np.fft.fft(air_pressure)
# Pyy = Pyy * np.conjugate(Pyy) / scale
# freqs_ogy = np.fft.rfftfreq(4096,d=1/4.0)[1:]
# freqs_Y, newPyy = stat.band_average_psd(freqs_ogy, Pyy[1:], 32)
# 
# Pxy = np.conjugate(np.fft.rfft(sea_pressure))*np.fft.rfft(air_pressure) / scale
# freqs_ogxy = np.fft.rfftfreq(4096,d=1/4.0)[1:]
# freqs_XY, newPxy = stat.band_average_psd(freqs_ogxy, Pxy[1:], 32)
# 
# new_coh = np.abs(newPxy)**2 / newPxx / newPyy

# print(stat.significant_wave_height(values, freqs, None, None))
# print(stat.significant_wave_height(new_coh,freqs_XY, None, None))
#  
# plt.plot(freqs,values)
# plt.plot(freqs_XY, new_coh)
# plt.show()

#phase angles

# new_pressure = np.abs(np.fft.rfft(sea_pressure))**2
# diff = (freqs_og[2]-freqs_og[1]) / 8.0
# print(diff)
# 
# int_freqs = []
# freq = 0
# for x in range(0, len(freqs_og)*8):
#     freq = freq + diff
#     int_freqs.append(freq)
# 
# print(len(freqs_og),len(new_pressure))
# new_pressure = np.interp(int_freqs, freqs_og, new_pressure[1:])
# 
# P_phase = np.angle(new_pressure)
# 
# constituents = []
# t_delta = .00006944444444
#  
# index = 0
# total_energy = 0
# for x in range(0, len(new_pressure)):
#             if new_pressure[x] != 0:
#                 total_energy += new_pressure[x]**(.5)
#                  
# for x,y,z in zip(int_freqs, new_pressure, P_phase):
#     transferred_freq = 1./(120*x)
#     angle = (1./transferred_freq)*(z/(2*np.pi))
#     constituents.append(constituent('1', transferred_freq, np.sqrt(y)/total_energy, angle))
#     index += 1
# p_level, p_time = final_answer(constituents, len(sea_pressure), t_delta, sea_time[0], False, 0)
 
# window_size = 4096
# current_start = 0
# current_end = window_size
# 
# 
# 
# while current_end <= len(sea_pressure):
#     
#     current_pressure = sea_pressure[current_start:current_end]
#     current_time = sea_time[current_start:current_end]
#     
#     coeff = np.polyfit(current_time,current_pressure,1)
#     static_p = coeff[1] + coeff[0]*current_time
#     current_pressure = current_pressure - static_p
#    
#     orifice_elev = np.linspace(-20,-20,len(current_pressure))
#     land_surface_elev = np.linspace(-20,-20,len(current_pressure))
#     scale = (len(current_pressure)/2) * 4.0
#     
#     elevation = np.mean(land_surface_elev)
#     h = np.abs(elevation - \
#                        np.mean(orifice_elev))
#     d = np.mean(p2d.hydrostatic_method(current_pressure)) + h
#     
#     
#     
#     sea_spec = np.fft.fft(current_pressure-np.mean(current_pressure))
#     sea_spec = sea_spec
#     psd_conj = np.conjugate(sea_spec)
#     
#     psd_spec = sea_spec * psd_conj / scale
#     
#     
#     freqs_wl = np.fft.fftfreq(4096,d=1/4.0)
#   
#     k = p2d.omega_to_k(2*np.pi*freqs_wl, h)
#     kz = np.array(np.cosh(h*k)/np.cosh(d*k))
#     
#     
#     # for x in kz:
#     #     print(x)
#     
#     wl_amps = psd_spec/kz**2
#     # avg_freqs, avg_amps = stat.band_average_psd(freqs_og, psd_spec,32)
#     # _, conj_amps = stat.band_average_psd(freqs_og, psd_conj, 32)
#     
#     new_wl = np.fft.ifft((wl_amps * scale / (psd_conj/kz**2))) + static_p
#     hydro_wl = h + p2d.hydrostatic_method(current_pressure-np.mean(current_pressure)) + static_p
#     
#     plt.plot(current_time,hydro_wl, color="blue")
#     # new_press = np.interp(current_end[0:4096],current_end[0:4096:64], new_press.real)
#     
#     plt.plot(current_time,h + new_wl.real, alpha=.5, color="red")
#     plt.plot(current_time,hydro_wl - (h + new_wl.real), color="green")
#     plt.show()
#     
#     current_start += window_size
#     current_end += window_size







# intm = Cxy / Pxx
# 
# Pyy = np.abs(np.fft.fft(air_pressure))**2 / (len(air_pressure)/2) / 4.0
# print(intm/Pyy)
# final = Cxy / Pxx / Pyy
# 
# print('final',final)
