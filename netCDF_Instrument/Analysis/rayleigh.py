'''
Created on Jul 25, 2014

@author: Gregory
'''
import numpy as np
class Rayleigh(object):
    
    def __init__(self,xmark):
        self.x = xmark
        self.poe = np.array(np.divide(range(1,11),10.0))[::-1]
        self.poe = self.poe.concatenate([.01,.005,.002,.001,.0005])
        self.y = np.sqrt((np.log(self.poe)))
        self.n = len(self.y)
        self.m = len(self.x)
        self.axis([x])
    
    
if __name__ == '__main__':
    r = Rayleigh()
    