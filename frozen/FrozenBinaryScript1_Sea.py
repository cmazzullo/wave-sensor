import matplotlib

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import os
import sys
sys.path.append('..')


import pytz
import netCDF4
import netCDF4_utils
import netcdftime

import tkinter as tk
from tools.script1_gui import Wavegui


root = tk.Tk()
gui = Wavegui(root, air_pressure=False)
root.mainloop()