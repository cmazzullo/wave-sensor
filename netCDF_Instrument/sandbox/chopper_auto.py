import netCDF4
from netCDF_Utils import nc

file_names = ['chop19-27','chop19-34','chop19-41']

def chop_files():
    for x in range(46,70):
        chop_file_name = "chop19-15_%d.nc" % x
        start, end = get_points(chop_file_name)
        for f in file_names:
            nc.chop_netcdf("%s.nc" % f, "%s_%d.nc" % (f,x), start, end)
        
        
def get_points(fname):
    time = nc.get_time(fname)
    return (time[0], time[:-1])
    

    