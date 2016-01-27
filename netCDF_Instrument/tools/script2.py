#!/usr/bin/env python3
"""
Created on Thu Aug  7 08:20:07 2014

@author: cmazzullo

Inputs: One netCDF file containing water pressure and one containing
air pressure.

Outputs: One netCDF file containing water pressure, interpolated air
pressure, and water level.
"""


import numpy as np
import shutil
import pressure_to_depth as p2d
import NetCDF_Utils.nc as nc
# import DataTests
import uuid
import pandas as pd


def make_depth_file(water_fname, air_fname, out_fname, method='combo', purpose='storm_surge', csv = False, step = 1):
    """Adds depth information to a water pressure file.
    """
    
    #These two declarations may not be used for the new linear wave theory calculations
    device_depth = -1 * nc.get_device_depth(water_fname)
    water_depth = nc.get_water_depth(water_fname)
     
    #Get the timestep, sea pressure, time and qc
    timestep = 1 / nc.get_frequency(water_fname)
    sea_pressure = nc.get_pressure(water_fname)
    sea_time = nc.get_time(water_fname)
#     sea_qc = nc.get_pressure_qc(water_fname)
    
    #This is going to be reflected by O(t)
    init_orifice_elevation, final_orifice_elvation = \
    nc.get_sensor_orifice_elevation(water_fname)
    O = np.linspace(init_orifice_elevation, final_orifice_elvation, len(sea_pressure))
    
    #This if going to be reflected by B(t)
    init_land_surface_elevation, final_land_surface_elevation = \
    nc.get_land_surface_elevation(water_fname)
    B = np.linspace(init_land_surface_elevation, final_land_surface_elevation, len(sea_pressure))
    
    #Sensor orifice Elevation Minus Land Surface Elevation
    X = O - B
    
    #Get air pressure, time, interpolation, subtract from sea_pressure, and get air qc data
    raw_air_pressure = nc.get_air_pressure(air_fname)
    instr_dict = nc.get_instrument_data(air_fname, 'air_pressure')
    air_time = nc.get_time(air_fname)
    air_pressure = np.interp(sea_time, air_time, raw_air_pressure,
                             left=np.NaN, right=np.NaN)
    sea_pressure = sea_pressure - air_pressure
    sea_pressure[np.where(air_pressure == np.NaN)] = np.NaN
    
    #Get index of first and last point of overlap
    itemindex = np.where(~np.isnan(sea_pressure))
    begin = itemindex[0][0]
    end = itemindex[0][len(itemindex[0]) - 1]
    print('indexes',begin,end)
    
    #Cut off the portion of time series that does not overlap
    sea_pressure = sea_pressure[begin:end]
    air_pressure = air_pressure[begin:end]
    O = O[begin:end]
    X = X[begin:end]
    
    #get the mean of the sea pressure
    sea_pressure_mean = np.mean(sea_pressure)
    sea_pressure = sea_pressure - sea_pressure_mean
    
    #if for storm surge low pass the pressure time series
    if purpose == 'storm_surge':
        sea_pressure = p2d.lowpass_filter(sea_pressure)
        sea_pressure = sea_pressure + sea_pressure_mean
        
    
    
#     air_qc, bad_data = DataTests.run_tests(air_pressure,1,1)
        
    #"combo" refers to linear wave theory, "naive" refers to hydrostatic 
    if method == 'combo':
        depth = p2d.combo_method(sea_time, sea_pressure,
                                 device_depth, water_depth, timestep)
    elif method == 'naive':
        #return sensor orifice elevation plus the hydrostatic calculation of sea pressure
        depth = O + p2d.hydrostatic_method(sea_pressure)
         
    if len(depth) == len(sea_pressure) - 1: # this is questionable
        depth = np.append(depth, np.NaN)
      
    if purpose == 'storm_surge':
        nc.custom_copy(water_fname, out_fname, begin, end, mode = 'storm_surge', step=step)
        nc.set_global_attribute(out_fname, 'time_coverage_resolution','P1.00S')
    else:  
        #copy all attributes from sea_pressure file
        shutil.copy(water_fname, out_fname)
        sea_uuid = nc.get_global_attribute(water_fname, 'uuid')
        nc.set_var_attribute(water_fname, 'sea_pressure', 'sea_uuid', sea_uuid)
        nc.set_global_attribute(out_fname, 'uuid', uuid.uuid4())
    
    # append air pressure
    nc.append_air_pressure(out_fname, air_pressure[::step], air_fname)
    nc.set_instrument_data(out_fname, 'air_pressure', instr_dict)
    air_uuid = nc.get_global_attribute(air_fname, 'uuid')
    nc.set_var_attribute(out_fname, 'air_pressure', 'air_uuid', air_uuid)
    
#     nc.append_depth_qc(out_fname, sea_qc[begin:end], air_qc, purpose)
    nc.append_depth(out_fname, depth[::step])
    
    if csv == True:
        excelFile = pd.DataFrame({'Time': sea_time[begin:end:step], 'AirPressure': air_pressure[::step], \
                                  'WaterLevel': depth[::step]})
        #append file name to new excel file
        last_index = out_fname.find('.')
        out_fname = out_fname[0:last_index]
        
        last_index = out_fname.find('.')
        #save with csv extension if not already done so
        if out_fname[last_index:] != '.csv':
            
            if last_index < 0:
                out_file_name = ''.join([out_fname,'.csv'])
            else:
                out_file_name = ''.join([out_fname[0:last_index],'.csv'])
        else:
            out_file_name = out_fname
            
        excelFile.to_csv(path_or_buf=out_file_name)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("water_fname",
                        help="a netCDF file containing water pressure data")
    parser.add_argument("air_fname",
                        help="a netCDF file containing air pressure data")
    parser.add_argument("out_fname",
                        help="where you want to put the output file")
    parser.add_argument("--fft",
                        help="don't remove linear trends first",
                        dest='method',
                        const='fft',
                        default='combo',
                        action='store_const')
    parser.add_argument("--naive",
                        help="only find the hydrostatic depth",
                        dest='method',
                        const='naive',
                        default='combo',
                        action='store_const')
    args = parser.parse_args()
    make_depth_file(args.water_fname, args.air_fname, args.out_fname,
                    method=args.method)
