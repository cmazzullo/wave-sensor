import sys
sys.path.append('..')
import os
import numpy as np
from datetime import datetime
from pytz import timezone
import pandas as pd
import pytz
from NetCDF_Utils.Testing import DataTests
from NetCDF_Utils.edit_netcdf import NetCDFWriter


class Waveguage(NetCDFWriter):
    """Reads in an ASCII file output by a Waveguage pressure sensor
    from Ocean Sensor Systems Inc.

    This class reads in data from a plaintext output file into a
    pandas Dataframe. This is then translated into numpy ndarrays
    and written to a netCDF binary file."""

    def __init__(self):
        self.tz_info = pytz.timezone("US/Eastern")
        super(Waveguage, self).__init__()
        self.data_tests = DataTests()


    def read(self):
        """Sets start_time to a datetime object, utc_millisecond_data
        to a numpy array of dtype=int64 and pressure_data to a numpy
        array of dtype float64."""

        data = self.get_data()
        chunks = self.get_pressure_chunks(data)
        timestamps = self.get_times(data)
        self.data_start_date = datetime.\
            strftime(timestamps[0], "%Y-%m-%dT%H:%M:%SZ")
        self.data_duration_time = timestamps[-1] - timestamps[0]
        self.frequency = self._get_frequency()
        self.utc_millisecond_data = self.get_ms_data(timestamps, chunks)
        self.pressure_data = np.add(np.multiply(self.make_pressure_array(timestamps, chunks),10.0),10.1325)

        #Test and utility methods
        ms = self.utc_millisecond_data[::-1][0]


    def make_pressure_array(self, t, chunks):
        def press_entries(t2, t1):
            seconds = self._ms_time_difference(t2, t1) / 1000
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
            if (e.startswith('+') or e.startswith('-')):
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
        epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
        offset = self._ms_time_difference(first_date, epoch_start)

        utc_ms_data = np.arange(total_ms, step=(1000 / self.frequency),
                                dtype='int64')
        utc_ms_data += offset
        return utc_ms_data

    def _ms_time_difference(self, t2, t1):
        return (t2 - t1).total_seconds() * 1000

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
        stamps = [datetime.strptime(stamp, date_format).\
                      replace(tzinfo=self.tzinfo)
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

    def write(self, sea_pressure = True):
        '''Write netCDF files

        sea_pressure - if true write sea_pressure data, otherwise write air_pressure data'''

        if sea_pressure == False:
            self.vstore.pressure_name = "air_pressure"
            self.vstore.pressure_var['standard_name'] = "air_pressure"

        self.vstore.pressure_data = self.pressure_data
        self.vstore.utc_millisecond_data = self.utc_millisecond_data
        self.vstore.latitutde = self.latitude
        self.vstore.longitude = self.longitude

        #Tests#
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')

        self.write_netCDF(self.vstore, len(self.pressure_data))

if __name__ == '__main__':
    # Just for testing!
    wg = Waveguage()
    wg.creator_email = "a@aol.com"
    wg.creator_name = "Jurgen Klinnsmen"
    wg.creator_url = "www.test.com"
    wg.in_filename = 'benchmark/wave-guage-14-07-2014.csv'
    wg.out_filename = 'newstuff.nc'
    wg.is_baro = True
    wg.pressure_units = "psi"
    wg.z_units = "meters"
    wg.longitude = np.float32(0.0)
    wg.latitude = np.float(0.0)
    wg.salinity_ppm = np.float32(0.0)
    wg.z = np.float32(0.0)
    wg.tzinfo = timezone('US/Eastern')

    wg.read()
    if os.path.isfile(wg.out_filename):
        os.remove(wg.out_filename)
    wg.write()
