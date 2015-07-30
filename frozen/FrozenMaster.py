import master
import tkinter as Tk
from tkinter import messagebox
from matplotlib.backends import backend_qt4agg

import scipy
from scipy.integrate.lsoda import *
import scipy.integrate.vode
import scipy.special._ufuncs_cxx
import scipy.sparse.csgraph._validation
from scipy.integrate import *

def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
            
root = Tk.Tk()
gui = master.MasterGui(root)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()