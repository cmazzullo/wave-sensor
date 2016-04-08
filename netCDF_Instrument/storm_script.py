'''
Created on Mar 3, 2016

@author: chogg
'''
import sys
import argparse

current_path = sys.path[0]
# sys.path.append(''.join([current_path,'\\..']))
# sys.path.append(''.join([current_path,'\\NetCDF_Utils']))

from tools.storm_options import StormOptions
from tools.storm_netCDF import Storm_netCDF
from tools.storm_graph import StormGraph, Bool
from tools.storm_csv import StormCSV


def process_files(args):
    
    so = StormOptions()
    
    so.air_fname = args.air_fname
    so.sea_fname = args.sea_fname
    
    #check to see if the correct type of files were uploaded
    if so.check_file_types() == False:
        return 3
    
    so.wind_fname = None
    
    so.format_output_fname(args.output_fname)
    so.timezone = args.tz_info
    so.daylight_savings = args.daylight_savings
    
    if args.baro_y_min is not None:
        so.baroYLims.append(args.baro_y_min)
        so.baroYLims.append(args.baro_y_max)
        
    if args.wl_y_min is not None:
        so.wlYLims.append(args.wl_y_min)
        so.wlYLims.append(args.wl_y_max)
    
    #check to see if the time series of the water and air file overlap
    overlap = so.time_comparison()
       
    #if there is no overlap             
    if overlap == 2:
        return 4
    
    try:
        snc = Storm_netCDF()
        so.netCDF['Storm Tide with Unfiltered Water Level'] = Bool(False)
        so.netCDF['Storm Tide Water Level'] = Bool(True)
        snc.process_netCDFs(so)
                 
        scv = StormCSV()
        so.csv['Storm Tide Water Level'] = Bool(True)
        so.csv['Atmospheric Pressure'] = Bool(True)
        scv.process_csv(so)
                
        sg = StormGraph()
        so.graph['Storm Tide with Unfiltered Water Level and Wind Data'] = Bool(False)
        so.graph['Storm Tide with Unfiltered Water Level'] = Bool(True)
        so.graph['Storm Tide Water Level'] = Bool(True)
        so.graph['Atmospheric Pressure'] = Bool(True)
        sg.process_graphs(so)
    except:
        return 5 
    
    #will be either 0 for perfect overlap or 1 for slicing some data
    return overlap

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('air_fname',
                        help='directory location of air pressure netCDF file')
    parser.add_argument('sea_fname',
                        help='directory location of sea pressure netCDF file')
    parser.add_argument('output_fname',
                        help='directory location to output netCDF, csv, and picture files')
    parser.add_argument('tz_info', 
                        help='time zone of instrument output dates')
    parser.add_argument('daylight_savings', type=bool,
                        help='if time zone is in daylight savings')
    parser.add_argument('--baro_y_min', 
                        help='y axis minimum for barometric pressure graph')
    parser.add_argument('--bar_y_max',
                        help='y axis maximum for barometric pressure graph')
    parser.add_argument('--wl_y_min', 
                        help='y axis minimum for water level graph')
    parser.add_argument('--wl_y_max',
                        help='y axis maximum for water level graph')
    
    args = parser.parse_args(sys.argv[1:])
    
    code = process_files(args)
    
    sys.stdout.write(str(code))
    sys.stdout.write('\n')
    sys.stdout.flush()
    
   
    
    
    
    
