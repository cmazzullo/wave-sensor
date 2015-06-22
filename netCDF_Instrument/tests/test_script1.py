"""Tests that netCDFs created by script1 contain the right data and metadata.

Uses some made up data files in the tests directory.

The user will need to make a fresh netCDF file using the GUI to make
sure that it's working. To do this, run the GUI on the file
leveltroll_test.csv in the test_data directory, and manually enter the
values in INPUTS into the fields of the GUI.

Coverage:
Metadata in the netCDF produced by script1 (variables and attributes)
Pressure data in the netCDF

"""

import unittest
from netCDF4 import Dataset
from os.path import join
from tools import script1
import os

IN_FILENAME = join('.', 'test_data', 'leveltroll_test.csv')
OUT_FILENAME = join('.', 'test_data', 'leveltroll_test.nc')
GUI_FILENAME = join('.', 'test_data', 'gui_leveltroll_test.nc')

INPUTS = {
    'instrument_name' : 'LevelTroll',
    'in_filename' : IN_FILENAME,
    'out_filename' : OUT_FILENAME,
    'latitude' : '20.0',
    'longitude' : '30.0',
    'salinity' : 'Brackish',
    'initial_water_depth' : '11.5',
    'final_water_depth' : '10.0',
    'device_depth' : '9.5',
    'deployment_time' : '20140101 0000',
    'retrieval_time' : '20140102 0000',
    'tzinfo' : 'US/Central',
    'sea_name' : 'Great Lakes',
    'creator_name' : 'Chris Mazzullo',
    'creator_email' : 'stuff@gmail.com',
    'creator_url' : 'zombo.com',
    'sea_pressure' : True }


class KnownValues(unittest.TestCase):

    def setUp(self):
        print("Remember to make a fresh file with the GUI if you want "
              "GUI functionality to be tested!")
        script1.convert_to_netcdf(INPUTS)

    def tearDown(self):
        if os.path.exists(OUT_FILENAME):
            os.remove(OUT_FILENAME)

    known_numerical_netcdf_attributes = [
        'initial_water_depth',
        'final_water_depth',
        'device_depth']

    known_string_netcdf_attributes = [
        'deployment_time',
        'retrieval_time',
        'sea_name',
        'creator_name',
        'creator_email',
        'creator_url',
        'salinity' ]

    known_numerical_netcdf_variables = [
        'longitude',
        'latitude' ]

    # this is pulled directly from the CSV
    known_pressure_series = [ 14.735, 14.735, 14.732, 14.731, 14.729,
                              14.731, 14.730, 14.723, 14.726, 14.723,
                              14.723, 14.721, 14.725, 14.726, 14.725,
                              14.726, 14.726, 14.731, 14.735, 14.734,
                              14.740, 14.737, 14.742, 14.742, 14.740,
                              14.744, 14.748, 14.749, 14.748, 14.746,
                              14.748, 14.747, 14.743, 14.742, 14.743,
                              14.743, 14.743, 14.740, 14.739, 14.735,
                              14.734, 14.733, 14.734, 14.730, 14.730,
                              14.726, 14.727, 14.724, 14.721, 14.725,
                              14.727, 14.727, 14.728, 14.729, 14.730,
                              14.729, 14.731, 14.730, 14.738, 14.739,
                              14.741, 14.745, 14.744, 14.745, 14.745,
                              14.745, 14.751, 14.751, 14.752, 14.754,
                              14.753, 14.753, 14.754, 14.755, 14.754,
                              14.751, 14.752, 14.750, 14.750, 14.749,
                              14.749, 14.748, 14.748, 14.743, 14.744,
                              14.739, 14.737, 14.735, 14.734, 14.731,
                              14.727, 14.726, 14.722, 14.721, 14.716,
                              14.713, 14.713, 14.708, 14.707, 14.704,
                              14.700, 14.700, 14.698, 14.700, 14.696,
                              14.694, 14.695, 14.695, 14.697, 14.697,
                              14.698, 14.699, 14.700, 14.704, 14.707,
                              14.710, 14.714, 14.715, 14.714, 14.716,
                              14.717, 14.718, 14.719, 14.724, 14.722,
                              14.722, 14.723, 14.722, 14.723, 14.721,
                              14.726, 14.724, 14.721, 14.722, 14.719,
                              14.719, 14.716, 14.712, 14.713, 14.711,
                              14.710, 14.709, 14.707, 14.709, 14.709,
                              14.706, 14.708, 14.710, 14.712, 14.713,
                              14.714, 14.716, 14.717, 14.717, 14.719,
                              14.719, 14.721, 14.725, 14.725, 14.726,
                              14.728, 14.728, 14.729, 14.729, 14.730,
                              14.732, 14.730, 14.731, 14.729, 14.730,
                              14.731, 14.729 ]

    def test_known_numerical_netcdf_attributes(self):
        with Dataset(OUT_FILENAME, 'r', format='NETCDF4_CLASSIC') as ds:
            for key in self.known_numerical_netcdf_attributes:
                known_value = INPUTS[key]
                result = getattr(ds, key)
                self.assertEqual(float(known_value), float(result))

    def test_known_string_netcdf_attributes(self):
        with Dataset(OUT_FILENAME, 'r', format='NETCDF4_CLASSIC') as ds:
            for key in self.known_string_netcdf_attributes:
                known_value = INPUTS[key]
                result = getattr(ds, key)
                self.assertEqual(str(known_value), str(result))

    def test_known_numerical_netcdf_variables(self):
        with Dataset(OUT_FILENAME, 'r', format='NETCDF4_CLASSIC') as ds:
            for key in self.known_numerical_netcdf_variables:
                known_value = INPUTS[key]
                result = ds.variables[key].getValue()
                self.assertEqual(str(known_value), str(result))

    def test_netcdf_known_variables(self):
        with Dataset(OUT_FILENAME, 'r', format='NETCDF4_CLASSIC') as ds:
            result_pressure_series = ds.variables['sea_water_pressure'][:]
            for known_p, result_p in zip(self.known_pressure_series,
                                         result_pressure_series):
                known_p = 0.6894757 * known_p
                self.assertEqual(round(known_p, 4), round(result_p, 4))

    # def test_gui_known_numerical_netcdf_attributes(self):
    #     with Dataset(GUI_FILENAME, 'r', format='NETCDF4_CLASSIC') as ds:
    #         for key in self.known_numerical_netcdf_attributes:
    #             known_value = INPUTS[key]
    #             result = getattr(ds, key)
    #             self.assertEqual(float(known_value), float(result))

    # def test_gui_known_string_netcdf_attributes(self):
    #     with Dataset(GUI_FILENAME, 'r', format='NETCDF4_CLASSIC') as ds:
    #         for key in self.known_string_netcdf_attributes:
    #             known_value = INPUTS[key]
    #             result = getattr(ds, key)
    #             self.assertEqual(str(known_value), str(result))

    # def test_gui_known_numerical_netcdf_variables(self):
    #     with Dataset(GUI_FILENAME, 'r', format='NETCDF4_CLASSIC') as ds:
    #         for key in self.known_numerical_netcdf_variables:
    #             known_value = INPUTS[key]
    #             result = ds.variables[key].getValue()
    #             self.assertEqual(str(known_value), str(result))

    # def test_gui_netcdf_known_variables(self):
    #     with Dataset(GUI_FILENAME, 'r', format='NETCDF4_CLASSIC') as ds:
    #         result_pressure_series = ds.variables['sea_water_pressure'][:]
    #         for known_p, result_p in zip(self.known_pressure_series,
    #                                      result_pressure_series):
    #             known_p = 0.6894757 * known_p
    #             self.assertEqual(round(known_p, 4), round(result_p, 4))


if __name__ == '__main__':
    unittest.main()
