import sys
sys.path.append('..')
from datetime import datetime
import pytz
import pandas as pd
from pytz import timezone
import numpy as np

from Instruments.house import House
from Instruments.waveguage2 import Waveguage
import matplotlib.pyplot as plt

# def getdata(fname):
#     lt = House()
#     lt.creator_email = "a@aol.com"
#     lt.creator_name = "Jurgen Klinnsmen"
#     lt.creator_url = "www.test.com"
#     lt.in_filename = fname
#     lt.out_filename = './plotter-output.nc'
#     lt.is_baro = True
#     lt.pressure_units = "bar"
#     lt.z_units = "meters"
#     lt.longitude = np.float32(0.0)
#     lt.latitude = np.float(0.0)
#     lt.salinity_ppm = np.float32(0.0)
#     lt.z = np.float32(0.0)
#     lt.read()
#     return lt

        
# def compress(data, n=10):
#     """Averages every group of n points in the data"""
#     result = []
#     summed = 0
#     for i, e in enumerate(data):
#         summed += e
#         if i % n == n - 1:
#             result.append(summed / n)
#             summed = 0
#     return result

fname1 = (r'/home/chris/csv/neag1-07-15-2014.csv')
fname2 = (r'/home/chris/csv/neag2-07-15-2014.csv')
start = 1000
end = -1000

def compress_np(arr, c=10):
    final = np.zeros(math.floor(len(arr) / c))
    summed = 0
    for i, e in enumerate(arr):
        summed += np.float64(e)
        if i % c == c - 1:
            final[math.floor(i / c)] = summed / n
            summed = 0
    return final

def mean(data):
    return sum(data) / len(data)

# if 0:
#     compression = 51
#     lt1 = getdata(fname1)
#     lt2 = getdata(fname2)
#     p1 = compress(lt1.pressure_data[start:end], compression)
#     p1 = p1 - mean(p1)
#     p2 = compress(lt2.pressure_data[start:end], compression)
#     p2 = p2 - mean(p2)
#     t1 = compress(lt1.temperature_data[start:end], compression)
#     t1 = t1 - mean(t1)
#     t2 = compress(lt2.temperature_data[start:end], compression)
#     t2 = t2 - mean(t2)

def plot(data1, data2=None):
    plt.plot(data1)
    if not data2 == None:
        plt.plot(data2)
    plt.show()

fname3 = ('/home/chris/wave-sensor/netCDF_Instrument'
          '/Instruments/benchmark/wave-guage-14-07-2014.csv')


if 1:
    wg = Waveguage()
    wg.creator_email = "a@aol.com"
    wg.creator_name = "Jurgen Klinnsmen"
    wg.creator_url = "www.test.com"
    wg.in_filename = 'benchmark/wave-guage-14-07-2014.csv'
    wg.out_filename = 'wg-output.nc'
    wg.is_baro = True
    wg.pressure_units = "psi"
    wg.z_units = "meters"
    wg.longitude = np.float32(0.0)
    wg.latitude = np.float(0.0)
    wg.salinity_ppm = np.float32(0.0)
    wg.z = np.float32(0.0)
    wg.tzinfo = timezone('US/Eastern')

# data = pd.read_csv(fname3, skiprows=0, header=None,
#                    lineterminator=',', sep=',', engine='c',
#                    names='p')

# data.p = data.p.apply(lambda x: x.strip())

# def test(x):
#     return x.startswith('+') or x.startswith('-')
# c = data.p.map(test)
# data = data[c]

# def removetemp(x):
#     return len(x) == 7
# c = data.p.map(removetemp)
# pressure_data = data[c].p
# pressure_data = pressure_data.apply(lambda x: np.float64(x))

# def gettemp(x):
#     return len(x) == 5
# c = data.p.map(gettemp)
# temperature_data = data[c].p
# temperature_data = temperature_data.apply(lambda x: np.float64(x))
# print(pressure_data)
# print(temperature_data)

# def get_pressure(data):
#     def test1(x):
#         return  (x.startswith('+') or x.startswith('-'))

#     c = data.p.map(test1)
#     data = data[c]

#     def removetemp(x):
#         return len(x) == 7
#     c = data.p.map(removetemp)
#     pressure_data = data[c].p

#     pressure_data = pressure_data.apply(lambda x: np.float64(x))

#     pressure_data = compress(pressure_data, 100)
#     plot(pressure_data)

data = pd.read_csv(fname3, skiprows=0, header=None,
                   lineterminator=',', sep=',', engine='c',
                   names='p')

data.p = data.p.apply(lambda x: x.strip())



def ms_time_difference(t2, t1):
    return (t2 - t1).total_seconds() * 1000



def press_length(master_column):
    return len([p for p in master_column if len(p) == 7])

# get pressure data arrays for every hour

master = [[]]
i = 0
for e in data.p:
    if (e.startswith('+') or e.startswith('-')):
        if len(e) == 7:
            master[i].append(e)
    else:
        if master[i] != []:
            master.append([])
            i += 1
master.pop()
# find difference between timestamp

t = wg.get_times(data.p)
first_date = t[0]
last = master[-1] 
frequency_Hz = 10 # Hertz
stamp_ms = ms_time_difference(t[-1], first_date)
last_chunk_entries = len(master[-1])
last_chunk_ms = 1000 * last_chunk_entries / frequency_Hz
total_milliseconds = stamp_ms + last_chunk_seconds
utc_millisecond_data = np.arange(total_milliseconds, dtype='int64')
first_date = first_date
epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
offset = ms_time_difference(first_date, epoch_start)
utc_millisecond_data += offset

def hours(seconds):
    return seconds / (60 * 60)

final = np.zeros(0, dtype=np.float64) # 
prev_stamp = None
for stamp, press in zip(t, master):
    if prev_stamp:
        n = press_entries(stamp, prev_stamp, frequency_Hz) - press_length(press)
        narr = np.zeros(n, dtype=np.float64)
        final = np.hstack((final, prev_press, narr))
    prev_stamp = stamp
    prev_press = press

final = np.hstack((final, master[-1]))
