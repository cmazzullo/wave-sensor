# import mpl_toolkits.axes_grid1 as host_plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# import matplotlib
# matplotlib.use('TkAgg', warn=False)
# import matplotlib.pyplot as plt
# import mpl_toolkits.axisartist as AA
# from mpl_toolkits.axes_grid1.parasite_axes import SubplotHost
# 
# fig = plt.figure()
# 
# ax2 = host_plt.host_subplot('111',figure=fig)
# ax2.axes.get_yaxis().set_visible(False)
# ax2.axes.get_xaxis().set_visible(True)
# ax2.axis('off')
# xticks = ax2.get_xticks()
# 
# ax = ax2.twinx()
# ax.axis('on')
# ax.set_xticks(xticks)
# 
# ax2.plot([1,2,3,4],[1,1,1,1], color='r', alpha=0.5)
# ax.plot([1,2,3,4],[2,2,2,2], color='b', alpha=0.5)
# 
# 
# exc_type, exc_value, exc_traceback = sys.exc_info()
# 
#             message = repr(traceback.format_exception(exc_type, exc_value,
#                                           exc_traceback))
# import csv
# with open('test.csv', 'w') as csvfile:
#     writer = csv.writer(csvfile, delimiter=',')
#     
#     csv_header = ["Latitude: %.4f, Longitude: %.4f, STN_Instrument_Id: %s"]
#     writer.writerow(csv_header)

# [a for a in dir(obj) if not a.startswith('__') and not callable(getattr(obj,a))]

# import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.gridspec as gridspec
# #  
# df = pd.read_csv('wind_data.csv', header=None)
#       
#     #generate 6 minute utc millisecond data
#     #millisecond is a time stamp for Fri Jan 22 2016 23:00:00
#       
# wind_direction = df[6]
# wind_speed = df[8]
# import numpy as np
#  
# # grid_spec = gridspec.GridSpec(3,2,
# #                                width_ratios=[1,2],
# #                                height_ratios=[1,2,2]
# #                                )
#   
# figure = plt.figure()
# ax = figure.add_subplot('111')
# 
# U = np.
# V
# ax.plot(np.arange(0,len(wind_direction)),wind_speed)
# 
#   
# plt.show()
# u = [1,2,3,4]
# v = [3,4,5,6]
# import numpy as np
# import unit_conversion
# a = [(np.sqrt(x**2 + y**2)) * \
#                  unit_conversion.METERS_PER_SECOND_TO_MILES_PER_HOUR \
#                  for x, y in zip(u,v)]
# print()
# import numpy as np
# a = np.array([1,2,3,4], dtype=np.double)
# b = np.array([2,3,0,5], dtype=np.double)
# a[np.where(a > b)] = np.NaN
# print(a)    
# import numpy as np
# 
# print(np.sqrt([1,2,3,4]))