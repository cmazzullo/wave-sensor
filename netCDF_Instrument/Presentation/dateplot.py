# A few programs to display datetime data along with the time series
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DayLocator, DateFormatter, MinuteLocator, AutoDateFormatter
import datetime
import numpy as np
import os
import DepthCalculation.pressure_to_depth as p2d
import NetCDF_Utils.nc as nc

folder = '..\\Presentation\\DepthPlot\\'
fname = folder + 'logger3.csv.nc'
naive_fname = folder + 'naive.nc'
fft_fname = folder + 'fft.nc'

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


# import datetime
# import random
# import matplotlib.pyplot as plt
# import matplotlib.dates as dates

# # make up some data
# x = [datetime.datetime.now() + datetime.timedelta(hours=i) for i in range(100)]
# y = [i+random.gauss(0,1) for i,_ in enumerate(x)]

# # plot
# plt.plot(x,y)
# # beautify the x-labels
# plt.gcf().autofmt_xdate()

# ax = plt.gca()
# # set date ticks to something sensible:
# xax = ax.get_xaxis()
# xax.set_major_locator(dates.DayLocator())
# xax.set_major_formatter(dates.DateFormatter('%d/%b'))

# xax.set_minor_locator(dates.HourLocator(byhour=range(0,24,3)))
# xax.set_minor_formatter(dates.DateFormatter('%H'))
# xax.set_tick_params(which='major', pad=15)

# plt.show()



# import matplotlib.pyplot as plt
# from matplotlib import dates
# from datetime import datetime
# import numpy as np

# import DepthCalculation.pressure_to_depth as p2d
# import NetCDF_Utils.nc as nc

# fname = ('C:\\Users\\cmazzullo\\wave-sensor-test-data\\'
#          'test-ncs\\logger1.csv.nc')
# p = nc.get_pressure(fname)
# t = nc.get_time(fname)
# z = -2
# H = 20 * np.ones_like(t)
# timestep = .25
# dfft = p2d.fft_method(t, p, z, H, timestep, gate=.3, window=True)
# d = p2d.method2(p)
# d[d < 8] = np.nan
# d[d > 13] = np.nan
# n = p2d.hydrostatic_method(p)
# s = t[:1000] / 1000
# dts = map(datetime.fromtimestamp, s)
# fds = dates.date2num(dts)
# hfmt = dates.DateFormatter('%m/%d %H:%M')


# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.plot(fds, p[:1000])

# ax.xaxis.set_major_locator(dates.MinuteLocator())
# ax.xaxis.set_major_formatter(hfmt)
# ax.set_ylim(bottom = 0)
# plt.xticks(rotation='vertical')
# plt.subplots_adjust(bottom=.3)
# plt.show()
