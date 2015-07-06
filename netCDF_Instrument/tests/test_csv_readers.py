"""
Tests CSV readers for all supported instruments:
HOBO
USGS Prototype
TrueBlu
LevelTROLL

TODO - RBRSolo support
"""

import numpy.testing as nptest
from csv_readers import Leveltroll, MeasureSysLogger, House, Hobo, RBRSolo
import numpy as np
from unit_conversion import PSI_TO_DBAR
import os.path

TOLERANCE = 1e-3 # we can only expect 3 digits of precision

# this is pulled directly from the CSVs, and is in PSI
KNOWN_PRESSURE = np.array([
    14.735, 14.735, 14.732, 14.731, 14.729, 14.731, 14.730, 14.723, 14.726,
    14.723, 14.723, 14.721, 14.725, 14.726, 14.725, 14.726, 14.726, 14.731,
    14.735, 14.734, 14.740, 14.737, 14.742, 14.742, 14.740, 14.744, 14.748,
    14.749, 14.748, 14.746, 14.748, 14.747, 14.743, 14.742, 14.743, 14.743,
    14.743, 14.740, 14.739, 14.735, 14.734, 14.733, 14.734, 14.730, 14.730,
    14.726, 14.727, 14.724, 14.721, 14.725, 14.727, 14.727, 14.728, 14.729,
    14.730, 14.729, 14.731, 14.730, 14.738, 14.739, 14.741, 14.745, 14.744,
    14.745, 14.745, 14.745, 14.751, 14.751, 14.752, 14.754, 14.753, 14.753,
    14.754, 14.755, 14.754, 14.751, 14.752, 14.750, 14.750, 14.749, 14.749,
    14.748, 14.748, 14.743, 14.744, 14.739, 14.737, 14.735, 14.734, 14.731,
    14.727, 14.726, 14.722, 14.721, 14.716, 14.713, 14.713, 14.708, 14.707,
    14.704, 14.700, 14.700, 14.698, 14.700, 14.696, 14.694, 14.695, 14.695,
    14.697, 14.697, 14.698, 14.699, 14.700, 14.704, 14.707, 14.710, 14.714,
    14.715, 14.714, 14.716, 14.717, 14.718, 14.719, 14.724, 14.722, 14.722,
    14.723, 14.722, 14.723, 14.721, 14.726, 14.724, 14.721, 14.722, 14.719,
    14.719, 14.716, 14.712, 14.713, 14.711, 14.710, 14.709, 14.707, 14.709,
    14.709, 14.706, 14.708, 14.710, 14.712, 14.713, 14.714, 14.716, 14.717,
    14.717, 14.719, 14.719, 14.721, 14.725, 14.725, 14.726, 14.728, 14.728,
    14.729, 14.729, 14.730, 14.732, 14.730, 14.731, 14.729, 14.730, 14.731,
    14.729 ])


def get_csv_fname(base):
    DIRNAME = os.path.dirname(__file__)
    CSV_DIRNAME = 'test_data'
    return os.path.join(DIRNAME, CSV_DIRNAME, base)


def verify_csv_reader(instrument, base, scale=1):
    instrument.in_filename = get_csv_fname(base)
    instrument.read()
    in_pressure = instrument.pressure_data
    nptest.assert_allclose(KNOWN_PRESSURE, scale*in_pressure, rtol=TOLERANCE)


def test_leveltroll_reader():
    verify_csv_reader(Leveltroll(), 'leveltroll.csv', scale=1/PSI_TO_DBAR)


def test_hobo_reader():
    verify_csv_reader(Hobo(), 'hobo.csv', scale=1/PSI_TO_DBAR)


def test_house_reader():
    verify_csv_reader(House(), 'house.csv')


def test_trueblu_reader():
    verify_csv_reader(MeasureSysLogger(), 'trueblu.csv', scale=1/PSI_TO_DBAR)
