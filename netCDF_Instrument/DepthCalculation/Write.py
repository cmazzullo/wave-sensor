from NetCDF_Utils.edit_netcdf import NetCDFReader as read
import os


a = read()
ts = a.read_file(os.path.join("..\Instruments","benchmark", "infosys2.nc"), milliseconds_bool = True)


f = open('test.txt','w')
f.write('test,12,33,45.5,1/2/2002\n')

for x in ts.values:
    value = (x + 43250) / 254.1
    f.write('$D,2,%f,5\n' % value)
