# import numpy as np
# from datetime import datetime
# import pytz
# 
# sven = ['14-May-2014 03:52:06.250', 
#         '14-May-2014 03:52:03.750', 
#         '14-May-2014 03:52:04.000']
# 
# 
# def convert_dateobject(datestring):
#     first_date = datetime.strptime(datestring, "%d-%B-%Y %H:%M:%S.%f")
#     return pytz.utc.localize(first_date)
# 
# 
# 
# 
# for x in sven:
#     offset = convert_dateobject(x) - datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
#     print(offset.total_seconds())
from datetime import datetime

first_date = datetime.strptime('20-Jun-2014 18:02:07.288', "%d-%b-%Y %H:%M:%S.%f")
print(first_date)   