#!/usr/bin/env python3
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from matplotlib.backends import backend_qt4agg

import tkinter as Tk
from tkinter import filedialog

import pytz
import netCDF4
import netCDF4_utils
import netcdftime
from netCDF4 import Dataset
from dateutil import parser
from datetime import datetime
from pytz import timezone
from tools.chopper import Chopper


root = Tk.Tk()
gui = Chopper(root)
root.mainloop()
