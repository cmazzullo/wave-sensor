import NetCDF_Utils.nc as nc
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

'''Showing the frequency before and after filtering and double filtering (and trends)'''
plot_trend = False
plot_pressure = True


# ax3 = fig.add_subplot(223)
# ax4 = fig.add_subplot(224)
# ax.set_title('Boxcar Filter')
# ax2.set_title('Butterworth Filter order 4')
# ax3.set_title('Butterworth Filt-Filt order 4')
# ax4.set_title('Butterworth Filter order 20')

fs = 4
# t = np.arange(0.,30., 1/fs)
# x = np.random.randn(len(t))

# x = nc.get_pressure('pressure4.nc')
# t = nc.get_time('pressure4.nc')
x = nc.get_pressure('real_data.nc')
t = nc.get_time('real_data.nc')
print(len(t))
average = np.average(x)
x = np.subtract(x,average)
 
hat = np.fft.rfft(x)
freqs = np.fft.rfftfreq(len(x), d= 1.0/fs)


# ax3.plot(freqs[1000:], np.abs(hat[1000:]), 'b', alpha=.5)
# ax4.plot(freqs[1000:], np.abs(hat[1000:]), 'b', alpha=.5)
# plt.plot(t,x)

# # 
lowcut = .00166666665 / (.5 * fs)
# # # highcut = 1.5 / (.5 * fs)
b, a = signal.butter(4, [lowcut], btype='lowpass')
# 
y = signal.lfilter(b, a, x)
  
yhat1 = np.fft.rfft(y)



boxcar_pressure = pd.rolling_window(x,center=True,window=120, win_type='boxcar',freq=.25)
series = pd.Series(boxcar_pressure,index=np.arange(0,len(boxcar_pressure)))
series = series.fillna(0)


bhat = np.fft.rfft(series.values)

z = signal.filtfilt(b,a,x)
# z2 = signal.filtfilt(b,a,z)
yhat2 = np.fft.rfft(z)
# b, a = signal.butter(4, [lowcut], btype='lowpass')
# 
# y = signal.lfilter(b, a, x)
# yhat3 = np.fft.rfft(y)



if plot_trend:
    fig = plt.figure(figsize=(12,4))
    ax = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    ax.plot(freqs[0:], np.abs(hat[0:]), 'b', alpha=.5)
    ax2.plot(freqs[0:], np.abs(hat[0:]), 'b', alpha=.5)
    final_hat = np.divide(bhat,hat)
    final_hat2 = np.divide(yhat1,hat)
#     final_hat3 = np.divide(yhat2,hat)
#     final_hat4 = np.divide(yhat3,hat)
    # final_hat = np.divide(bhat,hat)
    ax.plot(freqs[10:], np.abs(final_hat[10:]), alpha=0.5, color='r')
    ax2.plot(freqs[10:], np.abs(final_hat2[10:]), alpha=0.5, color='r')
#     ax3.plot(freqs[1000:], np.abs(final_hat3[1000:]), alpha=0.5, color='r')
#     ax4.plot(freqs[1000:], np.abs(final_hat4[1000:]), alpha=0.5, color='r')
    
    plt.show()
    
elif plot_pressure:
    fig = plt.figure(figsize=(12,4))
    ax = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    ax.plot(t,x)
    ax2.plot(t,z)
    plt.show()
    
else:
    fig = plt.figure(figsize=(12,4))
    ax = fig.add_subplot(111)
#     ax2 = fig.add_subplot(212)
    ax.plot(freqs[0:], np.abs(hat[0:]), 'b', alpha=.5)
#     ax2.plot(freqs[0:], np.abs(hat[0:]), 'b', alpha=.5)
    ax.plot(freqs[0:], np.abs(yhat2[0:]), 'r',alpha=.5)
#     ax2.plot(freqs[0:], np.abs(yhat2[0:]), 'r',alpha=.5)
#     ax3.plot(freqs[1000:], np.abs(yhat2[1000:]), 'r',alpha=.5)
#     ax4.plot(freqs[1000:], np.abs(yhat3[1000:]), 'r',alpha=.5)
    
    plt.show()
    



