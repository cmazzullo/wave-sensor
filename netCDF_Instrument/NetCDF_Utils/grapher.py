import matplotlib.pyplot as plt
import os
import numpy as np
import datetime

from NetCDF_Utils.edit_netcdf import NetCDFReader

    


# pd.set_option('display.mpl_style', 'default')
#This is for pressure and temperature data for now, will be extended as needed
class Grapher(NetCDFReader):
    """These are utilities to graph data, will be extended if there is time"""
    
    def __init__(self):
        super().__init__()
        self.pressure_data = None
        self.file_names = [ \
                            os.path.join("../../data_files","Big5_240dayNewNoise.nc"),
                            os.path.join("../../data_files","outts_filtered_boxcar.nc"),
                            os.path.join("../../data_files","outts_filtered_usgs.nc"),
#                             os.path.join("benchmark","RBRsolo2_716.csv.nc"),
#                             os.path.join("benchmark","RBRvirtuoso_716.csv.nc"),
#                         os.path.join("benchmark","newstuff.nc")
                            ]
        self.last_color = dict()
        self.fill_value_correction_bool = False
       
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
        
    def plot_part(self, series, name, subplot = None, zero_mean = False):
        """Plots the x and y of any data
        
        series -- the data in the form of a panda series
        name -- name of the data
        subplot -- if a subplot is passed in use it to plot data
        zero_mean -- a bool to indicate that all points of data will be subtracted by the mean"""
        
        skipIndex = 1
        if len(series) > 10000:
            skipIndex = int(len(series) / 10000)
            if skipIndex < 100:
                skipIndex = 100
            
        max_val = np.max(series[::skipIndex])   
        min_val = np.min(series[::skipIndex])
        mean = np.mean(series[::skipIndex])
        
        if max_val > self.ymax:
            self.ymax = max_val
        if min_val < self.ymin:
            self.ymin = min_val
        
       
        #color check for subplots to keep consistent
        color = None
        if len(self.last_color) <= 0:
            color = self.colors.pop()
            self.last_color['color'] = color
            self.last_color['name'] = name
        elif self.last_color['name'] == name:
            color = self.last_color['color'] 
        else:
            color = self.colors.pop()
            self.last_color['color'] = color
            self.last_color['name'] = name
          
        if subplot == None: 
            if zero_mean == True:
                return plt.plot(series.index[::skipIndex],np.subtract(series[::skipIndex],mean), \
                 alpha=0.70, color=color, linewidth="3.0", linestyle="-")
            else:
                return plt.plot(series.index[::skipIndex],series[::skipIndex], \
                 alpha=0.70, color=color, linewidth="3.0", linestyle="-")
        else:
            if zero_mean == True:
                return subplot.plot(series.index[::skipIndex],np.subtract(series[::skipIndex],mean), \
                  alpha=0.70,color=color, linewidth="3.0", linestyle="-")
            else:
                return subplot.plot(series.index[::skipIndex],series[::skipIndex], \
                  alpha=0.70,color=color, linewidth="3.0", linestyle="-")
        
    def re_initialize(self):
        self.mean_list = []
        self.dataframe_vals = dict()
        self.plot_data = []
        self.names = []
        self.ymax = 0
        self.ymin = 10000000
        
    def plot_multiple_series_graphs(self, pressure_bool, zero_mean = False, ylimits = None):
        """Plots multiple pressure series together or multiple temperature series
        
        pressure_bool -- plot pressure data, otherwise plot temperature data
        zero_mean -- subtract mean from all pint in data, or not
        ylimits -- set limits for vertical axis
        """
        self.re_initialize()
        
        fig = plt.figure(figsize=(12,4))
        ax = fig.add_subplot(111)
        ax.set_axis_bgcolor('#f7f7f7')
        
        if pressure_bool == True:
            self.get_pressures_only_dataframe()
            ax.set_ylabel('Pressure in dbars')
            if zero_mean == True:
                plt.title("Pressure Data Zero Mean")
            else: plt.title("Pressure Data")
        else:
            self.get_temperatures_only_dataframe()
            ax.set_ylabel('Temperature in celsius')
            if zero_mean == True:
                plt.title("Temperature Data Zero Mean")
            else: plt.title("Temperature Data")
        
       
        plt.grid(b=True, which='major', color='grey', linestyle="-")
        time = None
        
        for x in self.dataframe: 
           
            if self.dataframe[x][0] != None:
                if self.fill_value_correction_bool == True:
                    self.dataframe[x][self.dataframe[x] < -100] = 0
                self.mean_list.append(np.mean(self.dataframe[x]))  
                self.names.append(x)  
                p1, = self.plot_part(self.dataframe[x], x, zero_mean = zero_mean)
                self.plot_data.append(p1)
                time = self.dataframe[x].index
                
       
        if(zero_mean == False):
            mean = np.mean(self.mean_list)
            p2, = plt.plot(time,np.repeat(mean, len(time)),color="orange", \
                     linewidth="2.0", linestyle="-")
            self.plot_data.append(p2)
             
            self.names.append("Mean")
            self.names.append("Max/Min")
            p3, = plt.plot(time,np.repeat(self.ymax, len(time)), color="orange", \
                    linewidth="1.0", linestyle="--")
            self.plot_data.append(p3)
#             p4, = plt.plot(time,np.repeat(self.ymin, len(time)), color="orange", \
#                     linewidth="1.0", linestyle="--")
        
        if ylimits != None:
            plt.ylim(ylimits[0],ylimits[1])
            
        plt.legend(self.plot_data, self.names,bbox_to_anchor=(.80, 1.10), loc=2, borderaxespad=0.0)
     
        #plt.xlim(time[0],time[::-1][0] + datetime.timedelta(minutes=5))
        plt.show()
        
    def plot_test_data(self,file_name):
        """Makes a plot of testing data"""
        self.get_test_data(file_name)
        fig = plt.figure(figsize=(12,4))
        ax = fig.add_subplot(111)
        ax.set_axis_bgcolor('#f7f7f7')
        
    
        ax.set_ylabel('Pressure in dbars')
        colors = ["yellow", "orange", "purple", "green","blue", "red"]
        p1, = plt.plot(np.arange(len(self.pressure_data)),self.pressure_data, \
                 alpha=0.70, linewidth="4.0", linestyle="-", color = colors.pop())
        p2, = plt.plot(np.arange(len(self.pressure_data)),self.pressure_data, ".",\
                 alpha=0.70, linewidth="4.0",  color = 'red', ms=15)
        self.plot_data.append(p1)
        self.names.append('Pressure Data')
        
        qc_array = [[],[],[]]
        string_vals = [str(x) for x in self.pressure_qc]
    
        qc_values = [list(x) for x in string_vals]
      
        
        for x in range(0,len(self.pressure_qc)):
            if qc_values[x][3] == '0':
                qc_array[0].append(x)
            if qc_values[x][2] == '0':
                qc_array[1].append(x)  
            if qc_values[x][1] == '0':
                qc_array[2].append(x)
                
       
              
        for x in range(0,3):
            p2, = plt.plot(qc_array[x],np.repeat(0 - (x * 20), len(qc_array[x])), 'bx',\
                  linewidth="3.0", color = colors.pop(), ms = 15)
            self.plot_data.append(p2)
            if x == 0:
                self.names.append('Stuck Sensor Fail')
            elif x == 1:
                self.names.append('Valid Range Test Fail')
            else:
                self.names.append('Valid Rate of Change Fail')     
           
        plt.legend(self.plot_data, self.names,bbox_to_anchor=(.75, 1.10), loc=2, borderaxespad=0.0)
        plt.title("Pressure Test Data")
        plt.ylim(-75,75)
        plt.grid(b=True,  color='grey', linestyle="-")
        plt.show()
        
    def plot_both_together(self, zero_mean = False, pressure_ylimits = None, temperature_ylimits = None):
        """Makes a subplot for both the pressure and temperature data"""
        self.re_initialize()
        self.get_pressure_temperature_data()
        fig = plt.figure(figsize=(16,8))
        ax = fig.add_subplot(221)
        ax.set_axis_bgcolor('#f7f7f7')
        ax.set_ylabel('Pressure in dbars')
     
        ax.grid(b=True, which='major', color='grey', linestyle="-")
        ax2 = fig.add_subplot(223)
        ax2.set_axis_bgcolor('#f7f7f7')
        ax2.set_title('Temperature Data')
        ax2.set_ylabel('Temperature in celsius')
        ax2.grid(b=True, which='major', color='grey', linestyle="-")
        time = None
        
        for x in self.file_names:
            if(self.pressure_frame[x][0] != None): 
                self.mean_list.append(np.mean(self.pressure_frame[x]))   
                self.names.append(x)
                p1, = self.plot_part(self.pressure_frame[x], x, subplot = ax, zero_mean = zero_mean)
                self.plot_data.append(p1)
                time = self.pressure_frame[x].index
            if(self.temperature_frame[x][0] != None):  
                self.mean_list2.append(np.mean(self.temperature_frame[x]))  
                self.names2.append(x)
                p2, = self.plot_part(self.temperature_frame[x], x, subplot = ax2, zero_mean = zero_mean)
                self.plot_data2.append(p2)
                time = self.temperature_frame[x].index
           
        #ax2.set_xticks(np.linspace(time, 5))
        if(zero_mean == False): 
            ax.set_title('Pressure Data')
            ax2.set_title('Temperature Data')
            self.names.append("Mean")
            self.names2.append("Mean")
            
            p3, = ax.plot(time,np.repeat(np.mean(self.mean_list), len(time)), color="orange", \
                    linewidth="1.0", linestyle="--")
            self.plot_data.append(p3)
            p4, = ax2.plot(time,np.repeat(np.mean(self.mean_list2), len(time)), color="orange", \
                    linewidth="1.0", linestyle="--")
            self.plot_data2.append(p4)
        else:   
            ax.set_title('Pressure Data Zero Mean')
            ax2.set_title('Temperature Data Zero Mean')
        ax.legend(self.plot_data, self.names,bbox_to_anchor=(1.05, 1.0), loc=2, borderaxespad=0.0)
        ax2.legend(self.plot_data2, self.names2,bbox_to_anchor=(1.05, 1.0), loc=2, borderaxespad=0.0)
        ax.set_xlim(time[0],time[::-1][0] + datetime.timedelta(minutes=5))
        ax2.set_xlim(time[0],time[::-1][0] + datetime.timedelta(minutes=5))
        
        if pressure_ylimits != None:
            ax.set_ylim(pressure_ylimits[0],pressure_ylimits[1])
        if temperature_ylimits != None:
            ax2.set_ylim(temperature_ylimits[0],temperature_ylimits[1])
            
            
        plt.show()
        
    def simple_graph(self):
        confidence_array = [.01, .9, .25,.5,.9,.75]
        support_array = [.01, .01, .3, .3,.5, .4]
        
        plt.xlim(0,1)
        plt.ylim(0,1)
        plt.xlabel('Confidence Threshold')
        plt.ylabel('Support Threshold')
        
        plt.scatter(confidence_array, support_array)
        plt.show()
       
if __name__ == "__main__":
    
    #--create an instance    
    graph = Grapher()
    
#     graph.plot_multiple_series_graphs(True,True)
graph.simple_graph()
#     graph.plot_both_together(True)
#     graph.plot_both_together()
   
#     graph.plot_both_together()

#     graph.plot_multiple_series_graphs(True, True)
    

 #  graph.plot_test_data('../../data_files/Big5_240dayNewNoise.nc')
    #graph.plot_both_together(True)
