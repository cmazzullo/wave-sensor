from RBRTroll import pressure
import numpy as np
from datetime import datetime
from pytz import timezone
import pandas as pd

class Waveguage(pressure):
    """Reads in an ASCII file output by a Waveguage pressure sensor
    from Ocean Sensor Systems Inc."""

    def __init__(self):
        super(Waveguage, self).__init__()

    def read(self):
        """This gets the values of:
        data_start
        utc_millisecond_data
        pressure_data"""
        self.data_start = self.read_data_start()
        data = self.read_data()
        offset = self.data_start - self.epoch_start
        offset_ms = 1000 * offset.total_seconds()
        freq = self.get_frequency()
        self.utc_millisecond_data = np.\
          arange(data.shape[0], dtype='int64') * (1000 / freq)\
          + offset_ms
        self.pressure_data = np.array(data.p, dtype='float64')

    def get_frequency(self):
        with open(self.in_filename) as f:
            line = f.readline()
        freq = int(line[25:27])
        return freq
    
    def read_data_start(self):
        with open(self.in_filename) as f:
            for i, line in enumerate(f):
                if i > 0 and line.startswith('Y'):
                    break
        date_string = line[:23]
        date_format = 'Y%y,M%m,D%d,H%H,M%M,S%S'
        data_start = datetime.strptime(date_string, date_format).\
          replace(tzinfo=self.tzinfo)
        return data_start

    def read_data(self):
        data = pd.read_csv(self.in_filename, skiprows=20, header=None,
                          lineterminator=',', sep=',', engine='c',
                          names='p')
        data = data[:-1]
        data.p = [np.float64(string.strip()) for string in data.p]
        return data

if __name__ == '__main__':
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
