"""Build this script in the cmd in order to freeze the Frozen Binary Script.  Note:  pytz timezone files need
to be extracted manually for some reason, otherwise the executable will not run"""

import sys
from cx_Freeze import setup, Executable


options = {
    'pressure': {
        'compressed' : True,
        'path': sys.path + ['modules'],
        'copy_dependent_files': True
    }
}

executables = [
    Executable('ForzenBinaryScript.py', base = "Win32GUI")
]

setup(name='advanced_cx_Freeze_sample',
      version='0.1',
      description='Advanced sample cx_Freeze script',
      options=options,
      executables=executables
      )

