import netCDF4
import os



def append_air_pressure(fname, p, station, lat, lon):
    nc = netCDF4.Dataset(fname, 'a', format='NETCDF4_CLASSIC')
    try:
        pvar = nc.createVariable('air_pressure', 'f8', ('time',))
    except RuntimeError:
        print('Output file already contains air pressure!')
        return False
    pvar.ioos_category = 'Pressure'
    pvar.comment = ('This is air pressure pulled from the NOAA '
                    'database of buoy barometric pressure readings. '
                    'You can find it at '
                    '"http://opendap.co-ops.nos.noaa.gov/axis/". The '
                    'buoy used corresponds to the station number '
                    'given in the "station" attribute of this '
                    'variable.')
    pvar.standard_name = 'air_pressure'
    pvar.max = 1000
    pvar.min = -1000
    pvar.short_name = 'air_pressure'
    pvar.ancillary_variables = ''
    pvar.add_offset = 0.0
    pvar.coordinates = 'time latitude longitude altitude'
    pvar.long_name = 'buoy pressure record'
    pvar.nodc_name = 'PRESSURE'
    pvar.scale_factor = 1.0
    pvar.units = 'decibar'
    pvar.compression = 'not used at this time'
    pvar[:] = p
    return True


def append_corrected_water_pressure(fname, p):
    nc = netCDF4.Dataset(fname, 'a', format='NETCDF4_CLASSIC')
    name = 'sea_water_pressure_due_to_sea_water'
    try:
        pvar = nc.createVariable(name, 'f8', ('time',))
    except RuntimeError:
        print('Output file already contains corrected pressure!')
        return
    pvar.ioos_category = 'Pressure'
    pvar.comment = ('The corrected water pressure is the '
                    '"sea_water_pressure" variable minus the '
                    '"air_pressure" variable.')
    pvar.standard_name = name
    pvar.max = 1000
    pvar.min = -1000
    pvar.short_name = 'corrected_pressure'
    pvar.ancillary_variables = ''
    pvar.add_offset = 0.0
    pvar.coordinates = 'time latitude longitude altitude'
    pvar.long_name = 'corrected pressure record'
    pvar.nodc_name = 'PRESSURE'
    pvar.scale_factor = 1.0
    pvar.units = 'decibar'
    pvar.compression = 'not used at this time'
    pvar[:] = p
    return True


def nc_to_dict(fname):
    """
    Reads a netCDF file and returns the array inside
    """
    nc = netCDF4.Dataset(fname)
    return nc.variables


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


def add_height_to_file(fname, height):
    writer = netCDF4.Dataset(fname, 'a', format='NETCDF4_CLASSIC')
    wave_height = writer.createVariable('wave_height','f8',('time',))
    wave_height.units = 'meters'
    wave_height[:] = height
    writer.close()


if __name__ == '__main__':
    fname = ('C:\\Users\\cmazzullo\\wave-sensor-test-data\\'
             'wave-guage-14-07-2014.csv.nc')
    print(fname)
    nc = netCDF4.Dataset(fname)
