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
        self.sea_pressure_data = None
        self.pwave_data = None
        self.hydrostat_pressure_data = None
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
        self.density = 1030
        self.accel_to_grav = 9.81
        self.average_depth = None

        
    def acquire_data(self, pressure_file_bool = False):
        
        self.pressure_data = self.read_file(self.in_file_name, milliseconds_bool = True)
        self.pressure_data = pd.Series(np.multiply(self.pressure_data,10000), index = self.pressure_data.index)
        if pressure_file_bool == False:
            start = '20140512'
            fmt = '%Y%m%d'
            start = datetime.strptime(start, fmt)
            end = '20140514'
            end = datetime.strptime(end, fmt)
            ts = self.Buoydata.get_data(start, end)
            self.Buoydata.write_to_netCDF(ts,'air_pressure.nc')
            self.air_pressure_data = pd.Series(np.multiply(ts,10000), index = ts.index)
        else:
            self.air_pressure_data = self.read_file(self.air_pressure_file, milliseconds_bool = True)
    
        self.interpolate_data()
        self.filter_data()
        self.subtract_air_pressure()
        self.create_pwave_data()
        self.create_hyrostatic_pressure_data()
        self.create_depth_data()
                   
    def interpolate_data(self):
        x_var = [x for x in self.pressure_data.index]
        fp = [x for x in self.air_pressure_data]
        xp = [x for x in self.air_pressure_data.index]
         
        self.interp_data = pd.Series(np.interp(x_var, xp, fp, left=-10000, right=-10000),\
                                      index = self.pressure_data.index)
        
    def filter_data(self):
        self.interp_data = self.interp_data[self.interp_data != -10000]
        first_index = self.interp_data.index[0]  
        last_index = self.interp_data.index[::-1][0] 
        
        self.pressure_data = self.pressure_data[self.pressure_data.index >= first_index] 
        self.pressure_data = self.pressure_data[self.pressure_data.index <= last_index] 
        
    def subtract_air_pressure(self):
        self.sea_pressure_data = pd.Series(np.subtract(self.pressure_data,self.interp_data),
                                index = self.pressure_data.index)
        
    def create_pwave_data(self):
        range_index = np.multiply(np.arange(0,len(self.sea_pressure_data)),.25)
        a =  np.polyfit(range_index, self.sea_pressure_data, 1) # construct the polynomial #np.linalg.lstsq(A, self.sea_pressure_data)[0]
       
        p4 = np.poly1d(a)
         
        self.pwave_data = pd.Series(np.subtract(self.sea_pressure_data,p4(range_index)), \
                                    index=self.pressure_data.index)
        
        plt.plot(self.sea_pressure_data.index,self.sea_pressure_data, label='Original data')
        plt.plot(self.sea_pressure_data.index, p4(range_index),'r', label='FittedLine', linewidth=1.0, color='red')
        plt.legend()
        plt.grid(b=True, which='major', color='grey', linestyle="-")
        plt.show()

    def create_hyrostatic_pressure_data(self):
        self.hydrostat_pressure_data = pd.Series(np.subtract(self.sea_pressure_data, \
                                    self.pwave_data), index = self.pressure_data.index)
        
        print('hydrostat', self.hydrostat_pressure_data)
        
    def create_depth_data(self):
        hstat = self.hydrostat_pressure_data
        divide_rho_than_g = np.divide(np.divide(hstat,self.density),self.accel_to_grav)
        self.depth_data = pd.Series(divide_rho_than_g, index=self.pressure_data.index)
        
        self.average_depth = np.mean(self.depth_data)
        
             
    def plot_data(self):
        pressure_mean = np.mean(self.pressure_data)
        air_pressure_mean = np.mean(self.air_pressure_data)
        interp_mean = np.mean(self.interp_data)
        
        p1, = plt.plot(self.pressure_data.index,self.sea_pressure_data, label="sea pres"  \
                 ,alpha=0.70, linewidth="3.0", linestyle="-")
        p2, = plt.plot(self.pressure_data.index,self.pwave_data, label="pwave", \
                 alpha=0.70, linewidth="3.0", linestyle="-")
        p3, = plt.plot(self.pressure_data.index,self.hydrostat_pressure_data, label='hydro', \
                  alpha=0.70, linewidth="3.0", linestyle="-")
        p4, = plt.plot(self.pressure_data.index,self.depth_data,label='depth',
                    alpha=.60, linewidth="3.0", linestyle="-")
        
        plt.legend(bbox_to_anchor=(.80, 1.10), loc=2, borderaxespad=0.0)
        plt.show()
        
    def write_data(self):
        data_store = v_store.DataStore(1)
        data_store.pressure_data = [x for x in self.hydrostat_pressure_data]
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
    
if __name__ == "__main__":
    d = Depth()
    d.acquire_data()
    d.plot_data()
#     d.write_data()
