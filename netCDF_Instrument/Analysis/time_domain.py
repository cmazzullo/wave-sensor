'''
Created on Jul 25, 2014

@author: Gregory
'''
import sys
sys.path.append('..')

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
        self.TanAlfa = 0.001      #Bedslope
        self.individual_waves = []
        self.individual_wave_time = []
        self.dates = None
    
    def initialize(self):
        self.acquire_data()
        self.new_data = [x for x in self.pwave_data]

    def method2(self, pressure_data):
            
        self.initialize()
        Pwave = self.new_data
        P = pressure_data
        freq = 4
        t = np.arange(0, len(P)) / freq
        slope, intercept =  np.polyfit(t, P, 1)
        Pstatic = slope * t + intercept
        Pwave = P - Pstatic
        depth = Pstatic / (rho * g)
        # Downward crossing method: if the function crosses the x axis in
        # an interval and if its endpoint is below the x axis, we've found
        # a new wave.
        start = period = counter = Pmin = Pmax = 0
        periods = []                    # periods of found waves
        eta = np.zeros(len(P))
        interval = 1 / 4
        steepness = 0.03
        Hminimum = 0.10
        H = []

        for i in range(len(Pwave) - 1):
            if (Pwave[i] * Pwave[i+1]) < 0 and Pwave[i+1] < 0:
                print(i)
                periods.append(period)
                # w**2 = g * k, the dispersion relation for deep water
                wavelength = g * period**2 / (2 * np.pi)
                # if the water is too shallow
                if depth[i] / wavelength < 0.36:
                    wavelength = ((g * depth[i])**(1/2) *
                                  (1 - depth[i] / wavelength) *
                                  period)
                    height = (((Pmax - Pmin) / (rho * g)) *
                              np.cosh(2 * np.pi * depth[i] /
                                      wavelength))
                H.append(height)
                Hunreduced = Hreduced = height
                print('height = ' + str(height))
                print('wavelength = ' + str(wavelength))
                if height / wavelength > steepness:
                    print('Wave is too steep!')
                    Hreduced = steepness * wavelength
                    H.pop()
                    H.append(Hreduced)
                if height < Hminimum:
                    print('Wave is too small!')
                    Hreduced = Hminimum
                    counter -= 1
                reduction = Hreduced / Hunreduced
                for j in range(start, i):
                    eta[j] = ((Pwave[j] * reduction) / (rho * g)) * \
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
