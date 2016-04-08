from bottle import route, run
import netCDF_Utils.nc as nc
from bottle import response, request, template
import bottle
import numpy as np
import webbrowser
import unit_conversion as uc
import pytz
from datetime import datetime
from tools.storm_options import StormOptions
import matplotlib.pyplot as plt

# the decorator
def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors

def find_index(array, value):
    
    array = np.array(array)
    print(array-value)
    idx = (np.abs(array-value)).argmin()
    
    return idx

@route('/get')
@enable_cors
def hello():
    response.headers['Content-type'] = 'application/json'
    time = nc.get_time('MDWOR04586.csv.nc')
    pressure = nc.get_pressure('MDWOR04586.csv.nc')
    
    time = time[::240]
    pressure = pressure[::240]
    
    final = []
    for x in range(0, len(time)):
        final.append({"x": time[x], 'y': pressure[x]})
        
    return {'data': final}

@route('/newGraph', method='POST')
@enable_cors
def newGraph():
    '''This displays the single waterlevel and atmospheric pressure'''
    
    file_name = 'SSS.true.nc'
    air_file_name = 'SSS.hobo.nc'
    
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
    so.get_meta_data()
    so.get_air_meta_data()
    so.get_wave_water_level()
 
    
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
    print('milli',milli1,milli2)
    s_index = find_index(adjusted_times,float(milli1))
    e_index = find_index(adjusted_times, float(milli2))
    
    #slice data by the index
    adjusted_times = adjusted_times[s_index:e_index:240]
    so.raw_water_level = so.raw_water_level[s_index:e_index:240]
    so.surge_water_level = so.surge_water_level[s_index:e_index:240]
    so.wave_water_level = so.wave_water_level[s_index:e_index:240]
    so.interpolated_air_pressure = so.interpolated_air_pressure[s_index:e_index:240]
    
    #convert in format for javascript
    raw_final = []
    for x in range(0, len(adjusted_times)):
        raw_final.append({"x": adjusted_times[x], 'y':so.raw_water_level[x]})
        
    surge_final = []
    for x in range(0, len(adjusted_times)):
        surge_final.append({"x": adjusted_times[x], 'y':so.surge_water_level[x]})
        
    wave_final = []
    for x in range(0, len(adjusted_times)):
        wave_final.append({"x": adjusted_times[x], 'y':so.wave_water_level[x]})
        
    air_final = []
    for x in range(0, len(adjusted_times)):
        air_final.append({"x": adjusted_times[x], 'y':so.interpolated_air_pressure[x]})
     
    return {'raw_data': raw_final, 
            'surge_data': surge_final,
            'wave_data': wave_final,
            'air_data': air_final,
            'latitude': float(so.latitude), 'longitude': float(so.longitude), 
            'air_latitude': float(so.air_latitude), 'air_longitude': float(so.air_longitude), 
            'sea_stn': [so.stn_station_number,so.stn_instrument_id],
            'air_stn': [so.air_stn_station_number,so.air_stn_instrument_id]}

@route('/test')
def test():
    return template('./templates/lines.tpl')

@route('/test2')
def test2():
    return template('./templates/lines2.tpl')

# webbrowser.open('http://localhost:8080/test')
run(host='localhost', port=8080, debug=True)
