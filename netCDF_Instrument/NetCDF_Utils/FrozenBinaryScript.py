"""This class contains all the files necessary for cx freeze to package everything in to an 
executable file for windows -- will update shortly 8-6-2014"""

#!/usr/bin/env python3
import matplotlib
matplotlib.use('TkAgg')
import collections
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import numpy as np
import time
import time
import sys
from datetime import datetime
import pytz
import pandas
import re
import netCDF4
import netCDF4_utils
import netcdftime
import re
import sys
sys.path.append('..')

'''
Created on Jun 20, 2014

@author: Gregory
'''

#--python 3 compatibility
pyver = sys.version_info
if pyver[0] == 3:
    raw_input = input

class Sensor(object):
    '''super class for reading raw wave data and writing to netcdf file
    this class should not be instantiated directly
    '''
    
    def __init__(self):
        self.in_filename = None
        self.out_filename = None
        self.is_baro = None
        self.pressure_units = None
        self.z_units = 'meters'
        self.latitude = None
        self.longitude = None
        self.z = None
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
        self.data_start_date = None
        self.data_end_date = None
        self.data_duration_time = None

        self.valid_pressure_units = ["psi","pascals","atm"]
        self.valid_latitude = (np.float32(-90),np.float32(90))
        self.valid_longitude = (np.float32(-180),np.float32(180))
        self.valid_z = (np.float32(-10000),np.float32(10000))
        self.valid_salinity = (np.float32(0.0),np.float32(40000))
        self.valid_pressure = (np.float32(-10000),np.float32(10000))

        self.fill_value = np.float32(-1.0e+10)
        self.creator_name = None
        
        self.pressure_test16_data = None
        self.pressure_test17_data = None
        self.pressure_test20_data = None
        
    
    def convert_to_milliseconds(self, series_length, datestring):
        return  np.arange(series_length, dtype='int64') * (1000 / self.frequency)\
          + self.convert_date_to_milliseconds(datestring)
            
    
    def convert_date_to_milliseconds(self, datestring):
        first_date = pytz.utc.localize(datetime.strptime(datestring, self.date_format_string))
        self.data_start_date = datetime.strftime(first_date, "%Y-%m-%dT%H:%M:%SZ")
        print(self.data_start_date)
        return (first_date - self.epoch_start).total_seconds() * 1000
    
    def convert_milliseconds_to_datetime(self, milliseconds):
        date = datetime.fromtimestamp(milliseconds / 1000)
        new_dt = self.tz_info.localize(date)
        final_date = new_dt.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        print('lastdate',final_date)
        return(final_date)
        
    def get_time_duration(self, seconds_difference):
      
        days = int((((seconds_difference / 1000) / 60) / 60) / 24)
        hours =  int((((seconds_difference / 1000) / 60) / 60) % 24)
        minutes =  int(((seconds_difference / 1000) / 60)  % 60)
        seconds = (seconds_difference / 1000) % 60
         
        self.data_duration_time = "P%sDT%sH%sM%sS" % (days, hours, minutes, seconds)
        print(self.data_duration_time)

    def time_var(self,ds):
        time_var = ds.createVariable("time","f8",("time",))
        time_var.long_name = ''
        time_var.standard_name = "time"
        time_var.units = "milliseconds since "+self.epoch_start.strftime("%Y-%m-%d %H:%M:%S")
        time_var.calendar = "gregorian"
        time_var.axis = 't'
        time_var.ancillary_variables = ''        
        time_var.comment = "Original time zone: "+str(self.timezone_string)
        time_var[:] = self.utc_millisecond_data
        return time_var

    
    def longitude_var(self,ds):
        longitude_var = ds.createVariable("longitude","f4",fill_value=self.fill_value)
        longitude_var.long_name = "longitude of sensor"
        longitude_var.standard_name = "longitude"
        longitude_var.units = "degrees east"
        longitude_var.axis = 'X'
        longitude_var.min = self.valid_longitude[0]
        longitude_var.max = self.valid_longitude[1]        
        longitude_var.ancillary_variables = ''
        longitude_var.comment = "longitude 0 equals prime meridian"
        longitude_var[:] = self.longitude
        return longitude_var


    def latitude_var(self,ds):
        latitude_var = ds.createVariable("latitude","f4",fill_value=self.fill_value)
        latitude_var.long_name = "latitude of sensor"
        latitude_var.standard_name = "latitude"
        latitude_var.units = "degrees north"
        latitude_var.axis = 'Y'
        latitude_var.min = self.valid_latitude[0]
        latitude_var.max = self.valid_latitude[1]        
        latitude_var.ancillary_variables = ''
        latitude_var.comment = "latitude 0 equals equator"        
        latitude_var[:] = self.latitude
        return latitude_var


    def z_var(self,ds):    
        z_var = ds.createVariable("altitude","f4",fill_value=self.fill_value)
        z_var.long_name = "altitude of sensor"
        z_var.standard_name = "altitude"    
        z_var.units = self.z_units
        z_var.axis = 'Z'
        z_var.min = self.valid_z[0]
        z_var.max = self.valid_z[1]        
        z_var.ancillary_variables = ''
        z_var.comment = "altitude above NAVD88"
        z_var[:] = self.z
        return z_var


    def pressure_var(self,ds):
        pressure_var = ds.createVariable("pressure","f8",("time",),fill_value=self.fill_value)#fill_value is the default
        pressure_var.long_name = "sensor pressure record"
        pressure_var.standard_name = "pressure"    
        pressure_var.nodc_name = "pressure".upper()    
        pressure_var.units = self.pressure_units
        pressure_var.scale_factor = np.float32(1.0)
        pressure_var.add_offset = np.float32(0.0)        
        pressure_var.min = self.valid_pressure[0]
        pressure_var.max = self.valid_pressure[1]        
        pressure_var.ancillary_variables = ''
        pressure_var.coordinates = "time latitude longitude z"
        pressure_var[:] = self.pressure_data
        return pressure_var
    
    def pressure_test16(self,ds):
        pressure_test16 = ds.createVariable("pressure_test16","b",("time",))
        pressure_test16[:] = self.pressure_test16_data
        return pressure_test16
    
    def pressure_test17(self,ds):
        pressure_test17 = ds.createVariable("pressure_test17","b",("time",))
        pressure_test17[:] = self.pressure_test17_data
        return pressure_test17
    
    def pressure_test20(self,ds):
        pressure_test20 = ds.createVariable("pressure_test20","b",("time",))
        pressure_test20[:] = self.pressure_test20_data
        return pressure_test20
    
    
    def write(self):
        #assert not os.path.exists(self.out_filename),"out_filename already exists"
        #--create variables and assign data
        ds = netCDF4.Dataset(self.out_filename,'w',format="NETCDF4_CLASSIC")
        time_dimen = ds.createDimension("time",len(self.pressure_data))   
        time_var = self.time_var(ds)
        latitude_var = self.latitude_var(ds)
        longitude_var = self.longitude_var(ds)
        z_var = self.z_var(ds)
        pressure_var = self.pressure_var(ds)
        pressure_test16 = self.pressure_test16(ds)
        pressure_test17 = self.pressure_test17(ds)
        pressure_test20 = self.pressure_test20(ds)
        ds.salinity_ppm = np.float32(self.salinity_ppm)        
        ds.time_zone = "UTC"
        ds.readme = "file created by "+sys.argv[0]+" on "+str(datetime.now())+" from source file "+self.in_filename
        ds.cdm_data_type = "station"
        ds.comment = "not used at this time"
        ds.contributor_name = "USGS"
        ds.contributor_role = "data collector"
        ds.creator_email = self.creator_email
        ds.creator_name = self.creator_name
        ds.creator_url = self.creator_url
        ds.date_created = datetime.strftime(datetime.now(tz=pytz.utc), "%Y-%m-%dT%H:%M:%SZ")
        ds.date_modified = datetime.strftime(datetime.now(tz=pytz.utc), "%Y-%m-%dT%H:%M:%SZ")
        ds.geospatial_lat_min = self.latitude
        ds.geospatial_lat_max = self.latitude
        ds.geospatial_lon_min = self.longitude
        ds.geospatial_lon_max = self.longitude
        ds.geospatial_lat_units = "degrees_north"
        ds.geospatial_lat_resolution = "point"
        ds.geospatial_lon_units = "degrees_east"
        ds.geospatial_lon_resolution = "point"
        ds.geospatial_vertical_min = self.z
        ds.geospatial_vertical_max = self.z
        ds.geospatial_vertical_units = "meters"
        ds.geospatial_vertical_resolution = "point"
        ds.geospatial_vertical_positive = "up"
        ds.history = "not used at this time"
        ds.id = "not used at this time"
        ds.institution = "USGS"
        # ds.keywords = TBD
        ds.keywords_vocabulary = "not used at this time"
        ds.license = "This data may only be used upon the consent of the USGS"
        ds.Metadata_Conventions = "Unidata Dataset Discovery v1.0"
        ds.metadata_link = "usgs.katrinamapperinfo.com"
        ds.naming_authority = "not used at this time"
        ds.processing_level = "deferred with intention to implement"
        ds.project = "deferred with intention to implement"
        ds.publisher_email = "deferred with intention to implement"
        ds.publisher_name = "deferred with intention to implement"
        ds.publisher_url = "deferred with intention to implement"
        ds.standard_name_vocabulary = "CF-1.6"
        ds.summary = "This is data collected by a pressure instrument used for extrapolating information regarding weather patterns"
        ds.time_coverage_start = self.data_start_date
        ds.time_coverage_end = self.data_end_date
        ds.time_coverage_duration = self.data_duration_time
        ds.time_coverage_resolution = "P0.25S"
        ds.title = 'Measure of pressure at %s degrees latitude, %s degrees longitude, %s altitude by %s' \
        ' from the date range of %s to %s' % (self.latitude, self.longitude, self.z,self.creator_name, \
                                                   self.data_start_date, self.data_end_date)
        print('done write')

    def read(self):
        raise Exception("read() must be implemented in the derived classes")
    
    def read_start(self):
        raise Exception("read_start() must be implemented in the derived classes")

'''
Created on Jul 8, 2014

@author: Gregory
'''


class PressureTests(object):
    
    pressure_data = None
    pressure_test16_data = None
    pressure_test17_data = None
    pressure_test20_data = None
    five_count_list = list() # for IOOS test 16
    local_frequency_range = [11, 19] # for IOOS test 17
    mfg_frequency_range = [10, 20] # for IOOS test 17
    max_rate_of_change = 20 # for IOOS test 20
    prev_value = True # for IOOS test 20
        
    def __init__(self):
        pass
        
    def test_16_stucksensor(self):
        self.pressure_test16_data = [self.get_16_value(x) for x in self.pressure_data]
        
    def test_17_frequencyrange(self):
        self.pressure_test17_data = [self.get_17_value(x) for x in self.pressure_data]
        
    def test_20_rateofchange(self):
        self.pressure_test20_data = [self.get_20_value(x) for x in self.pressure_data]
   
            
    def get_15_value(self):
        print('start mean')
        print('mean', np.mean(self.pressure_data))
        print('mean', np.mean(self.pressure_data))
        
               
    def get_16_value(self,x):
           
        if len(self.five_count_list) > 5:
            self.five_count_list.pop()
            
        flags = np.count_nonzero(np.equal(x,self.five_count_list))
        self.five_count_list.insert(0,x)
        
        if flags <= 2:
            return 1
        elif flags <= 4:
            return 3
        else:
            return 4  
            
    def get_17_value(self, x):
        
        if np.greater_equal(x,self.local_frequency_range[0]) and \
        np.less_equal(x,self.local_frequency_range[1]):
            return 1
        elif np.greater_equal(x,self.mfg_frequency_range[0]) and \
                            np.less_equal(x,self.mfg_frequency_range[1]):
            return 3
        else:
            return 4
        
    def get_20_value(self, x):
      
        if np.isnan(self.prev_value) or \
        np.less_equal(np.abs(np.subtract(x,self.prev_value)), self.max_rate_of_change):
            self.prev_value = x
            return 1
        else:
            self.prev_value = x
            return 4
    
    
'''
Created on Jul 7, 2014

@author: Gregory
'''
'''
Created on Jun 20, 2014

@author: Gregory
'''
     

class House(Sensor, PressureTests):
    '''derived class for house ascii files
    '''
    def __init__(self):
        self.timezone_marker = "time zone"   
        self.temperature_data = None   
        super(House,self).__init__()
        self.tz_info = pytz.timezone("US/Eastern")
        self.frequency = 4
       
        self.date_format_string = '%Y.%m.%d %H:%M:%S '
    

    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
       
        skip_index = self.read_start('^[0-9]{4},[0-9]{4}$',' ') 
        df = pandas.read_table(self.in_filename,skiprows=skip_index, header=None, engine='c', sep=',', names=('a','b'))
       
        self.pressure_data = [self.pressure_convert(np.float64(x)) for x in df[df.b.isnull() == False].a]
        self.temperature_data = [self.temperature_convert(np.float64(x)) for x in df[df.b.isnull() == False].b]
            
        with open(self.in_filename, 'r') as wavelog:
            for x in wavelog:
                if re.match('^[0-9]{4}.[0-9]{2}.[0-9]{2}', x):
                    self.utc_millisecond_data = self.convert_to_milliseconds(len(self.pressure_data), x) #second arg has extra space that is unnecessary
                    break
       
        self.data_end_date = self.convert_milliseconds_to_datetime(self.utc_millisecond_data[::-1][0])
        print('time', self.utc_millisecond_data[::-1][0], self.utc_millisecond_data[0])
        self.get_time_duration(self.utc_millisecond_data[::-1][0] - self.utc_millisecond_data[0])
        self.test_16_stucksensor()
        self.test_17_frequencyrange()
        self.test_20_rateofchange()
        self.get_15_value()
        
    def pressure_convert(self, x):
        print('item', x)
        return x * (30 / 8184) - 6
    
    def temperature_convert(self, x):
        return x * (168 / 8184)
        
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

          

class Leveltroll(Sensor, PressureTests):
    '''derived class for leveltroll ascii files
    '''
    def __init__(self):
        self.numpy_dtype = np.dtype([("seconds",np.float32),("pressure",np.float32)])
        self.record_start_marker = "date and time,seconds"
        self.timezone_marker = "time zone" 
        super(Leveltroll,self).__init__()
        
    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        f = open(self.in_filename,'rb')
        
        self.read_header(f)
        self.data_start = self.read_datetime(f)

        data = np.genfromtxt(f,dtype=self.numpy_dtype,delimiter=',',usecols=[1,2])     
        f.close()
        
        long_seconds = data["seconds"]
        self.utc_millisecond_data = (long_seconds + np.float64(self.offset_seconds)) * 1000

        self.pressure_data = data["pressure"]
        
        self.data_end_date = self.convert_milliseconds_to_datetime(self.utc_millisecond_data[::-1][0])
        self.get_time_duration(self.utc_millisecond_data[::-1][0] - self.utc_millisecond_data[0])
        self.test_16_stucksensor()
        self.test_17_frequencyrange()
        self.test_20_rateofchange()
        

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
        dt_converter = lambda x: datetime.strptime(str(x),dt_fmt)\
            .replace(tzinfo=self.tzinfo)
        reset_point = f.tell()  
        bit_line = f.readline()          
        line = bit_line.decode()  

        raw = line.strip().split(',')
        dt_str = raw[0]
        try:
            data_start = dt_converter(dt_str)
            self.data_start_date = datetime.strftime(data_start, "%Y-%m-%dT%H:%M:%SZ")
            print('Datetime', data_start, self.data_start_date)
        except Exception as e:
            raise Exception("ERROR - cannot parse first date time stamp: "+str(self.td_str)+" using format: "+dt_fmt+'\n')
        f.seek(reset_point)
        return data_start


    def set_timezone(self):
        '''set the timezone from the timezone string found in the header - 
        needed to get the times into UTC
        '''
        tz_dict = {"central":"US/Central","eastern":"US/Eastern"}
        for tz_str,tz in tz_dict.items():
            if self.timezone_string.lower().startswith(tz_str):
                self.tzinfo = pytz.timezone(tz)
                return               
        raise Exception("could not find a timezone match for " + self.timezone_string)  
    
    @property    
    def offset_seconds(self):
        '''offsets seconds from specified epoch using UTC time
        '''        
        offset = self.data_start - self.epoch_start            
        return offset.total_seconds()       

    
    

class RBRSolo(Sensor, PressureTests):
    '''derived class for leveltroll ascii files
    '''
    def __init__(self):
        self.timezone_marker = "time zone"      
        super(RBRSolo,self).__init__()
        
        self.tz_info = pytz.timezone("US/Eastern")
        self.frequency = 4
        self.date_format_string = '%d-%b-%Y %H:%M:%S.%f'  
        
    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        skip_index = self.read_start('^[0-9]{2}-[A-Z]{1}[a-z]{2,8}-[0-9]{4}$',' ')
        #for skipping lines in case there is calibration header data
        df= pandas.read_csv(self.in_filename,skiprows=skip_index, delim_whitespace=True, \
                            header=None, engine='c', usecols=[0,1,2])
        for x in df[0:1].itertuples():
            if x[0] == 0:
                self.utc_millisecond_data = self.convert_to_milliseconds(df.shape[0] - 1, \
                                                                         ('%s %s' % (x[1],x[2])))
                break
        
        self.pressure_data = [x[1] for x in df[2][:-1].iteritems()]
        self.data_end_date = self.convert_milliseconds_to_datetime(self.utc_millisecond_data[::-1][0])
        self.get_time_duration(self.utc_millisecond_data[::-1][0] - self.utc_millisecond_data[0])
        self.test_16_stucksensor()
        self.test_17_frequencyrange()
        self.test_20_rateofchange()
        self.get_15_value()
        
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


class Waveguage(Sensor, PressureTests):
    """Reads in an ASCII file output by a Waveguage pressure sensor
    from Ocean Sensor Systems Inc.

    This class reads in data from a plaintext output file into a
    pandas Dataframe. This is then translated into numpy ndarrays
    and written to a netCDF binary file."""

    def __init__(self):
        self.tz_info = pytz.timezone("US/Eastern")
        super(Waveguage, self).__init__()
       
    def read(self):
        """Sets start_time to a datetime object, utc_millisecond_data
        to a numpy array of dtype=int64 and pressure_data to a numpy
        array of dtype float64."""
        print(self.local_frequency_range[0])
        self.start_time = self.get_start_time()
        self.pressure_data = self.get_pressure_data()
        self.utc_millisecond_data = self.get_millisecond_data(self.pressure_data)
     
        #Test and utility methods
        self.data_end_date = self.convert_milliseconds_to_datetime(self.utc_millisecond_data[::-1][0])
        self.get_time_duration(self.utc_millisecond_data[::-1][0] - self.utc_millisecond_data[0])
        self.test_16_stucksensor()
        self.test_17_frequencyrange()
        self.test_20_rateofchange()
        self.get_15_value()

    def get_millisecond_data(self, pressure_data):
        """Generates the time data using the initial timestamp in the
        file and the length of the pressure data array."""
        
        offset = self.start_time - self.epoch_start
        offset_ms = 1000 * offset.total_seconds()
        self.frequency = self._get_frequency()
        return np.arange(pressure_data.shape[0], dtype='int64')\
            * (1000 / self.frequency) + offset_ms

    def _get_frequency(self):
        with open(self.in_filename) as f:
            line = f.readline()
        freq = int(line[25:27])
        return freq
    
    def get_start_time(self):
        """Returns the time that the device started reading as a
        datetime object."""
        
        with open(self.in_filename) as f:
            for i, line in enumerate(f):
                if i > 0 and line.startswith('Y'):
                    break
        date_string = line[:23]
        date_format = 'Y%y,M%m,D%d,H%H,M%M,S%S'
        start_time = datetime.strptime(date_string, date_format).replace(tzinfo=self.tzinfo)
        self.data_start_date = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        return start_time

    def get_pressure_data(self):
        """Reads the pressure data from the current file and returns
        it in a numpy array of dtype float64."""
        
        data = pandas.read_csv(self.in_filename, skiprows=20, header=None,
                          lineterminator=',', sep=',', engine='c',
                          names='p')
        data = data[:-1]
        data.p = [np.float64(string.strip()) for string in data.p]
        data_array = np.array(data.p, dtype='float64')
        return data_array
    


class Variable:

    def __init__(self, name_in_device=None, label=None,
                 docs=None, options=None, required=True,
                 filename=False, default_value='',
                 valtype=str):

        self.name_in_device = name_in_device
        self.label = label
        self.docs = docs
        self.options = options
        self.stringvar = StringVar()
        self.required = required
        self.filename = filename
        self.default_value = default_value
        self.stringvar.set(default_value)
        self.valtype = valtype

    def getvalue(self):

        val = self.stringvar.get()
        return self.valtype(val)

class Datafile:

    def __init__(self, filename, instruments):

        self.instruments = instruments
        self.fields = fields = collections.OrderedDict()
        fields['latitude'] = \
            Variable(name_in_device='latitude',
                     label='Latitude:',
                     valtype=np.float32)
        fields['longitude'] = \
            Variable(name_in_device='longitude',
                     label='Longitude:',
                     valtype=np.float32)
        fields['altitude'] = \
            Variable(name_in_device='z',
                     label='Altitude:',
                     docs="Altitude in meters with respect to the "\
                         " WGS 84 ellipsoid.", valtype=np.float32)
        fields['salinity'] = \
            Variable(name_in_device='salinity',
                     label='Salinity:', valtype=np.float32)
        fields['timezone'] = \
            Variable(name_in_device='tzinfo',
                     label='Timezone:',
                     options=("US/Central", "US/Eastern"),
                     valtype=pytz.timezone)
        fields['instrument'] = \
            Variable(options=self.instruments.keys(),
                     label='Instrument:')
        fields['pressure_units'] = \
            Variable(name_in_device='pressure_units',
                     label='Pressure units:',
                     options=("atm", "bar", "psi"))
        fields['in_filename'] = \
            Variable(name_in_device='in_filename',
                     label='Input filename:',
                     filename='in')
        fields['out_filename'] = \
            Variable(name_in_device='out_filename',
                     label='Output filename:',
                     filename='out')

        fields['in_filename'].stringvar.set(filename)
        fields['out_filename'].stringvar.set(filename + '.nc')

class Wavegui:
    """A graphical interface to the netCDF conversion program. Prompts
    the user for information about the wave sensor and converts a CSV
    file from the sensor to a properly formatted netCDF file.
    """

    def __init__(self, root):

        self.log_file = 'wavegui_log.txt'

        self.instruments = {'LevelTroll' : Leveltroll(),
                            'RBRSolo' : RBRSolo(),
                            'Wave Guage' : Waveguage(),
                            'USGS Homebrew' : House()}
 
        generic_sensor = Sensor()
        fill_value = str(generic_sensor.fill_value)

        # Contains attributes applicable to all files

        self.global_fields = global_fields = collections.OrderedDict()

        global_fields['username'] =\
            Variable(label='Your full name:',
                     name_in_device='creator_name')
        global_fields['email'] = \
            Variable(label='Your email address:',
                     name_in_device='creator_email')
        global_fields['url'] = \
            Variable(label='Your personal url:',
                     name_in_device='creator_url')
        global_fields['project'] = Variable(label='Project name:')

        self.root = root

        self.buttonframe = self.setup_buttonframe(root)

        self.mainframe = self.setup_mainframe(root, global_fields)

        for row, var in enumerate(global_fields.values()):
            self.make_widget(self.mainframe, var, row)


        self.bookframe = self.setup_bookframe(root)



        self.book = ttk.Notebook(self.bookframe)

        self.book.grid(column=0, row=0)

    def setup_mainframe(self, root, global_fields):

        mainframe = ttk.Frame(root, padding="3 3 12 12",
                              relief='groove')
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.title("USGS Wave Data")
        mainframe.bind('<Return>', self.process_file)
        return mainframe

    def setup_bookframe(self, root):

        bookframe = ttk.Frame(root, padding="3 3 12 12",
                              relief='groove')
        bookframe.grid(column=0, row=1, sticky=(N, W, E, S))
        return bookframe

    def setup_buttonframe(self, root):

        buttonframe = ttk.Frame(root, padding="3 3 12 12")

        b1 = ttk.Button(buttonframe, text="Process File(s)",
                        command=self.process_files)
        b1.grid(column=0, row=0)
        
        b2 = ttk.Button(buttonframe, text="Quit",
                        command=lambda: root.destroy())
        b2.grid(column=1, row=0)
        
        b3 = ttk.Button(buttonframe, text="Select File(s)",
                        command=self.get_files)
        b3.grid(column=2, row=0)

        buttonframe.grid(column=0, row=2, sticky=(N, W, E, S))
        return buttonframe

    def get_files(self):
        
        for tab in self.book.tabs(): self.book.forget(tab) 
        fnames = filedialog.askopenfilename(multiple=True)
        self.datafiles = [Datafile(fname, self.instruments) \
                              for fname in fnames]
        for datafile in self.datafiles:
            tab =  ttk.Frame(self.bookframe)
            for row, var in enumerate(datafile.fields.values()):
                self.make_widget(tab, var, row)
            fname = datafile.fields['in_filename'].stringvar.get()
            fname = os.path.basename(fname)
            self.book.add(tab, text=fname)
        self.bookframe.update()
        self.root.update()

    def make_widget(self, frame, var, row):

        label = var.label
        # label = ('(*) ' if var.required else '') + label
        ttk.Label(frame, text=label).\
            grid(column=1, row=row, sticky=W)
        if var.filename:
            fname = os.path.basename(var.stringvar.get())
            w = ttk.Label(frame, text=fname)
            w.grid(column=2, row=row, sticky=W)
        elif var.options:
            w = OptionMenu(frame, var.stringvar,
                              *var.options)
            w.grid(column=2, row=row, sticky=(W, E))
        else:
            w = ttk.Entry(frame, width=20,
                              textvariable=var.stringvar)
            w.grid(column=2, row=row, sticky=(W, E))
        if row == 0 and frame == self.mainframe: w.focus_set()

        def display_help(docs):
            d = MessageDialog(root, message=docs, title='Help')
        if var.docs:
            ttk.Button(frame, text='Help',
                       command=lambda: display_help(var.docs))\
                       .grid(column=3, row=row, sticky=W)

    def process_files(self):
        
        success = False
        for datafile in self.datafiles:
            success = self.process_file(datafile)
            if not success: break

        if success:
            d = MessageDialog(root, message="Success! File saved.",
                              title='Success!')

            root.wait_window(d.top)
            d.top.destroy()
            root.destroy()
                        
    def process_file(self, datafile):

        root = self.root
        fields = self.global_fields
        fields.update(datafile.fields)
        for var in fields.values():
            if var.required and var.stringvar.get() == '':
                d = MessageDialog(root, message="Incomplete "\
                                      "entries, please fill out all "\
                                      "fields.", title='Incomplete!')
                root.wait_window(d.top)
                return False

        device = self.instruments[fields['instrument'].\
                                      getvalue()]

        d = MessageDialog(root, message="Processing file. "
                          "This may take a few minutes.",
                          title='Processing...', nobutton=True)

        for var in fields.values():
            if var.name_in_device:
                setattr(device, var.name_in_device, var.getvalue())

        device.z_units = 'meters'

        device.read()

        #e = EmbeddedPlot(root, device.pressure_data[:100])
        #root.wait_window(e.top)
        #start_time = e.get_start_time()

        out_file = fields['out_filename'].getvalue()
        if os.path.isfile(out_file): os.remove(out_file)

        device.write()
        print('Wrote to %s.' % out_file)
        d.top.destroy()
        return True

class MessageDialog:

    def __init__(self, parent, message="", title="",  nobutton=False):

        top = self.top = Toplevel(parent)
        top.transient(parent)
        top.title(title)
        Label(top, text=message).pack()
        if not nobutton:
            b = Button(top, text="OK", command=self.ok)
            b.pack(pady=5)
            top.initial_focus = top
        parent.update()
        parent.grab_set()

    def ok(self):
        self.top.destroy()

class EmbeddedPlot:

    def __init__(self, root, data):

        top = self.top = Toplevel(root)
        f = Figure(figsize=(5,4), dpi=100)
        self.a = a = f.add_subplot(111)
        a.plot(data)

        self.canvas = canvas = FigureCanvasTkAgg(f, master=top)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.toolbar = toolbar = NavigationToolbar2TkAgg(canvas, top)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        canvas.mpl_connect('button_press_event',
                           self.onclick)
        button = Button(master=top, text='Accept',
                        command=self._quit)
        button.pack(side=BOTTOM)

    def _quit(self):

        self.top.destroy()  # this is necessary on Windows to prevent

    def onclick(self, event):

        print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f ' % (
                event.button, event.x, event.y, event.xdata, event.ydata))
        self.xdata = event.xdata

    def get_start_time(self):

        return self.xdata

if __name__ == "__main__":
    root = Tk()
    root["height"] = 400;
    root["width"] = 500;
    gui = Wavegui(root)
    root.mainloop()
