'''
Created on Jul 14, 2014

@author: Gregory
'''
import netCDF4
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

class Grapher(object):
    
    def __init__(self):
        self.pressure_data = None
        self.in_file_name = os.path.join("benchmark","WaveLog.nc")

    def retrieve_data(self):
        nc = netCDF4.Dataset(self.in_file_name)
        pressure = nc.variables['sea_water_pressure']
        times = nc.variables['time']
        
        time_convert = netCDF4.num2date(times[:],'milliseconds since 1970-01-01 00:00:00')
#         if nc.variables['temperature'] != None:
#             temperature = nc.variables['temperature']
#             self.pressure_data = pd.Series(pressure,temperature,index=time_convert)
#         else:
        self.pressure_data = pd.Series(pressure,index=time_convert)
        
    def plot_graph(self):
        fig = plt.figure(figsize=(12,4))
        ax = fig.add_subplot(111)
       
        
        skipIndex = 1
        if len(self.pressure_data) > 10000:
            skipIndex = int(len(self.pressure_data) / 10000)
            if skipIndex < 100:
                skipIndex = 100
             
        #self.pressure_data[::100].plot(ax=ax,title='Pressure Data')
        ax.set_ylabel('Pressure in dbars')
        p1,= plt.plot(self.pressure_data.index[::skipIndex],self.pressure_data[::skipIndex], \
                  color="blue", linewidth="1.0", linestyle="-")
        
       
        
        mean = np.mean(self.pressure_data)
        p2, = plt.plot(self.pressure_data.index,np.repeat(mean, len(self.pressure_data)),color="orange", \
                 linewidth="2.0", linestyle="-")
        plt.title("Pressure Data")
        plt.legend([p1, p2], ["Pressure", "Mean"])
        plt.show()
        
if __name__ == "__main__":
    
    #--create an instance    
    graph = Grapher()
    graph.retrieve_data()
    graph.plot_graph()