#!/usr/bin/env python3
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

import matplotlib.pyplot as plt
from NetCDF_Utils import nc
import tools.script1_gui as gc

class Script2gui:
    def __init__(self, root):
        fname = filedialog.askopenfilename()
        root.destroy()
        plot_pressure(fname)

def get_digit(n, digit):
    return (n // 10**(digit - 1)) % 10

def plot_pressure(fname):
    t = nc.get_time(fname) / 1000
    p = nc.get_pressure(fname)
    qc = nc.get_flags(fname)
    bad_points = p[np.where(qc != 11110111)]
    bad_times = t[np.where(qc != 11110111)]
    plt.plot(t, p)
    plt.plot(bad_times, bad_points, 'rx', label='Bad data')
    plt.xlabel('Time (s)')
    plt.ylabel('Pressure (dBar)')
    plt.legend()
    plt.title('Water Pressure with Bad Data Marked')
    plt.show()


if __name__ == '__main__':
    root = Tk()
    g = Script2gui(root)
    root.mainloop()
