#!/usr/bin/env python3
import numpy as np
from pytz import timezone
from csv_readers import Leveltroll, MeasureSysLogger, House, Hobo, RBRSolo, Waveguage

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
    instrument.write(sea_pressure=translated['sea_pressure'])
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


if __name__ == '__main__':

    inputs = {
        'instrument_name' : 'MS TruBlue 255',
        'in_filename' : 'DEKEN11529 BHN4.csv',
        'out_filename' : 'DEKEN11529 BHN4.csv.nc',
        'latitude' : '20',
        'longitude' : '20',
        'salinity' : 'Salt Water (> 30 ppt)',
        'initial_water_depth' : '2',
        'final_water_depth' : '2',
        'device_depth' : '1.5',
        'deployment_time' : '20140101 0000',
        'retrieval_time' : '20140102 0000',
        'tz_info' : 'US/Central',
        'daylightSavings': False,
        'sea_name' : 'Chesapeake Bay',
        'creator_name' : 'Chris Mazzullo',
        'creator_email' : 'stuff@gmail.com',
        'creator_url' : 'zombo.com',
        'sea_pressure' : True,
        'stn_station_number': '1',
        'stn_instrument_id': '1',
        'datum': 'NAVD88',
        'initial_land_surface_elevation': 1,
        'final_land_surface_elevation': 1,
        'device_depth': 1,
        'device_depth2': 1,
        }
    
    convert_to_netcdf(inputs)
