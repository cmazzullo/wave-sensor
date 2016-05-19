# import pytz
# from datetime import datetime
#  
# data_string ='11111111 1111'
#  
# timezone = pytz.timezone('US/Eastern')
# timezone2 = pytz.timezone('GMT')
#  
# fmt_1 = '%Y%m%d %H%M'
# fmt_2 = '%Y%m%d %H:%M'
#  
#  
# # try:
# time = timezone.localize(datetime.strptime(data_string, fmt_1))
# time2 = timezone2.localize(time)
# print(time)
# except:
#     time = timezone.localize(datetime.strptime(data_string, fmt_2))
#     
# print(time)

# import re
# 
# match = re.fullmatch('^[0-9]{8}\s[0-9]{4}$', '11111111 1111') == None
# print(match)
# import re
# 
# s = "-----Transducer Serial Number 1407506"
# a = re.search("[0-9]{7}", s)
# 
# print(a.group(0))
# a = int('4')
# print(a)
# 
# import numpy as np
# # 
# # print(np.arange(30,30.05,.1))
# a = np.array([8,2,3,4])
# b = np.array([4,5,6,7])
# 
# b_mask = (b < 7).astype(float)
# c = a * b_mask
# print(c)
# import netCDF_Utils.nc as nc
# import unit_conversion as uc
# 
# files = \
# [
# 'C:\\Users\\chogg\\Desktop\\Deleware\\DEKEN11508 BHN1.csv.nc',
# 'C:\\Users\\chogg\\Desktop\\Deleware\\DEKEN11509 BHN2.csv.nc',
# 'C:\\Users\\chogg\\Desktop\\Deleware\\DEKEN11528 BHN3.csv.nc',
# 'C:\\Users\\chogg\\Desktop\\Deleware\\DEKEN11529 BHN4.csv.nc',
# 'C:\\Users\\chogg\\Desktop\\Deleware\\DEKEN11568 BHS2.csv.nc',
# ]
# 
# for x in files:
#     print(x, float(nc.get_global_attribute(x, 'sensor_orifice_elevation_at_deployment_time')) * uc.METER_TO_FEET)
#     print(x, float(nc.get_global_attribute(x, 'sensor_orifice_elevation_at_retrieval_time')) * uc.METER_TO_FEET)
