"""
A few convenience methods for quickly extracting/changing data in
netCDFs
"""

from datetime import datetime
from netCDF4 import Dataset
import netCDF4_utils, netcdftime # these make cx_freeze work
import pytz

# Constant

FILL_VALUE = -1e10

# Utility methods

def parse_time(fname, time_name):
    """Convert a UTC offset in attribute "time_name" to a datetime."""
    timezone_str = get_global_attribute(fname, 'time_zone')
    timezone = pytz.timezone(timezone_str)
    time_str = get_global_attribute(fname, time_name)
    fmt = '%Y%m%d %H%M'
    time = timezone.localize(datetime.strptime(time_str, fmt))
    epoch_start = datetime(year=1970, month=1, day=1, tzinfo=pytz.utc)
    time_ms = (time - epoch_start).total_seconds() * 1000
    return time_ms

# Append new variables

def append_air_pressure(fname, pressure):
    """Insert air pressure array into the netCDF file fname"""
    name = 'air_pressure'
    long_name = 'air pressure record'
    append_variable(fname, name, pressure, comment='',
                     long_name=long_name)


def append_depth(fname, depth):
    """Insert depth array into the netCDF file at fname"""
    comment = ('The depth, computed using the variable "corrected '
               'water pressure".')
    name = 'depth'
    print('len(depth) = ' + str(len(depth)))
    append_variable(fname, name, depth, comment=comment,
                     long_name=name)

# Get variable data

def get_water_depth(in_fname):
    """Get the static water depth from the netCDF at fname"""
    initial_depth = get_initial_water_depth(in_fname)
    final_depth = get_final_water_depth(in_fname)
    initial_time = get_deployment_time(in_fname)
    final_time = get_retrieval_time(in_fname)
    time = get_time(in_fname)
    slope = (final_depth - initial_depth) / (final_time - initial_time)
    depth_approx = slope * (time - initial_time) + initial_depth
    return depth_approx


def get_depth(fname):
    """Get the wave height array from the netCDF at fname"""
    return get_variable_data(fname, 'depth')


def get_time(fname):
    """Get the time array from the netCDF at fname"""
    return get_variable_data(fname, 'time')


def get_air_pressure(fname):
    """Get the air pressure array from the netCDF at fname"""
    return get_variable_data(fname, 'air_pressure')


def get_pressure(fname):
    """Get the water pressure array from the netCDF at fname"""
    return get_variable_data(fname, 'sea_water_pressure')

# Get global data

def get_frequency(fname):
    """Get the frequency of the data in the netCDF at fname"""
    freq_string = get_global_attribute(fname, 'time_coverage_resolution')
    return float(freq_string[1:-1])


def get_initial_water_depth(fname):
    """Get the initial water depth from the netCDF at fname"""
    return get_global_attribute(fname, 'initial_water_depth')


def get_final_water_depth(fname):
    """Get the final water depth from the netCDF at fname"""
    return get_global_attribute(fname, 'final_water_depth')


def get_deployment_time(fname):
    """Get the deployment time from the netCDF at fname"""
    return parse_time(fname, 'deployment_time')


def get_retrieval_time(fname):
    """Get the retrieval time from the netCDF at fname"""
    return parse_time(fname, 'retrieval_time')


def get_device_depth(fname):
    """Get the retrieval time from the netCDF at fname"""
    return get_global_attribute(fname, 'device_depth')


def get_variable_data(fname, variable_name):
    """Get the values of a variable from a netCDF file."""
    with Dataset(fname) as nc_file:
        var = nc_file.variables[variable_name]
        var_data = var[:]
        return var_data

# Backend

def get_global_attribute(fname, name):
    """Get the value of a global attibute from a netCDF file."""
    with Dataset(fname) as nc_file:
        attr = getattr(nc_file, name)
        return attr


def append_variable(fname, standard_name, data, comment='',
                     long_name=''):
    """Append a new variable to an existing netCDF."""
    with Dataset(fname, 'a', format='NETCDF4_CLASSIC') as nc_file:
        pvar = nc_file.createVariable(standard_name, 'f8', ('time',))
        pvar.ioos_category = ''
        pvar.comment = comment
        pvar.standard_name = standard_name
        pvar.max = 1000
        pvar.min = -1000
        pvar.short_name = standard_name
        pvar.ancillary_variables = ''
        pvar.add_offset = 0.0
        pvar.coordinates = 'time latitude longitude altitude'
        pvar.long_name = long_name
        pvar.scale_factor = 1.0
        if standard_name == 'depth':
            pvar.units = 'meters'
            pvar.nodc_name = 'WATER DEPTH'
        else:
            pvar.units = 'decibars'
            pvar.nodc_name = 'PRESSURE'
        pvar.compression = 'not used at this time'
        pvar[:] = data

def ncdump(fname):
    """Dump all attributes and variables in a netCDF to stdout"""
    f = Dataset(fname)


    print('\nDimensions:\n')
    for dim in f.dimensions:
        print(dim, ':\t\t', len(f.dimensions[dim]))

    print('\n\nAttributes:\n\n')
    for att in f.__dict__:
        name = (att + ':').ljust(35)
        value = str(f.__dict__[att]).ljust(50)
        print(name, value)

    print('\n\nVariables:\n\n')
    for att in f.variables:
        name = (att + ':').ljust(35)
        value = str(f.variables[att]).ljust(50)
        print(name, value)
    f.close()
