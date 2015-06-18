import netCDF4
from netCDF4 import Dataset
import netCDF4_utils
import netcdftime
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg

import PySide
import tkinter
import tkinter as Tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import StringVar
from tkinter.constants import W

class AverageGui:
    def __init__(self, root):
       
        self.in_file_name = ''
        self.root = root
        self.root.title('Pressure Average')
        self.Label = Tk.Label(self.root, text='Averaged Points: (Boxcar Window Size)')
        self.Label.pack(anchor=W, pady=2, padx=15)
        self.AveragedPoints = Tk.Entry(self.root)
        self.AveragedPoints.pack(anchor=W, pady=2, padx=15)
        self.Label2 = Tk.Label(self.root, text='Data Increments: (e.g. 4 is once a second, 480 is once every 2 mins)')
        self.Label2.pack(anchor=W, pady=2, padx=15)
        self.Increments = Tk.Entry(self.root)
        self.Increments.pack(anchor=W, pady=2, padx=15)
        
        methods = [('Excel CSV', 'excel'),
                   ('netCDF', 'netcdf'),
                   ('Excel CSV & netCDF', 'both')]

        self.methodvar = StringVar()
        self.methodvar.set('excel')

        ttk.Label(root, text='File Format: (Saves in same directory as file)').pack(anchor=W,pady=2, padx=15)
        for name, kwarg in methods:
            ttk.Radiobutton(root, text=name, variable=self.methodvar,
                            value=kwarg).pack(anchor=W,pady=2, padx=15)
                            
        self.b1 = Tk.Button(self.root, text='Select File', command=self.select_input)
        self.b1.pack(anchor=W,pady=2, padx=15)

    def twoMinAverage(self,in_file_name, window, increments):
        '''Method to average and slice pressure data files
          Per request, most likely used to get 2min space data'''
        
        #read in the netCDF file
        ds = Dataset(in_file_name,'r')
        sea_pressure = ds.variables['sea_water_pressure'][:]
        pressure_qc = ds.variables['pressure_qc'][:]
        time = ds.variables["time"][:]
        units = ds.variables['time'].units
        
        #input all of the global attributes to a dictionary
        attrDict = {}
        for x in ds.ncattrs():
            attrDict[x] = ds.getncattr(x)
        ds.close()
         
        time_resolution = .25 * increments
        attrDict['time_coverage_resolution'] = ''.join(["P",str(time_resolution),"S"])
        
        #create series for both pressure and pressure_qc
        data_series = pd.Series(sea_pressure, index=time)
        pressure_qc_series = pd.Series(pressure_qc, index=time)
        
        df = pd.DataFrame({"Pressure": data_series, "Pressure_QC": pressure_qc_series})
        
        #box car average and drop the NaN rows
        df.Pressure = pd.rolling_mean(data_series, window, center=True, min_periods=1)
        df = df[pd.notnull(df.Pressure)]
        
        rolling_mean = df.Pressure[::increments]
        pressure_qc = df.Pressure_QC[::increments]
        
        method = self.methodvar.get()
        
        if(method == "excel" or method == "both"):
            excelFile = pd.DataFrame({'Time': rolling_mean.index, 'Pressure': rolling_mean.values})
            #append file name to new excel file
            last_index = in_file_name.find('.')
            
            out_file_name = ''.join([in_file_name[0:last_index],'_average.csv'])
            excelFile.to_csv(path_or_buf=out_file_name)
            
            
        if(method == "netcdf" or method == "both"):
        #append file name to new netCDF file
            last_index = in_file_name.find('.')
            
            out_file_name = ''.join([in_file_name[0:last_index],'_average.nc'])
            
            #create new netCDF file with averaged data
            new_ds = Dataset(out_file_name,'w',format="NETCDF4_CLASSIC")
            new_ds.createDimension("time", size=len(rolling_mean))
            new_time = new_ds.createVariable("time","f8", ("time",))
            new_time.setncattr('units', units)
            new_time[:] = [x for x in rolling_mean.index]
            new_depth = new_ds.createVariable("sea_water_pressure","f8", ("time",))
            new_depth[:] = rolling_mean.values
            new_pressure_qc = new_ds.createVariable("pressure_qc", "f8", ("time",))
            new_pressure_qc[:] = [x for x in pressure_qc]
            
            for x in attrDict:
                new_ds.setncattr(x, attrDict[x])
            
            new_ds.close()
        MessageDialog(root, message="Success! Averaged Pressure File saved.",
                         title='Success!')
        
        plt.plot(rolling_mean.index,rolling_mean.values)
        plt.show()
         
    def select_input(self):
        self.in_file_name = filedialog.askopenfilename()
        print(self.AveragedPoints.get(), self.Increments.get())
        self.twoMinAverage(self.in_file_name, int(self.AveragedPoints.get()), int(self.Increments.get()))
         
  
class MessageDialog(tkinter.Toplevel):
    """ A template for nice dialog boxes. """

    def __init__(self, parent, message="", title="", buttons=1,
                 wait=True):
        tkinter.Toplevel.__init__(self, parent)
        body = ttk.Frame(self)
        self.title(title)
        self.boolean = None
        self.parent = parent
        self.transient(parent)
        ttk.Label(body, text=message).pack()
        if buttons == 1:
            b = ttk.Button(body, text="OK", command=self.destroy)
            b.pack(pady=5)
        elif buttons == 2:
            buttonframe = make_frame(body)

            def event(boolean):
                self.boolean = boolean
                self.destroy()

            b1 = ttk.Button(buttonframe, text='YES',
                            command=lambda: event(True))
            b1.grid(row=0, column=0)
            b2 = ttk.Button(buttonframe, text='NO',
                            command=lambda: event(False))
            b2.grid(row=0, column=1)
            buttonframe.pack()

        body.pack()
        self.grab_set()
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        if wait:
            self.wait_window(self)

def make_frame(frame, header=None):
    """Make a frame with uniform padding."""
    return ttk.Frame(frame, padding="3 3 5 5")


root = Tk.Tk()
gui = AverageGui(root)
root.mainloop()