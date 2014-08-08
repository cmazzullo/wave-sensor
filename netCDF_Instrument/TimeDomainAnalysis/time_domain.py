'''
Created on Jul 25, 2014

@author: Gregory
'''
import sys
import os
sys.path.append('..')

import numpy as np
from DepthCalculation.depth import Depth

class Time_Domain_Analysis(Depth):
    """This calculates the number,length, and height of waves in a time series with depth, and pressure data"""
    def __init__(self):
        self.counter = 0
        self.Pmin = 0
        self.Pmax = 0
        self.period = 0
        self.start = 1
        super().__init__()
        self.in_file_name = os.path.join("..\Instruments","benchmark", "infosys2.nc")
        self.TanAlfa = 0.001      #Bedslope
        self.individual_waves = []
        self.individual_wave_time = []
        self.periods = None
        self.dates = None
        self.tmean = None
    
    def run_time_domain_method(self, method2_bool = True):  
        if method2_bool == True:
            self.method2()
        else:
            self.method1()  
    
    def initialize(self):
        self.acquire_data()
        self.new_data = [x for x in self.pwave_data]

    def method1(self):
        """Uses the average period and specified limits to identify waves"""
        self.initialize()
        self.dates = [x for x in self.pressure_data.index]
        pwave = [x for x in self.pwave_data]
        depth = [x for x in self.depth_data]
        eta = []
        for x in range(0,len(pwave) - 1):
            if pwave[x] * pwave[x+1] > 0 and pwave[x] > 0:
                self.counter += 1
                self.Pmax = 0
                self.Pmin = 0
            if pwave[x] > self.Pmax: self.Pmax = pwave[x]
            if pwave[x] < self.Pmin: self.Pmin = pwave[x]
            
        self.tmean = (len(pwave) * .25) / self.counter
        
        for x in range(0,len(pwave)):
            period = self.tmean
            L0 = (self.g / 2) / np.pi*np.power(period,2.0)
            if depth[x] / L0 < 0.36:
                L= np.sqrt(self.g * depth[x]) * (1 - (depth[x] / L0)) * period
            else:
                L=L0
            eta.append( \
                        (((pwave[x] / self.rho) / self.g) \
                            * np.cosh(((2 * np.pi) / L) * depth[x])))
            
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
            
        self.periods = np.repeat(self.tmean, len(pwave))
            
    def method2(self):
        """Downward crossing method: if the function crosses the x axis in
        an interval and if its endpoint is below the x axis, we've found
        a new wave."""  
         
        self.initialize()
        Pwave = [x for x in self.pwave_data]
        depth = [x for x in self.depth_data]
        
        start = period = counter = Pmin = Pmax = 0
        periods = []                    # periods of found waves
        eta = np.zeros(len(Pwave))
        interval = 1 / 4
        steepness = 0.03
        Hminimum = 0.10
        H = []

        for i in range(len(Pwave) - 1):
            if Pwave[i] > 0 and Pwave[i+1] < 0:
                print(i)
                periods.append(period)
                # w**2 = g * k, the dispersion relation for deep water
                wavelength = self.g * period**2 / (2 * np.pi)
                # if the water is too shallow
                if depth[i] / wavelength < 0.36:
                    wavelength = ((self.g * depth[i])**(1/2) *
                                  (1 - depth[i] / wavelength) *
                                  period)
                    height = (((Pmax - Pmin) / (self.rho * self.g)) *
                              np.cosh(2 * np.pi * depth[i] /
                                      wavelength))
                H.append(height)
                Hunreduced = Hreduced = height
                print('height = ' + str(height))
                print('wavelength = ' + str(wavelength))
                if height / wavelength > steepness:
                    print('Wave is too steep!')
                    Hreduced = steepness * wavelength
                    H.append(Hreduced)
                if height < Hminimum:
                    print('Wave is too small!')
                    H.pop()
                    Hreduced = Hminimum
                    counter -= 1
                if str(wavelength) == 'nan':
                    print('nan pop')
                    H.pop()
                reduction = Hreduced / Hunreduced
                for j in range(start, i):
                    eta[j] = ((Pwave[j] * reduction) / (self.rho * self.g)) * \
                             np.cosh(2 * np.pi * depth[j] / wavelength)
                start = i + 1
                period = Pmax = Pmin = 0
                counter += 1
            period = period + interval
            if Pwave[i] > Pmax:
                Pmax = Pwave[i]
            if Pwave[i] < Pmin:
                Pmin = Pwave[i]

        self.individual_waves = H
      
        self.periods = np.sort(periods)
        self.tmean = np.mean(periods)
        
  
    
if __name__ == '__main__':
    td = Time_Domain_Analysis() 
    td.method2()
