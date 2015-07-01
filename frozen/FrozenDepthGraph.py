#!/usr/bin/env python3
import scipy
from scipy.integrate.lsoda import *
import scipy.integrate.vode
import scipy.special._ufuncs_cxx
import scipy.sparse.csgraph._validation
from scipy.integrate import *

import tkinter as Tk
from tools.depth_grapher_gui import DepthGui


root = Tk.Tk()
gui = DepthGui(root)
root.mainloop()