from sensor import Sensor
import numpy as np
from datetime import datetime
from pytz import timezone
import pandas as pd

class Waveguage(Sensor):
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
        
        self.start_time = self.get_start_time()
        self.pressure_data = self.get_pressure_data()
        self.utc_millisecond_data = self.get_millisecond_data(self.pressure_data)

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

if __name__ == '__main__':
    # Just for testing!
    wg = Waveguage()
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
