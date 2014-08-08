from NetCDF_Utils.edit_netcdf import NetCDFReader as read
import os


a = read()
ts = a.read_file(os.path.join("..\Instruments","benchmark", "infosys2.nc"), milliseconds_bool = True)


f = open('test.txt','w')
f.write('test,12,33,45.5,1/2/2002\n')

print(len(ts.values))
for x in ts.values:
    print(x)
    value = ((x * 10000) + 43250.1) /245.1
    print(value)
    f.write('$D,2,%f,5\n' % value)
