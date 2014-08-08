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
    append_variable(fname, name, p, comment, standard_name=name, 
                    short_name=name, long_name=long_name, station=station,
                    lat=lat, lon=lon, buoy=True)


def append_corrected_water_pressure(fname, p):
    comment = ('The corrected water pressure is the "sea_water_pressure" '
               'variable minus the "air_pressure" variable.')
    name = 'sea_water_pressure_due_to_sea_water'
    append_variable(fname, name, p, comment, standard_name=name, 
                    short_name='corrected_pressure', long_name=name)


def append_variable(fname, name, p, comment='', standard_name='', 
                    short_name='', long_name='', station=None, lat=None, 
                    lon=None, buoy=False):
    nc = netCDF4.Dataset(fname, 'a', format='NETCDF4_CLASSIC')
    pvar = nc.createVariable(name, 'f8', ('time',))
    pvar.ioos_category = 'Pressure'
    pvar.comment = comment
    pvar.standard_name = standard_name
    pvar.max = 1000
    pvar.min = -1000
    pvar.short_name = short_name
    pvar.ancillary_variables = ''
    pvar.add_offset = 0.0
    pvar.coordinates = 'time latitude longitude altitude'
    pvar.long_name = long_name
    pvar.nodc_name = 'PRESSURE'
    pvar.scale_factor = 1.0
    pvar.units = 'decibar'
    pvar.compression = 'not used at this time'
    if buoy:
        pvar.station = station
        pvar.station_latitude = lat
        pvar.station_longitude = lon
    pvar[:] = p

# Get variable data

def get_time(fname):
    return get_variable_data(fname, 'time')


def get_pressure(fname):
    return get_variable_data(fname, 'sea_water_pressure')


def get_air_pressure(fname):
    return get_variable_data(fname, 'air_pressure')


def get_corrected_pressure(fname):
    return get_variable_data(fname, 'sea_water_pressure_due_to_sea_water')


def get_variable_data(fname, variable_name):
    nc = netCDF4.Dataset(fname)
    var = nc.variables[variable_name]
    v = var[:]
    nc.close()
    return v


# Get global data

def get_initial_pressure(fname):
    return get_global_attribute(fname, 'initial_pressure')


def get_water_depth(fname):
    return get_global_attribute(fname, 'water_depth')


def get_device_depth(fname):
    return get_global_attribute(fname, 'device_depth')


def get_global_attribute(fname, name):
    nc = netCDF4.Dataset(fname)
    return getattr(nc, name)