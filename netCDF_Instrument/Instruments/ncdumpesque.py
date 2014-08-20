import netCDF4
from glob import glob
folder = 'C:\\Users\\cmazzullo\\wave-sensor-test-data\\test-csvs\\'
fname = 'C:\\Users\\cmazzullo\\wave-sensor-test-data\\test-csvs\\hobo.csv.nc'

def dump_all(fname):
    """Dump all attributes and variables in a netCDF to stdout"""
    f = netCDF4.Dataset(fname)

    dirset = set(dir(f))

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

for fname in glob(folder + '*.nc'):
    with netCDF4.Dataset(fname) as f:
        print(f.time_coverage_start)
# dump_all(fname)
