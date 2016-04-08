#!/usr/bin/env python3
import sys

current_path = sys.path[0]
sys.path.append(''.join([current_path,'\\..']))
sys.path.append(''.join([current_path,'\\..\\NetCDF_Utils']))

import numpy as np
import netCDF_Utils.nc as nc
from pytz import timezone
from csv_readers import Leveltroll, MeasureSysLogger, House, Hobo, RBRSolo, Waveguage
import unit_conversion as uc
import argparse


INSTRUMENTS = {
    'LevelTroll': Leveltroll,
    'RBRSolo': RBRSolo,
    'Wave Guage': Waveguage,
    'USGS Homebrew': House,
    'MS TruBlue 255': MeasureSysLogger,
    'Onset Hobo U20': Hobo }

def convert_to_netcdf(inputs):
    translated = translate_inputs(inputs)
    instrument = INSTRUMENTS[translated['instrument_name']]()
    instrument.user_data_start_flag = 0
    for key in translated:
        setattr(instrument, key, translated[key])
    instrument.read()
    instrument.write(pressure_type=translated['pressure_type'])
    return instrument.bad_data


DATATYPES = {
    'latitude': np.float32,
    'longitude': np.float32,
    'initial_water_depth': np.float32,
    'final_water_depth': np.float32,
    'device_depth': np.float32,
    'tzinfo': timezone,
    'sea_pressure' : bool }

def translate(inputs):
    translated = translate_inputs(inputs)
    instrument = INSTRUMENTS[translated['instrument_name']]()
    instrument.user_data_start_flag = 0
    for key in translated:
        setattr(instrument, key, translated[key])

def translate_inputs(inputs):
    translated = dict()
    for key in inputs: # cast everything to the right type
        if key in DATATYPES:
            translated[key] = DATATYPES[key](inputs[key])
        else:
            translated[key] = inputs[key]
    return translated

def find_index(array, value):
    
    array = np.array(array)
    idx = (np.abs(array-value)).argmin()
    
    return idx

def check_file_type(file_name):
    index = file_name.rfind('.')
    if file_name[index:] == '.csv':
        return True
    else:
        return False
    
def process_file(args):
    daylight_savings = False
    if args.daylight_savings.lower() == 'true':
        daylight_savings = True
        
    inputs = {
        'in_filename' : args.in_file_name,
        'out_filename' : args.out_file_name,
        'creator_name' : args.creator_name,
        'creator_email' : args.creator_email,
        'creator_url' : args.creator_url,
        'instrument_name' : args.instrument_name,
        'stn_station_number': args.stn_station_number,
        'stn_instrument_id': args.stn_instrument_id,
        'latitude' : args.latitude,
        'longitude' : args.longitude,
        'tz_info' : args.tz_info,
        'daylight_savings': daylight_savings,
        'datum': args.datum,
        'initial_sensor_orifice_elevation': args.initial_sensor_orifice_elevation,
        'final_sensor_orifice_elevation': args.final_sensor_orifice_elevation,
        'salinity' : args.salinity,
        'initial_land_surface_elevation': args.initial_land_surface_elevation,
        'final_land_surface_elevation': args.final_land_surface_elevation,
        'deployment_time' : args.deployment_time,
        'retrieval_time' : args.retrieval_time,
        'sea_name' : args.sea_name,    
        'pressure_type' : args.pressure_type,
        'good_start_date': args.good_start_date,
        'good_end_date': args.good_end_date
        }
     
    #checks for the correct file type
    if check_file_type(inputs['in_filename']) == False:
        return 2
       
    #check for dates in chronological order if sea pressure file
    if inputs['pressure_type'] == 'Sea Pressure':
        inputs['deployment_time'] = uc.datestring_to_ms(inputs['deployment_time'], '%Y%m%d %H%M', \
                                                             inputs['tz_info'],
                                                             inputs['daylight_savings'])
        
        inputs['retrieval_time'] = uc.datestring_to_ms(inputs['retrieval_time'], '%Y%m%d %H%M', \
                                                             inputs['tz_info'],
                                                             inputs['daylight_savings'])
        if inputs['retrieval_time'] <= inputs['deployment_time']:
            return 4
        
    
        
    data_issues = convert_to_netcdf(inputs)
     
    time = nc.get_time(inputs['out_filename'])
    
    start_index = find_index(time,uc.datestring_to_ms(inputs['good_start_date'], '%Y%m%d %H%M', \
                                                         inputs['tz_info'],
                                                         inputs['daylight_savings']))
    end_index = find_index(time,uc.datestring_to_ms(inputs['good_end_date'], '%Y%m%d %H%M', \
                                                         inputs['tz_info'],
            
                                                         inputs['daylight_savings']))
    #checks for chronological order of dates
    if end_index <= start_index:
        return 4
       
    
    air_pressure = False
    if args.pressure_type == 'Air Pressure':
        air_pressure = True
         
    try:
        nc.chop_netcdf(inputs['out_filename'], ''.join([inputs['out_filename'],'chop.nc']), 
                       start_index, end_index, air_pressure)
    except:
        return 5
        
    
    if data_issues:
        return 1
    else:
        return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file_name',
                        help='directory location of input csv')
    parser.add_argument('out_file_name',
                        help='directory location to output netCDF file')
    parser.add_argument('creator_name',
                        help='name of user running the script')
    parser.add_argument('creator_email',
                        help='email of user running the script')
    parser.add_argument('creator_url',
                        help='url of organization the user running the script belongs to')
    parser.add_argument('instrument_name',
                        help='name of the instrument used to measure pressure')
    parser.add_argument('stn_station_number',
                        help='STN Site ID')
    parser.add_argument('stn_instrument_id',
                        help='STN Instrument ID')
    parser.add_argument('latitude', type=float,
                        help='latitude of instrument')
    parser.add_argument('longitude', type=float,
                        help='longitude of instrument')
    parser.add_argument('tz_info', 
                        help='time zone of instrument output dates')
    parser.add_argument('daylight_savings', 
                        help='if time zone is in daylight savings')
    parser.add_argument('datum', 
                        help='geospatial vertical reference point')
    parser.add_argument('initial_sensor_orifice_elevation', type=float,
                        help='tape down to sensor at deployment time')
    parser.add_argument('final_sensor_orifice_elevation', type=float,
                        help='tape down to sensor at retrieval time')
    parser.add_argument('--salinity',
                        help='salinity of the sea surface')
    parser.add_argument('--initial_land_surface_elevation', type=float,
                        help='tape down to sea floor at deployment time')
    parser.add_argument('--final_land_surface_elevation', type=float,
                        help='tape down to sea floor at retrieval time')
    parser.add_argument('--deployment_time',
                        help='time when the instrument was deployed')
    parser.add_argument('--retrieval_time',
                        help='time when the instrument was retrieved')
    parser.add_argument('--sea_name',
                        help='name of the body of water the instrument was deployed in')
    parser.add_argument('pressure_type',
                        help='pick whether to run file as a sea or air pressure data')
    parser.add_argument('good_start_date',
                        help='first date for chopping the time series')
    parser.add_argument('good_end_date',
                        help='last date for chopping the time series')
    
    
    args = parser.parse_args(sys.argv[1:])
    code = process_file(args)
    
    sys.stdout.write(str(code))
    sys.stdout.write('\n')
    sys.stdout.flush()
    
    
