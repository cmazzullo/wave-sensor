'''
Created on Jun 20, 2014

@author: Gregory
'''
import os
import sys
from datetime import datetime
import pytz
import pandas
import re

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



class pressure(object):
    '''super class for reading raw wave data and writing to netcdf file
    this class should not be instantiated directly
    '''
    
    def __init__(self):
        self.in_filename = None
        self.out_filename = None
        self.is_baro = None
        self.pressure_units = None
        self.z_units = None
        self.latitude = None
        self.longitude = None
        self.z = None
        self.salinity_ppm = -1.0e+10
        self.utc_millisecond_data = None
        self.pressure_data = None
        self.epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
        self.data_start = None
        self.timezone_string = None

        self.valid_pressure_units = ["psi","pascals","atm"]
        self.valid_z_units = ["meters","feet"]
        self.valid_latitude = (np.float32(-90),np.float32(90))
        self.valid_longitude = (np.float32(-180),np.float32(180))
        self.valid_z = (np.float32(-10000),np.float32(10000))
        self.valid_salinity = (np.float32(0.0),np.float32(40000))
        self.valid_pressure = (np.float32(-10000),np.float32(10000))

        self.fill_value = np.float32(-1.0e+10)

    @property    
    def offset_seconds(self):
        '''offsets seconds from specified epoch using UTC time
        '''        
        offset = self.data_start - self.epoch_start            
        return offset.total_seconds()
    
    def convert_dateobject(self, datestring):
        print(datestring)
        first_date = datetime.strptime(datestring, "%d-%b-%Y %H:%M:%S.%f")
        return pytz.utc.localize(first_date)


    def time_var(self,ds):
        time_var = ds.createVariable("time","u8",("time",),fill_value=np.int64())
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
    
   
    def write(self):
        #assert not os.path.exists(self.out_filename),"out_filename already exists"
        #--create variables and assign data
        ds = netCDF4.Dataset(self.out_filename,'w',format="NETCDF4")
        time_dimen = ds.createDimension("time",len(self.pressure_data))   
        print(len(self.pressure_data))  
        time_var = self.time_var(ds)
        latitude_var = self.latitude_var(ds)
        longitude_var = self.longitude_var(ds)
        z_var = self.z_var(ds)
        pressure_var = self.pressure_var(ds)
        ds.salinity_ppm = np.float32(self.salinity_ppm)        
        ds.time_zone = "UTC"
        ds.readme = "file created by "+sys.argv[0]+" on "+str(datetime.now())+" from source file "+self.in_filename
        

    def get_user_input(self):        
        in_filename = raw_input("level troll filename\n")
        print(self.in_filename)
        while not os.path.exists(in_filename):
            print("file",in_filename,"does not exists - try again")
            in_filename = raw_input("level troll filename\n")
        self.in_filename = in_filename        

        baro = None
        is_baro = True
        while baro not in ['y','n']:
            baro = raw_input("is this a barometric correction dataset? (y/n)\n").lower()
        if baro == 'y':
            is_baro = True
        else:
            is_baro = False                            
        self.is_baro = baro

        pressure_units = ''
        while pressure_units not in self.valid_pressure_units:
            pressure_units = raw_input("what are the pressure units? ("+','.join(self.valid_pressure_units)+")?\n").lower()
        self.pressure_units = pressure_units

        latitude = self.fill_value
        while not self.inrange(latitude,self.valid_latitude):    
            while True:                
                latitude = raw_input("what is the latitude (DD) where these data were collected?\n")    
                try:
                    latitude = np.float32(latitude)
                    break
                except:
                    pass    
        self.latitude = latitude


        longitude = self.fill_value
        while not self.inrange(longitude,self.valid_longitude):    
            while True:                
                longitude = raw_input("what is the longitude (DD) where these data were collected?\n")    
                try:
                    longitude = np.float32(longitude)
                    break
                except:
                    pass    
        self.longitude = longitude

        z = self.fill_value
        while not self.inrange(z,self.valid_z):    
            while True:                
                z = raw_input("what is the altitude of the sensor?\n")    
                try:
                    z = np.float32(z)
                    break
                except:
                    pass    
        self.z = z

        z_units = raw_input("what are the z units (" +','.join(self.valid_z_units)+ ")\n")
        while z_units.lower() not in self.valid_z_units:
            z_units = raw_input("what are the z units (" +','.join(self.valid_z_units)+ ")\n")
        self.z_units = z_units            

        if not is_baro:
            salinity = self.fill_value
            while not self.inrange(salinity,self.valid_salinity):    
                while True:                
                    salinity = raw_input("what is the salinity (ppm or mg/l) where these data were collected?\n")    
                    try:
                        salinity = np.float32(salinity)
                        break
                    except:
                        pass    
            self.salinity_ppm = salinity

        out_filename = raw_input("what is the output netcdf file name? (enter to use level troll filename with \'.nc\' suffix")        
        if out_filename == '':            
            out_filename = in_filename + ".nc"            
        if os.path.exists(out_filename):
            cont = raw_input("Warning - netcdf4 file "+out_filename+" already exists - overwrite? (y/n)?")
            if not cont:
                out_filename = raw_input("what is the output netcdf file name? (enter to use level troll filename with \'.nc\' suffix")
                if out_filename == '':
                    out_filename = self.in_filename + ".nc"
            else:
                try:
                    os.remove(out_filename)                    
                except:
                    raise Exception("unable to remove existing netcdf file: "+out_filename)                    
        
        self.out_filename = out_filename


    def inrange(self,val,limits):
        if val >= limits[0] and val <= limits[1]:
            return True
        else:
            return False


    def read(self):
        raise Exception("read() must be implemented in the derived classes")




class rbrsolo(pressure):
    '''derived class for leveltroll ascii files
    '''
    def __init__(self):
        self.timezone_marker = "time zone"        
        super(rbrsolo,self).__init__()
    

    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        skip_index = self.read_start() #for skipping lines in case there is calibration header data
        
        df2 = pandas.read_csv(self.in_filename,skiprows=skip_index, delim_whitespace=True, header=None, engine='c', usecols=[0,1,2])
    
        print('here we go')
        
        for x in df2.itertuples():
            if x[0] == 0:
                self.data_start = (self.convert_dateobject('%s %s' % (x[1],x[2])) - self.epoch_start).total_seconds()
                break

        self.utc_millisecond_data = []
      
        for x in range(0, df2.shape[0] - 1):
            self.utc_millisecond_data.append(self.data_start * 1000)
            self.data_start += .25
    
        self.pressure_data = [x[3] for x in df2[:-1].itertuples()]

        print('done read')
        
    def read_start(self):
        skip_index = 0;
        with open(self.in_filename,'r') as RBRText:
            for x in RBRText:
                file_string = x.split(' ')[0]
                if re.match('^[0-9-]{3}[A-Z]{1}[a-z]{2,8}[0-9-]{5}$', file_string):
                    print('Success! Index %s' % skip_index)
                    break
                skip_index += 1   
        return skip_index  

if __name__ == "__main__":
    
    #--create an instance    
    lt = rbrsolo()        
    
    #--for testing
    lt.in_filename = os.path.join("benchmark","RBRtest2.txt")
    lt.out_filename = os.path.join("benchmark","RBR.csv.nc")
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
    
    
    
    