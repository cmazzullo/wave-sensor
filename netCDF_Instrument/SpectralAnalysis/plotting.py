import matplotlib.pyplot as plt
from matplotlib import dates
from datetime import datetime
import numpy as np

import DepthCalculation.pressure_to_depth as p2d
import NetCDF_Utils.nc as nc

fname = ('C:\\Users\\cmazzullo\\wave-sensor-test-data\\'
         'test-ncs\\logger1.csv.nc')
p = nc.get_pressure(fname)
t = nc.get_time(fname)
z = -2
H = 20 * np.ones_like(t)
timestep = .25
dfft = p2d.fft_method(t, p, z, H, timestep, gate=.3, window=True)
d = p2d.method2(p)
d[d < 8] = np.nan
d[d > 13] = np.nan
n = p2d.hydrostatic_method(p)
s = t[:1000] / 1000
dts = map(datetime.fromtimestamp, s)
fds = dates.date2num(dts)
hfmt = dates.DateFormatter('%m/%d %H:%M')


fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(fds, p[:1000])

ax.xaxis.set_major_locator(dates.MinuteLocator())
ax.xaxis.set_major_formatter(hfmt)
ax.set_ylim(bottom = 0)
plt.xticks(rotation='vertical')
plt.subplots_adjust(bottom=.3)
plt.show()
