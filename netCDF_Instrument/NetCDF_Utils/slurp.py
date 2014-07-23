#!/usr/bin/env python3
'''
This module fetches pressure data from buoys from the internet.

You can get the raw data (by date and station number) or dump the 
readings to a netCDF file.
'''
import sys
sys.path.append('.')
from urllib.request import urlopen
import re
import matplotlib.pyplot as plt
import sys
from datetime import datetime
from datetime import timedelta
import pandas as pd
import netCDF4
import numpy as np
import pytz
import os

try:
    import NetCDF_Utils.DateTimeConvert as dateconvert
    from NetCDF_Utils.edit_netcdf import NetCDFWriter
    from NetCDF_Utils.VarDatastore import DataStore
    from NetCDF_Utils.Testing import DataTests
except:
    print('Check out packaging!')
# Constants
epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
delta = timedelta(days=30)
day = timedelta(days=1)

def get_data(station_id, begin_date, end_date, out_filename = None):
    if (end_date - begin_date) < delta:
        data = download(station_id, begin_date, end_date)
        if out_filename == None:
            out_filename = 'air_pressure.nc'
        write_to_netCDF(data,out_filename)
        return data
    else:
        p1 = get_data(station_id, begin_date, 
                      begin_date + delta - day)
        p2 = get_data(station_id, begin_date + delta, 
                      end_date)
        return p1.append(p2)

def datetime_to_string(dt):
    fmt = '%Y%m%d'
    return dt.strftime(fmt)

def download(station_id, begin_date, end_date):

    begin_date = datetime_to_string(begin_date)
    end_date = datetime_to_string(end_date)
    url = ('http://opendap.co-ops.nos.noaa.gov/axis/webservices/'
           'barometricpressure/response.jsp?stationId=%s&'
           'beginDate=%s&endDate=%s&timeZone=0&format=text&Submit='
           'Submit' % (str(station_id), begin_date, end_date))
    pressures = []
    times = []
    precount = 0
    print('Downloading pressure data...')
    for line in urlopen(url):
        line = line.decode('utf-8')
        if line.startswith('</pre>'):
            break
        if precount == 2:
            row = line.split()
            pressures.append(np.float64(row[5]))
            time_str = row[3] + ' ' + row[4]
            time = convert_buoy_time_string(time_str)
            times.append(time)
        if line.startswith('<pre>'):
            precount += 1

    times = [dateconvert.convert_date_to_milliseconds(None,None,date_time=x) for x in times]
    return pd.Series(pressures, index=times)

def convert_buoy_time_string(time_str):
    date_format = '%Y-%m-%d %H:%M'
    utc = pytz.utc
    return utc.localize(datetime.strptime(time_str, date_format))

def write_to_netCDF(ts, out_filename):
    '''Dumps downloaded pressure data to a netCDF for archiving.'''
    print('Writing to netCDF...')
   
    net_writer = NetCDFWriter()
  
    net_writer.vstore.pressure_data = [x for x in ts.values]
    net_writer.vstore.utc_millisecond_data = [x for x in ts.index]
    net_writer.vstore.latitutde = net_writer.latitude
    net_writer.vstore.longitude = net_writer.longitude
    net_writer.out_filename = out_filename
    
    net_writer.vstore.pressure_name = "air_pressure"
    net_writer.vstore.pressure_var['long name'] =  "buoy pressure record",
    net_writer.vstore.pressure_var['standard_name'] = "air_pressure",
#       
    #Tests#
    net_writer.data_tests.pressure_data = ts.values
    net_writer.vstore.pressure_qc_data = net_writer.data_tests.select_tests('pressure')
    
    net_writer.write_netCDF(net_writer.vstore, len(ts.values))     

if __name__ == '__main__':
    usage = """
usage: slurp STATIONID STARTTIME ENDTIME OUTFILE
Slurps down data from the internet concerning the pressure at certain
buoys and stores it in OUTFILE.
OUTFILE is formatted as a netCDF.

	STATIONID    the ID of the buoy you're interested in
	STARTTIME    format: YYYYMMDD
	ENDTIME	     format: YYYYMMDD
	OUTFILE	     dump to this file
"""
    
#
