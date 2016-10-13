'''
Created on Sep 14, 2016

@author: chogg
'''
import numpy as np
import matplotlib.pyplot as plt
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
    
thirty_sec_4hz = .00833333333332
t_delta = .00006944444444
a = constituent('1', thirty_sec_4hz, 1, 0)
a_level, a_time = final_answer([a], 121, t_delta, False, 0)
plt.plot(a_time,a_level)

complex_num = 2.0j
angle = (1./thirty_sec_4hz)*(np.angle(complex_num)/(2*np.pi))
print(np.angle(complex_num, deg=True))

b = constituent('2', thirty_sec_4hz, 1, angle)
b_level, b_time = final_answer([b], 121, t_delta, False, 0)
plt.plot(b_time,b_level)
 
plt.grid(which = 'major')
plt.show()
plt.plot([x for x in range(0,50)], [a.get_calculation(t) for t in range(0,50)])