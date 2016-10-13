import numpy as np
import scipy.stats as stats
import unit_conversion as uc
import pressure_to_depth as p2d
import scipy.signal as signal
import matplotlib.pyplot as plt
#Statistics calculation pulled from Storm Surge Matlab Project by
#Joe Vrabel and Sam Rendon at the USGS in Texas

G = uc.GRAVITY
std_dev = False

class Stats(object):

    def __init__(self):
        self.low_cut = 0
        self.high_cut = 1.0
         
    def power_spectrum(self, y, tstep, h, d):
        """Calculate the power spectrum of the series y"""
        #calculate the Power Spectral Density (PSD)
        scale = (len(y)/2.0) * 4.0
        spec = np.fft.rfft(y)
        spec = spec * np.conjugate(spec) / scale
        freqs = np.fft.rfftfreq(len(y), d=tstep)
        spec = spec[1:]
        self.frequencies = freqs = freqs[1:]
      
        #band average the spectra
        freqs, spec = self.band_average_psd(freqs, spec, 32)
        
        #radial frequency Units 1/T
        omega = np.array(2* np.pi * freqs)
          
        #1st wave number estimate
        k = p2d.omega_to_k(omega, d)
       
        #pressure response factor
        kz = np.array(np.cosh(h*k)/np.cosh(d*k))
        #get upper and lower band for PSD estimate
        #DEGREES OF FREEDOM ARE STATICALLY 32 FOR NOW AS WELL AS A 90% CONFIDENCE INTERVAL
        upper_spec, lower_spec = self.psd_confidence_intervals(spec,32,.9)
           
        #convert to water level PSD 
        wl_amps = spec/kz**2
        wl_up = upper_spec/kz**2
        wl_down = lower_spec/kz**2
        
        return (freqs, wl_amps, wl_up, wl_down)     
        
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
        if type(spec) is float:
            return np.NaN
        else:
            if len(np.where(np.isnan(spec))[0]) > 0:
                return np.NaN
            else:   
                return 1/ freq[np.argmax(spec)]
    
    
    def significant_wave_period(self, spec, freq, depth, tstep):
       
        freq_max = freq[np.argmax(np.abs(spec))]
        return .9451 / freq_max
    
    
    def split_into_chunks(self, depth, tstep, chunk_length):
        """Split an array into chunks of size chunk_length.
    
        chunk_length and tstep must have the same units of time (seconds, etc)"""
        n_chunks = len(depth) * tstep / chunk_length
        return np.array_split(depth, n_chunks)
    
    def psd_confidence_intervals(self, PSD, df, ci):
        '''method from NDBC Technical document to return confidence intervals for 
        spectral estimates'''
        upper = PSD*df/stats.chi2.ppf((1 - ci)/2.0, df)
        lower = PSD*df/stats.chi2.ppf((1 + ci)/2.0, df)
        return (upper, lower)
    
    def band_average_psd(self, freqs, psd_amps, df):
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
        high_cut_off = np.where(freqs <= self.high_cut)
        freqs = freqs[high_cut_off]
        psd_avg_amps = psd_avg_amps[high_cut_off].real
        
        low_cut_off = np.where(freqs >= self.low_cut)
        freqs = freqs[low_cut_off]
        psd_avg_amps = psd_avg_amps[low_cut_off]
        
        return freqs, psd_avg_amps
    
    
