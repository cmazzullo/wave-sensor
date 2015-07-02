import netCDF4
from netCDF4 import Dataset
import netCDF4_utils
import netcdftime
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg

import PySide
import tkinter as Tk
import easygui
from tools.average_gui import AverageGui
    


root = Tk.Tk()
gui = AverageGui(root)
root.mainloop()

    
