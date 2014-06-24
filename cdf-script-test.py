from matplotlib import pyplot as plt
import pandas as pd
import netCDF4

nc = netCDF4.Dataset(url)
h = nc.variables[vname]
times = nc.variables['time']
jd = netCDF4.num2date(times[:],times.units)
hs = pd.Series(h[:,station],index=jd)

fig = plt.figure(figsize=(12,4))
ax = fig.add_subplot(111)
hs.plot(ax=ax,title='%s at %s' % (h.long_name,nc.id))
ax.set_ylabel(h.units)
