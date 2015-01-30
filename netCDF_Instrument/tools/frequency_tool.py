#!/usr/bin/env python3
from frequency import get_transform
import NetCDF_Utils.nc as nc
# import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Take a filename (a netCDF) containing pressure
# Plot some frequency info

def plot_frequency(fname):
    p = nc.get_pressure(fname)
    t = nc.get_time(fname)
    t -= t[0]
    t /= 1000 # convert ms to seconds
    a, f = get_transform(p, t[1])

    plt.subplot(211)
    plt.semilogy(f, np.absolute(a), '.')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Water pressure (dbar)')
    plt.subplot(212)
    plt.plot(t, p)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Water pressure (dbar)')
    plt.show()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="a netCDF file to analyze")
    args = parser.parse_args()
    plot_frequency(args.filename)
