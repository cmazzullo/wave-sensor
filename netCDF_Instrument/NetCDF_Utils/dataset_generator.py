'''
Created on Feb 10, 2016

@author: chogg
'''

from netCDF4 import Dataset
import pandas as pd
import random
import unit_conversion
import shutil
import netCDF_Utils.nc as nc

def wind_data(file_name, mode='netCDF'):
    
    #every fifteen minutes maybe not necessary
    frequency = 1/900
    series_length = 1440
    time = unit_conversion.generate_ms(1404647999870, series_length, frequency)
    wind_direction = get_rand_circular_data(series_length, 15, 360)
    wind_speed = get_rand_discrete_data(series_length, 2, 5, 0)
    
    if mode == 'netCDF':
        ds = Dataset(file_name, 'w', format="NETCDF4_CLASSIC")
        ds.createDimension('time',len(time))
        time_var = ds.createVariable('time','f8',('time'))
        time_var[:] = time
        wind_speed_var = ds.createVariable('wind_speed','f8',('time'))
        wind_speed_var[:] = wind_speed
        wind_direction_var = ds.createVariable('wind_direction','f8',('time'))
        wind_direction_var[:] = wind_direction
        ds.close()
    else:
        excelFile = pd.DataFrame({'Time': time, 
                                  'Wind Speed in m/s': wind_speed,
                                  'Wind Direction in degrees': wind_direction,
                                  })
        
        excelFile.to_csv(path_or_buf= file_name)
        
    
    print('total:', len(time), len(wind_direction), len(wind_speed))

def quick_dirty_wind_data(in_file_name, out_file_name):  
    df = pd.read_csv(in_file_name, header=None)
    
    #generate 6 minute utc millisecond data
    #millisecond is a time stamp for Fri Jan 22 2016 23:00:00
    time = unit_conversion.generate_ms(1453503600000.0, 1213, 1/360)
    wind_direction = df[6]
    wind_speed = df[8]
    
    ds = Dataset(out_file_name, 'w', format="NETCDF4_CLASSIC")
    ds.createDimension('time',len(time))
    time_var = ds.createVariable('time','f8',('time'))
    time_var[:] = time
    wind_speed_var = ds.createVariable('wind_speed','f8',('time'))
    wind_speed_var[:] = wind_speed.values
    wind_direction_var = ds.createVariable('wind_direction','f8',('time'))
    wind_direction_var[:] = wind_direction.values
    ds.close()  
                   
def get_rand_circular_data(series_len, threshold, data_max):
    '''Generates a data series of random pints within a threshold, 
    lends itself to circular data e.g degrees (direction)'''
    
    data_series = []
    last_point = -1
    bounds_changed = False
    
    for x in range(0,series_len):
    
        if last_point < 0:
            rand_float = last_point = float( random.randint(0,data_max* 100.0) /100.0)
            
        else:
            min_d = last_point - threshold
            if last_point - threshold < 0:
    
                min_d = data_max + min_d
                bounds_changed = True
    
            max_d = last_point + threshold
            if last_point + threshold > data_max:
                
                max_d = max_d - data_max
                bounds_changed = True
            
            if bounds_changed == True:
                rand_inverse = random.randint(0,1)
                 
                first_range = random.randint(0, int(max_d * 100))
                second_range = random.randint(int(min_d * 100), int(data_max * 100))
                
                rand_float1 = float(first_range / 100.0)
                rand_float2 = float(second_range / 100.0)
                
                if rand_inverse == 0:
                    rand_float = last_point = rand_float1
                else:
                    rand_float = last_point = rand_float2
                
            else:
                rand_float = last_point = float( random.randint(int(min_d * 100),int(max_d * 100))/ 100.0)
               
            bounds_changed = False
            
        data_series.append(rand_float)
        print(rand_float)
        
    return data_series

def get_rand_discrete_data(series_len, threshold, data_max, data_min):
    '''Generates a data series of random pints within a threshold, 
    lends itself to bound'''
    
    data_series = []
    last_point = None

    for x in range(0,series_len):
    
        if last_point is None:
            rand_float = last_point = float( random.randint(data_min * 100,data_max* 100.0) /100.0)
            
        else:
            min_d = last_point - threshold
            if last_point - threshold < data_min:
    
                min_d = data_min
    
            max_d = last_point + threshold
            if last_point + threshold > data_max:
                
                max_d = data_max
                
            rand_float = last_point = float( random.randint(int(min_d * 100),int(max_d * 100))/ 100.0)
                    
        data_series.append(rand_float)
        print(rand_float)
        
    return data_series


def change_netCDFTime(in_file_name, out_file_name, start_ms):
    shutil.copy(in_file_name, out_file_name)
    time_len = len(nc.get_time(out_file_name))
    new_time = unit_conversion.generate_ms(start_ms, time_len, 1/900)
    nc.set_variable_data(out_file_name, 'time', new_time)
    

if __name__ == '__main__':
    quick_dirty_wind_data('wind_data.csv', 'wind_data_CT.nc')