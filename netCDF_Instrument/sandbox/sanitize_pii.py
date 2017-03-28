'''
Created on Dec 19, 2016

@author: chogg
'''
import os
from netCDF4 import Dataset
from netCDF_Utils import nc
from unit_conversion import FILL_VALUE

def custom_copy(fname, out_fname):
    if os.path.exists(out_fname):
        os.remove(out_fname)
    
    #get station id for the station_id dimension
    stn_site_id = nc.get_variable_data(fname, 'station_id')
    t = nc.get_time(fname)[:]
    d = Dataset(fname)
    output = Dataset(out_fname, 'w', format='NETCDF4_CLASSIC')
    output.createDimension('time', len(t))
    output.createDimension("timeSeries", 1)
    output.createDimension("station_id", len(stn_site_id))
    
    # copy globals
    for att in d.ncattrs():
        setattr(output, att, d.__dict__[att])
    setattr(output, "creator_name", "N/a")
    setattr(output, "creator_email", "N/a")
    setattr(output, "cdm_data_type", "STATION")
   
    # copy variables
    for key in d.variables:
        
        
        if key == 'wave_wl':
            continue
        
        
        
        name = key
            
        datatype = d.variables[key].datatype 
          
        dim = d.variables[key].dimensions
        
        if datatype == "int32":
            var = output.createVariable(name, datatype, dim)
        else:
            if name == "station_id":
                var = output.createVariable("station_name", datatype, dim, fill_value=FILL_VALUE)
                data = output.getncattr('stn_station_number')
            else:
                var = output.createVariable(name, datatype, dim, fill_value=FILL_VALUE)
                data = None
        
        for att in d.variables[key].ncattrs():
            if att != '_FillValue':
                if att == "cf_role":
                    setattr(var, att, "timeseries_id")
                elif att == "long_name" and name == "station_id":
                    setattr(var, att, data)
                else:
                    setattr(var, att, d.variables[key].__dict__[att])
         
        if key in ['time', 'latitude','longitude','altitude']:       
            setattr(var, 'featureType', 'Point')
        else:
            setattr(var, 'featureType', 'Station')
           
        if data is None: 
            var[:] = d.variables[key][:]
        else:
            var[:] = list(data)
                
    d.close()
    output.close()
    

def copy_files(path_base, dest_base):
    for root, sub_folders, files in os.walk(dest_base):
        for file_in_root in files:
             
            try:
                os.remove(''.join([root,'\\',file_in_root]))
            except:
                print(''.join([root,'\\',file_in_root]),'\n ','file not found')
    
    
    #copy the files over
    
    file_types = ['.nc']
    for root, sub_folders, files in os.walk(path_base):
        for file_in_root in files:
             
            format_path = root.replace(path_base,'')
            
            index = file_in_root.rfind('.')
            if file_in_root[index:] in file_types:
                custom_copy(''.join([root,'\\',file_in_root]),
                       ''.join([dest_base,format_path,'\\',file_in_root]))
    
if __name__ == "__main__":
    copy_files(
               path_base = "C:\\Users\\chogg\\Documents\\GitHub\\wave-sensor\\netCDF_Instrument\\sandbox\\data",
               dest_base = "C:\\Users\\chogg\\Documents\\GitHub\\wave-sensor\\netCDF_Instrument\\sandbox\\data_copy")