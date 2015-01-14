"""
Tests that netCDFs created by script1 contain the right data and metadata.

Uses some made up data files in the tests directory.
"""

# idea: make up some csv data file
# we manually make a netCDF with appropriate metadata
# then we compare the netCDF made by our tool with our correct one

import unittest
from netCDF4 import Dataset

csv_fname = './test_data/leveltroll_test.csv'
# correct_nc_fname = './test_data/leveltroll_test_data_sea.nc'
test_nc_fname = './test_data/leveltroll_test.nc'

instrument_name = 'LevelTroll'
in_filename = csv_fname,
out_filename = test_nc_fname

# all REAL metadata inputs
latitude = '20'
longitude = '30'
salinity = '100'
initial_water_depth = '11.5'
final_water_depth = '10'
device_depth = '9.5'
deployment_time = '20140101 0000'
retrieval_time = '20140102 0000'
tzinfo = 'US/Central'
sea_name = 'Great Lakes'
creator_name = 'Chris Mazzullo'
creator_email = 'stuff@gmail.com'
creator_url = 'zombo.com'


tzinfo = 'US/Central' # how is this used?

class KnownValues(unittest.TestCase):
    known_global_values = (
        ('deployment_time', '20140101 0000'),
        ('retrieval_time', '20140102 0000'),
        ('sea_name', 'Great Lakes'),
        ('creator_name', 'Chris Mazzullo'),
        ('creator_email', 'stuff@gmail.com'),
        ('initial_water_depth', '11.5'),
        ('final_water_depth', '10.0'), # have to add decimal point to all numbers because they are converted to floats internally
        ('device_depth', '9.5'),
        ('creator_url', 'zombo.com'))

    def test_netcdf_known_global_values(self):
        with Dataset(test_nc_fname, 'r', format='NETCDF4_CLASSIC') as ds:
            for tag, value in self.known_global_values:
                result = getattr(ds, tag)
                self.assertEqual(str(value), str(result))

if __name__ == '__main__':
    unittest.main()
