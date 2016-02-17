'''
Created on Feb 17, 2016

@author: chogg
'''
import tools.script1 as script1

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
    
script1.convert_to_netcdf(inputs)