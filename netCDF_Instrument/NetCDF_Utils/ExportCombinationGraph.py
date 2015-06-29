from NetCDF_Utils.edit_netcdf import NetCDFWriter
import unit_conversion
from datetime import datetime
import pytz

class export_netCDF(NetCDFWriter):
    """Exports the combined sin and cos waves that make up a time series of presure to a netcdf file"""

    def __init__(self, values, equation):
        super().__init__()
        self.pressure_data = values
        self.equation = equation
        self.out_filename = 'combo.nc'

    def export(self):
        """Calculates milliseconds given the 4hz freq, then writes data to netcdf file"""
        self.vstore.pressure_data = self.pressure_data
        start_ms = unit_conversion.date_to_ms(datetime.now(tz=pytz.utc))
        series_len = len(self.pressure_data, dtype='int64')
        timestep = 1000 / 4
        self.vstore.utc_millisecond_data = np.arange(series_len * timestep + start_ms)
        self.vstore.latitutde = self.latitude
        self.vstore.longitude = self.longitude

        #Tests#
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')
        self.vstore.global_vars_dict['equation'] = self.equation
        self.write_netCDF(self.vstore, len(self.pressure_data))
