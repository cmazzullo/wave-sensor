import netCDF4
import matplotlib.pyplot as plt
import sys

def read(fname):
    """
    Reads a netCDF file and returns the array inside
    """
    nc = netCDF4.Dataset(fname)
    pvar = nc.variables['sea_water_pressure']
    return pvar[:]
