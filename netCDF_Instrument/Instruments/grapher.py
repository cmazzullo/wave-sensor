'''
Created on Jul 14, 2014

@author: Gregory
'''
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import datetime
from Instruments.edit_netcdf import NetCDFReader

# pd.set_option('display.mpl_style', 'default')
#This is for pressure and temperature data for now, will be extended as needed
class Grapher(NetCDFReader):
    
    def __init__(self):
        super().__init__()
        self.pressure_data = None
        self.file_names = [os.path.join("benchmark","RBRsolo2-1.nc"),os.path.join("benchmark","RBRsolo1-1.nc"),
                           os.path.join("benchmark","Neag2-1.nc"),os.path.join("benchmark","RBRvirtuoso.nc")]
       
        self.colors = ["yellow", "orange", "purple", "green","blue", "red"]
        for x in range(6,48):
            self.colors.append(self.colors[x % 6])
        self.names = []
        self.names2 = []
        self.plot_data = []
        self.plot_data2 = []
        self.mean_list = []
        self.mean_list2 = []
        self.ymax = 0
        self.ymin = 10000000
        
    def plot_part(self, series, name, subplot = None):
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
           
        if subplot == None: 
            return plt.plot(series.index[::skipIndex],series[::skipIndex], \
                  color=self.colors.pop(), linewidth="3.0", linestyle="-")
        else:
            return subplot.plot(series.index[::skipIndex],series[::skipIndex], \
                  color=self.colors.pop(), linewidth="3.0", linestyle="-")
        
    def re_initialize(self):
        self.mean_list = []
        self.dataframe_vals = dict()
        self.plot_data = []
        self.names = []
        self.ymax = 0
        self.ymin = 10000000
        
    def plot_multiple_series_graphs(self, pressure_bool):
        self.re_initialize()
        
        fig = plt.figure(figsize=(12,4))
        ax = fig.add_subplot(111)
        ax.set_axis_bgcolor('#f7f7f7')
        
        if pressure_bool == True:
            self.get_pressures_only_dataframe()
            ax.set_ylabel('Pressure in dbars')
        else:
            self.get_temperatures_only_dataframe()
            ax.set_ylabel('Temperature in celsius')
        
       
        plt.grid(b=True, which='major', color='grey', linestyle="-")
        time = None
        
        for x in self.dataframe: 
           
            if self.dataframe[x][0] != None:
                print(pressure_bool, x)
                self.mean_list.append(np.mean(self.dataframe[x]))  
                self.names.append(x)  
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
        plt.legend(self.plot_data, self.names,bbox_to_anchor=(.80, 1.10), loc=2, borderaxespad=0.0)
        
        plt.xlim(time[0],time[::-1][0] + datetime.timedelta(minutes=5))
         
        plt.show()
        
    def plot_both_together(self):
        self.re_initialize()
        self.get_pressure_temperature_data()
        fig = plt.figure(figsize=(16,8))
        ax = fig.add_subplot(221)
        ax.set_axis_bgcolor('#f7f7f7')
        ax.set_ylabel('Pressure in dbars')
        ax.set_title('Pressure Data')
        ax.grid(b=True, which='major', color='grey', linestyle="-")
        ax2 = fig.add_subplot(223)
        ax2.set_axis_bgcolor('#f7f7f7')
        ax2.set_title('Temperature Data')
        ax2.set_ylabel('Temperature in celisus')
        ax2.grid(b=True, which='major', color='grey', linestyle="-")
        time = None
        
        for x in self.file_names:
            if(self.pressure_frame[x][0] != None): 
                self.mean_list.append(np.mean(self.pressure_frame[x]))   
                self.names.append(x)
                p1, = self.plot_part(self.pressure_frame[x], x, subplot = ax)
                self.plot_data.append(p1)
                time = self.pressure_frame[x].index
            if(self.temperature_frame[x][0] != None):  
                self.mean_list2.append(np.mean(self.temperature_frame[x]))  
                self.names2.append(x)
                p2, = self.plot_part(self.temperature_frame[x], x, subplot = ax2)
                self.plot_data2.append(p2)
                time = self.temperature_frame[x].index
           
        #ax2.set_xticks(np.linspace(time, 5)) 
        self.names.append("Mean")
        self.names2.append("Mean")
        
        p3, = ax.plot(time,np.repeat(np.mean(self.mean_list), len(time)), color="orange", \
                linewidth="1.0", linestyle="--")
        self.plot_data.append(p3)
        p4, = ax2.plot(time,np.repeat(np.mean(self.mean_list2), len(time)), color="orange", \
                linewidth="1.0", linestyle="--")
        self.plot_data2.append(p4)
        ax.legend(self.plot_data, self.names,bbox_to_anchor=(1.05, 1.0), loc=2, borderaxespad=0.0)
        ax2.legend(self.plot_data2, self.names2,bbox_to_anchor=(1.05, 1.0), loc=2, borderaxespad=0.0)
        ax.set_xlim(time[0],time[::-1][0] + datetime.timedelta(minutes=5))
        ax2.set_xlim(time[0],time[::-1][0] + datetime.timedelta(minutes=5))
        plt.show()
       
         
        
if __name__ == "__main__":
    
    #--create an instance    
    graph = Grapher()
    graph.plot_multiple_series_graphs(True)
    graph.plot_multiple_series_graphs(False)
    graph.plot_both_together()