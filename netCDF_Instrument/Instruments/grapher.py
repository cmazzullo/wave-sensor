'''
Created on Jul 14, 2014

@author: Gregory
'''
import netCDF4
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import datetime
from Instruments.edit_netcdf import NetCDFReader

class Grapher(NetCDFReader):
    
    def __init__(self):
        super().__init__()
        self.pressure_data = None
        self.file_names = [os.path.join("benchmark","RBRvirtuoso.nc"),os.path.join("benchmark","RBRsolo2.nc"),os.path.join("benchmark","RBRsolo1.nc"),
                           os.path.join("benchmark","Neag2-1.nc")]
        self.colors = ["yellow", "orange", "purple", "green","blue", "red"]
        self.names = []
        self.plot_data = []
        self.mean_list = []
        self.ymax = 0
        self.ymin = 10000000
        
    def plot_part(self, series, name):
        self.names.append(name)
        self.mean_list.append(np.mean(series))
        skipIndex = 1
        if len(series) > 10000:
            skipIndex = int(len(series) / 10000)
            if skipIndex < 100:
                skipIndex = 100
        
        max = np.max(series[::skipIndex])   
        min = np.min(series[::skipIndex])
        
        if max > self.ymax:
            self.ymax = max
        if min < self.ymin:
            self.ymin = min
            
        return plt.plot(series.index[::skipIndex],series[::skipIndex], \
                  color=self.colors.pop(), linewidth="3.0", linestyle="-")
        
    def plot_graph(self):
        fig = plt.figure(figsize=(12,4))
        ax = fig.add_subplot(111)
        ax.set_ylabel('Pressure in dbars')
        plt.grid(b=True, which='major', color='grey', linestyle="-")
        time = None
        for x in self.dataframe:     
        #self.pressure_data[::100].plot(ax=ax,title='Pressure Data')
            p1, = self.plot_part(self.dataframe[x], x)
            self.plot_data.append(p1)
            time = self.dataframe[x].index
        
       
        mean = np.mean(self.mean_list)
        p2, = plt.plot(time,np.repeat(mean, len(time)),color="orange", \
                 linewidth="2.0", linestyle="-")
        self.plot_data.append(p2)
        plt.title("Pressure Data")
        self.names.append("Mean")
        self.names.append("Max/Min")
        p3, = plt.plot(time,np.repeat(self.ymax, len(time)), color="orange", \
                linewidth="1.0", linestyle="--")
        self.plot_data.append(p3)
        p4, = plt.plot(time,np.repeat(self.ymin, len(time)), color="orange", \
                linewidth="1.0", linestyle="--")
        plt.legend(self.plot_data, self.names)
        plt.xlim(time[0]  + datetime.timedelta(minutes=25),time[::-1][0] + datetime.timedelta(minutes=5))
        
        plt.show()
        
if __name__ == "__main__":
    
    #--create an instance    
    graph = Grapher()
    graph.get_dataframe()
    graph.plot_graph()