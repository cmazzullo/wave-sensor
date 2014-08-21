import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DayLocator, DateFormatter, MinuteLocator, AutoDateFormatter
import datetime
import numpy as np

import DepthCalculation.pressure_to_depth as p2d
import NetCDF_Utils.nc as nc

folder = 'C:\\Users\\cmazzullo\\wave-sensor-test-data\\test-ncs\\'
fname = folder + 'logger3.csv.nc'
naive_fname = folder + 'logger3_naive_depth.nc'
fft_fname = folder + 'logger3_fft_depth.nc'

p = nc.get_pressure(naive_fname) - nc.get_air_pressure(naive_fname)
naive_depth = nc.get_depth(naive_fname)
fft_depth = nc.get_depth(fft_fname)
s = nc.get_time(fname) / 1000

dates = list(map(datetime.datetime.fromtimestamp, s))

days = DayLocator()
hours = HourLocator()           # every year
minutes = MinuteLocator(interval=10)
daysFmt = AutoDateFormatter(days)
hoursFmt = DateFormatter('%H')

fig, ax = plt.subplots()
marker = ''
#ax.plot_date(dates, p, 'b' + marker)
ax.plot_date(dates, naive_depth, 'bx' + marker, label='Hydrostatic')
ax.plot_date(dates, fft_depth, 'r-' + marker, label='Linear wave theory')

# format the ticks
ax.xaxis.set_major_locator(days)
ax.xaxis.set_major_formatter(daysFmt)
ax.xaxis.set_minor_locator(hours)
ax.xaxis.set_minor_formatter(hoursFmt)
plt.ylabel('water height (m)')
plt.title('Water Height During a July 2014 Storm Surge')
plt.legend()
ax.autoscale_view()
ax.grid(True, which='both')

fig.autofmt_xdate()

xax = ax.get_xaxis()
xax.set_tick_params(which='major', pad=15)

plt.show()
