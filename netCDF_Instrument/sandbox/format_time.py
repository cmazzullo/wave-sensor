'''
Created on Mar 10, 2016

@author: chogg
'''
import os
import argparse
import sys
from netCDF4 import Dataset
from datetime import datetime

def process_files(path_base):

    directories = ['']
    file_types = ['.nc']
    for root, sub_folders, files in os.walk(path_base):
        for file_in_root in files:
             
            format_path = root.replace(path_base,'')
            if  format_path in directories:
                index = file_in_root.rfind('.')
                if file_in_root[index:] in file_types:
                    
                    with Dataset(file_in_root, 'a') as nc_file:
                        var = nc_file.variables['time']
                        setattr(var, 'title', 'Time')
                        setattr(var, 'calendar', 'gregorian')
                        setattr(var, 'axis', 'T')
                        
                        units = var.getncattr('units')
                        units = units.replace('seconds since ','')
                        dt = datetime.strptime(units, '%Y-%m-%d %H:%M:%S')
                        format_time = dt.strftime('%Y-%b-%d %H:%M:%S')
                        
                        setattr(var, 'time_origin', format_time.upper())
                        setattr(var, 'units', ''.join(['days since ', units]))
                        
                        setattr(var, 'title', 'Time')
                        setattr(var, 'title', 'Time')
                        setattr(var, 'title', 'Time')
                        
                        time = var[:]
                        time = [x / 86400.0 for x in time]
                        var[:] = time
                        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory',
                        help='directory location to process netCDF files')
  
    args = parser.parse_args(sys.argv[1:])
    
    code = process_files(args.directory)
    
    print('Done processing!\n')