"""
A few convenience methods for quickly extracting/changing data in
netCDFs
"""
import numpy as np
import os
from datetime import datetime
from netCDF4 import Dataset
# import netCDF4_utils, netcdftime # these make cx_freeze work
import pytz
from bitarray import bitarray as bit
# Constant

FILL_VALUE = -1e10

# Utility methods

def chop_netcdf(fname, out_fname, begin, end):
    """Truncate the data in a netCDF file between two indices"""
    if os.path.exists(out_fname):
        os.remove(out_fname)
    length = end - begin
    p = get_pressure(fname)[begin:end]
    t = get_time(fname)[begin:end]
    flags = get_flags(fname)[begin:end]
    alt = get_variable_data(fname, 'altitude')
    lat = get_variable_data(fname, 'latitude')
    long = get_variable_data(fname, 'longitude')
    d = Dataset(fname)
    output = Dataset(out_fname, 'w', format='NETCDF4_CLASSIC')
    output.createDimension('time', length)
    # copy globals
    for att in d.ncattrs():
        setattr(output, att, d.__dict__[att])
    # copy variables
    for key in d.variables:
        name = key
        # datatype = d.variables[key].datatype
        datatype = np.dtype('float64')
        dim = d.variables[key].dimensions
        var = output.createVariable(name, datatype, dim, fill_value=FILL_VALUE)
        for att in d.variables[key].ncattrs():
            if att != '_FillValue':
                setattr(var, att, d.variables[key].__dict__[att])
    output.variables['time'][:] = t
    output.variables['sea_water_pressure'][:] = p
    output.variables['pressure_qc'][:] = flags
    output.variables['altitude'][:] = alt
    output.variables['longitude'][:] = long
    output.variables['latitude'][:] = lat
    d.close()
    output.close()

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

def append_depth_qc(fname, sea_qc, air_qc):
    """Insert depth qc array"""
    depth_name = 'depth_qc'
    air_name = "air_qc"
    air_comment = 'The air_qc is a binary and of the (sea)pressure_qc and air_pressure_qc if an air file is used to calculate depth'
    depth_comment = 'The depth_qc is a binary and of the (sea)pressure_qc and air_pressure_qc'
    flag_masks = '11111111 11111110 11111101 11111011 11110111'
    flag_meanings =  "no_bad_data last_five_vals_identical, outside_valid_range, invalid_rate_of_change, interpolated_data"

    if air_qc != None:
        air_qc = [bit(x) for x in air_qc]
        sea_qc = [bit(str(x)) for x in sea_qc]

        depth_qc = [(air_qc[x] & sea_qc[x]).to01() for x in range(0,len(sea_qc))]
        append_variable(fname, air_name, [x.to01() for x in air_qc], comment=air_comment, long_name=air_name,
                        flag_masks = flag_masks, flag_meanings= flag_meanings)
        append_variable(fname, depth_name, depth_qc, comment=depth_comment, long_name=depth_name,
                         flag_masks = flag_masks, flag_meanings= flag_meanings)
    else:
        append_variable(fname, depth_name, sea_qc, comment=depth_comment, long_name=depth_name,
                         flag_masks = flag_masks, flag_meanings= flag_meanings)


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


def get_flags(fname):
    """Get the time array from the netCDF at fname"""
    return get_variable_data(fname, 'pressure_qc')

def get_time(fname):
    """Get the time array from the netCDF at fname"""
    return get_variable_data(fname, 'time')


def get_air_pressure(fname):
    """Get the air pressure array from the netCDF at fname"""
    return get_variable_data(fname, 'air_pressure')


def get_pressure(fname):
    """Get the water pressure array from the netCDF at fname"""
    return get_variable_data(fname, 'sea_water_pressure')

def get_pressure_qc(fname):
    return get_variable_data(fname, 'pressure_qc')

# Get global data

def get_frequency(fname):
    """Get the frequency of the data in the netCDF at fname"""
    freq_string = get_global_attribute(fname, 'time_coverage_resolution')
    return 1 / float(freq_string[1:-1])


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
                     long_name='', flag_masks = None, flag_meanings = None):
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
        if flag_masks != None:
            pvar.flags_masks = flag_masks
            pvar.flag_meanings = flag_meanings
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
