#!/usr/bin/env python3
"""View wave statistics using a graphical interface"""
import numpy as np
import NetCDF_Utils.nc as nc
import tkinter as tk
from tkinter.filedialog import askopenfilename
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import sys
import stats
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import pytz
import unit_conversion as uc

def format_date(x,arb=None):
    '''Format dates so that they are padded away from the x-axis'''
    date_str = mdates.num2date(x).strftime('%I:%M %p \n %b-%d-%Y')
    return ''.join([' ','\n',date_str])

def plot_stats(time, depth, stat_time, stat, ylabel):
    fig, ax1 = plt.subplots()
    # ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    ax1.plot(time, depth, label='Depth')
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('depth (m)', color='b')
    ax2 = ax1.twinx()
    ax2.plot(stat_time, stat, 'ro-')
    ax2.set_ylabel(ylabel, color='r')
    plt.tight_layout()


class StatsViewer:
    def __init__(self, root):
        root.title('Wave Statistics')
        tk.Button(root, text='Load File', command=self.load_file).pack()
        self.stat = tk.StringVar()
        self.stat.set('H1/3')
        tk.OptionMenu(root, self.stat, 'H1/3', 'T1/3').pack()
        self.chunk_size = tk.StringVar()
        self.sizes = {
            'minute(s)': 60,
            'second(s)': 1,
            'hour(s)': 60 * 60,
            'day(s)': 60 * 60 * 24}
        self.chunk_size.set('hour(s)')
        self.number = tk.StringVar()
        self.number.set('1')
        subframe = tk.Frame(root)
        tk.Entry(subframe, textvariable=self.number).pack(side='left')
        tk.OptionMenu(subframe, self.chunk_size, *self.sizes.keys()).pack()
        subframe.pack()
        self.display_button = tk.Button(root, text='Display', command=self.display,
                                        state='disabled')
        self.display_button.pack()

    def load_file(self):
        self.filename = askopenfilename()
        self.display_button['state'] = 'normal'

    def display(self):
        t = nc.get_time(self.filename) / 1000
        d = nc.get_depth(self.filename)
        tstep = t[1] - t[0]
        periodfunc = lambda depth: stats.significant_wave_period(depth, tstep)
        sigfunc = stats.significant_wave_height
        funcs = {'H1/3': (sigfunc, 'H 1/3 (m)'), # contains functions and labels
                 'T1/3': (periodfunc, 'T 1/3 (s)')}
        size = self.sizes[self.chunk_size.get()] * float(self.number.get())
        try:
            tchunks = stats.split_into_chunks(t, tstep, size)
            dchunks = stats.split_into_chunks(d, tstep, size)
        except ValueError:
            tchunks = [t]
            dchunks = [d]
        t_stat = [np.average(tchunk) for tchunk in tchunks]
        # t_stat = [uc.convert_ms_to_datestring(t, pytz.utc) for t in t_stat]
        func = funcs[self.stat.get()][0]
        label = funcs[self.stat.get()][1]
        d_stat = [func(dchunk) for dchunk in dchunks]
        plot_stats(t, d, t_stat, d_stat, label)
        plt.show()


root = tk.Tk()
StatsViewer(root)
root.mainloop()
