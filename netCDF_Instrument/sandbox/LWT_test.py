'''
Created on Apr 21, 2016

@author: chogg
'''

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import random
import pressure_to_depth as p2d
import unit_conversion as uc



class LWT_Test(object):
    
    def __init__(self, sensor_depth, water_depth, k, amplitude):
        #meters
        self.sensor_depth = sensor_depth
        self.water_depth = water_depth
        self.k = k
        self.amplitude = amplitude
        
        
        #original water level and calculated water level
        #using hyrostatic assumption to compare
        self.og_water_level = None
        self.hyrdo_water_level = None
        
        #presure time series calculated using LWT
        self.pressure_ts = None
        self.time_data = None
        
        self.phase = None
        
        
    def compute_og_wl(self, series_length):
        '''This is the initial time series created using our static parameters'''
      
      
        time_data = range(0,series_length)
#    
        k = self.k
        omega = p2d.k_to_omega(k, self.water_depth)
        self.time_data = time_data
        self.og_water_level = np.array([self.amplitude*np.cos(t*omega) \
                                        for t in self.time_data]) + self.water_depth
        print(self.og_water_level)
                                               
    def make_lwt_pressure_ts(self):
        '''This method uses Linear Wave Theory to convert water level to pressure'''
        k = self.k
        omega = p2d.k_to_omega(k, self.water_depth)
        
        
        self.pressure_ts = np.array([p2d.eta_to_pressure(self.amplitude, omega, k, -self.sensor_depth, \
                                                 +self.water_depth, t) for t in self.time_data]) /10000
        print(self.pressure_ts) 
        
        
            
    def convert_back_to_wl(self):
        '''This converts the pressure back to water level using the hydrostatic assumption'''
        print(p2d.hydrostatic_method(self.pressure_ts))
        self.hyrdo_water_level = p2d.hydrostatic_method(self.pressure_ts)
        
        
    def comparison_graph(self):
        
        fig = plt.figure(figsize=(12,8))
        print(self.og_water_level)
        ax = fig.add_subplot('311')
        ax.plot(self.time_data, self.og_water_level, alpha=.5)
        
        ax2 = fig.add_subplot('312')
        ax2.plot(self.time_data, self.pressure_ts, alpha=.5)
#        
        ax3 = fig.add_subplot('313')
        ax3.plot(self.time_data, p2d.hydrostatic_method(self.pressure_ts))
        
        plt.show()
        
        
if __name__ == '__main__':
    
    T = np.arange(.1,20,.1)
    H = np.linspace(1, 20, len(T))
    
    vals = []
    vals2 = []
    for x in H:
        inner_vals= []
        inner_vals2 = []
        for y in T:
            lt = LWT_Test(sensor_depth=20,water_depth=20.0,k=(2*np.pi)/140.0,amplitude=2.0)
            inner_vals.append(np.average(lt.og_water_level - lt.hyrdo_water_level))
            inner_vals2.append(np.average(lt.hyydro_water_level/lt.og_water_level))
            
        vals.append(inner_vals)
        vals2.append(inner_vals2)
        
    
    
    lt.phase = phase = random.randint(0,36000) / 100.0

    lt.compute_og_wl(4096)
    lt.make_lwt_pressure_ts()
    lt.convert_back_to_wl()
    lt.comparison_graph()
            
        
        