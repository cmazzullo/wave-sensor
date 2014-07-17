from Instruments.sensor import Sensor
from Instruments.InstrumentTests import PressureTests
import os
import sys
from datetime import datetime
from pytz import timezone


#--python 3 compatibility
pyver = sys.version_info
if pyver[0] == 3:
    raw_input = input

#--some import error trapping
try:
    import numpy as np
except:
    raise Exception("numpy is required")
try:        
    import netCDF4
except:
    raise Exception("netCDF4 is required")        

class Leveltroll(Sensor, PressureTests):
    '''derived class for leveltroll ascii files
    '''
    def __init__(self):
        self.numpy_dtype = np.dtype([("seconds",np.float32),("pressure",np.float32)])
        self.record_start_marker = "date and time,seconds"
        self.timezone_marker = "time zone" 
        super(Leveltroll,self).__init__()
        self.date_format_string = "%m/%d/%Y %I:%M:%S %p "
        self.temperature_data = None
        
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
        
        self.pressure_data = np.divide(data["pressure"], 14.5037738)
        self.temperature_data = [x for x in data["temperature"]]
        self.data_end_date = self.convert_milliseconds_to_datetime(self.utc_millisecond_data[::-1][0])
        self.get_time_duration(self.utc_millisecond_data[::-1][0] - self.utc_millisecond_data[0])
        self.test_16_stucksensor()
        self.test_17_frequencyrange()
        self.test_20_rateofchange()
        self.get_15_value()
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
            self.data_start = self.convert_date_to_milliseconds(dt_str)
#             self.data_start_date = datetime.strftime(self.data_start, "%Y-%m-%dT%H:%M:%SZ")
#             print('Datetime', self.data_start, self.data_start_date)
        except Exception as e:
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


if __name__ == "__main__":
    
    #--create an instance    
    lt = Leveltroll()        
    
    lt.creator_email = "a@aol.com"
    lt.creator_name = "Jurgen Klinnsmen"
    lt.creator_url = "www.test.com"
    #--for testing
    lt.in_filename = os.path.join("benchmark","data.csv")
    lt.out_filename = os.path.join("benchmark","data.csv.nc")
    if os.path.exists(lt.out_filename):
        os.remove(lt.out_filename)
    lt.is_baro = True
    lt.pressure_units = "psi"
    lt.z_units = "meters"
    lt.longitude = np.float32(0.0)
    lt.latitude = np.float(0.0)
    lt.salinity_ppm = np.float32(0.0)
    lt.z = np.float32(0.0)
    
  
    #--get input
    #lt.get_user_input()
    
    #--read the ASCII level troll file
    lt.read()    

    #--write the netcdf file
    lt.write()
    
    
