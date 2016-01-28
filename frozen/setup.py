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
sys.path.append('C:\\Users\\chogg\\Documents\\GitHub\\wave-sensor\\netCDF_Instrument')


include_files = [
                 ('C:\\Python34\\Lib\\site-packages\\scipy\\special\\_ufuncs.pyd','_ufuncs.pyd'),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\libifcoremd.dll','libifcoremd.dll'),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\libmmd.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\libifportmd.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\libimalloc.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\libiomp5md.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\libiompstubs5md.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_avx.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_avx2.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_avx512.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_core.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_intel_thread.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_p4m.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_p4m3.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_sequential.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_tbb_thread.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_vml_avx.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_vml_avx2.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_vml_avx512.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_vml_cmpt.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_vml_ia.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_vml_p4.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_vml_p4m.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_vml_p4m2.dll',''),
                 ('C:\\Python34\\Lib\\site-packages\\numpy\\core\\mkl_vml_p4m3.dll','')
                
                 ]
build_exe_options = {
                    'path': sys.path, 
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

