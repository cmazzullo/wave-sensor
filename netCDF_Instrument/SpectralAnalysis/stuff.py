import datetime
import random
import matplotlib.pyplot as plt
import matplotlib.dates as dates

# make up some data
x = [datetime.datetime.now() + datetime.timedelta(hours=i) for i in range(100)]
y = [i+random.gauss(0,1) for i,_ in enumerate(x)]

# plot
plt.plot(x,y)
# beautify the x-labels
plt.gcf().autofmt_xdate()

ax = plt.gca()
# set date ticks to something sensible:
xax = ax.get_xaxis()
xax.set_major_locator(dates.DayLocator())
xax.set_major_formatter(dates.DateFormatter('%d/%b'))

xax.set_minor_locator(dates.HourLocator(byhour=range(0,24,3)))
xax.set_minor_formatter(dates.DateFormatter('%H'))
xax.set_tick_params(which='major', pad=15)

plt.show()
