"""Contains conversion factors between different units.

Example:
pressure_in_atm = 1.023 pressure_in_dbar = ATM_TO_DBAR * pressure_in_atm

Also contains functions to convert dates to UTC seconds and milliseconds.
"""

import numpy as np
import pytz
from datetime import datetime


def pressure_convert(x):
    '''Convert volts to pascals'''
    return ((x * (30 / 8184) - 6) + 14.7) / 1.45037738


PSI_TO_DBAR = 0.68947573
ATM_TO_DBAR = 10.1325
PASCAL_TO_DBAR = 0.0001
METER_TO_FEET = 3.28084

USGS_PROTOTYPE_V_TO_DBAR = lambda v: 2.5274e-3 * v + 5.998439
USGS_PROTOTYPE_V_TO_C = lambda v: 0.0114044 * v - 17.778

EPOCH_START = datetime(year=1970, month=1, day=1, tzinfo=pytz.utc)


def get_time_duration(ms_difference):
    days = int(ms_difference / 1000 / 60 / 60 / 24)
    hours =  int((ms_difference / 1000 / 60 / 60) % 24)
    minutes =  int((ms_difference / 1000 / 60)  % 60)
    seconds = (ms_difference / 1000) % 60
    data_duration_time = "P%sDT%sH%sM%sS" % (days, hours, minutes, seconds)
    return data_duration_time


def datestring_to_ms(datestring, datestring_fmt, tz = None):
    """Convert a string containing a formatted date to UTC milliseconds."""
    if tz == None:
        tz = "UTC"
    time_zone = pytz.timezone(str(tz))
    date = time_zone.localize(datetime.strptime(datestring, datestring_fmt))
    date = date.astimezone(pytz.UTC)
    return date_to_ms(date)


def date_to_ms(date):
    """Convert a datetime to UTC milliseconds."""
    return date_to_s(date) * 1000


def date_to_s(date):
    """Convert a datetime to UTC seconds."""
    return (date - EPOCH_START).total_seconds()


def generate_ms(start_ms, series_length, freq):
    timestep = 1000 / freq
    stop_ms = start_ms + series_length * timestep
    return np.arange(start_ms, stop_ms, timestep, dtype='int64')


def convert_ms_to_datestring(ms, tzinfo, script = None):
        '''Used when you want a date time string'''
        date = datetime.fromtimestamp(ms / 1000, tzinfo)
        
        if script == None:
            final_date = date.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            final_date = date.strftime('%m/%d/%y %H:%M')
        return final_date
    

