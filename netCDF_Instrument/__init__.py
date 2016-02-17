# import re
# 
# line = '# Date Time, GMT-05:00 Abs Pres, psi (LGR S/N: 2238127, SEN S/N: 2238127, LBL: Barometer) \
# Temp, F (LGR S/N: 2238127, SEN S/N: 2238127, LBL: Temp) Stopped (LGR S/N: 2238127)'
# 
# if re.search('[0-9]{6}', line):
#     match = re.search('[0-9]{6}', line)
#     print(match.group(0))
# else:
#     print('no mas')

import matplotlib.pyplot as plt
import numpy as np
import datetime as dtime
from matplotlib.dates import date2num

""" fake dates starting now """
x = np.arange(0, 20, 5)
start = dtime.datetime.now()
dates = [start + dtime.timedelta(days=n) for n in range(len(x))]
""" dummy u, v """
U = np.sin(x * np.pi / 180)
V = np.cos(x * np.pi / 180)
print(x)
print(U)
print(V)
print([[0]*len(x)])
print(np.arange(1,5))
fig, ax = plt.subplots(1, 1, figsize=(16,6))
print(len(dates), len([[0]*len(x)]))
ax.plot(date2num(dates),[0]*len(x))
qiv = ax.quiver(date2num(dates), [[0]*len(x)], [[0]*len(x)], [[1]*len(x)], headlength=0, 
headwidth=0, headaxislength=0,  scale=3 , alpha=.5, width=0.001, units='width')
# key = ax.quiverkey(qiv, 0.25, 0.75, 0.5, "0.5 N m$^{-2}$", labelpos='N', 
# coordinates='axes' )
plt.setp( ax.get_yticklabels(), visible=False)
plt.gca().xaxis_date()
plt.show()

