'''
Created on Jul 28, 2014

@author: Gregory
'''
import numpy as np
from Analysis.time_domain import Time_Domain_Analysis
from Analysis.rayleigh import Rayleigh as ray
class Probabilities(Time_Domain_Analysis):
    
    def __init__(self):
        pass
    
    def analyze_probabilites(self):
        counter = len(self.individual_waves)
        