
import netCDF4
import netCDF4_utils
import netcdftime
from netCDF4 import Dataset

from scipy.optimize import newton
import scipy.sparse.csgraph._validation
import scipy.special._ufuncs_cxx

from tkinter import Tk

import tools.script2_gui as sc2



root = Tk()
g = sc2.Script2gui(root)
root.mainloop()
