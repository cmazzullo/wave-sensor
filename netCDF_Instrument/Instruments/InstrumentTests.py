'''
Created on Jul 8, 2014

@author: Gregory
'''
import numpy as np

class PressureTests(object):
    
    pressure_data = None
    pressure_test16_data = None
    pressure_test17_data = None
    pressure_test20_data = None
    five_count_list = list()
    local_frequency_range = [11, 19] # for IOOS test 17
    mfg_frequency_range = [10, 20] # for IOOS test 17
    max_rate_of_change = 20
    prev_value = True # for IOOS test 20
        
    def __init__(self):
        pass
        
    def test_16_stucksensor(self):
        self.pressure_test16_data = [self.get_16_value(x) for x in self.pressure_data]
        
    def test_17_frequencyrange(self):
        self.pressure_test17_data = [self.get_17_value(x) for x in self.pressure_data]
        
    def test_20_rateofchange(self):
        self.pressure_test20_data = [self.get_20_value(x) for x in self.pressure_data]
   
            
    def get_15_value(self):
        print('start mean')
        print('mean', np.mean(self.pressure_data))
        print('mean', np.mean(self.pressure_data))
        
               
    def get_16_value(self,x):
           
        if len(self.five_count_list) > 5:
            self.five_count_list.pop()
            
        flags = np.count_nonzero(np.equal(x,self.five_count_list))
        self.five_count_list.insert(0,x)
        
        if flags <= 2:
            return 1
        elif flags <= 4:
            return 3
        else:
            return 4  
            
    def get_17_value(self, x):
        
        if np.greater_equal(x,self.local_frequency_range[0]) and \
        np.less_equal(x,self.local_frequency_range[1]):
            return 1
        elif np.greater_equal(x,self.mfg_frequency_range[0]) and \
                            np.less_equal(x,self.mfg_frequency_range[1]):
            return 3
        else:
            return 4
        
    def get_20_value(self, x):
      
        if np.isnan(self.prev_value) or \
        np.less_equal(np.abs(np.subtract(x,self.prev_value)), self.max_rate_of_change):
            self.prev_value = x
            return 1
        else:
            self.prev_value = x
            return 4
    
    