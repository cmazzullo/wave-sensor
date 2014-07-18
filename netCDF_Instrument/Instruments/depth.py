'''
Created on Jul 17, 2014

@author: Gregory
'''
import numpy as np
import os
import pandas as pd

try:
    from Instruments.edit_netcdf import NetCDFReader
except:
    from edit_netcdf import NetCDFReader

class Depth(NetCDFReader):
    
    def __init__(self):
        self.latitude = 30
        self.in_file_name = os.path.join("benchmark", "RBRtester1.nc")
        self.air_pressure_file = os.path.join("benchmark","RBRtester2.nc")
        self.pressure_data = None
        self.air_pressure_data = None
        self.depth_data = None
        
    def acquire_data(self, pressure_file_bool = False):
        if self.air_pressure_file == None:
            print("Weather Website Data")
        else:
            self.pressure_data = self.read_file(self.in_file_name)
            self.pressure_data.columns = ['Pressure']
            self.air_pressure_data = self.read_file(self.air_pressure_file)
            self.air_pressure_data.columns = ['Air Pressure']
            final = pd.DataFrame({'pressure': self.pressure_data,"air pressure": self.air_pressure_data})
            
            for x in final:
                print ('final,',x, x['Pressure'], x['Air Pressure'])
                
    def convert_pressure_to_depth(self):
        pressure = self.get_series(self.in_file_name)
        
        x1 = np.square(np.sin(self.latitude /57.29578))
        print('x1,', x1 )
        
        depth_data = [self.calculate_Depth(x1, x) for x in pressure]
        
        print('depths are as follows:\n')
        for x in range(0,len(depth_data)):
            print(x, 'pressure:', pressure[x], 'depth:', depth_data[x])
        
    def calculate_GR(self, X, P):
        a = 9.780318 * (1.0 + ((5.2788 * np.power(10,-3.0)) + (2.36 * np.power(10,-5.0)) * X) \
                    * X) + (1.092 * np.power(10,-6.0)) * P
        print('GR', a)
        return a
    
    def calculate_DepthTerm(self, P):
        a = ((((-1.82 * np.power(10,-15.0)) * P + (2.279 * np.power(10,-10.0))) * P \
          - (2.2512 * np.power(10,-5.0))) * P + 9.72659) * P
        print('Depth Term',a)
        return a
          
    def calculate_Depth(self, X, P):
        a =  self.calculate_DepthTerm(P) / self.calculate_GR(X,P) 
        #ask about del / 9.8
        print("Depth", a)
        return a
    
if __name__ == "__main__":
    d = Depth()
    d.acquire_data()