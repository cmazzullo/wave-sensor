#!/usr/bin/env python3
'''
This module fetches pressure data from buoys from the internet.

You can get the raw data (by date and station number) or dump the 
readings to a netCDF file.
'''
import sys
sys.path.append('..')
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
import math





try:
    import NetCDF_Utils.DateTimeConvert as dateconvert
    from NetCDF_Utils.edit_netcdf import NetCDFWriter
    from NetCDF_Utils.VarDatastore import DataStore
    from NetCDF_Utils.Testing import DataTests
except:
    print('Check out packaging!')


class Buoydata:
        
    def __init__(self, station_id):
        # Constants
        self.epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
        self.delta = timedelta(days=30)
        self.day = timedelta(days=1)
        self.station_id = station_id
        self.lat = None
        self.lon = None
        self.z = None



# Constants
epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
delta = timedelta(days=30)
day = timedelta(days=1)

def get_data(station_id, begin_date, end_date, out_filename = None):
    print((end_date - begin_date), delta)
    if (end_date - begin_date) < delta:
        data = download(station_id, begin_date, end_date)
        return data
    else:
        print('more')
        p1 = get_data(station_id, begin_date, 
                      begin_date + delta - day)
        p2 = get_data(station_id, begin_date + delta, 
                      end_date)
        return p1.append(p2)

def datetime_to_string(dt):
    fmt = '%Y%m%d'
    return dt.strftime(fmt)

def download(station_id, begin_date, end_date):


    def get_data(self, begin, end):
        '''If the requested time interval is too long, download several 
smaller time intervals and return the concatenated results.'''
        if (end - begin) < self.delta:
            data = self.download(begin, end)
            return data
        else:
            p1 = self.get_data(begin, begin + self.delta - self.day)
            p2 = self.get_data(begin + self.delta, end)
            return p1.append(p2)


    def datetime_to_string(self, dt):
        fmt = '%Y%m%d'
        return dt.strftime(fmt)


    times = [dateconvert.convert_date_to_milliseconds(None,None,date_time=x) for x in times]


    return pd.Series(pressures, index=times)


    def download(self, begin, end):
        begin = self.datetime_to_string(begin)
        end = self.datetime_to_string(end)
        station = str(self.station_id)
        url = ('http://opendap.co-ops.nos.noaa.gov/axis/webservices/'
               'barometricpressure/response.jsp?stationId=%s&'
               'beginDate=%s&endDate=%s&timeZone=0&format=text&Submit='
               'Submit' % (station, begin, end))
        pressures = []
        times = []
        precount = 0
        print('Downloading pressure data...')
        for line in urlopen(url):
            line = line.decode('utf-8')
            if line.strip().startswith('Latitude'):
                l = line.split()
                self.lat = float(l[2])
            if line.strip().startswith('Longitude'):
                l = line.split()
                self.lon = float(l[2])
            elif line.startswith('</pre>'):
                break
            elif precount == 2:
                row = line.split()
                pressures.append(np.float64(row[5]))
                time_str = row[3] + ' ' + row[4]
                time = self.convert_buoy_time_string(time_str)
                times.append(time)
            elif line.startswith('<pre>'):
                precount += 1


        to_ms = dateconvert.convert_date_to_milliseconds
        times = [to_ms(None, None, date_time=t) for t in times]
        return pd.Series(pressures, index=times)



def datetime_to_ms(timestamp):
    d = (timestamp.to_datetime() - epoch_start.replace(tzinfo=None))
    return np.int64(d.total_seconds() * 1000)


    def convert_buoy_time_string(self, time_str):
        date_format = '%Y-%m-%d %H:%M'
        utc = pytz.utc
        return utc.localize(datetime.strptime(time_str, date_format))

    def write_to_netCDF(self, ts, out_filename):
        '''Dumps downloaded pressure data to a netCDF for archiving'''
        print('Writing to netCDF...')
        net_writer = NetCDFWriter()
        vs = net_writer.vstore
        vs.pressure_data = [x for x in ts.values]
        vs.utc_millisecond_data = [x for x in ts.index]
        vs.latitutde = self.lat
        vs.longitude = self.lon
#        vs.z = self.z
        net_writer.out_filename = out_filename
        globs = vs.global_vars_dict
        globs['license'] = ''
        globs['time_coverage_resolution'] = 'P6M'
        globs['summary'] = 'pressure readings from an NCAR buoy.'
        globs['sea_name'] = ''
        vs.pressure_name = "air_pressure"
        vs.pressure_var['long_name'] =  "buoy pressure record"
        vs.pressure_var['standard_name'] = "air_pressure"


        #Tests#
        net_writer.data_tests.pressure_data = ts.values
        ptest = net_writer.data_tests.select_tests('pressure')
        vs.pressure_qc_data = ptest
        net_writer.write_netCDF(vs, len(ts.values))     

def write_to_netCDF(ts, out_filename):
    '''Dumps downloaded pressure data to a netCDF for archiving.'''
    print('Writing to netCDF...')
    if os.path.isfile(out_filename): os.remove(out_filename)
    
    ds = netCDF4.Dataset(out_filename, 'w', format="NETCDF4_CLASSIC")
    time_dimen = ds.createDimension("time",len(ts))
    times = [datetime_to_ms(t) for t in ts.index]
    times = np.array(times, dtype=np.float64)
    p_var = make_pressure_var(ts.values, ds)
    t_var = make_time_var(times, ds)
    ds.comment = "not used at this time"
    
# def write_to_netCDF(ts, out_filename):
#     '''Dumps downloaded pressure data to a netCDF for archiving.'''
#     print('Writing to netCDF...')
#     if os.path.isfile(out_filename): os.remove(out_filename)
#     ds = netCDF4.Dataset(out_filename, 'w', format="NETCDF4_CLASSIC")
#     time_dimen = ds.createDimension("time",len(ts))
#     times = [datetime_to_ms(t) for t in ts.index]
#     times = np.array(times, dtype=np.float64)
#     p_var = make_pressure_var(ts.values, ds)
#     t_var = make_time_var(times, ds)
#     ds.comment = "not used at this time"

    

def write_to_netCDF(ts, out_filename):
    '''Dumps downloaded pressure data to a netCDF for archiving.'''
    print('Writing to netCDF...')
   
    net_writer = NetCDFWriter()
  
    net_writer.vstore.pressure_data = [x for x in ts.values]
    net_writer.vstore.utc_millisecond_data = [x * 1000 for x in ts.index]
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



def compress_np(arr, c=10):
    final = np.zeros(math.floor(len(arr) / c))
    summed = 0
    for i, e in enumerate(arr):
        summed += np.float64(e)
        if i % c == c - 1:
            final[math.floor(i / c)] = summed / c
            summed = 0
    return final

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
        print('emacs')
        station = 8454000
        b = Buoydata(station)
        # Just for testing purposes
        y = '2014'
        m = '04'
        d = '03'
        start = y + m + d
        fmt = '%Y%m%d'
        start = datetime.strptime(start, fmt)
        y = '2014'
        m = '07'
        d = '06'
        end = y + m + d
        end = datetime.strptime(end, fmt)
        pressures = b.get_data(start, end)
        p = compress_np(pressures.values, 5) 
        plt.plot(p)
        plt.show()
        outfile = 'OUTPUT.nc'
        b.write_to_netCDF(pressures, outfile)
    elif len(sys.argv) == 5:
        print(5)
        station = sys.argv[1]
        station = 8454000
        start = sys.argv[2]
        end = sys.argv[3]
        outfile = sys.argv[4]
        b = Buoydata(station)
        ts = b.get_data(start, end)
        b.write_to_netCDF(ts, outfile)
    else:
        print(usage)

