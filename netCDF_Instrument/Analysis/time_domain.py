'''
Created on Jul 25, 2014

@author: Gregory
'''

import numpy as np
import matplotlib.pyplot as plt
from DepthCalculation.depth import Depth

class Time_Domain_Analysis(Depth):
    
    def __init__(self):
        self.counter = 0
        self.Pmin = 0
        self.Pmax = 0
        self.period = 0
        self.start = 1
        super().__init__()
        self.in_file_name = '../Instruments/Benchmark/RBRrsk.nc'
        self.individual_waves = []
        self.individual_wave_time = []
        self.dates = None
    
    def initialize(self):
        self.acquire_data()
        self.new_data = [x for x in self.pwave_data]
        
    def method1(self):
        self.initialize()
        self.dates = [x for x in self.pressure_data.index]
        pwave = self.new_data
      
        
        depth = [x for x in self.depth_data]
        eta = []
        for x in range(0,len(pwave) - 1):
            if pwave[x] * pwave[x+1] > 0 and pwave[x] > 0:
                self.counter += 1
                self.Pmax = 0
                self.Pmin = 0
            if pwave[x] > self.Pmax: self.Pmax = pwave[x]
            if pwave[x] < self.Pmin: self.Pmin = pwave[x]
            
        Tmean = (len(pwave) * .25) / self.counter
        
        for x in range(0,len(pwave)):
            period = Tmean
            L0 = self.accel_to_grav/2/np.pi*np.power(period,2.0)
            if depth[x] / L0 < 0.36:
                L= np.sqrt(self.accel_to_grav*depth[x])*(1-depth[x]/L0)*period
            else:
                L=L0
            eta.append( \
                        (((pwave[x]/self.density)/self.accel_to_grav)\
                            *np.cosh(2*np.pi/L*depth[x])))
            
        counter2 = 0
        etamax = 0
        etamin = 0
        
        for x in range(0,len(pwave) - 1):
            if eta[x+1]*eta[x] < 0 and eta[x+1] < 0 :
                counter2 += 1
                self.individual_waves.append(etamax - etamin)
                self.individual_wave_time.append(self.dates[x])
                etamax = 0
                etamin = 0
            if eta[x] > etamax: etamax = eta[x]
            if eta[x] < etamin: etamin = eta[x]
  
    
if __name__ == '__main__':
    td = Time_Domain_Analysis() 
    td.method1()