import netCDF4

fname = 'C:\\Users\\cmazzullo\\wave-sensor-test-data\\test-ncs\\logger1.csv.nc'

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
