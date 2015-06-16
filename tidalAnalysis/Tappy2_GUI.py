from netCDF4 import Dataset
import pandas as pd
import matplotlib.pyplot as plt
from tappy2 import *

import Tkinter as Tk
import Tkinter
import tkFileDialog as filedialog
from Tkinter import StringVar
from Tkinter import W

class TappyGui:
    def __init__(self, root):
       
        self.in_file_name = ''
        self.root = root
        self.root.title('Tappy (Tidal Analysis Package)')
        
        methods = [('None', 'none'),
                   ('Transform', 'transform'),
                   ('USGS', 'usgs')]

        self.methodvar = StringVar()
        self.methodvar.set('none')

        Tk.Label(root, text='Filter:').pack(anchor=W,pady=2, padx=15)
        for name, kwarg in methods:
            Tk.Radiobutton(root, text=name, variable=self.methodvar,
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
            last_index = 0
            for x in range(0,len(self.in_file_name)):
                if self.in_file_name[x] == '.':
                    last_index = x
                    break
            out_file_name = ''.join([in_file_name[0:last_index],'_average.csv'])
            excelFile.to_csv(path_or_buf=out_file_name)
            
            
        if(method == "netCDF" or method == "both"):
        #append file name to new netCDF file
            last_index = 0
            for x in range(0,len(self.in_file_name)):
                if self.in_file_name[x] == '.':
                    last_index = x
                    break
            
            out_file_name = ''.join([in_file_name[0:last_index],'_average.nc'])
            
            #create new netCDF file with averaged data
            new_ds = Dataset(out_file_name,'w',format="NETCDF4_CLASSIC")
            new_ds.createDimension("time", size=len(rolling_mean))
            new_time = new_ds.createVariable("time","f8", ("time",))
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
        analysis(in_filename,filter="transform")
        if len(filter_filename) > 0:
            for x in filter_filename:
                dotIndex = x.find('.')
                out_filename = "Final%s.nc" % x[0:dotIndex]
                filter_subtraction(in_filename,x,out_filename)
                analysis(out_filename)
        
class MessageDialog(Tkinter.Toplevel):
    """ A template for nice dialog boxes. """

    def __init__(self, parent, message="", title="", buttons=1,
                 wait=True):
        Tkinter.Toplevel.__init__(self, parent)
        body = Tk.Frame(self)
        self.title(title)
        self.boolean = None
        self.parent = parent
        self.transient(parent)
        Tk.Label(body, text=message).pack()
        if buttons == 1:
            b = Tk.Button(body, text="OK", command=self.destroy)
            b.pack(pady=5)
        elif buttons == 2:
            buttonframe = make_frame(body)

            def event(boolean):
                self.boolean = boolean
                self.destroy()

            b1 = Tk.Button(buttonframe, text='YES',
                            command=lambda: event(True))
            b1.grid(row=0, column=0)
            b2 = Tk.Button(buttonframe, text='NO',
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
    return Tk.Frame(frame, padding="3 3 5 5")


root = Tk.Tk()
gui = TappyGui(root)
root.mainloop()

    
