'''
Created on Jul 7, 2014

@author: Gregory
'''
import sys
import os
from cx_Freeze import setup, Executable

# def include_tz():
#     path_base = "C:\\Python34\\Lib\\site-packages\\pytz\\zoneinfo\\"
#     skip_count = len(path_base)
#     zip_includes = [(path_base, "pytz/zoneinfo/")]
#     for root, sub_folders, files in os.walk(path_base):
#         for file_in_root in files:
#             zip_includes.append(
#                                 ("{}".format(os.path.join(root, file_in_root)),
#                                  "{}",format(os.path.join("pytz/zoneinfo", root[skip_count:], file_in_root))
#                                  )
#                                 )
#     return zip_includes

options = {
    'pressure': {
        'compressed' : True,
#         'includes': [
#             'testfreeze_1',
#             'testfreeze_2'
#         ],
        'path': sys.path + ['modules'],
        'copy_dependent_files': True
    }
}

executables = [
    Executable('UltimateScript2.py', base = "Win32GUI")
]

setup(name='advanced_cx_Freeze_sample',
      version='0.1',
      description='Advanced sample cx_Freeze script',
      options=options,
      executables=executables
      )

