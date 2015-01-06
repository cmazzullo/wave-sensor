# -*- coding: utf-8 -*-
"""
Created on Mon Aug 11 15:16:01 2014

@author: cmazzullo
"""
import gui.guicore as core
from tkinter import *

if __name__ == '__main__':
    root = Tk()
    gui = core.Wavegui(root, air_pressure=True)
    root.mainloop()
