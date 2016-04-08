'''
Created on Mar 29, 2016

@author: chogg
'''


import unit_conversion as uc
import numpy as np
import matplotlib.pyplot as plt
import random
import stats


    
g = uc.GRAVITY
g_sq = g**2

def compute_jonswap_spectrum(freqs):
    
    spectrum = []
    

    s = compute_s(Hs,Tz)
    gamma = compute_gamma(s)
    f_max= compute_fm(Tz, gamma)
    alpha = compute_alpha(s, gamma)
    
    #this is the shape parameter
    beta = -1.25
    
    for f in freqs:
        if f < f_max:
            theta = .07
        else:
            theta = .09
            
        r = np.exp(-1* ((f / f_max) - 1)**2 / (2*(theta**2)))
        
        #this is the peak enhancement factor
        p_e_f = gamma ** r
        
        val = alpha*g_sq * ((2*np.pi)**-4) * (f**-5) * \
        np.exp(beta*((f/f_max)**-4)) * p_e_f
        
        spectrum.append(val)
      
    print('Params(s,gamma,fm,alpha',s,gamma,f_max*Tz,alpha/s**2)  
    sig_wave_height = 4* np.sqrt(np.trapz(spectrum * freqs**0, x=freqs))
    avg_zero_up_crossings = np.sqrt(np.trapz(spectrum * freqs**0, x=freqs) \
                                    / np.trapz(spectrum * freqs**2, x=freqs))
    print('Hm',sig_wave_height,'Tz', avg_zero_up_crossings)
#     plt.plot(freqs,spectrum)
# #     plt.plot(freqs,sig_wave_height)
#     plt.show()
    
    return spectrum
    
def compute_s(Hs, Tz):
    '''wave steepness'''
    return (2*np.pi * Hs) / (g*Tz**2)
    
def compute_gamma(s):
    '''peak enhancement factor'''
    
    #wave steepness above 0.037 is not getting accurate measurements of Hs or Tz
    #I will have to re-check the math at a later time
    if s >= 0.037:
        return 10.54 - (1.34 * s**-0.5) - np.exp(-19 + 3.775 * s**-0.5)
    else:
        return 0.9 + np.exp(18.86 - 3.67 * s**-0.5)
    
def compute_fm(Tz,gamma):
    '''compute peak frequency'''
    return (0.6063 + 0.1164 * gamma**0.5 - 0.01224*gamma) / Tz

def compute_alpha(s, gamma):
    return (2.964 + 0.4788 * gamma**0.5 - 0.3430 * gamma + 0.04225 * gamma ** (3/2)) * s**2



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
                total_energy += spectrum[x]**(.5)
         
        waves = []   
        for x in range(0, len(freqs)):
    #         print('spec',spectrum[x],total_energy)
            
            if spectrum[x] != 0:
                amp =  Hs * (1/scale_factor) * \
                (spectrum[x]**(.5)/ total_energy)
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
    ht = stats.significant_wave_height([x/1000.0 for x in time], wl)
    azc = stats.average_zero_crossing_period([x/1000.0 for x in time], wl)
    
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
    for x in (range(0,10)):
        Tz = x+1
        spectrum = compute_jonswap_spectrum(freqs)
        ht = compute_time_series(freqs, spectrum, calc=False)
        heights.append(ht)
        
    plt.scatter(range(1,11),heights)
    plt.show()
        
    a1,b1,c1,d1,e1,f1,g1,h1,i1,j1 = np.polyfit(range(1,11), heights, deg=9)
    
    calc_func = lambda tz: j1 + i1*tz + h1*tz**2 + g1*tz**3 + f1*tz**4 + \
    e1*tz**5 + d1*tz**6 + c1*tz**7 + b1*tz**8 + a1*tz**9
    
    for x in (range(0,10)):
        Tz = x+1
        spectrum = compute_jonswap_spectrum(freqs)
        compute_time_series(freqs, spectrum, calc=True,scale_factor=calc_func(Tz))
        
    