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