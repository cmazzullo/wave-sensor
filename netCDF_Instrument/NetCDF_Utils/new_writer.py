from netCDF4 import Dataset
from datetime import datetime
import pytz
import numpy as np
import uuid
import NetCDF_Utils.DateTimeConvert as timeconvert
from Instruments.ncdumpesque import dump_all

fname = r'C:\Users\cmazzullo\Desktop\nc_file.nc'
epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)

def make_empty_nc(fname):
    with Dataset(fname, 'w', format='NETCDF4_CLASSIC') as new_file:
        pass

# def make_dimension(fname, name, size):
#     with Dataset(nc_file, 'a') as nc_file:
#         return nc_file.createDimension(name, size)

# def make_variable(nc_file, name, dtype, dimension):
#     return nc_file.createVariable(name, dtype, (dimension,))

def make_attribute(nc_file, name, value, variable_name=''):
    if variable_name:
        variable = nc_file.variables.get(variable_name)
        setattr(variable, name, value)
    else:
        setattr(nc_file, name, value)
        return value

def write_attributes(nc_file, attributes, variable_name=''):
    for name in attributes:
        make_attribute(nc_file, name, attributes.get(name),
                       variable_name=variable_name)

# instrument_var = {
#     'long_name': 'Attributes for instrument 1',
#     'make_model': '',
#     'serial_number': '',
#     'calibration_date': '',
#     'factory_calibration': '',
#     'user_calibrated': '',
#     'calibration_report': '',
#     'accuracy': '',
#     'valid_range': [0,1],
#     'precision': '',
#     'comment': '',
#     'ancillary_variables': '' }

# time_var = {
#     'long_name': 'Time',
#     'short_name': 'time',
#     'standard_name': "time",
#     'units': ("milliseconds since " +
#               self.epoch_start.strftime("%Y-%m-%d %H:%M:%S")),
#     'calendar': "gregorian",
#     'axis': 'T',
#     'ancillary_variables': '',
#     'comment': "Original time zone future gui",
#     'ioos_category': "Time",
#     'add_offset': 0.0,
#     'scale_factor': 1.0,
#     'compression': "not used at this time"}

# lon_var = {
#     'long_name': "longitude of sensor",
#     'standard_name': "longitude",
#     'short_name': 'longitude',
#     'units': "degrees",
#     'axis': 'X',
#     'valid_min': self.longitude,
#     'valid_max': self.longitude,
#     'ancillary_variables': '',
#     'comment': "longitude 0 equals prime meridian",
#     'ioos_category': "Location",
#     'add_offset': 0.0,
#     'scale_factor': 1.0,
#     'compression': "not used at this time"}

# lat_var = {
#     'long_name': "latitude of sensor",
#     'standard_name': "latitude",
#     'short_name': 'latitude',
#     'units': "degrees",
#     'axis': 'Y',
#     'valid_min': self.latitude,
#     'valid_max': self.latitude,
#     'ancillary_variables': '',
#     'comment': "latitude 0 equals equator",
#     'ioos_category': "Location",
#     'add_offset': 0.0,
#     'scale_factor': 1.0,
#     'compression': "not used at this time",}

# z_var = {
#     'long_name': "altitude of sensor",
#     'standard_name': "altitude",
#     'short_name': 'altitude',
#     'units': "degrees",
#     'axis': 'Z',
#     'valid_min': self.z_range[0],
#     'valid_max': self.z_range[1],
#     'ancillary_variables': '',
#     'comment': "altitude of instrument",
#     'ioos_category': "Location",
#     'add_offset': 0.0,
#     'scale_factor': 1.0,
#     'compression': "not used at this time"}

# z_var_qc = {
#     'flag_masks': '1111 1110 1101 1011',
#     'flag_meanings': ('no_known_bad_data last_five_vals_identical, '
#                       'outside_valid_range, invalid_rate_of_change'),
#     'comment': ('1 signifies the value passed the test while a 0 '
#                 'flags a failed test, leading 1 is a placeholder')}

# pressure_var = {
#     'long_name': "sensor pressure record",
#     'standard_name': "sea_water_pressure",
#     'short_name': "pressure",
#     'nodc_name': "pressure".upper(),
#     'units': "decibar",
#     'scale_factor': np.float32(1.0),
#     'add_offset': np.float32(0.0),
#     'compression': "not used at this time",
#     'min': self.pressure_range[0],
#     'max': self.pressure_range[1],
#     'ancillary_variables': '',
#     'coordinates': "time latitude longitude altitude",
#     'ioos_category': "Pressure",
#     'comment': "",}

# pressure_var_qc = {
#     'flag_masks': '1111 1110 1101 1011',
#     'flag_meanings': ('no_bad_data last_five_vals_identical, '
#                       'outside_valid_range, invalid_rate_of_change'),
#     'comment': ('1 signifies the value passed the test while a 0 '
#                 'flags a failed test, leading 1 is a placeholder')}

# temp_var= {
#     'long_name': "sensor temperature record",
#     'standard_name': "temperature",
#     'short_name': "temp",
#     'nodc_name': "temperature".upper(),
#     'units': "degree_Celsius",
#     'scale_factor': np.float32(1.0),
#     'add_offset': np.float32(0.0),
#     'compression': "not used at this time",
#     'min': self.temperature_range[0],
#     'max': self.temperature_range[1],
#     'ancillary_variables': '',
#     'coordinates': "time latitude longitude altitude",
#     'ioos_category': "Temperature",
#     'comment': "",}

# temp_var_qc = {
#     'flag_masks': '111 110 101 011',
#     'flag_meanings': ('no_bad_data last_five_vals_identical, '
#                       'outside_valid_range, invalid_rate_of_change'),
#     'comment': ('1 signifies the value passed the test while a 0 '
#                 'flags a failed test, leading 1 is a placeholder')}

# global_vars_dict = {
#     "cdm_data_type": "station",
#     "comment": "not used at this time",
#     "contributor_name": "USGS",
#     "contributor_role": "data collector",
#     "Conventions": "CF-1.6",
#     "date_created": datetime.strftime(datetime.now(tz=pytz.utc),
#                                       "%Y-%m-%dT%H:%M:%SZ"),
#     "date_modified": datetime.strftime(datetime.now(tz=pytz.utc),
#                                        "%Y-%m-%dT%H:%M:%SZ"),
#     "geospatial_lat_min": self.latitude_range[0],
#     "geospatial_lat_max": self.latitude_range[1],
#     "geospatial_lon_min": self.longitude_range[0],
#     "geospatial_lon_max": self.longitude_range[1],
#     "geospatial_lat_units": "degrees_north",
#     "geospatial_lat_resolution": "point",
#     "geospatial_lon_units": "degrees_east",
#     "geospatial_lon_resolution": "point",
#     "geospatial_vertical_min": self.z,
#     "geospatial_vertical_max": self.z,
#     "geospatial_vertical_units": "meters",
#     "geospatial_vertical_resolution": "point",
#     "geospatial_vertical_positive": "up",
#     "history": "not used at this time",
#     "id": "not used at this time",
#     "institution": "USGS",
#     "keywords": "not used at this time",
#     "keywords_vocabulary": "not used at this time",
#     "license": "This data may only be used upon the consent of the USGS",
#     "Metadata_Conventions": "Unidata Dataset Discovery v1.0",
#     "metadata_link": "http://54.243.149.253/home/webmap/viewer.html?webmap=c07fae08c20c4117bdb8e92e3239837e",
#     "naming_authority": "not used at this time",
#     "processing_level": "deferred with intention to implement",
#     "project": "deferred with intention to implement",
#     "publisher_email": "deferred with intention to implement",
#     "publisher_name": "deferred with intention to implement",
#     "publisher_url": "deferred with intention to implement",
#     "readme": "file created by "+ "gui creator " + str(datetime.now()) +" with files " + "gui filenames",
#     "salinity_ppm": self.salinity,
#     "sea_name": "gui sea name",
#     "standard_name_vocabulary": "CF-1.6",
#     "summary": "This is data collected by a pressure instrument used for extrapolating information regarding weather patterns",
#     "time_coverage_start": "utility coverage start",
#     "time_coverage_end": "utility coverage end",
#     "time_coverage_duration": "utility coverage duration",
#     "time_coverage_resolution": "P0.25S",
#     "uuid": str(uuid.uuid4())}

# variables = [
#     ('instrument', 'i4', None, instrument),
#     ('time', 'f8', None, time_var),
#     ('latitude', 'f8', None, lat_var),
#     ('longitude', 'f8', None, lon_var),
#     ('altitude', 'f8', None, z_var),
#     ('altitude_qc', 'i4', None, z_var_qc),
#     ('sea_water_pressure', 'f8', None, pressure_var),
#     ('pressure_qc', 'i4', None, pressure_var_qc),
#     ('temperature_at_transducer', 'f8', None, temp_var),
#     ('temperature_qc', 'i4', None, temp_var_qc)]


def make_variable(nc_file, name, dtype, dimension=None,
                  attributes=dict()):
    if dimension:
        variable = nc_file.createVariable(name, dtype, (dimension,))
    else:
        variable = nc_file.createVariable(name, dtype)
    write_attributes(nc_file, attributes, variable_name=name)
    return variable

def make_template(fname, dimensions, global_attributes, variables):
    make_empty_nc(fname)
    with Dataset(fname, 'a') as nc_file:
        for dim in dimensions:
            nc_file.createDimension(dim.get('name'), dim.get('size'))
        for var in variables:
            make_variable(nc_file, var[0], var[1],
                          dimension=var[2], attributes=var[3])

instrument_attributes = {
    'name': 'rbrsolo',
    'rating': '4',
    'number': '27'}

pressure_attributes = {
    'name': 'pressure',
    'NODC name': 'sea_water_pressure'}

variables = [
    ('instrument', 	'i4', 	None, 	instrument_attributes),
    ('pressure',	'i4', 	None, 	pressure_attributes)]

make_template(fname, dimensions, global_attributes, variables)

dump_all(fname)
