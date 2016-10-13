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

#mock data base
wv_data = ['./data/0_NYRIC13728_1510688_wv_chop.csv.nc',
                        './data/2_NYNEW07501_1510698_wv_chop.csv.nc',
                        './data/3_NYQUE04755_1510693_wl_chop.csv.nc',
                        './data/4_NYSUF00011_1511364_wl_chop.csv.nc',
                        './data/5_NYSUF04781_1510678_wv_chop.csv.nc',
                        './data/6_wv.nc',
                        './data/SSS.true.nc',
                        './data/wv.nc'
                         ]
         
bp_data = ['./data/0_NYRIC00002_9800742_bp_chop.csv.nc',
                        './data/2_NYNEW07501_1510685_bp_chop.csv.nc',
                        './data/3_NYQUE13828_10223966_bp_chop.csv.nc',
                        './data/4_NYSUF00011_1510699_bp_chop.csv.nc',
                        './data/5_NYSUF04781_1411333_bp_chop.csv.nc',
                        './data/6_bp.nc',
                        './data/SSS.hobo.nc',
                        './data/bp.nc'
                         ]

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

    def process_data(self,so, s, e, dst, timezone, step, data_type=None):
        '''adjust the data based on the parameters and get storm object data'''
        
        #get meta data and water level
        so.get_meta_data()
        so.get_air_meta_data()
        so.get_wave_water_level()
        
        if data_type is not None and data_type=="stat":
            so.chunk_data()
            so.get_wave_statistics()
            
        if data_type is not None and data_type=="wind":
            so.get_wind_meta_data()
            
     
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
        adjusted_times = adjusted_times[s_index:e_index:step]
        so.raw_water_level = so.raw_water_level[s_index:e_index:step]
        so.surge_water_level = so.surge_water_level[s_index:e_index:step]
        so.wave_water_level = so.wave_water_level[s_index:e_index:step]
        so.interpolated_air_pressure = so.interpolated_air_pressure[s_index:e_index:step]
        
        if data_type is not None and data_type=="wind":
            so.sea_time = adjusted_times
            so.slice_wind_data()
        
        #This is assuming SO object gets modified by reference
        if data_type is not None and data_type=="stat":
            s_stat_index = find_index(so.stat_dictionary['time'],float(milli1))
            e_stat_index = find_index(so.stat_dictionary['time'], float(milli2))
            so.stat_dictionary['time'] = so.stat_dictionary['time'][s_stat_index:e_stat_index]
            for i in so.statistics:
                if i != 'PSD Contour':
                    so.stat_dictionary[i] = so.stat_dictionary[i][s_stat_index:e_stat_index]
        
        #gather statistics if necessary  
        return adjusted_times
        
    @route('/single_data', method='GET')
    def single_data(self):
        return template('single.html')
    
    @route('/multi_data', method='GET')
    def multi_data(self):
        return template('multi.html')
    
    @route('/multi_data2', method='GET')
    def multi_data2(self):
        return template('multi2.html')
    
    @route('/spectra_data', method='GET')
    def spectra_data(self):
        return template('spectra.html')
    
    @route('/stat_data', method='GET')
    def stat_data(self):
        return template('statistics.html')
    
    @route('/test', method='GET')
    def test(self):
        return template('test_graph.html')
    
    @route('/<filename:path>', method="GET")
    def send_static(self, filename):
        return static_file(''.join(['./',filename]), root='./')
    
    
    @route('/single', method='POST')
    def single(self):
        '''This displays the single waterlevel and atmospheric pressure'''
        
        #get the request parameters
        s = request.forms.get('start_time', type=str)
        e = request.forms.get('end_time', type=str)
        dst = request.forms.get('daylight_savings')
        timezone = request.forms.get('timezone')
        sea_file = request.forms.get('sea_file')
        baro_file = request.forms.get('baro_file')
        multi = request.forms.get('multi')
    
        if sea_file is None:
            file_name = './data/SSS.true.nc'
            air_file_name = './data/SSS.hobo.nc'
        else:
            file_name = wv_data[int(sea_file)]
            air_file_name = bp_data[int(baro_file)]
        
    #     filter = request.forms.get('filter')
       
        #add a response header so the service understands it is json
        response.headers['Content-type'] = 'application/json'
        
        #process data
        so = StormOptions()
        so.sea_fname = file_name
        so.air_fname = air_file_name
        so.high_cut = 1.0
        so.low_cut = 0.045
        
        #temp deferring implementation of type of filter
        if multi == 'True':
            step = 200
        else:
            step = 25
            
        adjusted_times = self.process_data(so, s, e, dst, timezone, step=step)
        
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
        

    @route('/statistics', method='POST')
    def statistics(self):
        
        #get the request parameters
        s = request.forms.get('start_time', type=str)
        e = request.forms.get('end_time', type=str)
        dst = request.forms.get('daylight_savings')
        timezone = request.forms.get('timezone')
        sea_file = request.forms.get('sea_file')
        baro_file = request.forms.get('baro_file')
        #add a response header so the service understands it is json
        response.headers['Content-type'] = 'application/json'
        
        if sea_file is None:
            file_name = './data/SSS.true.nc'
            air_file_name = './data/SSS.hobo.nc'
        else:
            file_name = wv_data[int(sea_file)]
            air_file_name = bp_data[int(baro_file)]
            
        #process data
        so = StormOptions()
        so.sea_fname = file_name
        so.air_fname = air_file_name
        so.high_cut = 1.0
        so.low_cut = 0.045
        
        #temp deferring implementation of type of filter
        self.process_data(so, s, e, dst, timezone, 25, data_type="stat")
        stat_data = {}
        
        ignore_list = ['PSD Contour', 'time', 'Spectrum', 'HighSpectrum', 'LowSpectrum', 'Frequency']
        for i in so.stat_dictionary:
            if i not in ignore_list:
                stat = []
                upper_ci = []
                lower_ci = []
                for x in range(0, len(so.stat_dictionary['time'])):
                    stat.append({"x": so.stat_dictionary['time'][x], 'y':so.stat_dictionary[i][x]})
                    upper_ci.append({"x": so.stat_dictionary['time'][x], 'y':so.upper_stat_dictionary[i][x]})
                    lower_ci.append({"x": so.stat_dictionary['time'][x], 'y':so.lower_stat_dictionary[i][x]})
                
                stat_data[i] = stat
                stat_data[''.join(['upper_', i])] = upper_ci
                stat_data[''.join(['lower_', i])] = lower_ci
        #add land surface elevation to water level so statistics can be superimposed
#             wave_data = []
#             scale = 0 - np.min(so.wave_water_level)        
#             for x in range(0, len(adjusted_times)):
#                 wave_data.append({"x": adjusted_times[x], "y": (so.wave_water_level[x] + scale) * uc.METER_TO_FEET}) 
#                 
#             stat_data['wave_wl'] = wave_data
        self.stat_data = stat_data
        
        return self.stat_data
    
    @route('/psd_contour', method='POST')
    def psd_contour(self):
        
        #get the request parameters
        s = request.forms.get('start_time', type=str)
        e = request.forms.get('end_time', type=str)
        dst = request.forms.get('daylight_savings')
        timezone = request.forms.get('timezone')
        sea_file = request.forms.get('sea_file')
        baro_file = request.forms.get('baro_file')
        
        #keep this number static for now, will make dynamic if necessary
        num_colors = 11
        #add a response header so the service understands it is json
        response.headers['Content-type'] = 'application/json'
        
        if sea_file is None:
            file_name = './data/SSS.true.nc'
            air_file_name = './data/SSS.hobo.nc'
        else:
            file_name = wv_data[int(sea_file)]
            air_file_name = bp_data[int(baro_file)]
            
        #process data
        so = StormOptions()
        so.sea_fname = file_name
        so.air_fname = air_file_name
        so.high_cut = 1.0
        so.low_cut = 0.045
        
        #temp deferring implementation of type of filter
        self.process_data(so, s, e, dst, timezone, 25, data_type="stat")
        
        psd_data = {}
        #Get the min and max for the PSD since it is easier to compute on the server
        
        print('time len', len(so.stat_dictionary['time']))
        x_max = so.stat_dictionary['time'][len(so.stat_dictionary['time'])-1]
        x_min = so.stat_dictionary['time'][0]
        
        freqs = [x for x in so.stat_dictionary['Frequency'][0] if x > .033333333]
        y_min = 1.0/np.max(freqs)
        y_max = 1.0/np.min(freqs)
        z_max = np.max(np.max(so.stat_dictionary['Spectrum'], axis = 1))
        z_min = np.min(np.min(so.stat_dictionary['Spectrum'], axis = 1))
                
        z_range = np.linspace(z_min, z_max, num_colors)
        
        print(z_range[1] - z_range[0])
        
       
        psd_data['x'] = list(so.stat_dictionary['time'])
#         psd_data['y'] = list(so.stat_dictionary['Frequency'][0])
        psd_data['z'] = list([list(x) for x in so.stat_dictionary['Spectrum']])
        psd_data['x_range'] = list([x_min,x_max])
        psd_data['y_range']  = list([y_min,y_max])
        psd_data['z_range'] = list(z_range)
       
        self.psd_data = psd_data
        self.stat_so = so.stat_dictionary
        
        return self.psd_data   
    
    def find_index(self, array, value):
    
        array = np.array(array)
        idx = (np.abs(array-value)).argmin()
    
        return idx

    @route('/single_psd', method='POST')
    def single_psd(self):
        
        #get the request parameters
        s = request.forms.get('spectra_time', type=float)
        
        single_psd = {'Spectrum': [], 'upper_Spectrum': [], 'lower_Spectrum': []}
        index = self.find_index(self.psd_data['x'], s)
        
        for x in range(0,len(self.stat_so['Frequency'][0])):
            
            single_psd['Spectrum'].append({'x': self.stat_so['Frequency'][0][x],
                                          'y': self.stat_so['Spectrum'][index][x]})
            single_psd['upper_Spectrum'].append({'x': self.stat_so['Frequency'][0][x],
                                          'y': self.stat_so['HighSpectrum'][index][x]})
            single_psd['lower_Spectrum'].append({'x': self.stat_so['Frequency'][0][x],
                                          'y': self.stat_so['LowSpectrum'][index][x]}) 
        
        single_psd['time'] = self.psd_data['x'][index]
        #add a response header so the service understands it is json
        response.headers['Content-type'] = 'application/json'
        
        return single_psd
    
    @route('/wind', method='POST')
    def wind(self):
        
        #get the request parameters
        s = request.forms.get('start_time', type=str)
        e = request.forms.get('end_time', type=str)
        dst = request.forms.get('daylight_savings')
        timezone = request.forms.get('timezone')
        sea_file = request.forms.get('sea_file')
        baro_file = request.forms.get('baro_file')
        
        response.headers['Content-type'] = 'application/json'
        
        if sea_file is None:
            file_name = './data/SSS.true.nc'
            air_file_name = './data/SSS.hobo.nc'
        else:
            file_name = wv_data[int(sea_file)]
            air_file_name = bp_data[int(baro_file)]
            
        so = StormOptions()
        so.sea_fname = file_name
        so.air_fname = air_file_name
        so.wind_fname = "./data/ny_wind.nc"
        
        self.process_data(so, s, e, dst, timezone, 1, data_type="wind")
        
        wind = {'Wind_Speed': None, 'Wind_Direction': None}
        
        wind['Wind_Speed'] = so.derive_wind_speed(so.u, so.v)
        wind['Wind_Max'] = np.max(wind['Wind_Speed'])
        wind['Wind_Direction'] = so.derive_wind_direction(so.u, so.v)
        wind['time'] = list(so.wind_time)
        
        #add a response header so the service understands it is json
        response.headers['Content-type'] = 'application/json'
        
        
        return wind
    
# webbrowser.open('http://localhost:8080/test')
if __name__ == '__main__':
   
    app = bottle.app()
    app.install(BottleApp())
    app.run(host='localhost', port=8080, debug=True)
