import netCDF4

class DataStore(object):
    
    def __init__(self, grouping, var_list = None):
        self.data__grouping = grouping
        self.time_var = None
        self.pressure_var = None
        self.pressure_var_qc = None
        self.lat_var = None
        self.lon_var = None
        self.z_var = None
        self.temp_var = None
        self.temp_var_qc = None
        self.calc_depth_var = None
        self.calc_depth_var = None
        self.global_vars_dict = {"test": "hello"}
        
    def get_global_vars(self, ds):
        for x in self.global_vars_dict:
            ds.setncattr(x,self.global_vars_dict[x])
            
    class PresureVar(object):
        
        def __init__(self):
            self.units = "test"
            
        def get_presure_vars(self,ds):
            ds.create
    
        
        