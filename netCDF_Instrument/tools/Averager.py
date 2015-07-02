import pandas as pd
from netCDF4 import Dataset     
        
def file_average(in_file_name, window, increments, method):
    
        #Get netCDF info      
        ds = Dataset(in_file_name,'r')
        sea_pressure = ds.variables['sea_water_pressure'][:]
        sea_pressure_attr = get_attributes(ds, "sea_water_pressure")
        pressure_qc = ds.variables['pressure_qc'][:]
        pressure_qc_attr = get_attributes(ds, "pressure_qc")
        time = ds.variables["time"][:]
        time_attr = get_attributes(ds, "time")
        lat = ds.variables["latitude"][:]
        lat_attr = get_attributes(ds, "latitude")
        lon = ds.variables["longitude"][:]
        lon_attr = get_attributes(ds, "longitude")
        alt = ds.variables["altitude"][:]
        alt_attr = get_attributes(ds, "altitude")
        
        #input all of the global attributes to a dictionary
        attrDict = {}
        for x in ds.ncattrs():
            attrDict[x] = ds.getncattr(x)
        ds.close()
        
        
         
        time_resolution = .25 * increments
        attrDict['time_coverage_resolution'] = ''.join(["P",str(time_resolution),"S"])
        
        #create series for both pressure and pressure_qc
        data_series = pd.Series(sea_pressure, index=time)
        pressure_qc_series = pd.Series(pressure_qc, index=time)
        
        df = pd.DataFrame({"Pressure": data_series, "Pressure_QC": pressure_qc_series})
        
        #box car average and drop the NaN rows
        df.Pressure = pd.rolling_mean(data_series, window, center=True, min_periods=1)
        df = df[pd.notnull(df.Pressure)]
        
        rolling_mean = df.Pressure[::increments]
        pressure_qc = df.Pressure_QC[::increments]
        
        if(method == "excel" or method == "both"):
            excelFile = pd.DataFrame({'Time': rolling_mean.index, 'Pressure': rolling_mean.values})
            #append file name to new excel file
            last_index = in_file_name.find('.')
            
            out_file_name = ''.join([in_file_name[0:last_index],'_average.csv'])
            excelFile.to_csv(path_or_buf=out_file_name)
            
            
        if(method == "netcdf" or method == "both"):
        #append file name to new netCDF file
            last_index = in_file_name.find('.')
            
            out_file_name = ''.join([in_file_name[0:last_index],'_average.nc'])
            
            #create new netCDF file with averaged data
            new_ds = Dataset(out_file_name,'w',format="NETCDF4_CLASSIC")
            new_ds.createDimension("time", size=len(rolling_mean))
            
            #time
            new_time = new_ds.createVariable("time","f8", ("time",))
            set_attributes(new_ds, "time", time_attr)
            new_time[:] = [x for x in rolling_mean.index]
           
            #sea pressure
            new_pressure = new_ds.createVariable("sea_water_pressure","f8", ("time",))
            set_attributes(new_ds, "sea_water_pressure", sea_pressure_attr)
            new_pressure[:] = rolling_mean.values
            
            #pressure qc
            new_pressure_qc = new_ds.createVariable("pressure_qc", "i4", ("time",))
            set_attributes(new_ds, "pressure_qc", pressure_qc_attr)
            new_pressure_qc[:] = [x for x in pressure_qc]
            
            #altitude
            new_altitude = new_ds.createVariable("altitude", "f8")
            set_attributes(new_ds, "altitude", alt_attr)
            new_altitude[:] = alt
            
            #latitude
            new_latitude = new_ds.createVariable("latitude", "f8")
            set_attributes(new_ds, "latitude", lat_attr)
            new_latitude[:] = lat
            
            #longitude
            new_longitude = new_ds.createVariable("longitude", "f8")
            set_attributes(new_ds, "longitude", lon_attr)
            new_longitude[:] = lon
           
            
            for x in attrDict:
                new_ds.setncattr(x, attrDict[x])
            
            new_ds.close()
     
def get_attributes(ds, name):
    attr_dict = {}
    for x in ds.variables[name].ncattrs():
            attr_dict[x] = ds.variables[name].getncattr(x)
    return attr_dict
    
def set_attributes(ds, name, attr):
        for x in attr:
            ds.variables[name].setncattr(x, attr[x])
            