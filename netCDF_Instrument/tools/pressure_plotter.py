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
    for i, flag in enumerate(qc):
        # f = str(flag)
        # if get_digit(flag, 1) == 0:
        #     plt.axvspan(t[i], t[i+1], alpha=0.5, color='red', linewidth=0)
        # if get_digit(flag, 2) == 0:
        #     plt.axvspan(t[i], t[i+1], alpha=0.5, color='green', linewidth=0)
        # if get_digit(flag, 3) == 0:
        #     plt.axvspan(t[i], t[i+1], alpha=0.5, color='blue', linewidth=0)
        # if get_digit(flag, 4) == 0:
        #     plt.axvspan(t[i], t[i+1], alpha=0.5, color='yellow', linewidth=0)
        if flag != 1111:
            plt.axvspan(t[i], t[i+1], alpha=0.5, color='red', linewidth=0)
    plt.plot(t, p)
    plt.xlabel('Time (s)')
    plt.ylabel('Pressure (dBar)')
    plt.show()


if __name__ == '__main__':
    root = Tk()
    g = Script2gui(root)
    root.mainloop()
