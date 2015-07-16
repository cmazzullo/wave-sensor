"""Contains classes that read CSV files output by pressure sensors."""

from datetime import datetime
from NetCDF_Utils.edit_netcdf import NetCDFWriter
import DataTests
import unit_conversion as uc
import numpy as np
import pandas as pd
import pytz
import re


def find_first(fname, expr):
    '''Search for the first occurrence of expr in fname, return the line no.'''
    with open(fname, 'r') as text:
        for i, line in enumerate(text):
            if re.search(expr, line):
                return i + 1


class Hobo(NetCDFWriter):
    '''derived class for hobo csv files '''
    def __init__(self):
        self.timezone_marker = "time zone"
        super().__init__()
        self.date_format_string = '%m/%d/%y %I:%M:%S %p'

    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        skip_index = find_first(self.in_filename, '"#"')
        df = pd.read_table(self.in_filename, skiprows=skip_index, header=None,
                           engine='c', sep=',', usecols=(1, 2))
        df = df.dropna()
        first_stamp = uc.datestring_to_ms(df.values[0][0], self.date_format_string)
        second_stamp = uc.datestring_to_ms(df.values[1][0], self.date_format_string)
        self.frequency = 1000 / (second_stamp - first_stamp)
        start_ms = uc.datestring_to_ms(df[1][0], self.date_format_string)
        self.utc_millisecond_data = uc.generate_ms(start_ms, df.shape[0], self.frequency)
        self.pressure_data = df[2].values * uc.PSI_TO_DBAR


class House(NetCDFWriter):
    '''Processes files coming out of the USGS-made sensors'''
    def __init__(self):
        self.timezone_marker = "time zone"
        self.temperature_data = None
        super(House, self).__init__()
        self.frequency = 4
        self.date_format_string = '%Y.%m.%d %H:%M:%S '

    def read(self):
        '''Load the data from in_filename'''
        skip_index = find_first(self.in_filename, '^[0-9]{4},[0-9]{4}$') - 1
        df = pd.read_table(self.in_filename, skiprows=skip_index, header=None,
                           engine='c', sep=',', names=('a', 'b'))
        self.pressure_data = np.array([
            uc.USGS_PROTOTYPE_V_TO_DBAR(np.float64(x))
            for x in df[df.b.isnull() == False].a])
        self.temperature_data = [
            uc.USGS_PROTOTYPE_V_TO_C(np.float64(x))
            for x in df[df.b.isnull() == False].b]
        with open(self.in_filename, 'r') as wavelog:
            for x in wavelog:
                # second arg has extra space that is unnecessary
                if re.match('^[0-9]{4}.[0-9]{2}.[0-9]{2}', x):
                    start_ms = uc.datestring_to_ms(x, self.date_format_string)
                    self.utc_millisecond_data = uc.generate_ms(start_ms,
                                                               len(self.pressure_data),
                                                               self.frequency)
                    break


class Leveltroll(NetCDFWriter):
    '''derived class for leveltroll ascii files
    '''
    def __init__(self):
        self.numpy_dtype = np.dtype([("seconds", np.float32),
                                     ("pressure", np.float32)])
        self.record_start_marker = "date and time,seconds"
        self.timezone_marker = "time zone"
        super().__init__()
        self.date_format_string = "%m/%d/%Y %I:%M:%S %p"
        self.temperature_data = None

    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        with open(self.in_filename, 'rb') as f:
            self.read_header(f)
            self.read_datetime(f)
            data = np.genfromtxt(f, dtype=self.numpy_dtype, delimiter=',',
                                 usecols=[1, 2, 3])
        long_seconds = data["seconds"]
        print(long_seconds[::-1])
        self.utc_millisecond_data = [(x * 1000) + self.data_start
                                     for x in long_seconds]
        self.pressure_data = data["pressure"] * uc.PSI_TO_DBAR
        self.frequency = 1 / (long_seconds[1] - long_seconds[0])
        print(len(self.pressure_data))

    def read_header(self, f):
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
            raise Exception("ERROR - could not find time zone in file " +
                            self.in_filename+" header before line "
                            + str(line_count)+'\n')
        self.set_timezone()

    def read_datetime(self, f):
        '''read the first datetime and cast
        '''
        dt_fmt = "%m/%d/%Y %I:%M:%S %p "
        reset_point = f.tell()
        bit_line = f.readline()
        line = bit_line.decode()
        raw = line.strip().split(',')
        dt_str = raw[0]
        try:
            self.data_start = uc.datestring_to_ms(dt_str, self.date_format_string)
        except Exception:
            try:
                self.data_start = uc.datestring_to_ms(dt_str, dt_fmt)
            except Exception:
                raise Exception("ERROR - cannot parse first date time stamp: "+str(self.td_str)+" using format: "+dt_fmt+'\n')
        f.seek(reset_point)

    def set_timezone(self):
        '''set the timezone from the timezone string found in the header -
        needed to get the times into UTC
        '''
        tz_dict = {"central":"US/Central", "eastern":"US/Eastern"}
        for tz_str, tz in tz_dict.items():
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


class MeasureSysLogger(NetCDFWriter):
    '''derived class for Measurement Systems cvs files
    '''
    def __init__(self):
        self.timezone_marker = "time zone"
        super(MeasureSysLogger, self).__init__()
        self.frequency = 4
        self.date_format_string = '%m/%d/%Y %I:%M:%S.%f %p'

    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        skip_index = find_first(self.in_filename, '^ID') - 1
        # for skipping lines in case there is calibration header data
        df = pd.read_table(self.in_filename, skiprows=skip_index + 1, header=None,
                           engine='c', sep=',', usecols=[3, 4, 5 ,6])
        self.data_start = uc.datestring_to_ms(df[3][3][1:],
                                              self.date_format_string)
        second_stamp = uc.datestring_to_ms(df[3][4][1:],
                                           self.date_format_string)
        self.frequency = 1000 / (second_stamp - self.data_start)
        # Since the instrument is not reliably recording data at 4hz
        # we have decided to interpolate the data to avoid any
        # potential complications in future data analysis
        self.pressure_data = df[5].values * uc.PSI_TO_DBAR
        start_ms = uc.datestring_to_ms('%s' % df[3][0][1:], self.date_format_string)
        self.utc_millisecond_data = uc.generate_ms(start_ms, df.shape[0], self.frequency)
        if re.match('^[0-9]{1,3}.[0-9]+$', str(df[6][0])):
            self.temperature_data = [x for x in df[6]]


class RBRSolo(NetCDFWriter):
    '''derived class for RBR solo engineer text files, (exported via ruskin software)
    '''
    def __init__(self):
        self.timezone_marker = "time zone"
        super().__init__()
        self.frequency = 4
        self.date_format_string = '%d-%b-%Y %H:%M:%S.%f'

    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        skip_index = find_first(self.in_filename, '^[0-9]{2}-[A-Z]{1}[a-z]{2,8}-[0-9]{4}')
        print(skip_index)
        df = pd.read_csv(self.in_filename, skiprows=skip_index, delim_whitespace=True,
                         header=None, engine='c', usecols=[0, 1, 2])
        
        self.datestart = uc.datestring_to_ms('%s %s' % (df[0][0], df[1][0]), self.date_format_string)
        self.utc_millisecond_data = uc.generate_ms(self.datestart, df.shape[0] - 1,
                                                    self.frequency)
        self.pressure_data = np.array([x for x in df[2][:-1]])
        print(self.pressure_data[0], len(self.pressure_data))


class Waveguage(NetCDFWriter):
    """Reads in an ASCII file output by a Waveguage pressure sensor
    from Ocean Sensor Systems Inc.

    This class reads in data from a plaintext output file into a
    pandas Dataframe. This is then translated into numpy ndarrays
    and written to a netCDF binary file."""
    def __init__(self):
        super(Waveguage, self).__init__()

    def read(self):
        """Sets start_time to a datetime object, utc_millisecond_data
        to a numpy array of dtype=int64 and pressure_data to a numpy
        array of dtype float64."""
        data = self.get_data()
        chunks = self.get_pressure_chunks(data)
        timestamps = self.get_times(data)
        self.data_start_date = datetime.strftime(timestamps[0], "%Y-%m-%dT%H:%M:%SZ")
        self.data_duration_time = timestamps[-1] - timestamps[0]
        with open(self.in_filename) as f:
            self.frequency = f.readline()[25:27]
        self.utc_millisecond_data = self.get_ms_data(timestamps, chunks)
        raw_pressure = self.make_pressure_array(timestamps, chunks)
        self.pressure_data = raw_pressure * 10.0 + uc.ATM_TO_DBAR
        return self.pressure_data, self.utc_millisecond_data

    def make_pressure_array(self, t, chunks):
        def press_entries(t2, t1):
            seconds = (t2 - t1).total_seconds()
            return seconds * self.frequency
        final = np.zeros(0, dtype=np.float64)
        prev_stamp = None
        prev_press = None
        for stamp, press in zip(t, chunks):
            if prev_stamp:
                n = press_entries(stamp, prev_stamp) - len(prev_press)
                print(n)
                narr = np.zeros(n, dtype=np.float64) + self.fill_value
                print('narr = %d' % narr[1])
                final = np.hstack((final, prev_press, narr))
            prev_stamp = stamp
            prev_press = press
        final = np.hstack((final, chunks[-1]))
        return final

    def get_pressure_chunks(self, data):
        master = [[]]
        i = 0
        for e in data:
            if e.startswith('+') or e.startswith('-'):
                if len(e) == 7:
                    master[i].append(np.float64(e))
            else:
                if master[i] != []:
                    master.append([])
                    i += 1
        master.pop()
        return master

    def get_ms_data(self, timestamps, chunks):
        """Generates the time data using the initial timestamp in the
        file and the length of the pressure data array."""
        first_stamp = timestamps[0]
        last_stamp = timestamps[-1]
        def del_t_ms(t2, t1):
            return (t2 - t1).total_seconds() * 1000
        total_stamp_ms = del_t_ms(last_stamp, first_stamp)
        last_chunk = chunks[-1]
        last_chunk_ms = 1000 * len(last_chunk) / self.frequency
        total_ms = total_stamp_ms + last_chunk_ms
        first_date = timestamps[0]
        epoch_start = datetime(year=1970, month=1, day=1, tzinfo=pytz.utc)
        offset = (first_date - epoch_start).total_seconds() * 1e3
        utc_ms_data = np.arange(total_ms, step=(1000 / self.frequency),
                                dtype='int64')
        utc_ms_data += offset
        return utc_ms_data

    def _get_frequency(self):
        with open(self.in_filename) as f:
            line = f.readline()
        freq = int(line[25:27])
        return freq

    def get_times(self, p):
        """Returns the time that the device started reading as a
        datetime object."""
        def make_stamps(p):
            added = ''
            result = []
            for i, s in enumerate(p):
                added += s
                if i % 6 == 5:
                    result.append(added)
                    added = ''
            return result
        def test2(x):
            return not  (x.startswith('+') or x.startswith('-'))
        c = p.map(test2)
        p = p[c]
        p = p[14:-1]
        stamps = make_stamps(p)
        date_format = 'Y%yM%mD%dH%HM%MS%S'
        stamps = [datetime.strptime(stamp, date_format).replace(tzinfo=self.tzinfo)
                  for stamp in stamps]
        return stamps

    def get_data(self):
        """Reads the pressure data from the current file and returns
        it in a numpy array of dtype float64."""
        data = pd.read_csv(self.in_filename, skiprows=0, header=None,
                           lineterminator=',', sep=',', engine='c',
                           names='p')
        data.p = data.p.apply(lambda x: x.strip())
        return data.p
