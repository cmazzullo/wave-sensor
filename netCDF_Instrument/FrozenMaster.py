import master
import tkinter as Tk
from tkinter import messagebox


import scipy
from scipy import signal
from scipy.integrate.lsoda import *
import scipy.integrate.vode
import scipy.special._ufuncs_cxx
import scipy.special._ufuncs
from scipy.special._ufuncs import *
import scipy.sparse.csgraph._validation
from scipy.integrate import *
import scipy.__config__
import netCDF4.utils

def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
            
root = Tk.Tk()
gui = master.MasterGui(root)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()