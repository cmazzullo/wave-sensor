import netCDF4
import matplotlib.pyplot as plt
import os
import netCDF4

def read(fname):
    """
    Reads a netCDF file and returns the array inside
    """
    nc = netCDF4.Dataset(fname)
    pvar = nc.variables['sea_water_pressure']
    return pvar[:]


def write(fname, in_t, in_p):
    remove_if_existing(fname)
    ds = netCDF4.Dataset(fname, 'w', format="NETCDF4_CLASSIC")
    ds.createDimension("time", len(in_t))
    t = ds.createVariable('time', 'f8', ('time',))
    p = ds.createVariable('sea_water_pressure', 'f8', ('time',))
    t[:] = in_t
    p[:] = in_p
    
    
def remove_if_existing(fname):
    if os.path.isfile(fname):
        os.remove(fname)