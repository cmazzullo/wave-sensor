'''
Created on Jul 17, 2014

@author: Gregory
'''
import numpy as np
import os
import pandas as pd
from datetime import datetime

try:
    from NetCDF_Utils.edit_netcdf import NetCDFReader, NetCDFWriter
    import NetCDF_Utils.slurp as slurp
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
        self.in_file_name = os.path.join("..\Instruments","benchmark", "RBRtester1.nc")
        self.air_pressure_file = os.path.join("..\Instruments","benchmark","RBRtester2.nc")
        self.pressure_data = None
        self.air_pressure_data = None
        self.depth_data = None
        self.data_frame = None
        self.date_format_string = "%Y-%m-%d %H:%M:%S"
        self.data_tests = tests.DataTests()
        
    def acquire_data(self, pressure_file_bool = False):
        
        self.pressure_data = pd.DataFrame(self.read_file(self.in_file_name, milliseconds_bool = True))
        if pressure_file_bool == False:
            station = 8454000
            start = '20140501'
            fmt = '%Y%m%d'
            start = datetime.strptime(start, fmt)
            end = '20140701'
            end = datetime.strptime(end, fmt)
            ts = slurp.get_data(station, start, end)
            self.air_pressure_data = pd.DataFrame(ts)  
        else:
            self.air_pressure_data = pd.DataFrame(self.read_file(self.air_pressure_file, milliseconds_bool = True))
    
        self.df = pd.DataFrame.join(self.pressure_data,self.air_pressure_data,lsuffix = "a", rsuffix = "b")
        self.df.columns = ["Pressure", "Air Pressure"]
        self.interpolate_data()
        self.depth_pressure = [x for x in np.subtract(self.df['Pressure'],self.df['Air Pressure'])]
        self.convert_pressure_to_depth()      
        
    def interpolate_data(self):
        air_pressure = self.df['Air Pressure']
        print(air_pressure)
        nan_check = np.isnan(air_pressure.values)
        #Checks to see if no time data matchers up between 1st and second file, if not a linspace caluclates the air pressure
        if len(nan_check[nan_check == False]) == 0:
          
            first_index = self.air_pressure_data.index[self.air_pressure_data.index \
                                                             < air_pressure.index[0]][::-1][0]
            last_index = self.air_pressure_data.index[self.air_pressure_data[0].index \
                                                             > air_pressure.index[::-1][0]][0]
                                                             
            air_pressure[:] = np.linspace(self.air_pressure_data[0][first_index],\
                                          self.air_pressure_data[0][last_index],len(air_pressure))
           
        else:
            prev_index = -1
            current_index = None
            for x in range(0, len(nan_check)):
                if nan_check[x] == False:
                    current_index = x
                    if prev_index > -1:
                        
                        air_pressure[prev_index:current_index] = \
                        np.linspace(air_pressure[prev_index], air_pressure[current_index], \
                                    num = current_index - (prev_index), endpoint = False)
                    prev_index = x
                elif x == 0:
                    air_pressure[0] = self.air_pressure_data.index[self.air_pressure_data.index \
                                                                < air_pressure.index[0]][::-1][0]
                    prev_index = 0
                elif x == len(nan_check):
                    current_index = x
                    air_pressure[x] = self.air_pressure_data.index[self.air_pressure_data.index \
                                                                   > air_pressure.index[x]][0]
                    air_pressure[prev_index:current_index] = \
                        np.linspace(air_pressure[prev_index], air_pressure[current_index], \
                                    num = current_index - (prev_index), endpoint = False)
    
    def write_data(self):
        data_store = v_store.DataStore(1)
        data_store.pressure_data = [x for x in self.df['Pressure']]
        data_store.utc_millisecond_data = [x * 1000 for x in self.df['Air Pressure'].index]
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
        
        
        self.write_netCDF(data_store, self.df.shape[0])        
                
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
