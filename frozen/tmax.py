'''
Created on Sep 9, 2016

@author: chogg
'''
import os
import argparse
import sys
import numpy
import netCDF4
import netCDF4.utils
from netCDF4 import netcdftime
import netcdftime
from netCDF4 import Dataset
from datetime import datetime

def process_files(path_base):
    
    file_name = ''.join([path_base,"\\","tmax.nc"])
    with Dataset(file_name, 'w', format="NETCDF4_CLASSIC") as ds:
        
            ds.createDimension("time", None)
            ds.createDimension("y", 647)
            ds.createDimension("x", 602)
            
            albers = ds.createVariable("albers_conical_equal_area", "S1")
            setattr(albers, "grid_mapping_name", "albers_conical_equal_area")
            setattr(albers, "false_easting", 0.0)
            setattr(albers, "false_northing" , 0.0)
            setattr(albers, "latitude_of_projection_origin", 23.0)
            setattr(albers, "longitude_of_central_meridian", -84.0)
            setattr(albers, "standard_parallel", (29.5, 45.5))
            setattr(albers, "longitude_of_prime_meridian", 0.0)
            setattr(albers, "semi_major_axis", 6378137.0)
            setattr(albers, "inverse_flattening", 298.257222101)
            setattr(albers, "spatial_ref", "PROJCS[\"unnamed\",GEOGCS[\"NAD83\",DATUM[\"North_American_Datum_1983\",SPHEROID[\"GRS 1980\",6378137,298.257222101,AUTHORITY[\"EPSG\",\"7019\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6269\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9108\"]],AUTHORITY[\"EPSG\",\"4269\"]],PROJECTION[\"Albers_Conic_Equal_Area\"],PARAMETER[\"standard_parallel_1\",29.5],PARAMETER[\"standard_parallel_2\",45.5],PARAMETER[\"latitude_of_center\",23],PARAMETER[\"longitude_of_center\",-84],PARAMETER[\"false_easting\",0],PARAMETER[\"false_northing\",0],UNIT[\"METERS\",1]]")
            setattr(albers, "GeoTransform", "-478000 1524 0 1460296 0 -1524 ")
            
            precip = ds.createVariable("tmax",'f4',(['time','y','x']), fill_value=-9999.0)
            setattr(precip, "long_name", "Maximum Daily Temperature")
            setattr(precip, "units", "Degrees Fahrenheit")
            setattr(precip, "missing_value", -9999.0)
            setattr(precip, "grid_mapping", "albers_conical_equal_area")
            
            time = ds.createVariable("time",'f8',('time'))
            setattr(time, "standard_name", "time")
            setattr(time, "units", "hour since 1895-01-01 00:00:00")
            setattr(time, "calendar", "standard")
            
            x = ds.createVariable("x",'f8',('x'))
            setattr(x, "long_name", "x coordinate of projection")
            setattr(x, "standard_name", "projection_x_coordinate")
            setattr(x, "units", "m")
            
            y = ds.createVariable("y",'f8',('y'))
            setattr(y, "long_name", "y coordinate of projection")
            setattr(y, "standard_name", "projection_y_coordinate")
            setattr(y, "units", "m")
            
    directories = ['']
    file_types = ['.nc']
    xy_data = False
    for root, sub_folders, files in os.walk(path_base):
        nc_index = 0
        for file_in_root in files:
            format_path = root.replace(path_base,'')
            if  format_path in directories:
                index = file_in_root.rfind('.')
                if file_in_root[index:] in file_types:
                    current_file = '\\'.join([root,file_in_root])
                    tmax, x, y = None, None, None
                    
                    if current_file != file_name:
                        with Dataset(current_file, 'a')  as ds:
                            p_val = ds.variables["maximum daily temp"]
                            tmax = p_val[:,:]
                            
                            x_val = ds.variables["x"]
                            x = x_val[:]
                            
                            y_val = ds.variables["y"]
                            y = y_val[:]
                            
                        with Dataset(file_name, 'a') as ds:
                            p_val = ds.variables["tmax"]
                            p_val[nc_index,:,:] = tmax
                        
                            if xy_data == False:
                                x_val = ds.variables["x"]
                                x_val[:] = x
                                
                                y_val = ds.variables["y"]
                                y_val[:] = y
                                
                                xy_data = True
                            
                            time = ds.variables["time"]
                            time[nc_index] = nc_index * 24
                            
                        nc_index += 1
                        
                        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory',
                        help='directory location to process netCDF files')
#     parser.add_argument('file_type',
#                         help='type of file to concatenate')
#   
    args = parser.parse_args(sys.argv[1:])
#     
#     
    process_files(args.directory)
   
    print('Done processing tmax.nc!\n')