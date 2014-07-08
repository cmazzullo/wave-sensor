from Instruments.sensor import Sensor
import numpy as np
from datetime import datetime
from pytz import timezone
import pandas as pd
import pytz

class Waveguage(Sensor):
    """Reads in an ASCII file output by a Waveguage pressure sensor
    from Ocean Sensor Systems Inc.

    This class reads in data from a plaintext output file into a
    pandas Dataframe. This is then translated into numpy ndarrays
    and written to a netCDF binary file."""

    def __init__(self):
        self.tz_info = pytz.timezone("US/Eastern")
        super(Waveguage, self).__init__()
         
        self.local_frequency_range = [11, 19] # for IOOS test 17
        self.mfg_frequency_range = [10, 20] # for IOOS test 17
        self.max_rate_of_change = 20
        self.prev_value = True # for IOOS test 20
        self.five_count_list = list()
        
       
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
        
        data = pd.read_csv(self.in_filename, skiprows=20, header=None,
                          lineterminator=',', sep=',', engine='c',
                          names='p')
        data = data[:-1]
        data.p = [np.float64(string.strip()) for string in data.p]
        data_array = np.array(data.p, dtype='float64')
        return data_array
    
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
        print(self.local_frequency_range[0])
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

if __name__ == '__main__':
    # Just for testing!
    wg = Waveguage()
    wg.creator_email = "a@aol.com"
    wg.creator_name = "Jurgen Klinnsmen"
    wg.creator_url = "www.test.com"
    wg.in_filename = 'waveguage.csv'
    wg.out_filename = 'wg-output.nc'
    wg.is_baro = True
    wg.pressure_units = "psi"
    wg.z_units = "meters"
    wg.longitude = np.float32(0.0)
    wg.latitude = np.float(0.0)
    wg.salinity_ppm = np.float32(0.0)
    wg.z = np.float32(0.0)
    wg.tzinfo = timezone('US/Eastern')
    wg.read()
    wg.write()
