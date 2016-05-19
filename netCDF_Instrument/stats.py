from matplotlib.pyplot import *
import numpy as np
import scipy.stats as stats
import unit_conversion as uc
import pressure_to_depth as p2d
import scipy.signal as signal

#Statistics calculation pulled from Storm Surge Matlab Project by
#Joe Vrabel and Sam Rendon at the USGS in Texas

G = uc.GRAVITY
std_dev = False
spectrum = None
frequencies = None
last_t = None

class Stats(object):

    def __init__(self):
        pass
        
        
    def power_spectrum(self, y, tstep):
        """Calculate the power spectrum of the series y"""
        spec = abs(np.fft.rfft(y))**2 / (len(y)/2)
        freqs = np.fft.rfftfreq(len(y), d=tstep)
        freqs = freqs[0:len(y)/2 + 1]
        spec = spec[1:]
        self.frequencies = freqs = freqs[1:]
         
       
       
        h = np.abs(np.mean(y))
     
    #     #radial frequency Units 1/T
        om2 = np.array((2* np.pi * freqs) ** 2)
          
    #     print(np.sqrt(np.tanh(om2 * h / G)))
    #     print(np.sqrt(np.tanh(om2 * h / G)))
          
        #1st wavenumber estimate
        k = om2 / (G * np.sqrt(np.tanh(om2 * h / G)))
          
        #tangent iteration to get better estimate of wavenumber
        for x in range(0,6):
            f0 = om2 - G * k * np.tanh(k * h)
            dfdk = -G * np.tanh(k*h) - G*k*h / ((np.cosh(k*h))**2)
            k = k - f0/dfdk
              
        #adjust power spectrum by the calculated wavenumber
          
        #pressure respnse factor
        kp = np.array(np.cosh(k*h))
          
        #scale
        spec = (spec * (kp**2)) * (kp < 11).astype(float)
    #     
        return freqs, spec

#         return signal.welch(y, 1/tstep, nperseg=256, window='hanning', detrend='linear')
        
    def welch_power_spectrum(self, y,tstep):
        """Welch power spectrum"""
        return signal.welch(y, 1/tstep, nperseg=256, window='hann', detrend='linear')
    
    def moment(self, x, y, n):
        """Calculate the nth statistical moment of the x, y data."""
        
        return np.trapz(y * x**n, x=x)
    
    
    def spec_moment(self, n, spec, freq):
        """Calculate the nth statistical moment of the data's power spectrum."""
        
        moment = self.moment(freq, spec, n)    
        return moment
    
    def median_wave_height(self, spec, freq, t, depth):
        if not std_dev:
            return 2.36 * np.sqrt(self.spec_moment(0, spec, freq))
        
        return 2.36 * np.std(depth)
    
    
    def rms_wave_height(self, spec, freq, t, depth):
        if not std_dev:
            return 2.83 * np.sqrt(self.spec_moment(0, spec, freq))
        
        return 2.83 * np.std(depth)
    
    
    def significant_wave_height(self, spec, freq, t, depth):
        '''There is a discrepancy regarding the calculation sig wave height
        , will have to understand the context of the implementation better'''
        if not std_dev:
            return 4 * np.sqrt(self.spec_moment(0, spec, freq))
        
        return 4 * np.std(depth) 
   
    
    def maximum_wave_height(self, spec, freq, t, depth):
        if not std_dev:
            return 1.86 * 4 * np.sqrt(self.spec_moment(0, spec, freq))
        
        return 1.86 * 4 * np.std(depth)
    
    
    def ten_percent_wave_height(self, spec, freq, t, depth):
        if not std_dev:
            return 5.091 * np.sqrt(self.spec_moment(0, spec, freq))
        
        return 5.091 * np.std(depth)
    
    
    def one_percent_wave_height(self, spec, freq, t, depth):
        if not std_dev:
            return 6.672 * np.sqrt(self.spec_moment(0, spec, freq))
        
        return 6.672 * np.std(depth)
    
    
    def significant_wave_height_standard(self, depth):
        return 4 * np.std(depth)
    
    
    def average_wave_height(self, spec, freq, t, depth):
        if not std_dev:
            return 2.51 * np.sqrt(self.spec_moment(0,spec, freq))
        
        return 2.51 * np.std(depth)
    
    
    def average_zero_crossing_period(self, spec, freq, t, depth):
        return np.sqrt(self.spec_moment(0, spec, freq) / self.spec_moment(2, spec, freq))
    
    
    def mean_wave_period(self, spec, freq, t, depth):
        return self.spec_moment(0, spec, freq) / self.spec_moment(1, spec, freq)
    
    
    def crest_wave_period(self, spec, freq, t, depth):
        return np.sqrt(self.spec_moment(2, spec, freq) / self.spec_moment(4, spec, freq))
    
    
    def peak_wave_period(self, spec, freq, t, depth):
        '''value given in seconds; inverse of the frequency with the highest energy in the reported spectrum.'''   
        return 1/ freq[np.argmax(spec)]
    
    
    def significant_wave_period(self, spec, freq, depth, tstep):
        freq_max = freq[np.argmax(np.abs(spec))]
        return .9451 / freq_max
    
    
    def split_into_chunks(self, depth, tstep, chunk_length):
        """Split an array into chunks of size chunk_length.
    
        chunk_length and tstep must have the same units of time (seconds, etc)"""
        n_chunks = len(depth) * tstep / chunk_length
        return np.array_split(depth, n_chunks)
    
    def lwt_pressure_to_wl_spectrum(self,time, corrected_pressure, water_depth, sensor_depth):
        '''Using Steve Mr. Clean Suttles method to calculate the water level spectrum'''
        
        #take out the linear trend
        coeff = np.polyfit(time, corrected_pressure, 1)
        lin_trend = coeff[1] + coeff[0]*time
        detrended_pressure = corrected_pressure - lin_trend
        
        #create a window the size of the detrended pressure divided by 16
        window = np.hanning(len(detrended_pressure)/16)
    
        #apply the welch algorithm to convolve pressure by the window, and perform ffts the size of the segs
        #and ensemble average the calculated values to create one pressure spectrum
        freqs,amps = signal.welch(detrended_pressure, 4, window = window, nperseg=256, noverlap=128, detrend=None)
        
        #remove zero component from freqs and amps to avoid divide by zero errors
        freqs, amps = freqs[1:], amps[1:]
        
        #keep all data up to one hertz
        cut_off = np.where(freqs<=1.0)
        
        #filter based on the above cutoff
        freqs = freqs[cut_off]
        amps = amps[cut_off]

        #get the approximate depth
        approx_depth = 2 + 0.15
        
        #get the wave numbers using the echart dispersion relation and then its 
        #corresponding pressure response factor coefficient
        k = p2d.echart_omega_to_k(freqs * 2.0 * np.pi, np.repeat(approx_depth,len(freqs)))
        kz = np.array(np.cosh(-0.15*k)/np.cosh(approx_depth*k))
         
        #ughh I'll keep this or now...
        query = np.where(kz < 0.1)
         
        #if there is kz less than .1
        if len(query[0]) > 0:
            
            #get the first index of the kz to be cutoff, (all kz after will also be less than kz)
            cut = query[0][0]
            lin_trans1 = amps[0:cut]/(kz[0:cut]**2)
               
            #this adds the f^-4 tail to the end of the spectrum
            lin_trans2 = (lin_trans1[cut-1] * (freqs[cut-1:]**-4)) \
            * ( 1 /  (freqs[cut-1]**-4))
               
            #this concatenates the two transforms to get the final water level spectrum
            lin_transform = np.concatenate((  
                                            lin_trans1[:len(lin_trans1)-1],
                                            lin_trans2
                                            ))
        else:
            #converts by pressure response factor coefficients to get the water level spectrum
            lin_transform = amps/(kz**2) 
            
        return (freqs,lin_transform)
    
