#!/usr/bin/env python3
from urllib.request import urlopen
import re
import matplotlib.pyplot as plt
import sys

def get_buoy_pressure(station_id, begin_date, end_date):
    '''Grabs buoy pressure data from the noaa site and plots it.

get_buoy_pressure(station_id, begin_date, end_date)'''

    station_id = str(station_id)
    url = ('http://opendap.co-ops.nos.noaa.gov/axis/webservices/'
           'barometricpressure/response.jsp?stationId=%s&'
           'beginDate=%s&endDate=%s&timeZone=0&'
           'format=text&Submit=Submit' % (station_id, begin_date, 
                                         end_date))
    result = []
    precount = 0
    for line in urlopen(url):
        line = line.decode('utf-8')
        if line.startswith('</pre>'):
            break
        if precount == 2:
            row = line.split()
            pressure = row[5]
            result.append(pressure)
        if line.startswith('<pre>'):
            precount += 1

    plt.plot(result)
    plt.show()

def convert_buoy_time_string(time_str):
    date_format = 'Y%yM%mD%dH%HM%MS%S'
    stamps = datetime.strptime(time_str, date_format).\
        replace(tzinfo=self.tzinfo)

def array_to_dataframe(pressure, start_time):
    '''Turns a pressure array and a datetime into a time series'''
    start_ms = start_time.total_seconds() * 1000
    
        
if __name__ == '__main__':
    if 'emacs' in dir():
        station = 8454000
        start = 20140710
        end = 20140711
    else:
        station = sys.argv[1]
        station = 8454000
        start = sys.argv[2]
        end = sys.argv[3]
        print(sys.argv)
    get_buoy_pressure(station, start, end)    

