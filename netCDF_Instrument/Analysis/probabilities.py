'''
Created on Jul 28, 2014

@author: Gregory
'''
import numpy as np
from Analysis.time_domain import Time_Domain_Analysis
from Analysis.rayleigh import Rayleigh as ray
from Analysis.BG import BG
class Probabilities(Time_Domain_Analysis):
    
    def __init__(self):
        self.Hsorted = None
        self.HMean = None
        self.Hrms = None
        self.TanAlfa = 0.001
        self.T3 = None
        self.H2_Percent_Measured = None
        self.H2_Percent_Rayleigh = None
        self.H1_Percent_Measuerd = None
        self.H1_Percent_Rayleigh = None
        self.H1_Per_Mile_Measured = None
        self.H1_Per_Mile_Rayleigh = None
        self.Htr = None
        self.BG = BG()
        super().__init__()
        self.counter = None
        self.probsorted2 = []
    
    def run_probabilities(self):
        self.run_time_domain_method()
        self.analyze_probabilites()
        self.weibull_probability()
        
    def analyze_probabilites(self):
        self.counter = len(self.individual_waves)
        self.Hsorted = np.sort(np.array(self.individual_waves))
        self.Hrms = np.sqrt(np.mean(np.power(self.Hsorted,2)))
        self.HMean = np.mean(self.Hsorted)
        Tsorted = np.sort(np.array(self.periods))
        from_index  = np.round(2 * self.counter/3)
        to_index = np.round(self.counter)
        Hs = np.mean(self.Hsorted[from_index -1:to_index-1])
        
        self.T3 = np.mean(Tsorted[from_index - 1:to_index])
        two_percent = np.round(self.counter - self.counter/50)
        if two_percent != self.counter:
            self.H2_Percent_Measured = self.Hsorted[two_percent - 1]   
        self.H2_Percent_Rayleigh = 1.4 * Hs
        
        one_percent = np.round(self.counter - self.counter / 100)
        if one_percent != self.counter:
            self.H1_Percent_Measuerd = self.Hsorted[one_percent - 1]
        self.H1_Percent_Rayleigh = 1.5 * Hs
        
        one_per_mile = np.round(self.counter - self.counter / 1000)
        if one_per_mile != self.counter:
            self.H1_Per_Mile_Measured = self.Hsorted[one_per_mile - 1]
        self.H1_Per_Mile_Rayleigh = 1.85 * Hs
        
    def weibull_probability(self):
        self.Htr = (0.35 + (5.8 * self.TanAlfa)) * self.average_depth
        
        H3 = self.Hrms * self.BG.get_bg_value(self.Htr, 3)
        H10 = self.Hrms * self.BG.get_bg_value(self.Htr, 10)
        H2 = self.Hrms * self.BG.get_bg_value(self.Htr, 0.02)
        H1 = self.Hrms * self.BG.get_bg_value(self.Htr, .01)
        H01 = self.Hrms * self.BG.get_bg_value(self.Htr, .001)
        
        for x in range(0,self.counter):
            self.probsorted2.append(1 - ((x + 1) / (self.counter + 1)))
                                    
        maxh = 1.3 * self.Hsorted[self.counter - 1]
        step = 1
        if maxh < 5.1: step = 0.5
        if maxh < 2.6: step = 0.25
        
        xmark = self.array_utility(0,maxh,step)
        rayleigh_plot = ray(self.Hsorted,self.probsorted2,xmark,self.Hrms,self.Htr)
        rayleigh_plot.exceedance_graph()
        
    
    def array_utility(self,start,end,step):
        a = list([start])
        start += step
        while start < end:
            a.append(start)
            start += step
        a.append(end)
        return a
            
if __name__ == '__main__':
    prob_object = Probabilities()
    prob_object.run_probabilities()   
    
    
        