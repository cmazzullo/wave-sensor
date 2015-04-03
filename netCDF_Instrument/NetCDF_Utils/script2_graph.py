import mpl_toolkits.axes_grid1 as host_plt
import matplotlib.dates as mdates
import mpl_toolkits.axisartist as AA
import matplotlib.pyplot as plt
import netCDF4
from netCDF4 import Dataset
import numpy as np

def make_depth_graph(in_file_name):
    ds = Dataset(in_file_name)
    time = netCDF4.num2date(ds.variables['time'][:],ds.variables['time'].units)
    sea_pressure = ds.variables['sea_water_pressure'][:]
    depth = ds.variables['depth'][:]
    ds.close();

    sea_pressure = np.multiply(sea_pressure,1.45037738)
    
    plt.Figure(figsize=(12,4))
    ax = host_plt.host_subplot(111,axes_class=AA.Axes)
    
    par1 = ax.twinx()
  
    ax.set_ylabel('Pressure in PSI')
    par1.set_ylabel('Depth in Meters')
   
    plt.grid(b=True, which='major', color='grey', linestyle="-")
    
    #formats the x axis time labels
    time_nums = [mdates.date2num(x) for x in time[0:10000]]
    time_format = mdates.DateFormatter('%H:%M %p \n %d')
    ax.xaxis.set_major_formatter(time_format)
    
    
    p1, = ax.plot(time[0:10000],sea_pressure[0:10000], color="red",alpha=.5)
    p2, = par1.plot(time[0:10000],depth[0:10000], color="blue", alpha=.5)
    
    #ax.set_xticklabels(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.title('Water Pressure and Depth')
    plt.show()
    
if __name__ == '__main__':
    make_depth_graph('depth.nc')
    
    