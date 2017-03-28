import pandas as pd
import numpy as np
import scipy
import matplotlib.pyplot as plt
import scipy.stats as st
import statsmodels.api as sm
from statsmodels.graphics.api import qqplot
import statsmodels as st_sm
import datetime
import statsmodels

plt.rcParams['figure.figsize'] = (16,10)

def mean_forecast_err(y, yhat):
    return np.mean(y - yhat)

def spec_moment(freq,spec,n):
    '''trapezoidal rule for integrating over a spectrum to get the appropriate 
    spectral moment'''
    return np.trapz(spec * freq**n, x=freq)

def band_average_psd(freqs, psd_amps, df):
    '''method to average spectra bands at a center frequency'''
    new_freqs = []     
    new_amps = []
    step, index = int(df/2), 0
    
    #WHILE THE INDEX IS LESS THAN FREQUENCY ARRAY LENGTH, AVERAGE EVERY 16 FREQUENCY BANDS
    #AND ADD THE CENTER FREQUENCY TO THE NEW LIST OF FREQUENCIES
    while index < len(freqs):
        
        new_freqs.append(np.average(freqs[np.arange(index,index+step)]))
        new_amps.append(np.average(psd_amps[np.arange(index,index+step)]))
        index += step;
    
    psd_avg_amps = np.array(new_amps)      
    freqs = np.array(new_freqs)
    
    #CUTOFF ALL FREQUENCIES THAT ARE GREATER THAN 1HZ
#         high_cut_off = np.where(freqs <= .0000047)
#         freqs = freqs[high_cut_off]
#         psd_avg_amps = psd_avg_amps[high_cut_off].real
    
#         low_cut_off = np.where(freqs >= .0000008)
#         freqs = freqs[low_cut_off]
#         psd_avg_amps = psd_avg_amps[low_cut_off]
    
    return freqs, psd_avg_amps
    
def interpolate_nans(data):
    real_values = np.invert(np.isnan(data))
    xp = real_values.nonzero()[0]
    fp = data[xp]
    
    nan_values = np.isnan(data)
    x = nan_values.nonzero()[0]
    data[nan_values] = np.interp(x, xp, fp)
    
    return data

def normal_val(vals):
    val_min = np.abs(np.min(vals))
    val_max = np.max(np.max(vals))
    if val_min > val_max:
        return val_min
    else:
        return val_max
    
df = pd.read_csv("Connecticut.csv") 
df.columns = ["1","2","3"]
df["1"] = [datetime.datetime(1890, 1, 1) + datetime.timedelta(int(x)) for x in df["1"]]
df["2"] = interpolate_nans(df["2"].values)
df["3"] = interpolate_nans(df["3"].values)
df.set_index("1", inplace=True)

window_size = 30
start, end = 41, window_size + 41
step = 1
deg_of = window_size / 16
bic = True

time = []
max_corr = []

max_coherence = []
mean_coherence_period = []
coherence_area = []
discharge_resid, nitrate_resid = [], []

fails2 = []
fails3 = []

while end <= df.shape[0]:#df.shape[0] - (df.shape[0] % window_size):
    temp_df = df[start:end].copy()
    
#     if bic:
#         discharge_order = \
#         st_sm.api.tsa.stattools.arma_order_select_ic(temp_df["2"]) \
#         .bic_min_order
#         
#         nitrate_order = \
#         st_sm.api.tsa.stattools.arma_order_select_ic(temp_df["3"]) \
#         .bic_min_order
#     else:
#         discharge_order = \
#         st_sm.api.tsa.stattools.arma_order_select_ic(temp_df["2"]) \
#         .aic_min_order
#         
#         nitrate_order = \
#         st_sm.api.tsa.stattools.arma_order_select_ic(temp_df["3"]) \
#         .aic_min_order
    cont = False
    
#     try:
    arma_mod_discharge = sm.tsa.ARMA(temp_df["2"], (2,1)).fit()
        
#     except:
#         fails2.append(start)
#         cont = True
#     
#     try:
    arma_mod_nitrate = sm.tsa.ARMA(temp_df["3"], (2,1)).fit()
#     except:
#         fails3.append(start)
#         cont = True
        
    if cont:
        start += step
        end += step
        continue
    
    resid = pd.Series(arma_mod_discharge.resid.values)
    resid2 = pd.Series(arma_mod_nitrate.resid.values)
    
    discharge_resid.append(resid)
    nitrate_resid.append(resid2)
    
    
#     corr = st_sm.api.tsa.stattools.ccf(resid \
#                                     ,resid2, \
#                                      unbiased=False)
#     
#     time.append(temp_df.index[window_size/2])
#     max_corr.append(corr[np.max(np.abs(corr)).argmax()])
# 
#     scale = (temp_df.shape[0]/2) * 4.0
#     Pxx = np.fft.fft(resid)
#     Pxx = Pxx * np.conjugate(Pxx) / scale
#     freqs_og = np.fft.rfftfreq(window_size,d=86400)[1:]
#     freqs_X, newPxx = band_average_psd(freqs_og, Pxx[1:], deg_of)
#      
#     Pyy = np.fft.fft(resid2)
#     Pyy = Pyy * np.conjugate(Pyy) / scale
#     freqs_ogy = np.fft.rfftfreq(window_size,d=86400)[1:]
#     freqs_Y, newPyy = band_average_psd(freqs_ogy, Pyy[1:], deg_of)
#     
#     Pxy = np.conjugate(np.fft.rfft(resid)*np.fft.rfft(resid2)) / scale
#     freqs_ogxy = np.fft.rfftfreq(window_size,d=86400)[1:]
#     freqs_XY, newPxy = band_average_psd(freqs_ogxy, Pxy[1:], deg_of)
#     
#     new_coh = np.abs(newPxy)**2 / newPxx / newPyy
#     
#     coherence_area.append(np.max(new_coh))
#     mean_coherence_period.append(freqs_XY[np.max(new_coh).argmax()])
#     
    start += step
    end += step
#     
    print(end)
    
    
# df2 = pd.DataFrame(discharge_resid)
# df2.to_csv(path_or_buf="discharge_residuals_ar_2.csv")
# 
# df3 = pd.DataFrame(nitrate_resid)
# df3.to_csv(path_or_buf="nitrate_residuals_ar_2.csv")
for x in fails2:
    print(x)
    
for x in fails3:
    print(x)


