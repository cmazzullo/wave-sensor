"""
Freezing script for tools in this package.

To build into an executable:
python3 setup.py build

To create binary distribution:
python3 setup.py bdist

To create an executable installer for MS Windows:
python3 setup.py bdist_wininst
"""

from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('netCDF_Instrument/tools/script1_gui.py', base=base)
]

setup(name='compare_methods',
      version = '1.0',
      description = 'Compare different ways of calculating water depth.',
      options = dict(build_exe = buildOptions),
      executables = executables)
