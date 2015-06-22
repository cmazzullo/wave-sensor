import tkinter
from tkinter import ttk
from pytz import timezone
import os
import numpy as np
from numpy import random
from functools import partial
from tkinter.filedialog import askopenfilename as fileprompt
import os
from collections import OrderedDict

import shutil
from numpy import arange

from datetime import datetime, timedelta
import netCDF4
import netCDF4_utils
import netcdftime
from netCDF4 import Dataset

from bitarray import bitarray as bit
import pandas
import pytz

from scipy.optimize import newton
import scipy.sparse.csgraph._validation
import scipy.special._ufuncs_cxx

# Constants
g = 9.8  # gravity (m / s**2)
rho = 1030  # density of seawater (kg / m**3)
min_coeff = 1/15
FILL_VALUE = -1e10


            
"""
Created on Thu Aug  7 2014

@author: cmazzullo

A frontend for script2, which takes one water pressure and one air
pressure file and outputs a file containing water pressure, air
pressure and depth.
"""

from tkinter import *
from tkinter import filedialog
from tkinter import ttk



class Script2gui:
    def __init__(self, root):
        root.title('Pressure -> Water Height')

        methods = [('Hydrostatic', 'naive'),
                ('Linear Wave', 'combo')]

        self.methodvar = StringVar()
        self.methodvar.set('combo')

        ttk.Label(root, text='Depth calculation:').pack(anchor=W)
        for name, kwarg in methods:
            ttk.Radiobutton(root, text=name, variable=self.methodvar,
                            value=kwarg).pack(anchor=W)

        self.sea_fname = None
        self.sea_var = StringVar()
        self.sea_var.set('File containing water pressure...')
        self.air_fname = ''
        self.air_var = StringVar()
        self.air_var.set('File containing air pressure (optional)...')
        self.make_fileselect(root, 'Water file:',
                             self.sea_var, 'sea_fname')
        self.make_fileselect(root, 'Air file:',
                             self.air_var, 'air_fname')
        c3 = lambda: self.select_output_file(root)
        self.b3 = self.make_button(root, "Export to File", c3,
                                   state=DISABLED)
        self.b3.pack(anchor=W, fill=BOTH)


    def select_file(self, varname, stringvar):
        fname = filedialog.askopenfilename()
        if fname != '':
            stringvar.set(fname)
            setattr(self, varname, fname)
            if self.sea_fname:
                self.b3['state'] = 'ENABLED'

    def make_button(self, root, text, command, state=None):
        b = ttk.Button(root, text=text, command=command, state=state,
                       width=10)
        return b

    def make_fileselect(self, root, labeltext, stringvar, varname):
        command = lambda: self.select_file(varname, stringvar)
        frame = make_frame(root)
        l = ttk.Label(frame, justify=LEFT, text=labeltext, width=10)
        l.grid(row=0, column=0, sticky=W)
        b = self.make_button(frame, 'Browse', command)
        b.grid(row=0, column=2, sticky=W)
        e = ttk.Label(frame, textvariable=stringvar, justify=LEFT,
                      width=32)
        e.grid(row=0, column=1, sticky=(W, E))
        frame.pack(anchor=W, fill=BOTH)

    def select_output_file(self, root):
        output_fname = filedialog.asksaveasfilename()
        method = self.methodvar.get()
        sea_t = get_time(self.sea_fname)
        if self.air_fname != '':
            air_t = get_time(self.air_fname)
            if (air_t[-1] < sea_t[0]) or (air_t[0] > sea_t[-1]):
                message = ("Air pressure and water pressure files don't "
                           "cover the same time period!\nPlease choose "
                           "other files.")
                MessageDialog(root, message=message, title='Error!')
                return
            elif (air_t[0] > sea_t[0] or air_t[-1] < sea_t[-1]):
                message = ("The air pressure file doesn't span the "
                "entire time period covered by the water pressure "
                "file.\nThe period not covered by both files will be "
                "set to the fill value:%d" % FILL_VALUE)
                MessageDialog(root, message=message, title='Warning')
                
        #check to see if time coverage resolution is small enough to perform combo
        timestep = 1 / get_frequency(self.sea_fname)
        print('timestep', timestep)
        if method =="combo" and timestep > .5:
            method = "naive"
            message = "Time resolution too large to run Linear Wave method.  Will run hydrostatic..."
            MessageDialog(root, message=message,
                         title='Success!')

        make_depth_file(self.sea_fname, self.air_fname,
                                output_fname, method=method)
        MessageDialog(root, message="Success! Files saved.",
                         title='Success!')

def make_depth_file(water_fname, air_fname, out_fname, method='combo'):
    """Adds depth information to a water pressure file.

    The argument air_fname is optional, when set to '' no air
    pressure is used.
    """
    device_depth = -1 * get_device_depth(water_fname)
    water_depth = get_water_depth(water_fname)
    timestep = 1 / get_frequency(water_fname)
    sea_pressure = get_pressure(water_fname)
    print('sea_pressure len')
    print(len(sea_pressure))
    sea_time = get_time(water_fname)
    sea_qc = get_pressure_qc(water_fname)
    air_qc = None
    #creating testing object
    test = DataTests()
    test.interpolated_data = True
    print('air_fname = ', air_fname)
    if air_fname != '':
        raw_air_pressure = get_air_pressure(air_fname)
        air_time = get_time(air_fname)
        air_pressure = np.interp(sea_time, air_time, raw_air_pressure,
                                 left=FILL_VALUE, right=FILL_VALUE)
        corrected_pressure = sea_pressure - air_pressure
        corrected_pressure[np.where(air_pressure == FILL_VALUE)] = FILL_VALUE
        test.pressure_data = air_pressure
        air_qc = test.select_tests('')
    else:
        corrected_pressure = sea_pressure
    if method == 'fft':
        depth = fft_method(corrected_pressure, device_depth,
                               water_depth, timestep)
    elif method == 'combo':
        depth = combo_method(sea_time, corrected_pressure,
                                 device_depth, water_depth, timestep)
    elif method == 'naive':
        depth = hydrostatic_method(corrected_pressure)
    else:
        raise TypeError('Accepted values for "method" are: fft, '
                        'method2 and naive.')
    if len(depth) == len(sea_pressure) - 1:
        depth = np.append(depth, np.NaN)
    shutil.copy(water_fname, out_fname)
    if air_fname != '':
        append_air_pressure(out_fname, air_pressure)
        # air_qc and depth qc
        air_qc = test.select_tests('')
        append_depth_qc(out_fname, sea_qc, air_qc)
    else:
        append_depth_qc(out_fname, sea_qc, None)

    append_depth(out_fname, depth)
    
FILL_VALUE = -1e10

# Utility methods

def chop_netcdf(fname, out_fname, begin, end):
    """Truncate the data in a netCDF file between two indices"""
    if os.path.exists(out_fname):
        os.remove(out_fname)
    length = end - begin
    p = get_pressure(fname)[begin:end]
    t = get_time(fname)[begin:end]
    flags = get_flags(fname)[begin:end]
    alt = get_variable_data(fname, 'altitude')
    lat = get_variable_data(fname, 'latitude')
    long = get_variable_data(fname, 'longitude')
    d = Dataset(fname)
    output = Dataset(out_fname, 'w', format='NETCDF4_CLASSIC')
    output.createDimension('time', length)
    # copy globals
    for att in d.ncattrs():
        setattr(output, att, d.__dict__[att])
    # copy variables
    for key in d.variables:
        name = key
        # datatype = d.variables[key].datatype
        datatype = np.dtype('float64')
        dim = d.variables[key].dimensions
        var = output.createVariable(name, datatype, dim, fill_value=FILL_VALUE)
        for att in d.variables[key].ncattrs():
            if att != '_FillValue':
                setattr(var, att, d.variables[key].__dict__[att])
    output.variables['time'][:] = t
    output.variables['sea_water_pressure'][:] = p
    output.variables['pressure_qc'][:] = flags
    output.variables['altitude'][:] = alt
    output.variables['longitude'][:] = long
    output.variables['latitude'][:] = lat
    d.close()
    output.close()

def parse_time(fname, time_name):
    """Convert a UTC offset in attribute "time_name" to a datetime."""
    timezone_str = get_global_attribute(fname, 'time_zone')
    timezone = pytz.timezone(timezone_str)
    time_str = get_global_attribute(fname, time_name)
    fmt = '%Y%m%d %H%M'
    time = timezone.localize(datetime.strptime(time_str, fmt))
    epoch_start = datetime(year=1970, month=1, day=1, tzinfo=pytz.utc)
    time_ms = (time - epoch_start).total_seconds() * 1000
    return time_ms

# Append new variables

def append_air_pressure(fname, pressure):
    """Insert air pressure array into the netCDF file fname"""
    name = 'air_pressure'
    long_name = 'air pressure record'
    append_variable(fname, name, pressure, comment='',
                     long_name=long_name)


def append_depth(fname, depth):
    """Insert depth array into the netCDF file at fname"""
    comment = ('The depth, computed using the variable "corrected '
               'water pressure".')
    name = 'depth'
    print('len(depth) = ' + str(len(depth)))
    append_variable(fname, name, depth, comment=comment,
                     long_name=name)

def append_depth_qc(fname, sea_qc, air_qc):
    """Insert depth qc array"""
    depth_name = 'depth_qc'
    air_name = "air_qc"
    air_comment = 'The air_qc is a binary and of the (sea)pressure_qc and air_pressure_qc if an air file is used to calculate depth'
    depth_comment = 'The depth_qc is a binary and of the (sea)pressure_qc and air_pressure_qc'
    flag_masks = '11111111 11111110 11111101 11111011 11110111'
    flag_meanings =  "no_bad_data last_five_vals_identical, outside_valid_range, invalid_rate_of_change, interpolated_data"
    
    if air_qc != None:
        air_qc = [bit(x) for x in air_qc]
        sea_qc = [bit(str(int(x))) for x in sea_qc]
    
        depth_qc = [(air_qc[x] & sea_qc[x]).to01() for x in range(0,len(sea_qc))]
        append_variable(fname, air_name, [x.to01() for x in air_qc], comment=air_comment, long_name=air_name, 
                        flag_masks = flag_masks, flag_meanings= flag_meanings)
        append_variable(fname, depth_name, depth_qc, comment=depth_comment, long_name=depth_name,
                         flag_masks = flag_masks, flag_meanings= flag_meanings)
    else:
        append_variable(fname, depth_name, sea_qc, comment=depth_comment, long_name=depth_name,
                         flag_masks = flag_masks, flag_meanings= flag_meanings)
   
        
# Get variable data

def get_water_depth(in_fname):
    """Get the static water depth from the netCDF at fname"""
    initial_depth = get_initial_water_depth(in_fname)
    final_depth = get_final_water_depth(in_fname)
    initial_time = get_deployment_time(in_fname)
    final_time = get_retrieval_time(in_fname)
    time = get_time(in_fname)
    slope = (final_depth - initial_depth) / (final_time - initial_time)
    depth_approx = slope * (time - initial_time) + initial_depth
    return depth_approx


def get_depth(fname):
    """Get the wave height array from the netCDF at fname"""
    return get_variable_data(fname, 'depth')


def get_flags(fname):
    """Get the time array from the netCDF at fname"""
    return get_variable_data(fname, 'pressure_qc')

def get_time(fname):
    """Get the time array from the netCDF at fname"""
    return get_variable_data(fname, 'time')


def get_air_pressure(fname):
    """Get the air pressure array from the netCDF at fname"""
    return get_variable_data(fname, 'air_pressure')


def get_pressure(fname):
    """Get the water pressure array from the netCDF at fname"""
    return get_variable_data(fname, 'sea_water_pressure')

def get_pressure_qc(fname):
    return get_variable_data(fname, 'pressure_qc')

# Get global data

def get_frequency(fname):
    """Get the frequency of the data in the netCDF at fname"""
    freq_string = get_global_attribute(fname, 'time_coverage_resolution')
    return 1 / float(freq_string[1:-1])


def get_initial_water_depth(fname):
    """Get the initial water depth from the netCDF at fname"""
    return get_global_attribute(fname, 'initial_water_depth')


def get_final_water_depth(fname):
    """Get the final water depth from the netCDF at fname"""
    return get_global_attribute(fname, 'final_water_depth')


def get_deployment_time(fname):
    """Get the deployment time from the netCDF at fname"""
    return parse_time(fname, 'deployment_time')


def get_retrieval_time(fname):
    """Get the retrieval time from the netCDF at fname"""
    return parse_time(fname, 'retrieval_time')


def get_device_depth(fname):
    """Get the retrieval time from the netCDF at fname"""
    return get_global_attribute(fname, 'device_depth')


def get_variable_data(fname, variable_name):
    """Get the values of a variable from a netCDF file."""
    with Dataset(fname) as nc_file:
        var = nc_file.variables[variable_name]
        var_data = var[:]
        return var_data

# Backend

def get_global_attribute(fname, name):
    """Get the value of a global attibute from a netCDF file."""
    with Dataset(fname) as nc_file:
        attr = getattr(nc_file, name)
        return attr


def append_variable(fname, standard_name, data, comment='',
                     long_name='', flag_masks = None, flag_meanings = None):
    """Append a new variable to an existing netCDF."""
    with Dataset(fname, 'a', format='NETCDF4_CLASSIC') as nc_file:
        pvar = nc_file.createVariable(standard_name, 'f8', ('time',))
        pvar.ioos_category = ''
        pvar.comment = comment
        pvar.standard_name = standard_name
        pvar.max = 1000
        pvar.min = -1000
        pvar.short_name = standard_name
        pvar.ancillary_variables = ''
        pvar.add_offset = 0.0
        pvar.coordinates = 'time latitude longitude altitude'
        pvar.long_name = long_name
        pvar.scale_factor = 1.0
        if flag_masks != None:
            pvar.flags_masks = flag_masks
            pvar.flag_meanings = flag_meanings
        if standard_name == 'depth':
            pvar.units = 'meters'
            pvar.nodc_name = 'WATER DEPTH'
        else:
            pvar.units = 'decibars'
            pvar.nodc_name = 'PRESSURE'
        pvar.compression = 'not used at this time'
        pvar[:] = data

def ncdump(fname):
    """Dump all attributes and variables in a netCDF to stdout"""
    f = Dataset(fname)
    print('\nDimensions:\n')
    for dim in f.dimensions:
        print(dim, ':\t\t', len(f.dimensions[dim]))
    print('\n\nAttributes:\n\n')
    for att in f.__dict__:
        name = (att + ':').ljust(35)
        value = str(f.__dict__[att]).ljust(50)
        print(name, value)
    print('\n\nVariables:\n\n')
    for att in f.variables:
        name = (att + ':').ljust(35)
        value = str(f.variables[att]).ljust(50)
        print(name, value)
    f.close()
    



def convert_to_netcdf(inputs):
    translated = translate_inputs(inputs)
    instrument = INSTRUMENTS[translated['instrument_name']]()
    instrument.user_data_start_flag = 0
    for key in translated:
        setattr(instrument, key, translated[key])
    instrument.read()
    instrument.write(sea_pressure=translated['sea_pressure'])


DATATYPES = {
    'latitude': np.float32,
    'longitude': np.float32,
    'initial_water_depth': np.float32,
    'final_water_depth': np.float32,
    'device_depth': np.float32,
    'tzinfo': timezone,
    'sea_pressure' : bool }


def translate_inputs(inputs):
    translated = dict()
    for key in inputs: # cast everything to the right type
        if key in DATATYPES:
            translated[key] = DATATYPES[key](inputs[key])
        else:
            translated[key] = inputs[key]
    return translated

class NetCDFWriter(object):

    def __init__(self):
        self.pressure_comments = None
        self.temperature_comments = None
        self.depth_comments = None
        self.out_filename = os.path.join("..\Instruments",'benchmark','DepthTest.nc')
        self.in_filename = None
        self.is_baro = None
        self.pressure_units = None
        self.z_units = 'meters'
        self.latitude = 0
        self.longitude = 0
        self.z = 0
        self.salinity_ppm = -1.0e+10
        self.utc_millisecond_data = None
        self.pressure_data = None
        self.presure_data_flags = None
        self.epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
        self.data_start = None
        self.timezone_string = None
        self.tz_info = pytz.timezone('US/Eastern')
        self.date_format_string = None
        self.frequency = None
        self.valid_pressure_units = ["psi","pascals","atm"]
        self.valid_z_units = ["meters","feet"]
        self.valid_latitude = (np.float32(-90),np.float32(90))
        self.valid_longitude = (np.float32(-180),np.float32(180))
        self.valid_z = (np.float32(-10000),np.float32(10000))
        self.valid_salinity = (np.float32(0.0),np.float32(40000))
        self.valid_pressure = (np.float32(-10000),np.float32(10000))
        self.valid_temp = (np.float32(-10000), np.float32(10000))
        self.fill_value = np.float64(-1.0e+10)
        self.creator_name = ""
        self.creator_email = ""
        self.creator_url = ""
        self.sea_name = "The Red Sea"
        self.user_data_start_flag = None
        self.vstore = DataStore(1)
        self.vdict = dict()
        self.data_tests = DataTests()

        self.initial_water_depth = 0
        self.final_water_depth = 0
        self.device_depth = 0
        self.deployment_time = 0
        self.retrieval_time = 0

    def write_netCDF(self,var_datastore,series_length):
        ds = netCDF4.Dataset(os.path.join(self.out_filename),'w',format="NETCDF4_CLASSIC")
        time_dimen = ds.createDimension("time",series_length)
        var_datastore.set_attributes(self.var_dict())
        var_datastore.send_data(ds)

    def var_dict(self):
        var_dict = dict()

        lat_dict = {'valid_min': self.latitude, 'valid_max': self.latitude}
        var_dict['lat_var'] = lat_dict
        lon_dict = {'valid_min': self.longitude, 'valid_max': self.longitude}
        var_dict['lon_var'] = lon_dict
        global_vars = {'creator_name': self.creator_name, 'creator_email': self.creator_email,
                       'creator_eamil': self.creator_email, 'geospatial_lat_min': self.latitude,
                       'geospatial_lat_max': self.latitude, 'geospatial_lon_min': self.longitude,
                       'geospatial_lon_max': self.longitude, 'geospatial_vertical_min': self.z,
                       'geospatial_vertical_max': self.z, 'sea_name': self.sea_name,
                       'initial_water_depth': self.initial_water_depth, 'final_water_depth': self.final_water_depth,
                       'deployment_time': self.deployment_time, 'retrieval_time': self.retrieval_time,
                       'device_depth': self.device_depth}
        var_dict['global_vars_dict'] = global_vars

        return var_dict
class Hobo(NetCDFWriter):
    '''derived class for hobo csv files
    '''
    def __init__(self):
        self.timezone_marker = "time zone"
        super().__init__()

        self.tz_info = pytz.timezone("US/Eastern")
        self.frequency = 1.0/30.0
        self.date_format_string = '%m/%d/%y %I:%M:%S %p'
        self.data_tests = DataTests()


    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        skip_index = self.read_start('"#"',',')
        # for skipping lines in case there is calibration header data
        df = pandas.read_table(self.in_filename,skiprows=skip_index, header=None, engine='c', sep=',')
        
        #apparently hobos have a mode to measure depth which triggers measurements at 2 second intervals
        #this may be arbitrary but a file with regular 30 second intervals breaks up in to 2 second intervals
        #with blank measurements for pressure at every interval between the initial
        #since we want evenly spaced data and interpolation would be a waste of time we will filter the records that are blank
        print(df[2][0], df[2][1])
        df.dropna()
        
        self.utc_millisecond_data = convert_to_milliseconds(df.shape[0], df[1][0], \
                                                                        self.date_format_string, self.frequency)

        self.pressure_data = [x for x in np.divide(df[2], 1.45037738)]

        print(len(self.pressure_data))


    def read_start(self, expression, delimeter):
        skip_index = 0;
        with open(self.in_filename,'r') as fileText:
            for x in fileText:
                file_string = x.split(delimeter)[0].strip()
                if expression == file_string:
                    print('Success! Index %s' % skip_index)
                    break
                skip_index += 1
        return skip_index + 1


    def write(self, sea_pressure = True):
        '''Write netCDF files

        sea_pressure - if true write sea_pressure data, otherwise write air_pressure data'''
        if sea_pressure == False:
            self.vstore.pressure_name = "air_pressure"
            self.vstore.pressure_var['standard_name'] = "air_pressure"

        self.vstore.pressure_data = self.pressure_data
        self.vstore.utc_millisecond_data = self.utc_millisecond_data
        self.vstore.latitude = self.latitude
        self.vstore.longitude = self.longitude

        #Tests#
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')

        self.write_netCDF(self.vstore, len(self.pressure_data))

class Leveltroll(NetCDFWriter):
    '''derived class for leveltroll ascii files
    '''
    def __init__(self):
        self.numpy_dtype = np.dtype([("seconds",np.float32),("pressure",np.float32)])
        self.record_start_marker = "date and time,seconds"
        self.timezone_marker = "time zone"
        super(Leveltroll,self).__init__()
        self.date_format_string = "%m/%d/%Y %I:%M:%S %p "
        self.temperature_data = None
        self.data_tests = DataTests()


    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        f = open(self.in_filename,'rb')

        self.read_header(f)
        self.read_datetime(f)

        data = np.genfromtxt(f,dtype=self.numpy_dtype,delimiter=',',usecols=[1,2,3])
        f.close()


        long_seconds = data["seconds"]
        print(long_seconds[::-1])
        self.utc_millisecond_data = [(x * 1000) + self.data_start for x in long_seconds]

        self.pressure_data = np.divide(data["pressure"], 1.45037738)
#         self.temperature_data = [x for x in data["temperature"]]

        print(len(self.pressure_data))

    def read_header(self,f):
        ''' read the header from the level troll ASCII file
        '''
        line = ""
        line_count = 0
        while not line.lower().startswith(self.record_start_marker):
            bit_line = f.readline()
            line = bit_line.decode()
            line_count += 1
            if line.lower().startswith(self.timezone_marker):
                self.timezone_string = line.split(':')[1].strip()
        if self.timezone_string is None:
            raise Exception("ERROR - could not find time zone in file "+\
                self.in_filename+" header before line "+str(line_count)+'\n')
        self.set_timezone()


    def read_datetime(self,f):
        '''read the first datetime and cast
        '''
        dt_fmt = "%m/%d/%Y %I:%M:%S %p "
#         dt_converter = lambda x: datetime.strptime(str(x),dt_fmt)\
#             .replace(tzinfo=self.tzinfo)
        reset_point = f.tell()
        bit_line = f.readline()
        line = bit_line.decode()

        raw = line.strip().split(',')
        dt_str = raw[0]
        try:
            self.data_start = convert_date_to_milliseconds(dt_str,self.date_format_string)
#             self.data_start_date = datetime.strftime(self.data_start, "%Y-%m-%dT%H:%M:%SZ")
#             print('Datetime', self.data_start, self.data_start_date)
        except Exception:
            raise Exception("ERROR - cannot parse first date time stamp: "+str(self.td_str)+" using format: "+dt_fmt+'\n')
        f.seek(reset_point)



    def set_timezone(self):
        '''set the timezone from the timezone string found in the header -
        needed to get the times into UTC
        '''
        tz_dict = {"central":"US/Central","eastern":"US/Eastern"}
        for tz_str,tz in tz_dict.items():
            if self.timezone_string.lower().startswith(tz_str):
                self.tzinfo = timezone(tz)
                return
        raise Exception("could not find a timezone match for " + self.timezone_string)

    @property
    def offset_seconds(self):
        '''offsets seconds from specified epoch using UTC time
        '''
        offset = self.data_start - self.epoch_start
        return offset.total_seconds()

    def write(self, sea_pressure = True):
        '''Write netCDF files

        sea_pressure - if true write sea_pressure data, otherwise write air_pressure data'''

        if sea_pressure == False:
            self.vstore.pressure_name = "air_pressure"
            self.vstore.pressure_var['standard_name'] = "air_pressure"

        self.vstore.pressure_data = self.pressure_data
        self.vstore.utc_millisecond_data = self.utc_millisecond_data
        self.vstore.latitude = self.latitude
        self.vstore.longitude = self.longitude

        #Tests#
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')

        self.write_netCDF(self.vstore, len(self.pressure_data))

class MeasureSysLogger(NetCDFWriter):
    '''derived class for Measurement Systems cvs files
    '''
    def __init__(self):
        self.timezone_marker = "time zone"
        super(MeasureSysLogger,self).__init__()
        self.tz_info = pytz.timezone("US/Eastern")
        self.frequency = 4
        self.date_format_string = '%m/%d/%Y %I:%M:%S.%f %p'
        self.data_tests = DataTests()

    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        skip_index = self.read_start('^ID$',',')
        #for skipping lines in case there is calibration header data
        df = pandas.read_table(self.in_filename,skiprows=skip_index + 1, header=None, engine='c', sep=',', usecols=[3,4,5,6])

        first_date = df[3][0][1:]
        self.data_start = convert_date_to_milliseconds(first_date, self.date_format_string)

        #Since the instrument is not reliably recording data at 4hz we have decided to
        #interpolate the data to avoid any potential complications in future data analysis
        original_dates = [(x * 1000) + self.data_start for x in df[4]]
        instrument_pressure = [x / 1.45037738 for x in df[5]]

        self.utc_millisecond_data = convert_to_milliseconds(df.shape[0] - 1, \
                                                            ('%s' % (df[3][0][1:])), \
                                                            self.date_format_string, self.frequency)

        self.pressure_data = np.interp(self.utc_millisecond_data, original_dates, instrument_pressure)

        if re.match('^[0-9]{1,3}.[0-9]+$', str(df[6][0])):
            self.temperature_data = [x for x in df[6]]

        print(len(self.pressure_data))

    def read_start(self, expression, delimeter):
        skip_index = 0;
        with open(self.in_filename,'r') as fileText:
            for x in fileText:
                file_string = x.split(delimeter)[0]
                if re.match(expression, file_string):
                    print('Success! Index %s' % skip_index)
                    break
                skip_index += 1
        return skip_index

    def write(self, sea_pressure = True):
        '''Write netCDF files

        sea_pressure - if true write sea_pressure data, otherwise write air_pressure data'''

        if sea_pressure == False:
            self.vstore.pressure_name = "air_pressure"
            self.vstore.pressure_var['standard_name'] = "air_pressure"

        self.vstore.pressure_data = self.pressure_data
        self.vstore.utc_millisecond_data = self.utc_millisecond_data
        self.vstore.latitude = self.latitude
        self.vstore.longitude = self.longitude

        #Tests#
        self.data_tests.interpolated_data = True
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')

        self.write_netCDF(self.vstore, len(self.pressure_data))
 
epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
       
def convert_to_milliseconds(series_length, datestring, date_format_string, frequency,date_seconds = None):
        if date_seconds == None:
            return  np.arange(series_length, dtype='int64') * (1000 / frequency)\
                + convert_date_to_milliseconds(datestring,date_format_string)
        else:
            return  np.arange(series_length, dtype='int64') * (1000 / frequency)\
                + date_seconds



def convert_date_to_milliseconds(datestring, date_format_string, date_time = None):
        if date_time == None:
            first_date = pytz.utc.localize(datetime.strptime(datestring, date_format_string))
            return (first_date - epoch_start).total_seconds() * 1000
        else:
            #pandas index will not take a long so I cannot multiply by 1000
            first_date = date_time
            return (first_date - epoch_start).total_seconds()
        
def convert_milliseconds_to_datetime(milliseconds, tzinfo):
        date = datetime.fromtimestamp(milliseconds / 1000, tzinfo)
        final_date = date.strftime('%Y-%m-%dT%H:%M:%SZ')
        return final_date
    
def get_time_duration(seconds_difference):

        days = int((((seconds_difference / 1000) / 60) / 60) / 24)
        hours =  int((((seconds_difference / 1000) / 60) / 60) % 24)
        minutes =  int(((seconds_difference / 1000) / 60)  % 60)
        seconds = (seconds_difference / 1000) % 60

        data_duration_time = "P%sDT%sH%sM%sS" % (days, hours, minutes, seconds)
        print(data_duration_time)
        return data_duration_time


import uuid

class DataStore(object):
    '''Use this as an abstract data store, then pass a netcdf write stream to send data method'''
    def __init__(self, grouping):
        self.utc_millisecond_data = None
        self.data_start_date = None
        self.data_end_date = None
        self.data_duration = None
        self.pressure_data = None
        self.pressure_qc_data = None
        self.pressure_range = [-1000,1000]
        self.pressure_name = None
        self.temperature_data = None
        self.temperature_qc_data = None
        self.temperature_range = [-20,50]
        self.z_data = 0
        self.z_qc_data = None
        self.z_range = [-1000,1000]
        self.z_name = None
        self.latitude = 0
        self.latitude_range = [-90,90]
        self.longitude = 0
        self.longitude_range = [-180,180]
        self.z = 0
        self.salinity = 35
        self.data_grouping = grouping
        self.epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
        self.fill_value = np.float64(-1.0e+10)
        self.instrument_var = { 'long_name': 'Attributes for instrument 1',
                                'make_model': '',
                                'serial_number': '',
                                'calibration_date': '',
                                'factory_calibration': '',
                                'user_calibrated': '',
                                'calibration_report': '',
                                'accuracy': '',
                                'valid_range': [0,1],
                                'precision': '',
                                'comment': '',
                                'ancillary_variables': ''}
        self.time_var = {
                        'long_name': 'Time',
                        'short_name': 'time',
                        'standard_name': "time",
                        'units': "milliseconds since " + self.epoch_start.strftime("%Y-%m-%d %H:%M:%S"),
                        'calendar': "Gregorian",
                        'axis': 'T',
                        'ancillary_variables': '',
                        'comment': "",
                        'ioos_category': "Time",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time"}
        self.lon_var = {
                        'long_name': "longitude of sensor",
                        'standard_name': "longitude",
                        'short_name': 'longitude',
                        'units': "degrees",
                        'axis': 'X',
                        'valid_min': self.longitude,
                        'valid_max': self.longitude,
                        'ancillary_variables': '',
                        'comment': "longitude 0 equals prime meridian",
                        'ioos_category': "Location",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time",
                        }
        self.lat_var = {
                        'long_name': "latitude of sensor",
                        'standard_name': "latitude",
                        'short_name': 'latitude',
                        'units': "degrees",
                        'axis': 'Y',
                        'valid_min': self.latitude,
                        'valid_max': self.latitude,
                        'ancillary_variables': '',
                        'comment': "latitude 0 equals equator",
                        'ioos_category': "Location",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time",
                        }
        self.z_var = {
                        'long_name': "altitude of sensor",
                        'standard_name': "altitude",
                        'short_name': 'altitude',
                        'units': "degrees",
                        'axis': 'Z',
                        'valid_min': self.z_range[0],
                        'valid_max': self.z_range[1],
                        'ancillary_variables': '',
                        'comment': "altitude of instrument",
                        'ioos_category': "Location",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time",
                      }
        self.z_var_qc = {
                                  'flag_masks': '11111111 11111110 11111101 11111011 11110111',
                                'flag_meanings': "no_bad_data last_five_vals_identical, outside_valid_range, invalid_rate_of_change, interpolated_data",
                                'comment': '1 signifies the value passed the test while a 0 flags a failed test, leading 1 is a placeholder'
                                }
        self.pressure_var = {
                             'long_name': "sensor pressure record",
                             'standard_name': "sea_water_pressure",
                             'short_name': "pressure",
                             'nodc_name': "pressure".upper(),
                             'units': "decibar",
                             'scale_factor': np.float32(1.0),
                             'add_offset': np.float32(0.0),
                             'compression': "not used at this time",
                             'min': self.pressure_range[0],
                             'max': self.pressure_range[1],
                             'ancillary_variables': '',
                             'coordinates': "time latitude longitude altitude",
                             'ioos_category': "Pressure",
                             'comment': "",
                             }
        self.pressure_var_qc = {
                                 'flag_masks': '11111111 11111110 11111101 11111011 11110111',
                                'flag_meanings': "no_bad_data last_five_vals_identical, outside_valid_range, invalid_rate_of_change, interpolated_data",
                                 'comment': '1 signifies the value passed the test while a 0 flags a failed test, leading 1 is a placeholder'
                                }
        self.temp_var= {
                             'long_name': "sensor temperature record",
                             'standard_name': "temperature",
                             'short_name': "temp",
                             'nodc_name': "temperature".upper(),
                             'units': "degree_Celsius",
                             'scale_factor': np.float32(1.0),
                             'add_offset': np.float32(0.0),
                             'compression': "not used at this time",
                             'min': self.temperature_range[0],
                             'max': self.temperature_range[1],
                             'ancillary_variables': '',
                             'coordinates': "time latitude longitude altitude",
                             'ioos_category': "Temperature",
                             'comment': "",
                             }
        self.temp_var_qc = {
                              'flag_masks': '11111111 11111110 11111101 11111011 11110111',
                                'flag_meanings': "no_bad_data last_five_vals_identical, outside_valid_range, invalid_rate_of_change, interpolated_data",
                             'comment': '1 signifies the value passed the test while a 0 flags a failed test, leading 1 is a placeholder'
                            }

        self.global_vars_dict = {"cdm_data_type": "station",
                                 "comment": "not used at this time",
                                 "contributor_name": "USGS",
                                 "contributor_role": "data collector",
                                 "Conventions": "CF-1.6",
                                 "creator_email": "gui email",
                                 "creator_name": "gui name",
                                 "creator_url": "gui url",
                                 "date_created": datetime.strftime(datetime.now(tz=pytz.utc), "%Y-%m-%dT%H:%M:%SZ"),
                                 "date_modified": datetime.strftime(datetime.now(tz=pytz.utc), "%Y-%m-%dT%H:%M:%SZ"),
                                 "geospatial_lat_min": self.latitude_range[0],
                                 "geospatial_lat_max": self.latitude_range[1],
                                 "geospatial_lon_min": self.longitude_range[0],
                                 "geospatial_lon_max": self.longitude_range[1],
                                 "geospatial_lat_units": "degrees_north",
                                 "geospatial_lat_resolution": "point",
                                 "geospatial_lon_units": "degrees_east",
                                 "geospatial_lon_resolution": "point",
                                 "geospatial_vertical_min": self.z,
                                 "geospatial_vertical_max": self.z,
                                 "geospatial_vertical_units": "meters",
                                 "geospatial_vertical_resolution": "point",
                                 "geospatial_vertical_positive": "up",
                                 "history": "not used at this time",
                                 "id": "not used at this time",
                                 "institution": "USGS",
                                 "keywords": "not used at this time",
                                 "keywords_vocabulary": "not used at this time",
                                 "license": "",
                                 "Metadata_Conventions": "Unidata Dataset Discovery v1.0",
                                 "metadata_link": "http://54.243.149.253/home/webmap/viewer.html?webmap=c07fae08c20c4117bdb8e92e3239837e",
                                 "naming_authority": "not used at this time",
                                 "processing_level": "deferred with intention to implement",
                                 "project": "deferred with intention to implement",
                                 "publisher_email": "deferred with intention to implement",
                                 "publisher_name": "deferred with intention to implement",
                                 "publisher_url": "deferred with intention to implement",
                                 "readme": "file created by "+ "gui creator " +str(datetime.now()),
                                 "salinity_ppm": self.salinity,
                                 "sea_name": "gui sea name",
                                 #add another variable to work with Marie's system will follow up with her
                                 "standard_name_vocabulary": "CF-1.6",
                                 "summary": "This is data collected by a pressure instrument used for extrapolating information regarding weather patterns",
                                 "time_coverage_start": "utilitiy coverage start",
                                 "time_coverage_end": "utility coverage end",
                                 "time_coverage_duration": "utility coverage duration",
                                 "time_coverage_resolution": "P0.25S",
                                 # "time_of_deployment": None,
                                 # "time_of_retrieval": None,
                                 "time_zone": "UTC",
#                                  "title": 'Measure of pressure at %s degrees latitude, %s degrees longitude' \
#                                  ' from the date range of %s to %s' % (self.latitude, self.longitude,self.creator_name, \
#                                                                        self.data_start_date, self.data_end_date),
                                 "uuid": str(uuid.uuid4())
                                 }
    def send_data(self,ds):
        self.get_time_var(ds)
        self.get_pressure_var(ds)
        self.get_pressure_qc_var(ds)
        if self.temperature_data != None:
            self.get_temp_var(ds)

        if type(self.z_data) != list:
            self.get_z_var(ds, False)
        else:
            self.get_z_var(ds, True)
            self.get_z_qc_var(ds)
        self.get_lat_var(ds)
        self.get_lon_var(ds)
        self.get_time_duration()
        self.get_global_vars(ds)

    def get_instrument_var(self,ds):
        instrument = ds.createVariable("instrument","i4")
        for x in self.instrument_var:
            instrument.setncattr(x,self.instrument_var[x])

    def get_time_var(self,ds):
        time = ds.createVariable("time","f8",("time",))
        for x in self.time_var:
            time.setncattr(x,self.time_var[x])
        time[:] = self.utc_millisecond_data

    def get_lat_var(self,ds):
        lat = ds.createVariable("latitude","f8",fill_value=self.fill_value)
        for x in self.lat_var:
            lat.setncattr(x,self.lat_var[x])
        lat[:] = self.latitude

    def get_lon_var(self,ds):
        lon = ds.createVariable("longitude","f8",fill_value=self.fill_value)
        for x in self.lon_var:
            lon.setncattr(x,self.lon_var[x])
        lon[:] = self.longitude

    def get_z_var(self,ds,time_dimen_bool = False):
        if time_dimen_bool == False:
            z = ds.createVariable("altitude", "f8",
                                  fill_value=self.fill_value)
        else:
            z = ds.createVariable("altitude", "f8",("time",),
                                  fill_value=self.fill_value)
        for x in self.z_var:
            z.setncattr(x,self.z_var[x])
        z[:] = self.z_data

    def get_z_qc_var(self,ds):
        if self.z_name != None:
            z_qc = ds.createVariable(self.z_name,'i4',('time'))
        else:
            z_qc = ds.createVariable("altitude_qc",'i4',('time'))
        for x in self.z_var_qc:
            z_qc.setncattr(x,self.z_var_qc[x])
        z_qc[:] = self.z_qc_data

    def get_pressure_var(self,ds):
        if self.pressure_name != None:
            pressure = ds.createVariable(self.pressure_name,"f8",("time",))
        else:
            pressure = ds.createVariable("sea_water_pressure","f8",("time",))
        for x in self.pressure_var:
            pressure.setncattr(x,self.pressure_var[x])
        pressure[:] = self.pressure_data

    def get_pressure_qc_var(self,ds):
        pressure_qc = ds.createVariable("pressure_qc",'i4',('time'))
        for x in self.pressure_var_qc:
            pressure_qc.setncattr(x,self.pressure_var_qc[x])
        pressure_qc[:] = self.pressure_qc_data

    def get_temperature_var(self,ds):
        temperature = ds.createVariable("temperature_at_transducer","f8", ("time",))
        for x in self.temperature_var:
            temperature.setncattr(x,self.temp_var[x])
        temperature[:] = self.temperature_data

    def get_temperature_qc_var(self,ds):
        temperature_qc = ds.createVariable("temperature_qc",'i4',('time'))
        for x in self.temp_var_qc:
            temperature_qc.setncattr(x,self.temp_var_qc[x])
        temperature_qc[:] = self.temperature_qc_data

    def get_global_vars(self, ds):
        for x in self.global_vars_dict:
            if self.global_vars_dict[x] is not None:
                ds.setncattr(x,self.global_vars_dict[x])

    def get_time_duration(self):
        first_milli = self.utc_millisecond_data[0]
        second_milli = self.utc_millisecond_data[-1]
        self.global_vars_dict["time_coverage_start"] = \
        convert_milliseconds_to_datetime(first_milli, pytz.utc)

        self.global_vars_dict["time_coverage_end"] = \
        convert_milliseconds_to_datetime(second_milli, pytz.utc)

        self.global_vars_dict["time_coverage_duration"] = \
        get_time_duration(second_milli - first_milli)

        self.global_vars_dict['title'] = 'Measure of pressure at %s degrees latitude, %s degrees longitude  by %s' \
        ' from the date range of %s to %s' % (self.latitude, self.longitude, self.global_vars_dict["creator_name"], \
                                                  self.global_vars_dict["time_coverage_start"], \
                                                  self.global_vars_dict["time_coverage_end"])

    def set_attributes(self, var_dict):
        """Sets attributes in script

        var_dict -- key- attr name value- attr value"""

        for x in var_dict:
            for y in var_dict[x]:
                var1 = self.__dict__[x]
                var1[y] = var_dict[x][y]
        
sys.path.append('..')

class DataTests(object):
    """QC tests are performed on any data written to a netcdf file"""
     
    def __init__(self):
        self.five_count_list = list()
        self.pressure_data = None
        self.valid_pressure_range = [-1000,1000]
        self.pressure_max_rate_of_change = 10
        self.depth_data = None
        self.valid_depth_range = [-1000,1000]
        self.depth_max_rate_of_change = 20
        self.temperature_data = None
        self.valid_temperature_range = [-20,50]
        self.temperature_max_rate_of_change = None
        self.prev_value = np.NaN
        self.interpolated_data = False
        
       
    def select_tests(self, data_selection):
        '''Runs all of the netcdf Tests on the selected data, then performs an or binary mask (and) for
        those that passed, 1 for pass 0 for fail, and returns an unisgned 4bit integer, leading 1 is just a placeholder'''  
        
        if data_selection == 'depth':
            return self.run_tests(self.depth_data, self.valid_depth_range, self.depth_max_rate_of_change)
        elif data_selection == 'temperature':
            return self.run_tests(self.temperature_data, self.valid_temperature_range \
                                  , self.temperature_max_rate_of_change)
        else:
            return self.run_tests(self.pressure_data, self.valid_pressure_range, \
                                   self.pressure_max_rate_of_change)
        
  
    def run_tests(self, data, data_range, rate_of_change):
        """Runs all of the data tests"""
        
        bit_array1 = [self.get_1_value(x) for x in data]
        bit_array2 = [self.get_2_value(x, data_range) for x in data]
        bit_array3 = [self.get_3_value(x, rate_of_change) for x in data]
        if self.interpolated_data == True:
            bit_array4 = [bit('11110111') for x in data]
            bit_array4[0] = bit('11111111')
         
        else:
            bit_array4 = [bit('11111111') for x in data]
       
       
        final_bits = [bit_array1[x] & bit_array2[x] & bit_array3[x] & bit_array4[x]
                       for x in range(0,len(data))]
        
        return [x.to01() for x in final_bits]
    
   
    def get_1_value(self,x):
        """Checks to see if the sensor recorded 5 identical measurements previous the the current measurement, if so
        indicate an issue with a zero in the 1 bit"""
           
        if len(self.five_count_list) > 5:
            self.five_count_list.pop()
            
        flags = np.count_nonzero(np.equal(x,self.five_count_list))
        self.five_count_list.insert(0,x)
        
        if flags <= 4:
            return bit('11111111')
        else:
            return bit('11111110')  
            
    def get_2_value(self, x, data_range):
        '''Checks if the data point is within a valid range'''
        
        if np.greater_equal(x,data_range[0]) and \
        np.less_equal(x,data_range[1]):
            return bit('11111111')
        else:
            return bit('11111101')
        
    def get_3_value(self, x, rate_of_change):
        '''Checks to see if rate of change is within valid range'''
        
        if np.isnan(self.prev_value) or \
        np.less_equal(np.abs(np.subtract(x,self.prev_value)), rate_of_change):
            self.prev_value = x
            return bit('11111111')
        else:
            self.prev_value = x
            return bit('11111011')
                        
INSTRUMENTS = {
    'LevelTroll': Leveltroll,
    # 'RBRSolo': RBRSolo,
    # 'Wave Guage': Waveguage,
    # 'USGS Homebrew': House,
    'Measurement Specialties': MeasureSysLogger,
    'HOBO': Hobo }

def make_frame(frame, header=None):
    """Make a frame with uniform padding."""
    return ttk.Frame(frame, padding="3 3 5 5")


def add_button(frame, text, command, row, column):
    """Make and grid a button in a uniform way."""
    b = ttk.Button(frame, text=text, command=command, width=15)
    b.grid(column=column, row=row, sticky='w')
    return b


def make_buttonbox(frame, buttonlist):
    """Expects button tuples: (text, command, row, column)"""
    box = make_frame(frame)
    for b in buttonlist:
        text, command, row, column = b
        add_button(box, text, command, row, column)
    box.pack(fill='both', expand=1)
    return box


def add_label(frame, text, pos=None):
    """Make a label and pack/grid it"""
    label = ttk.Label(frame, text=text)
    if pos:
        row, column = pos
        label.grid(column=column, row=row, sticky='w')
    else:
        label.pack(fill='both', expand=1)
    return label


class MessageDialog(tkinter.Toplevel):
    """ A template for nice dialog boxes. """

    def __init__(self, parent, message="", title="", buttons=1,
                 wait=True):
        tkinter.Toplevel.__init__(self, parent)
        body = ttk.Frame(self)
        self.title(title)
        self.boolean = None
        self.parent = parent
        self.transient(parent)
        ttk.Label(body, text=message).pack()
        if buttons == 1:
            b = ttk.Button(body, text="OK", command=self.destroy)
            b.pack(pady=5)
        elif buttons == 2:
            buttonframe = make_frame(body)

            def event(boolean):
                self.boolean = boolean
                self.destroy()

            b1 = ttk.Button(buttonframe, text='YES',
                            command=lambda: event(True))
            b1.grid(row=0, column=0)
            b2 = ttk.Button(buttonframe, text='NO',
                            command=lambda: event(False))
            b2.grid(row=0, column=1)
            buttonframe.pack()

        body.pack()
        self.grab_set()
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        if wait:
            self.wait_window(self)


class Variable:
    """
    Stores data about each attribute to be added to the netCDF file.

    Also contains metadata that allows the GUI to build widgets from
    the Variable and use the data inside it in the csv-to-netCDF
    converters.
    """
    def __init__(self, name_in_device=None, label=None, doc=None,
                 options=None, filename=False, autosave=False,
                 in_air_pressure=True, in_water_pressure=True):
        self.name_in_device = name_in_device
        self.label = label
        self.doc = doc
        self.options = options
        self.stringvar = tkinter.StringVar()
        self.stringvar.set('')
        self.filename = filename
        self.autosave = autosave
        self.in_air_pressure = in_air_pressure
        self.in_water_pressure = in_water_pressure
        
g = 9.8  # gravity (m / s**2)
rho = 1030  # density of seawater (kg / m**3)


def combo_method(t,p,z,H,timestep):
    fill = FILL_VALUE
    f = (p==fill)
    idx = np.where(f[1:] ^ f[:-1])[0] + 1
    tchunk = np.split(t, idx)
    pchunk = np.split(p, idx)
    Hchunk = np.split(H, idx)
    dchunks = []
    tchunks = []
    for pc, tc, Hc in zip(pchunk, tchunk, Hchunk):
        if pc[0] == fill:
            dchunks.append(pc)
            continue
        dc = combo_backend(tc,pc,z,Hc,timestep)
        dchunks.append(dc)
    return np.concatenate(dchunks)


def combo_backend(t, p_dbar, z, H, timestep, window_func=np.hamming):
    coeff = np.polyfit(t, p_dbar, 1)
    static_p = coeff[1] + coeff[0]*t
    static_y = hydrostatic_method(static_p)
    wave_p = p_dbar - static_p
    cutoff = auto_cutoff(np.average(H))
    wave_y = fft_method(wave_p, z, H, timestep, hi_cut=cutoff,
                        window_func=window_func)
    wave_y = np.pad(wave_y, (0, len(t) - len(wave_y)), mode='edge')
    return static_y + wave_y


def hydrostatic_method(pressure):
    """Return the depth corresponding to a hydrostatic pressure."""
    return (pressure *  1e4) / (rho * g)


def auto_cutoff(h):
    return .9/np.sqrt(h)


def trim_to_even(seq):
    """Trim a sequence to make it have an even number of elements"""
    if len(seq) % 2 == 0:
        return seq
    else:
        return seq[:-1]

def omega_to_k(omega, H):
    k = np.arange(0, 10, .01)
    w = k_to_omega(k, H)
    deg = 10
    p = np.polyfit(w, k, deg)
    return sum(p[i] * omega**(deg - i) for i in range(deg + 1))


def fft_method(p_dbar, z, H, timestep, gate=0, window_func=np.ones,
               lo_cut=-1, hi_cut=float('inf')):
    """Create wave height data from an array of pressure readings.

    WARNING: FFT will truncate the last element of an array if it has
    an odd number of elements!
    """
    H = np.average(H)
    p_dbar = trim_to_even(p_dbar)
    n = len(p_dbar)
    window = window_func(n)
    scaled_p = p_dbar[:n] * 1e4 * window  # scale by the window

    p_amps = np.fft.rfft(scaled_p)
    freqs = np.fft.rfftfreq(n, d=timestep)
    k = omega_to_k(2 * np.pi * freqs, H)
    d_amps = pressure_to_eta(p_amps, k, z, H)
    d_amps[np.where((freqs <= lo_cut) | (freqs >= hi_cut))] = 0

    eta = np.fft.irfft(d_amps) # reverse FFT
    if window_func:
        eta = eta / window
    return eta


def _frequency_to_index(f, n, timestep):
    """
    Gets the index of a frequency in np.fftfreq.

    f -- the desired frequency
    n -- the length given to fftfreq
    sample_freq -- the sampling frequency
    """
    return np.round(n * f * timestep)


def binary_search(func, x1, x2, tol):
    y1 = func(x1)
    y2 = func(x2)
    x_mid = (x1 + x2) / 2
    y_mid = func(x_mid)
    if abs(y_mid) < tol:
        return x_mid
    elif y1 * y_mid < 0:
        return binary_search(func, x1, x_mid, tol)
    elif y_mid * y2 < 0:
        return binary_search(func, x_mid, x2, tol)
    else:
        print('Binary root finder failed to find a root!')


def k_to_omega(k, H):
    """Takes the wave number and water depth as arguments, returns the
    angular frequency."""
    return np.sqrt(k * g * np.tanh(k * H))


def pressure_to_eta(del_p, k, z, H):
    """Convert the non-hydrostatic pressure to height above z=0."""
    c = _coefficient(k, z, H)
    return del_p / c


def eta_to_pressure(eta, k, z, H):
    """Convert wave height to pressure using linear wave theory."""
    c = _coefficient(k, z, H)
    return eta * c


def _coefficient(k, z, H):
    """Return a conversion factor for pressure and wave height."""
    return rho * g * np.cosh(k * (H + z)) / np.cosh(k * H)



# def print_rmse(y, static_y, fft_y):
#     fft_rmse = rmse(fft_y, y)
#     static_rmse = rmse(static_y, y)
# 
#     print('FFT RMSE = %.4f meters' % fft_rmse)
#     print('Static RMSE = %.4f meters' % static_rmse)
# 
#     if static_rmse < fft_rmse:
#         print("""STATIC IS DOING BETTER
#     SOMETHING IS HORRIBLY WRONG""")

def make_waves(length, sample_frequency, waves, h, z):
    """Create wave pressure given frequencies, amplitudes and phases"""
    t = np.arange(length, step=1/sample_frequency)
    total_height = np.zeros_like(t)
    total_pressure = np.zeros_like(t)
    h = np.average(h)
    for wave in waves:
        f = wave[0]
        a = wave[1]
        phi = wave[2]
        eta = a*np.sin(2*np.pi*f*t + phi)
        total_height += eta
        k = omega_to_k(2 * np.pi * f, h)
        pressure = eta*rho*g*np.cosh(k*(z + h))/np.cosh(k*h)
        total_pressure += pressure
    c = random.rand()*20
    total_height += c*arange(len(total_height)) / len(total_height)
    total_pressure += rho*g*c * arange(len(total_height)) / len(total_height)
    return t, total_height, total_pressure

def random_waves(length, sample_frequency, h, z, max_f, max_a, n):
    waves = np.array([[max_f, max_a, 2*np.pi]]*n)*random.rand(n, 3)
    return make_waves(length, sample_frequency, waves, h, z)

def easy_waves(length, h, z, n):
    return random_waves(length, 4, h, z, .2, z/4, n)
    





if __name__ == '__main__':
    root = Tk()
    g2 = Script2gui(root)
    root.mainloop()
