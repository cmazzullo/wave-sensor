'''
Created on Dec 20, 2016

@author: chogg
'''
import netCDF4
from netCDF4 import Dataset

with Dataset('test.nc', 'w') as ds:
    time_dimen = ds.createDimension("time", 10)
    station_dimen = ds.createDimension("name_strlen", 5)
    
    u = ds.createVariable("lon",'f8')  
    u.setncattr("short_name","lon")  
    u.setncattr("standard_name","longitude")
    u.setncattr("long_name","station longitude")
    u.setncattr("units","degrees_east")
    u.setncattr("_CoordinateAxisType", "Lon")
    u[:] = 100
    
    v = ds.createVariable("lat",'f8')   
    v.setncattr("short_name","lat")  
    v.setncattr("standard_name","latitude")
    v.setncattr("long_name","station latitude")
    v.setncattr("units","degrees_north")
    v.setncattr("_CoordinateAxisType", "Lat")
    v[:] = 100
     
    w = ds.createVariable("alt",'f8')   
    w.setncattr("short_name","alt")   
    w.setncattr("standard_name","altitude")
    w.setncattr("long_name","vertical distance above the surface")
    w.setncattr("units","m")
    w.setncattr("positive", "up")
    w.setncattr("axis", "Z")
    w.setncattr("_CoordinateAxisType","Height")
    w.setncattr("_CoordinateZisPositive","down")
    w[:] =  100
    
    y = ds.createVariable("station_name",'c', ('name_strlen'))    
    y.setncattr("long_name","station name")
    y.setncattr("cf_role","timeseries_id")
    y[:] = '12345'
    
    z = ds.createVariable("time",'f8', ('time'))    
    z.setncattr("standard_name","time")
    z.setncattr("long_name","time of measurement")
    z.setncattr("units","days since 1970-01-01 00:00:00")
    z.setncattr("missing_value", "-999.9")
    z.setncattr("_CoordinateAxisType", "Time")
    z[:] = [(x * 250) + 1404647999870 for x in range(0,10)]
    
    a = ds.createVariable("humidity",'f8', ('time'))    
    a.setncattr("standard_name","specific_humidity")
    a.setncattr("coordinates","lat lon alt")
    a.setncattr("_FillValue",-999.9)
    a[:] = [x for x in range(0,10)]
    
    b = ds.createVariable("temp",'f8', ('time'))    
    b.setncattr("standard_name","air_temperature")
    b.setncattr("units","celsius")
    b.setncattr("coordinates","lat lon alt")
    b.setncattr("_FillValue",-999.9)
    b[:] = [x for x in range(0,10)]
    
    ds.setncattr('featureType', 'timeSeries')
    