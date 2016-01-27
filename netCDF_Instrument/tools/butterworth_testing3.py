import NetCDF_Utils.nc as nc
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

def butterworth_test3(fs = 4, cutoff = .00166666665, mode = 'phase'):
    '''Showing filtering and phase shift of created tide data (M2 and S2)'''
    fig = plt.figure(figsize=(12,4))
   
  
    x = nc.get_depth('M2_S2_plus4.nc')
    t = nc.get_time('M2_S2_plus4.nc')

    if mode == 'freq':
        
        ax = fig.add_subplot(111)
        
        hat = np.fft.rfft(x)
        freqs = np.fft.rfftfreq(len(x), d= 1.0/fs)
        
        ax.plot(freqs,np.abs(hat), 'b', alpha=.5)
        
        lowcut = cutoff / (.5 * fs)
        
        b, a = signal.butter(4, [lowcut], btype='lowpass')
        y = signal.filtfilt(b, a, x)
       
        yhat1 = np.fft.rfft(y)
        
        ax.plot(freqs,np.abs(yhat1),'r', alpha=.5)
        ax.set_title('4th order ButterWorth - 10 minute cutoff')
        plt.show()
        
        
    else:
        ax = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
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
    butterworth_test3(mode = 'freq')