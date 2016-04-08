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
import csv as csv_package
import shutil
import pressure_to_depth as p2d
import NetCDF_Utils.nc as nc
# import DataTests
import uuid
import pandas as pd
import unit_conversion
import pytz
from matplotlib import pyplot as plt
import unit_conversion

def make_depth_file(water_fname, air_fname, out_fname, method='combo', purpose='storm_surge', csv = False, step = 1, \
                    tz = None, dayLightSavings = None, graph = True):
    """Adds depth information to a water pressure file.
    """
    
    #These two declarations may not be used for the new linear wave theory calculations
#     device_depth = -1 * nc.get_device_depth(water_fname)
#     water_depth = nc.get_water_depth(water_fname)
     
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
    raw_pressure = sea_pressure
    sea_pressure[np.where(air_pressure == np.NaN)] = np.NaN
    
    #Get index of first and last point of overlap
    itemindex = np.where(~np.isnan(sea_pressure))
    begin = itemindex[0][0]
    end = itemindex[0][len(itemindex[0]) - 1]
    print('indexes',begin,end)
    
    #Cut off the portion of time series that does not overlap
    sea_time = sea_time[begin:end]
    sea_pressure = sea_pressure[begin:end]
    air_pressure = air_pressure[begin:end]
    raw_pressure = raw_pressure[begin:end]
    O = O[begin:end]
    X = X[begin:end]
    
    #get the mean of the sea pressure
    sea_pressure_mean = np.mean(sea_pressure)
    print(sea_pressure_mean)
    sea_pressure = sea_pressure - sea_pressure_mean
    
    #if for storm surge low pass the pressure time series
    if purpose == 'storm_surge':
        sea_pressure = p2d.lowpass_filter(sea_pressure)
        
        
        sea_pressure = sea_pressure + sea_pressure_mean
        print('sugre pressure max', np.max(sea_pressure), len(sea_pressure))
    elif purpose == 'surface_waves':
        filtered_pressure = p2d.lowpass_filter(sea_pressure)
        sea_pressure = sea_pressure - filtered_pressure
        
        plt.plot(sea_time,sea_pressure, alpha=0.5)
        plt.plot(sea_time,filtered_pressure, alpha=0.5)
        plt.savefig('test.jpg')
        
        sea_pressure = sea_pressure + sea_pressure_mean
    elif purpose == 'get_max':
        
        filtered_pressure = p2d.lowpass_filter(sea_pressure)
        wave_sea_pressure = sea_pressure - filtered_pressure
        filtered_pressure = filtered_pressure + sea_pressure_mean
        p = sea_pressure + sea_pressure_mean
#         sea_pressure = sea_pressure + sea_pressure_mean
        surge_depth = p2d.hydrostatic_method(filtered_pressure)
        wave_depth = p2d.hydrostatic_method(wave_sea_pressure)
        combined_depth = p2d.hydrostatic_method(p)
        final_depth = np.array(O+surge_depth+wave_depth)
       
        index = final_depth.argmax()
        print(O[0], O[-1])
        print(final_depth[index] * unit_conversion.METER_TO_FEET, \
              unit_conversion.convert_ms_to_datestring(sea_time[index], pytz.UTC))
        return (final_depth[index], sea_time[index])
        
        
#     air_qc, bad_data = DataTests.run_tests(air_pressure,1,1)
        
    #"combo" refers to linear wave theory, "naive" refers to hydrostatic 
    if method == 'combo':
        pass
#         depth = p2d.combo_method(sea_time, sea_pressure,
#                                  device_depth, water_depth, timestep)
    elif method == 'naive':
        #return sensor orifice elevation plus the hydrostatic calculation of sea pressure
        depth = O + p2d.hydrostatic_method(sea_pressure)
        print('max depth', np.max(depth))
        raw_depth = O + p2d.hydrostatic_method(raw_pressure)
         
    if len(depth) == len(sea_pressure) - 1: # this is questionable
        depth = np.append(depth, np.NaN)
      
    if purpose == 'storm_surge':
        nc.custom_copy(water_fname, out_fname, begin, end, mode = 'storm_surge', step=step)
        nc.set_global_attribute(out_fname, 'time_coverage_resolution','P1.00S')
    else:  
        #copy all attributes from sea_pressure file
        nc.custom_copy(water_fname, out_fname, begin, end, mode = 'storm_surge', step=step)
#         shutil.copy(water_fname, out_fname)
#         sea_uuid = nc.get_global_attribute(water_fname, 'uuid')
#         nc.set_var_attribute(water_fname, 'sea_pressure', 'sea_uuid', sea_uuid)
#         nc.set_global_attribute(out_fname, 'uuid', uuid.uuid4())
    
    # append air pressure
    nc.append_air_pressure(out_fname, air_pressure[::step], air_fname)
    nc.set_instrument_data(out_fname, 'air_pressure', instr_dict)
    air_uuid = nc.get_global_attribute(air_fname, 'uuid')
    nc.set_var_attribute(out_fname, 'air_pressure', 'air_uuid', air_uuid)
    
    #update the lat and lon comments
    lat_comment = nc.get_variable_attr(out_fname, 'latitude', 'comment')
    nc.set_var_attribute(out_fname, 'latitude', 'comment',  \
                         ''.join([lat_comment, ' Latitude of sea pressure sensor used to derive ' \
                                  'sea surface elevation.']))
    lon_comment = nc.get_variable_attr(out_fname, 'longitude', 'comment')
    nc.set_var_attribute(out_fname, 'longitude', 'comment',  \
                         ''.join([lon_comment, ' Longitude of sea pressure sensor used to derive ' \
                                  'sea surface elevation.']))
    
    #set sea_pressure instrument data to global variables in water_level netCDF
    sea_instr_data = nc.get_instrument_data(water_fname,'sea_pressure')
    for x in sea_instr_data:
        attrname = ''.join(['sea_pressure_',x])
        nc.set_global_attribute(out_fname,attrname,sea_instr_data[x])
        
    nc.set_global_attribute(out_fname,'summary','This file contains two time series: 1)' 
                            'air pressure 2) sea surface elevation.  The latter was derived'
                            ' from a time series of high frequency sea pressure measurements '
                            ' adjusted using the former and then lowpass filtered to remove '
                            ' waves of period 1 second or less.')
    
    lat = nc.get_variable_data(out_fname, 'latitude')
    lon = nc.get_variable_data(out_fname, 'longitude')
    stn_station = nc.get_global_attribute(out_fname, 'stn_station_number')
#     stn_id = nc.get_global_attribute(out_fname, 'stn_instrument_id')
    first_stamp = nc.get_global_attribute(out_fname, 'time_coverage_start')
    last_stamp = nc.get_global_attribute(out_fname, 'time_coverage_end')
    
    nc.set_global_attribute(out_fname,'title','Calculation of water level at %.4f latitude,'
                            ' %.4f degrees longitude from the date range of %s to %s.'
                            % (lat,lon,first_stamp,last_stamp))
    
#     nc.append_depth_qc(out_fname, sea_qc[begin:end], air_qc, purpose)
    nc.append_depth(out_fname, depth[::step])
    nc.append_variable(out_fname, 'raw_depth', raw_depth[::step], 'raw_depth', 'raw_depth')
    nc.set_var_attribute(out_fname, 'water_surface_height_above_reference_datum', \
                         'air_uuid', air_uuid)
    
    if csv == True:
        
        #adjust date times to appropriate time zone
        format_time = [unit_conversion.convert_ms_to_date(x, pytz.utc) for x in sea_time[::step]]
        format_time = unit_conversion.adjust_from_gmt(format_time, tz, dayLightSavings)
        format_time = [x.strftime('%m/%d/%y %H:%M:%S') for x in format_time]
        
        #convert decibars to inches of mercury
        format_air_pressure = air_pressure * unit_conversion.DBAR_TO_INCHES_OF_MERCURY
    
        #convert meters to feet
        format_depth = depth * unit_conversion.METER_TO_FEET
        
        if dayLightSavings != None and dayLightSavings == True: 
            column1 = '%s Daylight Savings Time' % tz 
        else:
            column1 = '%s Time' % tz 
            
        excelFile = pd.DataFrame({column1: format_time, 
                                  'Air Pressure in Inches of Hg': format_air_pressure[::step],
                                  'Storm Tide Water Level in Feet': format_depth[::step]})
        
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
            
        with open(out_file_name, 'w') as csvfile:
            writer = csv_package.writer(csvfile, delimiter=',')
            
            
            csv_header = ["","Latitude: %.4f" % lat, 'Longitude: %.4f' % lon, \
                'STN_Station_Number: %s' % stn_station]
            writer.writerow(csv_header)
           
        
        excelFile.to_csv(path_or_buf=out_file_name, mode='a', columns=[column1,
                                                             'Water Level in Feet',
                                                             'Air Pressure in Inches of Hg'])
        
if __name__ == '__main__':
    final_depth, final_date = make_depth_file('SSS-CT-NEW-04676WV.chop.true.nc', 'SSS-CT-NEW-00012BP.chop.hobo.nc',
                                    'arb', method='naive', purpose='storm_surge', \
                                    csv= False, step=1)
