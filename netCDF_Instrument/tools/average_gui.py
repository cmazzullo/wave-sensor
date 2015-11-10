from netCDF4 import Dataset
import pandas as pd
import matplotlib.pyplot as plt
from tools.Averager import file_average

import tkinter as Tk
import tkinter
from tkinter import filedialog
from tkinter import ttk
from tkinter import StringVar
from tkinter.constants import W
import easygui

class AverageGui:
    def __init__(self, root):
       
        self.in_file_name = ''
        self.root = root
        self.root.focus_force()
        self.root.title('Averager GUI')
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

    def average(self):
        '''Method to average and slice pressure data files
          Per request, most likely used to get 2min space data'''
        
        #read in the netCDF file
        try:
            file_average(self.in_file_name, int(self.AveragedPoints.get()), int(self.Increments.get()), self.methodvar.get())
            easygui.msgbox('Success processing the data.', 'Success')
        except:
            easygui.msgbox('Could not average file, check file type', 'Error')
        
       
         
    def select_input(self):
        self.in_file_name = filedialog.askopenfilename()
        self.average()
        self.root.focus_force()
        


if __name__ == '__main__':
    root = Tk.Tk()
    gui = AverageGui(root)
    root.mainloop()

    
