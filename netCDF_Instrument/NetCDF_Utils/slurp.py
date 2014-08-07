#!/usr/bin/env python3
"""
This module fetches pressure data from buoys from the internet.

You can get the raw data (by date and station number) or dump the
readings to a netCDF file.

You should be able to do just about everything with the
make_corresponding_file method!
"""

from urllib.request import urlopen
import sys
from datetime import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
import pytz

import SpectralAnalysis.nc as nc

import NetCDF_Utils.DateTimeConvert as dateconvert
from NetCDF_Utils.edit_netcdf import NetCDFWriter


delta = timedelta(days=30)
day = timedelta(days=1)
epoch_start = datetime(year=1970, month=1, day=1, tzinfo=pytz.utc)


def add_air_pressure(fname, station):
    data, lat, lon = get_corresponding_data(fname, station)
    sea_t = nc.get_time(fname)
    sea_p = nc.get_pressure(fname)
    air_t = np.array(data.index)
    air_p = data.values
    print(data.index)
    print(air_t)
    print(type(air_t))
    print(type(sea_t))
    print(type(air_p))
    interp_p = np.interp(sea_t, air_t, air_p)
    print('sea_t', sea_t, 'air_t', air_t)
    plt.plot(sea_t, sea_p)
    plt.plot(air_t, air_p)


def get_corresponding_data(fname, station):
    """Gets air pressure data that covers the time span of the input
    file.

    Inputs:
    fname -- the netCDF file that you'd like to get the corresponding
    air pressure for
    out_fname -- the name of the output file
    station -- the station that you'd like to get your data from

    You can look for buoys by location at:
        http://www.ndbc.noaa.gov/
    """

    t_ms = nc.get_time(fname)
    t = t_ms / 1000
    sea_begin = datetime.fromtimestamp(t[0])
    sea_end = datetime.fromtimestamp(t[-1])
    air_begin = sea_begin - day
    air_end = sea_end + day

    data, lat, lon = get_data(station, air_begin, air_end)
    return data, lat, lon


def get_data(station, begin, end):
    """If the requested time interval is too long, download several
    smaller time intervals and return the concatenated results."""
    if (end - begin) < delta:
        data, lat, lon = _download(station, begin, end)
        return data, lat, lon
    else:
        p1, lat, lon = get_data(station, begin, begin + delta - day)
        p2, lat, lon = get_data(station, begin + delta, end)
        return p1.append(p2), lat, lon


def _datetime_to_string(dt):
    fmt = '%Y%m%d'
    return dt.strftime(fmt)


def _download(station, begin, end):
    begin = _datetime_to_string(begin)
    end = _datetime_to_string(end)
    station = str(station)
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
            lat = float(l[2])
        if line.strip().startswith('Longitude'):
            l = line.split()
            lon = float(l[2])
        elif line.startswith('</pre>'):
            break
        elif precount == 2:
            row = line.split()
            pressures.append(np.float64(row[5]))
            time_str = row[3] + ' ' + row[4]
            time = convert_buoy_time_string(time_str)
            times.append(time)
        elif line.startswith('<pre>'):
            precount += 1
    p = np.array(pressures)
    #    to_ms = dateconvert.convert_date_to_milliseconds
    #    times = [to_ms(None, None, date_time=t) for t in times]
    ms_times = [date_to_ms(t) for t in times]
    # convert mbar to dbar
    return pd.Series(p / 100, index=times), lat, lon


def date_to_ms(date):
    return (date - epoch_start).total_seconds() * 1000

def convert_buoy_time_string(time_str):
    date_format = '%Y-%m-%d %H:%M'
    utc = pytz.utc
    return utc.localize(datetime.strptime(time_str, date_format))


def write_to_netCDF(fname, ts, lat, lon):
    '''Dumps downloaded pressure data to a netCDF for archiving'''
    print('Writing to netCDF...')
    net_writer = NetCDFWriter()
    vs = net_writer.vstore
    vs.pressure_data = list(ts.values)
    vs.utc_millisecond_data = list(ts.index * 1000)
    vs.latitutde = lat
    vs.longitude = lon
#        vs.z = self.z
    net_writer.out_filename = fname
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


import sys
sys.path.append('C:\\Users\\cmazzullo\\wave-sensor\\netCDF_Instrument')


fname = ('C:\\Users\\cmazzullo\\wave-sensor-test-data\\'
         'logger3.csv.nc')

air_fname = ''

out_fname = ''
# 1
sea_p = nc.get_pressure(fname)
sea_t = nc.get_time(fname)
add_air_pressure(fname,  8454000)



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
    if len(sys.argv) == 5:
        station = sys.argv[1]
        station = 8454000
        start = sys.argv[2]
        end = sys.argv[3]
        outfile = sys.argv[4]
        ts, lat, lon = get_data(station, start, end)
        write_to_netCDF(outfile, ts, lat, lon)
    else:
#        print(usage)
        pass
