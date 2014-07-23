'''
Created on Jul 17, 2014

@author: Gregory
'''
import numpy as np
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

try:
    from NetCDF_Utils.edit_netcdf import NetCDFReader, NetCDFWriter
    from NetCDF_Utils.slurp import Buoydata
    import NetCDF_Utils.VarDatastore as v_store
    import NetCDF_Utils.Testing as tests
except:
    from edit_netcdf import NetCDFReader, NetCDFWriter
    import ncar_rap as rap
    import VarDatastore as v_store
    import Testing as tests

class Depth(NetCDFWriter, NetCDFReader):
    
    def __init__(self):
        super().__init__()
        self.latitude = 30
        self.in_file_name = os.path.join("..\Instruments","benchmark", "RBRrsk.nc")
        self.air_pressure_file = os.path.join("..\Instruments","benchmark","RBRtester2.nc")
        self.pressure_data = None
        self.interp_data = None
        self.pressure_frequency = None
        self.air_pressure_frequency = None
        self.air_pressure_data = None
        self.depth_data = None
        self.data_frame = None
        self.date_format_string = "%Y-%m-%d %H:%M:%S"
        self.first_date = None
        self.last_date = None
        self.closest_a_first_date = None
        self.closest_a_last_date = None
        self.data_tests = tests.DataTests()
        self.Buoydata = Buoydata(8454000)

        
    def acquire_data(self, pressure_file_bool = False):
        
        self.pressure_data = self.read_file(self.in_file_name, milliseconds_bool = True)
        if pressure_file_bool == False:
            start = '20140501'
            fmt = '%Y%m%d'
            start = datetime.strptime(start, fmt)
            end = '20140701'
            end = datetime.strptime(end, fmt)
            ts = self.Buoydata.get_data(start, end)
            self.Buoydata.write_to_netCDF(ts,'air_pressure.nc')
            self.air_pressure_data = ts
        else:
            self.air_pressure_data = self.read_file(self.air_pressure_file, milliseconds_bool = True)
    
        self.interpolate_data()
        
        
        self.depth_pressure = [x for x in np.subtract(self.pressure_data,self.interp_data)]
        self.convert_pressure_to_depth()      
        
    
              
    def interpolate_data(self):
        x_var = [x for x in self.pressure_data.index]
        fp = [x for x in self.air_pressure_data]
        xp = [x for x in self.air_pressure_data.index]
    
#         ben = np.interp(x_var, xp, fp)
#         
#         plt.plot(self.air_pressure_data.index,self.air_pressure_data, \
#                  alpha=0.70, linewidth="3.0", linestyle="-")
#         plt.plot(self.pressure_data.index,ben, \
#                  alpha=0.70, linewidth="3.0", linestyle="-")
#         plt.show()
#         
        self.interp_data = np.interp(x_var, xp, fp)
             

    def write_data(self):
        data_store = v_store.DataStore(1)
        data_store.pressure_data = [x for x in self.depth_pressure]
        data_store.utc_millisecond_data = [x * 1000 for x in self.pressure_data.index]
        data_store.z_data = [x for x in self.depth_data]
        data_store.latitutde = self.latitude
        data_store.longitude = self.longitude
        self.out_filename = 'DepthCalc.nc'
#       
        #Tests#
        self.data_tests.depth_data = data_store.z_data
        self.data_tests.pressure_data = data_store.pressure_data
        data_store.pressure_qc_data = self.data_tests.select_tests('pressure')
        data_store.z_qc_data = self.data_tests.select_tests('depth')
        
        
        self.write_netCDF(data_store, len(self.pressure_data))        
                
    def convert_pressure_to_depth(self):
        latitude_elem = np.square(np.sin(self.latitude / 57.29578))
        
        self.depth_data = [self.calculate_Depth(latitude_elem, x) for x in self.depth_pressure]
        
        
#         print('depths are as follows:\n')
#         for x in range(0,len(self.depth_data)):
#             print(x, 'pressure:', self.depth_pressure[x], 'depth:', self.depth_data[x])
#         
    def calculate_GR(self, X, P):
        a = 9.780318 * (1.0 + ((5.2788 * np.power(10,-3.0)) + (2.36 * np.power(10,-5.0)) * X) \
                    * X) + (1.092 * np.power(10,-6.0)) * P
#         print('GR', a)
        return a
    
    def calculate_DepthTerm(self, P):
        a = ((((-1.82 * np.power(10,-15.0)) * P + (2.279 * np.power(10,-10.0))) * P \
          - (2.2512 * np.power(10,-5.0))) * P + 9.72659) * P
#         print('Depth Term',a)
        return a
          
    def calculate_Depth(self, X, P):
        a =  self.calculate_DepthTerm(P) / self.calculate_GR(X,P) 
        #ask about del / 9.8
#         print("Depth", a)
        return a
    
if __name__ == "__main__":
    d = Depth()
    d.acquire_data()
    d.write_data()
