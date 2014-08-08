'''
Created on Jul 17, 2014

@author: Gregory
'''
import numpy as np
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

from NetCDF_Utils.edit_netcdf import NetCDFReader, NetCDFWriter
import NetCDF_Utils.slurp as slurp
import NetCDF_Utils.VarDatastore as v_store
import NetCDF_Utils.Testing as tests

class Depth(NetCDFWriter, NetCDFReader):
    """Calculates depth by subtracting air pressure from pressure data, interpolating where necessary.
    creating pwave data via linear regression, and subtracting hydro-static pressure to get depth"""
    
    def __init__(self):
        super().__init__()
        self.latitude = 30
        self.in_file_name = os.path.join("..\Instruments","benchmark", "infosys2.nc")
        self.air_pressure_file = os.path.join("..\Instruments","benchmark",'infosys2.nc')
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
        self.station = 8454000
        self.rho = 1027 #density
        self.g = 9.81  #acceleration due to gravity
        self.average_depth = None
        self.flat_test = False
        
    def acquire_data(self, pressure_file_bool = False):
        """Reads in an external netcdf4 file or downloads buoy pressure data from NOA website,
        runs depth calculation methods
        
        pressure_file_bool -- choose whether to use an external file or download from web"""
         
        self.pressure_data = self.read_file(self.in_file_name, milliseconds_bool = True)
        self.pressure_data = pd.Series(np.multiply(self.pressure_data,10000), index = self.pressure_data.index)
        if pressure_file_bool == False:
            start = datetime(year=2014, month=7, day=3)
            end = datetime(year=2014, month=7, day=6)
            ts, lat, lon = slurp.get_data(self.station, start, end)
            fname = 'air_pressure.nc'
            slurp.write_to_netCDF(fname, ts, lat, lon)
           
            self.air_pressure_data = pd.Series(np.multiply(ts.values,10000), index = np.divide(ts.index,1000))
            
        else:
            self.air_pressure_data = self.read_file(self.air_pressure_file, milliseconds_bool = True)
    
        self.interpolate_data()
        self.filter_data()
        self.subtract_air_pressure()
        self.create_pwave_data()
        self.create_hyrostatic_pressure_data()
        self.create_depth_data()
                   
    def interpolate_data(self):
        """Performs linear interpolation on data"""
        
        x_var = [x for x in self.pressure_data.index]
        fp = [x for x in self.air_pressure_data]
        xp = [x for x in self.air_pressure_data.index]
    
        self.interp_data = pd.Series(np.interp(x_var, xp, fp, left=-10000, right=-10000),\
                                      index = self.pressure_data.index)
        
    def filter_data(self):
        """Filters any pressure data that does not fall within the start and end of air pressure data"""
        
        self.interp_data = self.interp_data[self.interp_data != -10000]
        first_index = self.interp_data.index[0]  
        last_index = self.interp_data.index[::-1][0] 
        
        self.pressure_data = self.pressure_data[self.pressure_data.index >= first_index] 
        self.pressure_data = self.pressure_data[self.pressure_data.index <= last_index] 
        
    def subtract_air_pressure(self):
        self.sea_pressure_data = pd.Series(np.subtract(self.pressure_data,self.interp_data),
                                index = self.pressure_data.index)
        
    def create_pwave_data(self, correct_tides=False):
        """Performs either simple 1d linear regression or accounts for tides with a sin interploation
        
        correct_tides -- 1d or sin interpolation"""
        
        range_index = np.multiply(np.arange(0,len(self.sea_pressure_data)),.25)
        a =  np.polyfit(range_index, self.sea_pressure_data, 1) # construct the polynomial #np.linalg.lstsq(A, self.sea_pressure_data)[0]
        
        if correct_tides == False:
            p1 = np.poly1d(a)
         
            self.pwave_data = pd.Series(np.subtract(self.sea_pressure_data,p1(range_index)), \
                                    index=self.pressure_data.index)
            
        else:

            samfreq = 4  # the sampling frequency
            p = self.sea_pressure_data
            clean_p = (p - np.average(p)) / (max(p) - min(p))
            Y = np.absolute(np.fft.fft(clean_p) / len(clean_p))**2
            nu = np.fft.fftfreq(len(clean_p), 1 / samfreq)
            max_freq = nu[np.argmax(Y[0:len(Y) / 2])]
            tide = (np.average(p) + (max(p) - min(p)) *
                    np.sin(2 * np.pi * max_freq * self.sea_pressure_data.index) / 2)
            self.pwave_data = pd.Series(self.sea_pressure_data - tide, index=self.pressure_data.index)


    def create_hyrostatic_pressure_data(self):
        """Subtracts sea pressure from pwave data unless performing a predetermined wave height data set for testing"""
        if(self.flat_test):
            self.hydrostat_pressure_data = pd.Series(self.sea_pressure_data, index = self.pressure_data.index)
        else:
            self.hydrostat_pressure_data = pd.Series(np.subtract(self.sea_pressure_data, \
                                        self.pwave_data), index = self.pressure_data.index)

        
    def create_depth_data(self):
        """Divides density and accel due to grav from hydrostatic pressure"""
        
        hstat = self.hydrostat_pressure_data
        divide_rho_and_g = np.divide(hstat,self.rho * self.g)
        self.depth_data = pd.Series(divide_rho_and_g, index=self.pressure_data.index)
        
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
        """Writes data to netcdf file"""
        
        data_store = v_store.DataStore(1)
        data_store.pressure_data = [x for x in self.hydrostat_pressure_data]
        data_store.utc_millisecond_data = [x * 1000 for x in self.pressure_data.index]
        data_store.z_data = [x for x in self.depth_data]
        data_store.latitutde = self.latitude
        data_store.longitude = self.longitude
        self.out_filename = 'DepthCalc.nc'

        #Tests#
        self.data_tests.depth_data = data_store.z_data
        self.data_tests.pressure_data = data_store.pressure_data
        data_store.pressure_qc_data = self.data_tests.select_tests('pressure')
        data_store.z_qc_data = self.data_tests.select_tests('depth')
        
        self.write_netCDF(data_store, len(self.pressure_data))
        
    def test(self):
        print((5.860543688291664 * 10000)/1027/9.81) 
        print((5.860543688291664 * 10000)/1000/9.81)
        
    
if __name__ == "__main__":
    d = Depth()
    d.acquire_data()
    d.write_data()
