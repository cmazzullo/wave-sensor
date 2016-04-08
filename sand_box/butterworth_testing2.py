import netCDF_Utils.nc as nc
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib as mp
import numpy as np


def butterworth_ts(fs = .1666666666, cutoff = .25):
    '''Proving stevens data phase shift is corrected'''
    fig = plt.figure(figsize=(12,4))
    ax = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
  
    x = nc.get_pressure('pressure3.nc')
    t = nc.get_time('pressure3.nc')
    
    lowcut = cutoff / (.5 * fs)
    # # # highcut = 1.5 / (.5 * fs)
    b, a = signal.butter(4, [lowcut], btype='lowpass')
    
    
    y = signal.lfilter(b, a, x)
    
    ax.plot(t,x,color="red", alpha=0.5)
    ax.plot(t,y,color="blue", alpha=0.5)

    z = signal.filtfilt(b, a, x)
    
    ax2.plot(t,x,color="red", alpha=0.5)
    ax2.plot(t,z,color="blue", alpha=0.5)
    
    plt.show()
    
    
if __name__ == '__main__':
    butterworth_ts(4, .25)