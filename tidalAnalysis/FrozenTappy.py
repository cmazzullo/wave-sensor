
import netCDF4
import netcdftime
import netCDF4_utils
from netCDF4 import Dataset
import Tkinter as Tk


import pandas as pd
import sys
import os
import os.path
import numpy as np
from scipy.optimize import leastsq
from scipy.optimize import minpack2
from scipy.integrate.lsoda import *
import scipy.integrate.vode
import scipy.special._ufuncs_cxx
import scipy.sparse.csgraph._validation
from scipy.integrate import * 
import datetime


import sparser
import astronomia.calendar as cal
import astronomia.util as uti
import pad.pad as pad
from parameter_database import _master_speed_dict, letter_to_factor_map
import baker

from Tappy2_GUI import TappyGui


root = Tk.Tk()
gui = TappyGui(root)
root.mainloop()

    
