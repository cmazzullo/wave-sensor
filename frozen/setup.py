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
sys.path.append('C:\\Users\\Gregory\\Documents\\GitHub\\wave-sensor\\netCDF_Instrument')
build_exe_options = {"path": sys.path}

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

