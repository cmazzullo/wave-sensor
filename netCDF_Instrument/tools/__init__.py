# # import mpl_toolkits.axes_grid1 as host_plt
# # from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# # import matplotlib
# # matplotlib.use('TkAgg', warn=False)
# # import matplotlib.pyplot as plt
# # import mpl_toolkits.axisartist as AA
# # from mpl_toolkits.axes_grid1.parasite_axes import SubplotHost
# # 
# # fig = plt.figure()
# # 
# # ax2 = host_plt.host_subplot('111',figure=fig)
# # ax2.axes.get_yaxis().set_visible(False)
# # ax2.axes.get_xaxis().set_visible(True)
# # ax2.axis('off')
# # xticks = ax2.get_xticks()
# # 
# # ax = ax2.twinx()
# # ax.axis('on')
# # ax.set_xticks(xticks)
# # 
# # ax2.plot([1,2,3,4],[1,1,1,1], color='r', alpha=0.5)
# # ax.plot([1,2,3,4],[2,2,2,2], color='b', alpha=0.5)
# # 
# # 


# # exc_type, exc_value, exc_traceback = sys.exc_info()
# # 
# #             message = repr(traceback.format_exception(exc_type, exc_value,
# #                                           exc_traceback))
# # import csv
# # with open('test.csv', 'w') as csvfile:
# #     writer = csv.writer(csvfile, delimiter=',')
# #     
# #     csv_header = ["Latitude: %.4f, Longitude: %.4f, STN_Instrument_Id: %s"]
# #     writer.writerow(csv_header)
# 
# # [a for a in dir(obj) if not a.startswith('__') and not callable(getattr(obj,a))]
# 
# # import pandas as pd
# # import matplotlib.pyplot as plt
# # import matplotlib.gridspec as gridspec
# # #  
# # df = pd.read_csv('wind_data.csv', header=None)
# #       
# #     #generate 6 minute utc millisecond data
# #     #millisecond is a time stamp for Fri Jan 22 2016 23:00:00
# #       
# # wind_direction = df[6]
# # wind_speed = df[8]
# # import numpy as np
# #  
# # # grid_spec = gridspec.GridSpec(3,2,
# # #                                width_ratios=[1,2],
# # #                                height_ratios=[1,2,2]
# # #                                )
# #   
# # figure = plt.figure()
# # ax = figure.add_subplot('111')
# # 
# # U = np.
# # V
# # ax.plot(np.arange(0,len(wind_direction)),wind_speed)
# # 
# #   
# # plt.show()
# # u = [1,2,3,4]
# # v = [3,4,5,6]
# # import numpy as np
# # import unit_conversion
# # a = [(np.sqrt(x**2 + y**2)) * \
# #                  unit_conversion.METERS_PER_SECOND_TO_MILES_PER_HOUR \
# #                  for x, y in zip(u,v)]
# # print()
# # import numpy as np
# # a = np.array([1,2,3,4], dtype=np.double)
# # b = np.array([2,3,0,5], dtype=np.double)
# # a[np.where(a > b)] = np.NaN
# # print(a)    
# # import numpy as np
# # 
# # print(np.sqrt([1,2,3,4]))
# 
# from tools.storm_options import StormOptions
# import netCDF4
# from stats import Stats
# 
# so = StormOptions()
# st = Stats()
# 
# so.sea_fname = 'C:\\Users\\chogg\\Desktop\\Wave Lab\\NY NC Data\\new_suf.nc'
# so.air_fname = 'C:\\Users\\chogg\\Desktop\\Wave Lab\\NY NC Data\\5_NYSUF04781_1411333_bp_chop.csv.nc'
# 
# so.get_corrected_pressure()
# so.get_meta_data()
# 
# so.get_wave_water_level()
# so.get_wave_statistics()
# 
# 
# 
# # ds = netCDF4.Dataset('wave_test.nc', 'w', format="NETCDF4_CLASSIC")
# # ds.createDimension('time',len(so.sea_time))
# # time_var = ds.createVariable('time','f8',('time'))
# # time_var.__setattr__('units', 'time in milliseconds after 1-1-1970 UTC(4hz data)')
# # time_var.__setattr__('timezone', 'UTC')
# # time_var[:] = so.sea_time
# # corrected_pressure_var = ds.createVariable('corrected_pressure','f8',('time'))
# # corrected_pressure_var.__setattr__('units', 'dbar (corrected by local air pressure instrument)')
# # corrected_pressure_var[:] = so.corrected_sea_pressure
# # ds.setncattr('initial land surface elevation', so.land_surface_elevation[0])
# # ds.setncattr('final land surface elevation', so.land_surface_elevation[-1])
# # ds.setncattr('initial sensor orifice elevation', so.sensor_orifice_elevation[0])
# # ds.setncattr('final sensor orifice elevation', so.sensor_orifice_elevation[-1])
# # ds.setncattr('elevation units', 'meters')
# # ds.setncattr('datum', so.datum)
# # 
# # ds.close()

# import requests
# import json
# 
# r = requests.get('https://stn.wim.usgs.gov/STNServices/Instruments/FilteredInstruments.json?Event=119&EventType=&EventStatus=0&States=&County=&SensorType=&CurrentStatus=&CollectionCondition=&DeploymentType=')
# jdata = json.loads(r.text)
# 
# for x in jdata:
#     if x['site_id'] == 'VAFAI04283':
#         print(x['sensorBrand'], x['latitude'], ' ', x['longitude'], '' , x['site_id'], ' ' , x['site_no'], ' ', x['instrument_id'])
# import numpy as np
# # 
# v = np.array([1,2,3])
# # query = np.where(v < 3)
# if type(v) is float:
#     pass
# else:
#     print(len(np.where(np.isnan(v))[0]))
# #     if np.isnan(v.all()):
# #         print('yuuuup')
# from netCDF_Utils import nc
# import numpy as np
# 
# print(np.mean(nc.get_pressure('VAACC17426 Chincoteague3.csv.nc')) - np.mean(nc.get_air_pressure('Chincoteague Baro.csv.nc')))
# print(np.mean(nc.get_pressure('VAACC17425 Chincoteague1.csv.nc'))  - np.mean(nc.get_air_pressure('Chincoteague Baro.csv.nc')))
# print(np.mean(nc.get_pressure('VAACC17427 Chincoteague2.csv.nc')) - np.mean(nc.get_air_pressure('Chincoteague Baro.csv.nc')))
# print(np.mean(nc.get_pressure('MDWOR04571.1 Assateague.csv.nc')) - np.mean(nc.get_air_pressure('Assateague Baro.csv.nc')))
# print(np.mean(nc.get_pressure('MDWOR045861 Assateague.csv.nc')) - np.mean(nc.get_air_pressure('Assateague Baro.csv.nc')))
