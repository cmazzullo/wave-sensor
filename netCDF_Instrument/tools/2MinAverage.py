from netCDF4 import Dataset
import pandas as pd
import matplotlib.pyplot as plt

import tkinter as Tk
from tkinter import filedialog
from tkinter import ttk


class AverageGui:
    def __init__(self, root):
       
        self.in_file_name = ''
        self.root = root
        self.root.title('Pressure Average')
        self.Label = Tk.Label(self.root, text='Averaged Points (Boxcar Window Size)')
        self.Label.pack()
        self.AveragedPoints = Tk.Entry(self.root)
        self.AveragedPoints.pack()
        self.Label2 = Tk.Label(self.root, text='Data Increments (4 is once a second 480 is once every 2 mins)')
        self.Label2.pack()
        self.Increments = Tk.Entry(self.root)
        self.Increments.pack()
        self.b1 = Tk.Button(self.root, text='Select File', command=self.select_input)
        self.b1.pack()

    def twoMinAverage(self,in_file_name, window, increments):
        ds = Dataset(in_file_name,'r')
        sea_pressure = ds.variables['sea_water_pressure'][:]
        pressure_qc = ds.variables['pressure_qc'][:]
        time = ds.variables["time"][:]
        
        attrDict = {}
        for x in ds.ncattrs():
            attrDict[x] = ds.getncattr(x)
        ds.close()
         
        time_resolution = .25 * increments
        attrDict['time_coverage_resolution'] = ''.join(["P",str(time_resolution),"S"])
        
        
        data_series = pd.Series(sea_pressure, index=time)
        
        rolling_mean = pd.rolling_mean(data_series, window, center=True, min_periods=1)
        rolling_mean = rolling_mean[::increments]
        pressure_qc = pressure_qc[::increments]
        print(len(data_series))
         
        last_index = 0
        for x in range(0,len(self.in_file_name)):
            if self.in_file_name[x] == '.':
                last_index = x
                break
        
        out_file_name = ''.join([in_file_name[0:last_index],'_average.nc'])
        
        print(out_file_name)
        new_ds = Dataset(out_file_name,'w',format="NETCDF4_CLASSIC")
        new_ds.createDimension("time", size=len(rolling_mean))
        new_time = new_ds.createVariable("time","f8", ("time",))
        new_time[:] = [x for x in rolling_mean.index]
        new_depth = new_ds.createVariable("sea_water_pressure","f8", ("time",))
        new_depth[:] = rolling_mean.values
        new_pressure_qc = new_ds.createVariable("pressure_qc", "f8", ("time",))
        new_pressure_qc[:] = pressure_qc
        
        for x in attrDict:
            new_ds.setncattr(x, attrDict[x])
        
        new_ds.close()
         
        plt.plot(rolling_mean.index,rolling_mean.values)
        plt.show()
         
    def select_input(self):
        self.in_file_name = filedialog.askopenfilename()
        print(self.AveragedPoints.get(), self.Increments.get())
        self.twoMinAverage(self.in_file_name, int(self.AveragedPoints.get()), int(self.Increments.get()))


root = Tk.Tk()
gui = AverageGui(root)
root.mainloop()

    
