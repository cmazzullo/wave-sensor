#!/usr/bin/env python3
from frequency import get_transform
import NetCDF_Utils.nc as nc
# import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Take a filename (a netCDF) containing pressure
# Plot some frequency info

def plot_frequency(fname):
    minute = 60*1000
    p = nc.get_pressure(fname)
    t = nc.get_time(fname)
    t = t - t[0]
    a, f = get_transform(p, t[1] - t[0])
    plt.subplot(211)
    plt.semilogy(f, np.absolute(a), '.')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Water pressure (dbar)')
    plt.subplot(212)
    plt.plot(t/minute/60, p)
    plt.xlabel('Time (hours)')
    plt.ylabel('Water pressure (dbar)')
    plt.show()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="a netCDF file to analyze")
    args = parser.parse_args()

    plot_frequency(args.filename)
