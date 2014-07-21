#!/usr/bin/env python3
'''
This module fetches pressure data from buoys from the internet.

You can get the raw data (by date and station number) or dump the 
readings to a netCDF file.
'''

from urllib.request import urlopen
import re
#import matplotlib.pyplot as plt
import sys
from datetime import datetime
import pandas as pd
import netCDF4
import numpy as np
import pytz
import os

epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)

def get_buoy_pressure(station_id, begin_date, end_date):
    '''Grabs buoy pressure data from the noaa site.

get_buoy_pressure(station_id, begin_date, end_date)'''

    station_id = str(station_id)
    url = ('http://opendap.co-ops.nos.noaa.gov/axis/webservices/'
           'barometricpressure/response.jsp?stationId=%s&'
           'beginDate=%s&endDate=%s&timeZone=0&format=text&Submit='
           'Submit' % (station_id, begin_date, end_date))
    pressures = []
    times = []
    precount = 0
    for line in urlopen(url):
        line = line.decode('utf-8')
        if line.startswith('</pre>'):
            break
        if precount == 2:
            row = line.split()
            pressures.append(row[5])
            time_str = row[3] + ' ' + row[4]
            time = convert_buoy_time_string(time_str)
            times.append(time)
        if line.startswith('<pre>'):
            precount += 1

    return pd.Series(pressures, index=times)

def convert_buoy_time_string(time_str):
    date_format = '%Y-%m-%d %H:%M'
    return datetime.strptime(time_str, date_format)

def datetime_to_ms(timestamp):
    return np.int64((timestamp.to_datetime() - epoch_start.replace(tzinfo=None)).\
        total_seconds() * 1000)

def make_pressure_var(pressure, ds):
    p_var = ds.createVariable('air_pressure', 'f8', ('time', ))
    p_var.long_name = "buoy pressure record"
    p_var.standard_name = "air_pressure"
    p_var.short_name = "pressure"
    p_var.nodc_name = "pressure".upper()
    p_var.units = "decibar"
    p_var.scale_factor = np.float32(1.0)
    p_var.add_offset = np.float32(0.0)
    p_var.compression = "not used at this time"
    p_var.min = np.float32(-10000)
    p_var.max = np.float32(10000)
    p_var.ancillary_variables = ''
    p_var.coordinates = "time latitude longitude altitude"
    p_var.ioos_category = "Pressure" ;
    p_var[:] = np.array(pressure, dtype=np.float64)
    return p_var

def make_time_var(times, ds):
    t_var = ds.createVariable("time", "f8", ("time", ))
    t_var.long_name = 'Time'
    t_var.short_name = 'time'
    t_var.standard_name = "time"
    t_var.units = ("milliseconds since " +
                   epoch_start.strftime("%Y-%m-%d %H:%M:%S"))
    t_var.calendar = "gregorian"
    t_var.axis = 'T'
    t_var.ancillary_variables = ''
    t_var.comment = ''
    t_var.ioos_category = "Time" ;
    t_var.add_offset = 0.0
    t_var.scale_factor = 1.0
    t_var.compression = "not used at this time"
    t_var[:] = times
    return t_var
    
def write_to_netCDF(ts, out_filename):
    '''Dumps downloaded pressure data to a netCDF for archiving.'''
    print('Writing to netCDF...')

    if os.path.isfile(out_filename):
        os.remove(out_filename)
        
    ds = netCDF4.Dataset(out_filename, 'w', format="NETCDF4_CLASSIC")
    time_dimen = ds.createDimension("time",len(ts))


    times = ts.index
    times = [datetime_to_ms(t) for t in times]
    times = np.array(times, dtype=np.float64)

    pressure = ts.values

    p_var = make_pressure_var(pressure, ds)
    t_var = make_time_var(times, ds)
    ds.comment = "not used at this time"
    
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
# Just for testing purposes
    if 'emacs' in dir():
        station = 8454000
        start = 20140710
        end = 20140711
        ts = get_buoy_pressure(station, start, end)
    elif len(sys.argv) == 5:
        station = sys.argv[1]
        station = 8454000
        start = sys.argv[2]
        end = sys.argv[3]
        outfile = sys.argv[4]
        ts = get_buoy_pressure(station, start, end)
        write_to_netCDF(ts, outfile)
    else:
        print(usage)
