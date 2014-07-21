'''
Created on Jul 21, 2014

@author: Gregory
'''
import numpy as np
import pytz
from datetime import datetime

epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)

def convert_to_milliseconds(series_length, datestring, frequency):
        return  np.arange(series_length, dtype='int64') * (1000 / frequency)\
          + convert_date_to_milliseconds(datestring)


def convert_date_to_milliseconds(datestring, date_format_string, datetime = None):
        if datetime == None:
            first_date = pytz.utc.localize(datetime.strptime(datestring, date_format_string))
            return (first_date - epoch_start).total_seconds() * 1000
        else:
            #pandas index will not take a long so I cannot multiply by 1000
            first_date = datetime
            return (first_date - epoch_start).total_seconds()
        
def convert_milliseconds_to_datetime(milliseconds, tzinfo):
        date = datetime.fromtimestamp(milliseconds / 1000)
        new_dt = tzinfo.localize(date)
        final_date = new_dt.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        return(final_date)
    
def get_time_duration(self, seconds_difference):

        days = int((((seconds_difference / 1000) / 60) / 60) / 24)
        hours =  int((((seconds_difference / 1000) / 60) / 60) % 24)
        minutes =  int(((seconds_difference / 1000) / 60)  % 60)
        seconds = (seconds_difference / 1000) % 60

        data_duration_time = "P%sDT%sH%sM%sS" % (days, hours, minutes, seconds)
        print(data_duration_time)