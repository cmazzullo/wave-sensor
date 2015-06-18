'''
Created on Mar 13, 2015

@author: Gregory
'''
#import netCDF4
import numpy
from netCDF4 import Dataset
from datetime import datetime
import pytz

def open_data(file_name, filter_name, out_filename):
    ds1 = Dataset(file_name);
   
    time1 = ds1.variables['time'][:]
    depth1 = ds1.variables['depth'][:]
    
    ds1.close()
    
    ds2 = Dataset(filter_name)
    
    time2 = ds2.variables['time'][:]
    depth2 = ds2.variables['depth'][:]
    
    ds2.close()
    
    depth2 = numpy.interp(time1,time2,depth2);
    
    final_depth = numpy.subtract(depth1,depth2);
    
    fds = Dataset(out_filename,'w',format="NETCDF4_CLASSIC")
    
    fds.createDimension('time', size=len(final_depth))
    final_time = fds.createVariable('time', 'f8',('time',))
    
    epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
    final_time.setncattr('units',"milliseconds since " + epoch_start.strftime("%Y-%m-%d %H:%M:%S"))
    final_time[:] = time1
    depth = fds.createVariable('depth', 'f8', ('time',))
    depth[:] = final_depth
    
    fds.close()
    
    
if __name__ == '__main__':
    open_data('M2_Only_2AmpNoise.nc','outts_filtered_usgs.nc','big5_usgs.nc')
    

