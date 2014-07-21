'''
Created on Jul 21, 2014

@author: Gregory
'''
#!/usr/bin/env python3
from urllib.request import urlopen
import re
import matplotlib.pyplot as plt
import sys
from datetime import datetime
import pandas as pd
import numpy as np
import pytz

try:
    import NetCDF_Utils.DateTimeConvert as nc
except:
    print('Check out packaging!')
def get_buoy_pressure(station_id, begin_date, end_date):
    '''Grabs buoy pressure data from the noaa site and plots it.

get_buoy_pressure(station_id, begin_date, end_date)'''

    station_id = str(station_id)
    url = ('http://opendap.co-ops.nos.noaa.gov/axis/webservices/'
           'barometricpressure/response.jsp?stationId=%s&'
           'beginDate=%s&endDate=%s&timeZone=0&'
           'format=text&Submit=Submit' % (station_id, begin_date, 
                                         end_date))
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
            
    pressures = [np.float64(x) for x in pressures]
    times = [nc.convert_date_to_milliseconds(None,None,datetime=x) for x in times]
    ts = pd.Series(np.divide(pressures,100), index=times)
    return ts
    # plt.plot(pressures)
    # plt.show()

def convert_buoy_time_string(time_str):
    date_format = '%Y-%m-%d %H:%M'
    utc = pytz.utc
    return utc.localize(datetime.strptime(time_str, date_format))

def array_to_dataframe(pressure, start_time):
    '''Turns a pressure array and a datetime into a time series'''
    start_ms = start_time.total_seconds() * 1000
    
        
if __name__ == '__main__':
    if 'emacs' in dir():
        station = 8454000
        start = 20140710
        end = 20140711
    else:
#         station = sys.argv[1]
#         station = 8454000
#         start = sys.argv[2]
#         end = sys.argv[3]
#         print(sys.argv)
        station = 8454000
        start = 20140513
        end = 20140513
    ts = get_buoy_pressure(station, start, end)  
    
    for x in range(0,len(ts)):
        print(ts[x], ts.index[x])

