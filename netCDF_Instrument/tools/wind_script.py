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
     'parameterCd': '00035,00036,61728'
    }

    r = requests.get('http://waterservices.usgs.gov/nwis/iv/', params=params)

    time, speed, u, v, gust =[],[],[],[],[]
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
            print(len(gust), len(v))
            var_datastore.gust_data = gust
            var_datastore.send_wind_data(ds)
#        
    else:
        print('fail')

    
if __name__ == '__main__':
    get_wind_data('jonas_wind-1.nc','01194815', start_date='2016-01-22 00:00', end_date='2016-01-28 06:00', \
                  tz = 'US/Eastern', ds =False)