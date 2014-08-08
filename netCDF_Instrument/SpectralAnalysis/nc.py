"""
A few convenience methods for quickly extracting/changing data in netCDFs
"""

import netCDF4
import os

# Append new variables

def append_air_pressure(fname, p, station, lat, lon):
    name = 'air_pressure'
    comment = ('This is air pressure pulled from the NOAA '
                    'database of buoy barometric pressure readings. '
                    'You can find it at '
                    '"http://opendap.co-ops.nos.noaa.gov/axis/". The '
                    'buoy used corresponds to the station number '
                    'given in the "station" attribute of this '
                    'variable.')
    long_name = 'buoy pressure record'
    _append_variable(fname, name, p, comment, standard_name=name, 
                    short_name=name, long_name=long_name, station=station,
                    lat=lat, lon=lon, buoy=True)


def append_corrected_water_pressure(fname, p):
    comment = ('The corrected water pressure is the "sea_water_pressure" '
               'variable minus the "air_pressure" variable.')
    name = 'sea_water_pressure_due_to_sea_water'
    _append_variable(fname, name, p, comment, standard_name=name, 
                    short_name='corrected_pressure', long_name=name)


def append_depth(fname, depth):
    comment = ('The depth, computed using the variable "corrected water '
               'pressure".')
    name = 'depth'
    _append_variable(fname, name, depth, comment, standard_name=name, 
                    short_name=name, long_name=name, depth=True)
                    
# Get variable data

def get_time(fname):
    return _get_variable_data(fname, 'time')


def get_air_pressure(fname):
    return _get_variable_data(fname, 'air_pressure')


def get_pressure(fname):
    return _get_variable_data(fname, 'sea_water_pressure')


def get_depth(fname):
    return _get_variable_data(fname, 'depth')


def get_corrected_pressure(fname):
    return _get_variable_data(fname, 'sea_water_pressure_due_to_sea_water')

# Get global data

def get_frequency(fname):
    freq_string = _get_global_attribute(fname, 'time_coverage_resolution')
    return float(freq_string[1:-1])
    
    
def get_initial_pressure(fname):
    return _get_global_attribute(fname, 'initial_pressure')


def get_water_depth(fname):
    return _get_global_attribute(fname, 'water_depth')


def get_device_depth(fname):
    return _get_global_attribute(fname, 'device_depth')


def _get_variable_data(fname, variable_name):
    nc = netCDF4.Dataset(fname)
    var = nc.variables[variable_name]
    v = var[:]
    nc.close()
    return v
    
    
def _get_global_attribute(fname, name):
    nc = netCDF4.Dataset(fname)
    return getattr(nc, name)
    
    
def _append_variable(fname, name, p, comment='', standard_name='', 
                    short_name='', long_name='', station=None, lat=None, 
                    lon=None, buoy=False, depth=False):
    nc = netCDF4.Dataset(fname, 'a', format='NETCDF4_CLASSIC')
    pvar = nc.createVariable(name, 'f8', ('time',))
    pvar.ioos_category = ''
    pvar.comment = comment
    pvar.standard_name = standard_name
    pvar.max = 1000
    pvar.min = -1000
    pvar.short_name = short_name
    pvar.ancillary_variables = ''
    pvar.add_offset = 0.0
    pvar.coordinates = 'time latitude longitude altitude'
    pvar.long_name = long_name
    pvar.scale_factor = 1.0
    if depth:
        units = 'meters'
        pvar.nodc_name = 'WATER DEPTH'
    else:
        units = 'decibars'
        pvar.nodc_name = 'PRESSURE'
    pvar.units = units
    pvar.compression = 'not used at this time'
    if buoy:
        pvar.station = station
        pvar.station_latitude = lat
        pvar.station_longitude = lon
    pvar[:] = p