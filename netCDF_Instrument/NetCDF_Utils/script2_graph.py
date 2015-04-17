import mpl_toolkits.axes_grid1 as host_plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.image as image
import mpl_toolkits.axisartist as AA
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib as mp
import netCDF4
from netCDF4 import Dataset
import numpy as np
import pandas as pd

def make_depth_graph(in_file_name, box_car_points):
    '''To compare water_pressure and depth in a graph by consuming a netCDF file'''
    
    #global options for matplotlib
    font = {'family' : 'Bitstream Vera Sans',
        'size'   : 18}

    mp.rc('font', **font)
    plt.rcParams['figure.figsize'] = (14,10)
    plt.rcParams['figure.facecolor'] = 'white'
 
    #reading
    ds = Dataset(in_file_name)
    time = netCDF4.num2date(ds.variables['time'][:],ds.variables['time'].units)
    sea_pressure = ds.variables['sea_water_pressure'][:]
    pressure_qc = ds.variables['pressure_qc'][:]
    depth_qc = ds.variables['depth_qc'][:]
    depth = ds.variables['depth'][:]
    ds.close();
    
    #convert dbars to psi   *Possibly convert meters to feet later on*
    sea_pressure = np.multiply(sea_pressure,1.45037738)
    
    #create dataframe
    data = {'Pressure': pd.Series(sea_pressure,index=time),
            'PressureQC': pd.Series(pressure_qc, index=time),
            'Depth': pd.Series(depth, index=time),
            'DepthQC': pd.Series(depth_qc, index=time)}
    df = pd.DataFrame(data)
    
    #Boxcar average for aesthetic purposes if desired
    if box_car_points > 0:
        df.Pressure = pd.rolling_window(df.Pressure,center=True,window=box_car_points, win_type='boxcar')
        df.Depth = pd.rolling_window(df.Depth,center=True,window=box_car_points, win_type='boxcar')
    
    #check if the pressure and depth pints do not pass QC
    pqc = df[(df.PressureQC != 11111111) & (df.PressureQC != 11110111)]
    dqc = df[(df.DepthQC != 11111111) & (df.DepthQC != 11110111)]
    
    #if points did not pass QC assign NaN to its value
    df.loc(pqc.index).Pressure = np.NaN
    df.loc(dqc.index).Depth = np.NaN
      
    #Read images 
    logo = image.imread('usgs.png', None)
    legend = image.imread('legend.png', None)

    #Create grids for section formatting
    gs = gridspec.GridSpec(2, 2,
                       width_ratios=[1,2],
                       height_ratios=[1,4]
                       )
   
    #---------------------------------------Logo Section
    ax2 = host_plt.host_subplot(gs[0,0])
    ax2.imshow(logo)
    ax2.axes.get_yaxis().set_visible(False)
    ax2.axes.get_xaxis().set_visible(False)
  
    #-----------------------------------------Data Section
    
    #create mirror subplot of first so that there can be two overlapping y axis labels
    ax = host_plt.host_subplot(gs[1,0:],axes_class=AA.Axes)
    par1 = ax.twinx()
 
    ax.set_ylabel('Barometric Pressure in Pounds Per Square Inch')
    par1.set_ylabel('Water Elevation in Meters')
   
    #plot major grid lines
    plt.grid(b=True, which='major', color='grey', linestyle="-")
    
    #converts dates to numbers for matplotlib to consume
    time_nums = [mdates.date2num(x) for x in df.Pressure.index]
    
    #x axis formatter for dates (function format_date() below)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
   
    #get minimum depth, then plot the pressure, depth, and min depth
    depth_min = np.min(df.Depth)
    p1, = ax.plot(time_nums,df.Pressure, color="red")
    p2, = par1.plot(time_nums,df.Depth, color="blue")
    p3, = par1.plot(time_nums,np.repeat(depth_min, len(df.Depth)), linestyle="--", color="orange")
   
    ax.toggle_axisline('')
    
    #Legend options not needed but for future reference
    ax.legend([p2,p3,p1],['Water Elevation',
    'Min Recordable Water Elevation','Barometric Pressure',], bbox_to_anchor=(.95, 1.37), loc=1, borderaxespad=0.0)
 
    plt.show()

def format_date(x,arb=None):
    '''Format dates so that they are padded away from the x-axis'''
    date_str = mdates.num2date(x).strftime('%I:%M %p \n %b-%d-%Y')
    return ''.join([' ','\n',date_str])    
    
if __name__ == '__main__':
    
    make_depth_graph('depth.nc',25)
    
    