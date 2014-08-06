'''
Created on Jul 31, 2014

@author: Gregory
'''
from NetCDF_Utils.edit_netcdf import NetCDFWriter
import NetCDF_Utils.DateTimeConvert as date_convert 
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
        first_date_seconds = date_convert.convert_date_to_milliseconds(None, None, datetime.now(tz=pytz.utc))
        self.vstore.utc_millisecond_data = date_convert.convert_to_milliseconds(len(self.pressure_data), None, None,\
                                                                        4,date_seconds = first_date_seconds)
        self.vstore.latitutde = self.latitude
        self.vstore.longitude = self.longitude
#       
        #Tests#
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')
        self.vstore.global_vars_dict['equation'] = self.equation
        self.write_netCDF(self.vstore, len(self.pressure_data))    
  
