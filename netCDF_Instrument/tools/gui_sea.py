#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 11 15:20:35 2014

@author: cmazzullo
"""
import tools.script1_gui as core
import tkinter as tk

if __name__ == '__main__':
    root = tk.Tk()
    gui = core.Wavegui(root, air_pressure=False)
    root.mainloop()
