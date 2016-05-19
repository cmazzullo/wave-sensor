import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from tools.storm_options import StormOptions
import pytz
import unit_conversion

x_data = []
y_data = []
smax, smin = None, None

def format_date(x,arb=None):
        '''Format dates so that they are padded away from the x-axis'''
        scale_index = int(float(len(so.stat_dictionary['time'])/2500.0) * x)
        
        
        if scale_index >= len(so.stat_dictionary['time']):
            scale_index = len(so.stat_dictionary['time']) -1
        date = unit_conversion.convert_ms_to_date(so.stat_dictionary['time'][scale_index], pytz.UTC)
        format_date = mdates.date2num(date)
        
        date_str = mdates.num2date(format_date).strftime('%b-%d-%Y \n %H:%M')
        return ''.join([' ','\n',date_str])
    
def format_spec(x,arb=None):
        '''Format dates so that they are padded away from the x-axis'''
        index = int(x*10.0)
        print('index',index)
        if index -1 >=0:
            return '%.6f' % np.linspace(smin,smax,10)[index-1]
        else:
            return 0
    
def my_formatter_fun(x, p):
    if x >= 0 and x <= 2000:
        fl = '%.1f' % (1 / so.stat_dictionary['Frequency'][0][int(x)])
        if fl[len(fl) - 1] == '1':
            fl = ''.join([fl[0:len(fl)-1],'0'])
        return fl
    

#     so.stat_dictionary['Frequency'][x]

so = StormOptions()
so.sea_fname = 'DEKEN11529 BHN4.csv.nc'
so.air_fname = 'DEKEN11529 BHN4a.nc'
so.get_meta_data()
so.get_air_meta_data()
so.get_wave_water_level()
so.chunk_data()
so.get_wave_statistics()

data = np.transpose(so.stat_dictionary['Spectrum'])


font = {'family' : 'Bitstream Vera Sans',
                    'size'   : 13}
        
matplotlib.rc('font', **font)
plt.rcParams['figure.figsize'] = (14,9)
plt.rcParams['figure.facecolor'] = 'white'


figure = plt.figure(figsize=(14,9))

smax = np.max([np.max(x) for x in so.stat_dictionary['Spectrum']])
smin = np.min([np.min(x) for x in so.stat_dictionary['Spectrum']])


ax = figure.add_subplot('111')
ax.set_title('Wave Period Vs. Spectral Energy Over Time (DEKEN11529)')
image = ax.imshow(data**.125, extent=[0,2500,2048,0],vmin=0, vmax=1, aspect=1)
colorbar = figure.colorbar(image)
colorbar.set_label('Energy in $m^{1/4} / Hz$')
colorbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(format_spec))

ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(my_formatter_fun))
ax.set_ylabel('Time in GMT')
ax.set_ylabel('Wave Period in Seconds')
ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
ax.set_yticks([50,100,200,500,1000,2000])
ax.grid(b=True, which='major', color='black', linestyle="-")

plt.show()