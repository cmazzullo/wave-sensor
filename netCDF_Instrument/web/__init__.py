from bottle import route, run, static_file
import netCDF_Utils.nc as nc
from bottle import response, request, template
import bottle
import numpy as np
import webbrowser
import unit_conversion as uc
import pytz
from datetime import datetime
from tools.storm_options import StormOptions
from tools.multi_series_options import MultiOptions
import matplotlib.pyplot as plt
import os


def find_index(array, value):
    
    array = np.array(array)
    idx = (np.abs(array-value)).argmin()
    
    return idx

class BottleApp(object):
    
    def __init__(self):
        self.stat_data = None
        
        self.name = 'enable_cors'
        self.api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if bottle.request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(self,*args, **kwargs)

        return _enable_cors

    def process_data(self,so, s, e, dst, timezone, type=None):
        '''adjust the data based on the parameters and get storm object data'''
        
        #get meta data and water level
        so.get_meta_data()
        so.get_air_meta_data()
        so.get_wave_water_level()
        
        if type is not None and type=="stat":
            so.chunk_data()
            so.get_wave_statistics()
     
        
        #get the time from the netCDF file and adjust according to timezone and dst params
        start_datetime = uc.convert_ms_to_date(so.sea_time[0], pytz.utc)
        end_datetime = uc.convert_ms_to_date(so.sea_time[-1], pytz.utc)
        new_times = uc.adjust_from_gmt([start_datetime,end_datetime], timezone, dst)
        adjusted_times = np.linspace(uc.date_to_ms(new_times[0]), \
                                     uc.date_to_ms(new_times[1]), len(so.sea_time))
        
        #find the closest starting and ending index according to the params
        t_zone = pytz.timezone(timezone)
        milli1 = uc.date_to_ms(t_zone.localize(datetime.strptime(s,'%Y/%m/%d %H:%M')))
        milli2 = uc.date_to_ms(t_zone.localize(datetime.strptime(e,'%Y/%m/%d %H:%M')))
        s_index = find_index(adjusted_times,float(milli1))
        e_index = find_index(adjusted_times, float(milli2))
        
        #slice data by the index
        adjusted_times = adjusted_times[s_index:e_index:240]
        so.raw_water_level = so.raw_water_level[s_index:e_index:240]
        so.surge_water_level = so.surge_water_level[s_index:e_index:240]
        so.wave_water_level = so.wave_water_level[s_index:e_index:240]
        so.interpolated_air_pressure = so.interpolated_air_pressure[s_index:e_index:240]
        
        if type is not None and type=="stat":
            s_stat_index = find_index(so.stat_dictionary['time'],float(milli1))
            e_stat_index = find_index(so.stat_dictionary['time'], float(milli2))
            so.stat_dictionary['time'] = so.stat_dictionary['time'][s_stat_index:e_stat_index]
            for i in so.statistics:
                so.stat_dictionary[i] = so.stat_dictionary[i][s_stat_index:e_stat_index]
        
        #gather statistics if necessary
        
            
        return adjusted_times
        
        
    
    @route('/single_data', method='GET')
    def single_data(self):
        return template('single.html')
    
    @route('/multi_data', method='GET')
    def multi_data(self):
        return template('multi.html')
    
    @route('/spectra_data', method='GET')
    def spectra_data(self):
        return template('spectra.html')
    
    @route('/stat_data', method='GET')
    def stat_data(self):
        return template('statistics.html')
    
    @route('/<filename:path>', method="GET")
    def send_static(self, filename):
        return static_file(''.join(['./',filename]), root='./')
    
    
    @route('/single', method='POST')
    def single(self):
        '''This displays the single waterlevel and atmospheric pressure'''
        
        file_name = './data/SSS.true.nc'
        air_file_name = './data/SSS.hobo.nc'
        
        #get the request parameters
        s = request.forms.get('start_time', type=str)
        e = request.forms.get('end_time', type=str)
        dst = request.forms.get('daylight_savings')
        timezone = request.forms.get('timezone')
        
    #     filter = request.forms.get('filter')
       
        #add a response header so the service understands it is json
        response.headers['Content-type'] = 'application/json'
        
        #process data
        so = StormOptions()
        so.sea_fname = file_name
        so.air_fname = air_file_name
        
        #temp deferring implementation of type of filter
        adjusted_times = self.process_data(so, s, e, dst, timezone)
        
        #convert in format for javascript
        raw_final = []
        for x in range(0, len(adjusted_times)):
            raw_final.append({"x": adjusted_times[x], 'y':so.raw_water_level[x] * uc.METER_TO_FEET})
            
        surge_final = []
        for x in range(0, len(adjusted_times)):
            surge_final.append({"x": adjusted_times[x], 'y':so.surge_water_level[x] * uc.METER_TO_FEET})
            
        wave_final = []
        for x in range(0, len(adjusted_times)):
            wave_final.append({"x": adjusted_times[x], 'y':so.wave_water_level[x] * uc.METER_TO_FEET})
            
        air_final = []
        for x in range(0, len(adjusted_times)):
            air_final.append({"x": adjusted_times[x], 'y':so.interpolated_air_pressure[x] * uc.DBAR_TO_INCHES_OF_MERCURY})
         
        return {'raw_data': raw_final , 
                'surge_data': surge_final,
                'wave_data': wave_final,
                'air_data': air_final ,
                'latitude': float(so.latitude), 'longitude': float(so.longitude), 
                'air_latitude': float(so.air_latitude), 'air_longitude': float(so.air_longitude), 
                'sea_stn': [so.stn_station_number,so.stn_instrument_id],
                'air_stn': [so.air_stn_station_number,so.air_stn_instrument_id]}
        
        
    @route('/multiple', method='POST')
    def multiple(self):

        #get the request parameters
        s = request.forms.get('start_time', type=str)
        e = request.forms.get('end_time', type=str)
        dst = request.forms.get('daylight_savings')
        timezone = request.forms.get('timezone')
        toggle_state = request.forms.get('toggle_state')
        
        if toggle_state is None:
            tstate = [[1,1,1,0,0],[1,1,1,0,0]]
        else:
            tstate = toggle_state

        wv_data = ['./data/0_NYRIC13728_1510688_wv_chop.csv.nc',
                         './data/2_NYNEW07501_1510698_wv_chop.csv.nc',
                         './data/3_NYQUE04755_1510693_wl_chop.csv.nc',
                         './data/4_NYSUF00011_1511364_wl_chop.csv.nc',
                         './data/5_NYSUF04781_1510678_wv_chop.csv.nc'
                         ]
        
        bp_data = ['./data/0_NYRIC13728_1510688_bp_chop.csv.nc',
                         './data/2_NYNEW07501_1510698_bp_chop.csv.nc',
                         './data/3_NYQUE13828_10223966_bp_chop.csv.nc',
                         './data/4_NYSUF00011_1511364_bp_chop.csv.nc',
                         './data/5_NYSUF04781_1510678_bp_chop.csv.nc'
                         ]
        
        mo = MultiOptions()
        
        for x in range(0, len(tstate[0])):
            if tstate[0][x] == 1:
                mo.sea_fnames.append(wv_data[x])
                
        for x in range(0, len(tstate[1])):
            if tstate[1][x] == 1:
                mo.air_fnames.append(bp_data[x])
        
        mo.create_storm_objects()
        
        adjusted_times = []
        for x in range(0,len(mo.storm_objects)):
            adjusted_times.append(self.process_data(mo.storm_objects[x], s, e, dst, timezone))
            
        raw_final = []
        surge_final = []
        wave_final = []
        air_final = []
        for si in range(0,len(mo.storm_objects)):
            
            for x in range(0, len(adjusted_times)):
                raw_final.append({"x": adjusted_times[x], 'y':mo.storm_objects[si].raw_water_level[x] * uc.METER_TO_FEET})
                
            for x in range(0, len(adjusted_times)):
                surge_final.append({"x": adjusted_times[x], 'y':mo.storm_objects[si].surge_water_level[x] * uc.METER_TO_FEET})
                
            for x in range(0, len(adjusted_times)):
                wave_final.append({"x": adjusted_times[x], 'y':mo.storm_objects[si].wave_water_level[x] * uc.METER_TO_FEET})
                
            for x in range(0, len(adjusted_times)):
                air_final.append({"x": adjusted_times[x], 'y':mo.storm_objects[si].interpolated_air_pressure[x] \
                                  * uc.DBAR_TO_INCHES_OF_MERCURY})
        
        return {'raw_data': raw_final , 
                'surge_data': surge_final,
                'wave_data': wave_final,
                'air_data': air_final,
                'toggle_state': tstate}
        

    @route('/statistics', method='POST')
    def statistics(self):
        file_name = './data/SSS.true.nc'
        air_file_name = './data/SSS.hobo.nc'
        
        #get the request parameters
        s = request.forms.get('start_time', type=str)
        e = request.forms.get('end_time', type=str)
        dst = request.forms.get('daylight_savings')
        timezone = request.forms.get('timezone')
        change = request.forms.get('change')
       
        #add a response header so the service understands it is json
        response.headers['Content-type'] = 'application/json'
        
        if change == 'true':
            #process data
            so = StormOptions()
            so.sea_fname = file_name
            so.air_fname = air_file_name
            
            #temp deferring implementation of type of filter
            adjusted_times = self.process_data(so, s, e, dst, timezone, type="stat")
            
            stat_data = {}
            for i in so.statistics:
                stat = []
                for x in range(0, len(so.stat_dictionary['time'])):
                    stat.append({"x": so.stat_dictionary['time'][x], 'y':so.stat_dictionary[i][x]})
                    
                stat_data[i] = stat
                
            #add land surface elevation to water level so statistics can be superimposed
            wave_data = []
            scale = 0 - np.min(so.wave_water_level)        
            for x in range(0, len(adjusted_times)):
                wave_data.append({"x": adjusted_times[x], "y": (so.wave_water_level[x] + scale) * uc.METER_TO_FEET}) 
                
            stat_data['wave_wl'] = wave_data
            self.stat_data = stat_data
        
        return self.stat_data  
            

# webbrowser.open('http://localhost:8080/test')
if __name__ == '__main__':
   
    app = bottle.app()
    app.install(BottleApp())
    app.run(host='localhost', port=8080, debug=True)
