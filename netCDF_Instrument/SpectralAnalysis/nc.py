"""A few convenience methods for quickly extracting/changing data in
netCDFs

"""

from datetime import datetime, timedelta
import netCDF4
import os
import pytz

# Constant
fill_value = -1e10

# Append new variables

def append_air_pressure(fname, p):
    name = 'air_pressure'
    long_name = 'air pressure record'
    _append_variable(fname, name, p, '', standard_name=name,
                    short_name=name, long_name=long_name)


def append_depth(fname, depth):
    comment = ('The depth, computed using the variable "corrected water '
               'pressure".')
    name = 'depth'
    _append_variable(fname, name, depth, comment, standard_name=name,
                    short_name=name, long_name=name, depth=True)

# Get variable data

def get_water_depth(in_fname):
    H0 = get_initial_water_depth(in_fname)
    Hf = get_final_water_depth(in_fname)
    t0 = get_deployment_time(in_fname)
    tf = get_retrieval_time(in_fname)
    time = get_time(in_fname)
    m = (Hf - H0) / (tf - t0)
    H = m * time + H0 - m * t0
    return H


def get_depth(fname):
    return _get_variable_data(fname, 'depth')


def get_time(fname):
    return _get_variable_data(fname, 'time')


def get_air_pressure(fname):
    return _get_variable_data(fname, 'air_pressure')


def get_pressure(fname):
    return _get_variable_data(fname, 'sea_water_pressure')

# Get global data

def get_frequency(fname):
    freq_string = _get_global_attribute(fname, 'time_coverage_resolution')
    return float(freq_string[1:-1])


def get_initial_water_depth(fname):
    return _get_global_attribute(fname, 'initial_water_depth')


def get_final_water_depth(fname):
    return _get_global_attribute(fname, 'final_water_depth')


def get_deployment_time(fname):
    return parse_time(fname, 'deployment_time')


def get_retrieval_time(fname):
    return parse_time(fname, 'retrieval_time')


def parse_time(fname, time_name):
    tz = pytz.timezone(_get_global_attribute(fname, 'time_zone'))
    time_str = _get_global_attribute(fname, time_name)
    fmt = '%Y%m%d %H%M'
    time = tz.localize(datetime.strptime(time_str, fmt))
    epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
    time_ms = (time - epoch_start).total_seconds() * 1000
    return time_ms


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
    attr = getattr(nc, name)
    nc.close()
    return attr


def _append_variable(fname, name, p, comment='', standard_name='',
                     short_name='', long_name='', depth=False):
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
    pvar[:] = p
    nc.close()


if __name__ == '__main__':
    ## UNIT TESTS ##
    import matplotlib.pyplot as plt
    print('Running unit test...')
    in_fname = ('C:\\Users\\cmazzullo\\wave-sensor-test-data\\'
                'test-ncs\\logger1.csv.nc')

    time = get_time(in_fname)
    sea_p = get_pressure(in_fname)
    depth = get_water_depth(in_fname)

    plt.plot(time, sea_p, color='b', label='Water pressure')
    plt.plot(time, depth, color='b', label='Water depth')
    plt.legend()
    plt.show()

    f = netCDF4.Dataset(in_fname, 'r', format='NETCDF4_CLASSIC')
    print(f.variables['sea_water_pressure'])
    print(dir(f))
    print(f.device_depth)
    print(f.initial_water_depth)
    print(f.final_water_depth)
    f.close()
