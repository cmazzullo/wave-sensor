"""
Script 2 has 4 responsibilities:
  1. Copy data and metadata from the pressure NC file
  2. Insert additional metadata (???)
  3. Combine air pressure and water pressure NCs
  4. Append depth data to the final NC
"""

from nose.tools import *
from numpy import *
import numpy.testing as nptest
import os
from tools.script2 import make_depth_file
import NetCDF_Utils.nc as nc

DIRNAME = os.path.dirname(__file__)
WATER_BASENAME = 'script2test.nc'
IN_FILENAME = os.path.join(DIRNAME, 'test_data', WATER_BASENAME)
OUT_BASENAME = 'output.nc'
OUT_FILENAME = os.path.join(DIRNAME, 'test_data', OUT_BASENAME)
FILL_VALUE = -1e10

# cases:

def make_known_pressure(water_interval, air_interval):
    t0 = water_interval[0]
    p = zeros(water_interval[-1] - water_interval[0] + 1)
    w1 = 0
    w2 = water_interval[1] - t0
    a1 = air_interval[0] - t0
    a2 = air_interval[1] - t0
    if a1 > w1:
        p[:a1] = FILL_VALUE
    if a2 < w2:
        p[a2+1:] = FILL_VALUE
    return p


water_fname = os.path.join(DIRNAME, 'test_data', 'water.csv.nc')
water_interval = (1429528731, 1429528879)

# air inside
case1_fname = os.path.join(DIRNAME, 'test_data', 'air_case1.csv.nc')
case1_interval = (1429528751, 1429528869)

# air half in
case2_fname = os.path.join(DIRNAME, 'test_data', 'air_case2.csv.nc')
case2_interval = (1429528827, 1429528902)

# air out
case3_fname = os.path.join(DIRNAME, 'test_data', 'air_case3.csv.nc')
case3_interval = (1429528891, 1429528902)

fnames = [case1_fname, case2_fname, case3_fname]
intervals = [case1_interval, case2_interval, case3_interval]

# no air

def test_script2_no_air_file():
    make_depth_file(water_fname, '', OUT_FILENAME)
    known_p = nc.get_pressure(water_fname)
    p = nc.get_pressure(OUT_FILENAME)
    nptest.assert_equal(known_p, p)


def check_case(case_fname, case_interval):
    make_depth_file(water_fname, case_fname, OUT_FILENAME)
    known_depth = make_known_pressure(water_interval, case_interval)
    d = nc.get_depth(OUT_FILENAME)
    nptest.assert_equal(d, known_depth)


def test_script2_air_file_cases():
    for case_fname, case_interval in zip(fnames, intervals):
        check_case(case1_fname, case1_interval)


def test_make_depth_file():
    make_depth_file(IN_FILENAME, '', OUT_FILENAME)
    os.remove(OUT_FILENAME)
