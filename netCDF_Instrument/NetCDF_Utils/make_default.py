from netCDF4 import Dataset
import numpy as np

"""This file contains the attributes of a netCDF file as dictionaries.
The goal here is to make it easy to create netCDF files stocked with
default information."""
FILL_VALUE = -99999
# GLOBAL ATTRIBUTES
globs = {
    'date_created': "2014-08-19T18:33:52Z",
    'creator_url': "gui url",
    'license': "This data may only be used upon the consent of the USGS",
    'geospatial_lat_min': 21,
    'keywords_vocabulary': "not used at this time",
    'distance_from_referencepoint_to_transducer': "When Deployed: 0 - When Retrieved: 0",
    'salinity_ppm': 35,
    'uuid': "c8578e40-a7f5-4e32-bce6-d4b247a2964c",
    'time_of_deployment': "20140910 0101",
    'creator_eamil': "hjenter@usgs.gov",
    'contributor_role': "data collector",
    'geospatial_vertical_units': "meters",
    'geospatial_lon_units': "degrees_east",
    'time_of_retrieval': "20141010 0101",
    'retrieval_time': "20141010 0101",
    'id': "not used at this time",
    'summary': "This is data collected by a pressure instrument used for extrapolating information regarding weather patterns",
    'geospatial_lat_units': "degrees_north",
    'time_zone': "UTC",
    'metadata_link': "http://54.243.149.253/home/webmap/viewer.html?webmap=c07fae08c20c4117bdb8e92e3239837e",
    'standard_name_vocabulary': "CF-1.6",
    'geospatial_lon_min': 21,
    'Metadata_Conventions': "Unidata Dataset Discovery v1.0",
    'geospatial_lon_resolution': "point",
    'time_coverage_start': "utilitiy coverage start",
    'geospatial_vertical_max': 0,
    'publisher_email': "deferred with intention to implement",
    'history': "not used at this time",
    'device_depth': 5,
    'project': "deferred with intention to implement",
    'time_coverage_resolution': "P0.25S",
    'deployment_time': "20140910 0101",
    'creator_email': "hjenter@usgs.gov",
    'keywords': "not used at this time",
    'geospatial_lat_max': 21,
    'comment': "not used at this time",
    'sea_name': "Gulf of Alaska",
    'time_coverage_duration': "utility coverage duration",
    'contributor_name': "USGS",
    'time_coverage_end': "utility coverage end",
    'creator_name': "Harry Jenter",
    'Conventions': "CF-1.6",
    'publisher_url': "deferred with intention to implement",
    'publisher_name': "deferred with intention to implement",
    'final_water_depth': 21,
    'date_modified': "2014-08-19T18:33:52Z",
    'geospatial_vertical_resolution': "point",
    'geospatial_lon_max': 21,
    'geospatial_vertical_positive': "up",
    'cdm_data_type': "station",
    'naming_authority': "not used at this time",
    'geospatial_lat_resolution': "point",
    'geospatial_vertical_min': 0,
    'institution': "USGS",
    'distance_from_transducer_to_seabed': "When Deployed: 0 - When Retrieved: 0",
    'readme': "file created by gui creator 2014-08-19 14:33:52.402037 with files gui filenames",
    'initial_water_depth': 21,
    'processing_level': "deferred with intention to implement"}

# VARIABLE ATTRIBUTES

timedict = {
    'ancillary_variables':  "",
    'compression':  "not used at this time",
    'calendar':  "gregorian",
    'ioos_category':  "Time",
    'scale_factor':  1.,
    'long_name':  "Time",
    'units':  "milliseconds since 1970-01-01 00:00:00",
    'short_name':  "time",
    'axis':  "T",
    'add_offset':  0.,
    'comment':  "Original time zone future gui",
    'standard_name':  "time"}

sea_water_pressuredict = {
    'ancillary_variables':  "",
    'compression':  "not used at this time",
    'coordinates':  "time latitude longitude altitude",
    'nodc_name':  "PRESSURE",
    'scale_factor':  1,
    'comment':  "",
    'units':  "decibar",
    'short_name':  "pressure",
    'add_offset':  0,
    'max':  1000,
    'long_name':  "sensor pressure record",
    'min':  -1000,
    'standard_name':  "sea_water_pressure",
    'ioos_category':  "Pressure",
    'flag_meanings':  "no_bad_data last_five_vals_identical, outside_valid_range, invalid_rate_of_change",
    'flag_masks':  "1111 1110 1101 1011",
    'comment':  "1 signifies the value passed the test while a 0 flags a failed test, leading 1 is a placeholder"}
altitudedict = {
    'valid_max':  1000,
    'compression':  "not used at this time",
    'ioos_category':  "Location",
    'ancillary_variables':  "",
    'scale_factor':  1.,
    'valid_min':  -1000,
    'long_name':  "altitude of sensor",
    'units':  "degrees",
    'short_name':  "altitude",
    'axis':  "Z",
    'add_offset':  0.,
    'comment':  "altitude of instrument",
    'standard_name':  "altitude"}
latitudedict = {
    'valid_max':  21,
    'compression':  "not used at this time",
    'ioos_category':  "Location",
    'ancillary_variables':  "",
    'scale_factor':  1.,
    'valid_min':  21,
    'long_name':  "latitude of sensor",
    'units':  "degrees",
    'short_name':  "latitude",
    'axis':  "Y",
    'add_offset':  0.,
    'comment':  "latitude 0 equals equator",
    'standard_name':  "latitude"}
longitudedict = {
    'valid_max':  21,
    'compression':  "not used at this time",
    'ioos_category':  "Location",
    'ancillary_variables':  "",
    'scale_factor':  1.,
    'valid_min':  21,
    'long_name':  "longitude of sensor",
    'units':  "degrees",
    'short_name':  "longitude",
    'axis':  "X",
    'add_offset':  0.,
    'comment':  "longitude 0 equals prime meridian",
    'standard_name':  "longitude"}

def set_attributes(variable, attributedict):
    [setattr(variable, key, attributedict[key])
     for key in attributedict]

time = np.arange(100)
pressure = np.arange(100)
altitude = 10
longitude = 25
latitude = 33.3

def make_netcdf(filename, time, pressure, altitude, longitude,
                latitude, globs, timedict, sea_water_pressuredict,
                altitudedict, longitudedict, latitudedict):
    with Dataset(filename, 'w', format='NETCDF4_CLASSIC') as d:
        d.createDimension('time', len(time))
        set_attributes(d, globs)

        pressure_var = d.createVariable('sea_water_pressure', 'f8', ('time',))
        pressure_var[:] = pressure
        set_attributes(pressure_var, sea_water_pressuredict)

        time_var = d.createVariable('time', 'f8', ('time',), fill_value=FILL_VALUE)
        time_var[:] = time
        set_attributes(time_var, timedict)

        altitude_var = d.createVariable('altitude', 'f8', fill_value=FILL_VALUE)
        altitude_var[:] = altitude
        set_attributes(altitude_var, altitudedict)

        longitude_var = d.createVariable('longitude', 'f8', fill_value=FILL_VALUE)
        longitude_var[:] = longitude
        set_attributes(longitude_var, longitudedict)

        latitude_var = d.createVariable('latitude', 'f8', fill_value=FILL_VALUE)
        latitude_var[:] = latitude
        set_attributes(latitude_var, latitudedict)

def make_default_netcdf(filename, time, pressure):
    make_netcdf(filename, time, pressure, altitude, longitude, latitude,
                globs, timedict, sea_water_pressuredict, altitudedict,
                longitudedict, latitudedict)
