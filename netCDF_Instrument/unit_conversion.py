"""Contains conversion factors between different units.

Example:
pressure_in_atm = 1.023 pressure_in_dbar = ATM_TO_DBAR * pressure_in_atm

Also contains functions to convert dates to UTC seconds and milliseconds.
"""

import numpy as np
import pytz
from datetime import datetime
from datetime import timedelta


def pressure_convert(x):
    '''Convert volts to pascals'''
    return ((x * (30 / 8184) - 6) + 14.7) / 1.45037738


PSI_TO_DBAR = 0.68947573
ATM_TO_DBAR = 10.1325
PASCAL_TO_DBAR = 0.0001
METER_TO_FEET = 3.28084
DBAR_TO_INCHES_OF_MERCURY = 2.9529983071415975
DBAR_TO_MM_OF_MERCURY = 75.0061561303
METERS_PER_SECOND_TO_MILES_PER_HOUR = 2.236936292054

USGS_PROTOTYPE_V_TO_DBAR = lambda v: 2.5274e-3 * v + 5.998439
USGS_PROTOTYPE_V_TO_C = lambda v: 0.0114044 * v - 17.778

EPOCH_START = datetime(year=1970, month=1, day=1, tzinfo=pytz.utc)

FILL_VALUE = -1e10

GRAVITY = 9.8  # (m / s**2)
GRAVITY_FEET = 32.1740 #(f / s**2)
SALT_WATER_DENSITY = 1027  # density of seawater (kg / m**3)
FRESH_WATER_DENSITY = 1000
BRACKISH_WATER_DENSITY = 1015

FILL_VALUE = -1e10


def get_time_duration(ms_difference):
    days = int(ms_difference / 1000 / 60 / 60 / 24)
    hours =  int((ms_difference / 1000 / 60 / 60) % 24)
    minutes =  int((ms_difference / 1000 / 60)  % 60)
    seconds = (ms_difference / 1000) % 60
    data_duration_time = "P%sDT%sH%sM%sS" % (days, hours, minutes, seconds)
    return data_duration_time


def datestring_to_ms(datestring, datestring_fmt, tz = None, dst = None):
    """Convert a string containing a formatted date to UTC milliseconds."""
    if tz == None:
        tz = "GMT"
    time_zone = pytz.timezone("GMT")
    dt = datetime.strptime(datestring, datestring_fmt)
    dt = adjust_to_gmt(dt, tz, dst)
    date = time_zone.localize(dt)
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
        elif script == 'csv':
            final_date = date.strftime('%m/%d/%y %H:%M:%S')
        else:
            final_date = date.strftime('%m/%d/%y %H:%M')
        return final_date
    
def convert_ms_to_date(ms, tzinfo, script = None):
        '''Used when you want a date time string'''
        return datetime.fromtimestamp(ms / 1000, tzinfo)
    
def adjust_to_gmt(datetime, tzinfo, dst):
    if tzinfo == 'US/Eastern':
        delta = timedelta(seconds = 18000)
        datetime = datetime + delta
    elif tzinfo == "US/Central":
        delta = timedelta(seconds = 21600)
        datetime = datetime + delta
    elif tzinfo == "US/Mountain":
        delta = timedelta(seconds = 25200)
        datetime = datetime + delta
    elif tzinfo == "US/Pacific":
        delta = timedelta(seconds = 28800)
        datetime = datetime + delta
    elif tzinfo == "US/Aleutian" or tzinfo == "US/Hawaii":
        delta = timedelta(seconds = 36000)
        datetime = datetime + delta
        
    if dst:
        delta = timedelta(seconds=3600)
        datetime = datetime - delta
        
    return datetime
    
def adjust_from_gmt(datetimes, tzinfo, dst):
    if tzinfo == 'US/Eastern':
        delta = timedelta(seconds = 18000)
        datetimes = [x - delta for x in datetimes]
    elif tzinfo == "US/Central":
        delta = timedelta(seconds = 21600)
        datetimes = [x - delta for x in datetimes]
    elif tzinfo == "US/Mountain":
        delta = timedelta(seconds = 25200)
        datetimes = [x - delta for x in datetimes]
    elif tzinfo == "US/Pacific":
        delta = timedelta(seconds = 28800)
        datetimes = [x - delta for x in datetimes]
    elif tzinfo == "US/Aleutian" or tzinfo == "US/Hawaii":
        delta = timedelta(seconds = 36000)
        datetimes = [x - delta for x in datetimes]
        
    if dst:
        delta = timedelta(seconds=3600)
        datetimes = [x + delta for x in datetimes]
        
    return datetimes

def adjust_by_hours(datetimes, hours):
    
    delta = timedelta(hours=hours)
    datetimes = [x - delta for x in datetimes]
    time_zone = pytz.timezone("GMT") 
    datetimes = [time_zone.localize(x) for x in datetimes]
    return datetimes

def make_timezone_aware(datetime, tz, daylight_savings):
    
    time_zone = pytz.timezone(tz)
    datetime = time_zone.localize(datetime, is_dst=daylight_savings)
    
    if daylight_savings == True:
        delta = timedelta(hours=1)
        datetime = datetime - delta
   
    return datetime
    

