import netCDF4
import os


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
