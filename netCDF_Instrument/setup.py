"""Build this script in the cmd in order to freeze the Frozen Binary Script.  Note:  pytz timezone files need
to be extracted manually for some reason, otherwise the executable will not run"""

import sys
import traceback
from cx_Freeze import setup, Executable

# options = {
#         'include_files': [("C:/Anaconda/Lib/site-packages/mpl_toolkits","mpl_toolkits")],
# #         'compressed' : True,
#         'path': sys.path + ['modules'],
# #         'copy_dependent_files': True
#      
# }


include_files = [
                 ('C:\\Python34\\Lib\\site-packages\\scipy\\special\\_ufuncs.pyd','_ufuncs.pyd'),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\libifcoremd.dll','libifcoremd.dll'),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\libmmd.dll','')
                 ]
build_exe_options = {
#                     'path': sys.path + ['modules'], 
                    'packages': ["tkinter", "matplotlib"],
                    'include_files':include_files,
#                     'copy_dependent_files': True
                     }

executables = [
                 Executable('FrozenMaster.py', base = "Win32GUI"),
#                Executable('FrozenAverager.py', base = "Win32GUI"),
#                Executable('FrozenBinaryScript1_Air.py', base = "Win32GUI"),
#                Executable('FrozenBinaryScript1_Sea.py', base = "Win32GUI"),
#                Executable('FrozenBinaryScript2.py', base = "Win32GUI"),
#                Executable('FrozenChopper.py', base = "Win32GUI"),
#                Executable('FrozenDepthGraph.py', base = "Win32GUI")
]




setup(name='advanced_cx_Freeze_sample',
      version='0.1',
      description='Advanced sample cx_Freeze script',
      executables=executables,
      options={"build_exe": build_exe_options},
      )

