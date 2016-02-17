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
# 
# print(np.arange(30,30.05,.1))