'''
Created on Feb 23, 2016

@author: chogg
'''
import requests
import defusedxml.ElementTree as ET
from datetime import datetime
import unit_conversion
from netCDF4 import Dataset
import numpy as np
from netCDF_Utils.var_datastore import DataStore
import pandas as pd
import pytz

def appendHTMLPrefix(string, prefix_type=''):
    if prefix_type == 'gml':
        return ''.join(['{http://www.opengis.net/gml/3.2}', string])
    elif prefix_type == 'om':
        return ''.join(['{http://www.opengis.net/om/2.0}',string])
    else:
        return ''.join(['{http://www.opengis.net/waterml/2.0}',string])
    
def format_time(dates):
    dash_index = dates[0].rfind('+')

    if dash_index == -1:
        dash_index = dates[0].rfind('-')
    
    colon_index = dates[0].rfind(':')
    hour_difference = float(dates[0][dash_index:colon_index])
    dates = [datetime.strptime(x[0:dash_index], '%Y-%m-%dT%H:%M:%S') \
             for x in dates]
    
    dates = unit_conversion.adjust_by_hours(dates, hour_difference)
    dates = [unit_conversion.date_to_ms(x) for x in dates]
    return dates

def get_data_type(attrib, sites):
    site_len = len(sites)
    index = attrib.find(sites)
    first = int(index + site_len+1)
    last = int(index + site_len+6)
    return attrib[first:last]
          
def get_wind_data(file_name,sites,start_date = None, end_date = None, tz=None, ds=None):
    
    
    var_datastore = DataStore(0)
    dt1 = datetime.strptime(start_date,'%Y-%m-%d %H:%M')
    dt1 = unit_conversion.make_timezone_aware(dt1, tz, ds)
    dt2 = datetime.strptime(end_date,'%Y-%m-%d %H:%M')
    dt2 = unit_conversion.make_timezone_aware(dt2,tz,ds)
    
#     print(dt1,dt2)
    
    params = { 'sites': sites,
     'format': 'waterml,2.0',
    'startDT': dt1.isoformat('T'),
    'endDT': dt2.isoformat('T'),
     'parameterCd': '00035,00036,61728,00025'
    }

    r = requests.get('http://waterservices.usgs.gov/nwis/iv/', params=params)
    print(r.url)
    time, speed, u, v, gust, baro =[],[],[],[],[],[]
    lat, lon, name, data_type = None, None, None, None
    
    if r.status_code not in [503, 504]:
        root = ET.fromstring(r.text)
        
        name_search = ''.join(['.//',appendHTMLPrefix('name', prefix_type='gml')])
        for child in root.findall(name_search):
            name = child.text
    
        search = ''.join(['.//',appendHTMLPrefix('observationMember')])
        for child in root.findall(search):
            
            search2 = ''.join(['.//',appendHTMLPrefix('OM_Observation', prefix_type='om')])
            for y in child.findall(search2):
                data_type = get_data_type(y.attrib[appendHTMLPrefix('id', prefix_type='gml')], sites)
            
            
            index = 0
            found_speed = False
            if lat is None:
                c = ''.join(['.//',appendHTMLPrefix('pos', prefix_type='gml')])
                for x in child.findall(c):
                    lat_lon = x.text.split(' ')
                    lat = lat_lon[0]
                    lon = lat_lon[1]
            
            if len(time) == 0:
                a = ''.join(['.//',appendHTMLPrefix('time')])
                for x in child.findall(a):
                    time.append(x.text)
                
            b = ''.join(['.//',appendHTMLPrefix('value')])
            for x in child.findall(b):
                
                if data_type == '00035':
                    speed.append(float(x.text) / unit_conversion.METERS_PER_SECOND_TO_MILES_PER_HOUR)
                
                elif data_type == '00036':
                    u.append(speed[index] * np.sin(float(float(x.text) * np.pi/180)))
                    v.append(speed[index] * np.cos(float(float(x.text) * np.pi/180)))
                    index += 1
                        
                elif data_type == '00025':
                    baro.append(float(x.text) / unit_conversion.DBAR_TO_MM_OF_MERCURY)
                else:
                    gust.append(float(x.text) / unit_conversion.METERS_PER_SECOND_TO_MILES_PER_HOUR)
               
        
        time = format_time(time)
        with Dataset(file_name, 'w', format="NETCDF4_CLASSIC") as ds:
            time_dimen = ds.createDimension("time", len(time))
            station_dimen = ds.createDimension("station_id", len(sites))
            ds.setncattr('stn_station_number',sites)
            var_datastore.global_vars_dict['stn_station_number'] = sites
            var_datastore.global_vars_dict['summary'] = name
            var_datastore.global_vars_dict['comment'] = ''
            var_datastore.global_vars_dict['datum'] = 'NAVD88'
            var_datastore.utc_millisecond_data = time
            var_datastore.latitude = lat
            var_datastore.longitude = lon
            var_datastore.u_data = u
            var_datastore.v_data = v
            var_datastore.gust_data = gust
            var_datastore.pressure_data = baro
            var_datastore.pressure_name = "air_pressure"
            var_datastore.send_wind_data(ds)
#        
    else:
        print('fail')

if __name__ == '__main__':
#     get_wind_data('baro1.nc','0231462300', start_date='2016-10-11 00:00', end_date='2016-10-12 00:00', \
#                   tz = 'US/Eastern', ds =False)
    df = pd.read_csv("C:\\Users\\chogg\\Desktop\\wind.csv", header=None, sep=",")
    
    
    time = ["".join([x," ",y])[:-3] for x, y in zip(df[2].values,df[3].values)]
    speed = np.array(df[5], dtype=float) / unit_conversion.METERS_PER_SECOND_TO_MILES_PER_HOUR
    u = speed * np.sin(np.array(df[7],dtype=float) * np.pi/180)
    v = speed * np.cos(np.array(df[7],dtype=float) * np.pi/180)
    
    var_datastore = DataStore(0)
#     dt1 = datetime.strptime("2016-10-06 00:00",'%Y-%m-%d %H:%M')
#     dt1 = unit_conversion.make_timezone_aware(dt1, "UTC", False)
#     dt2 = datetime.strptime("2016-10-12 12:00",'%Y-%m-%d %H:%M')
#     dt2 = unit_conversion.make_timezone_aware(dt2,"UTC", False)
#     

    time = [pytz.timezone("US/Eastern").localize(datetime.strptime(x, '%Y-%m-%d %H:%M:%S')) \
             for x in time]
    
    time = [unit_conversion.date_to_ms(x) for x in time]
    time = sorted(time)
  
        
     
     
     
    with Dataset("fl_wind.nc", 'w', format="NETCDF4_CLASSIC") as ds:
            time_dimen = ds.createDimension("time", len(time))
            station_dimen = ds.createDimension("station_id", 1)
            ds.setncattr('stn_station_number','1')
            var_datastore.global_vars_dict['stn_station_number'] = '0'
            var_datastore.global_vars_dict['summary'] = '0'
            var_datastore.global_vars_dict['comment'] = ''
            var_datastore.global_vars_dict['datum'] = 'NAVD88'
            var_datastore.utc_millisecond_data = time
            var_datastore.latitude = 0
            var_datastore.longitude = 0
            var_datastore.u_data = u
            var_datastore.v_data = v
            var_datastore.gust_data = list()
            var_datastore.pressure_data = list()
            var_datastore.pressure_name = "air_pressure"
            var_datastore.send_wind_data(ds)