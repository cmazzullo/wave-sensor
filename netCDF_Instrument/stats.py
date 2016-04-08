from matplotlib.pyplot import *
import numpy as np
import scipy.stats as stats
import unit_conversion as uc
import pressure_to_depth as p2d

#Statistics calculation pulled from Storm Surge Matlab Project by
#Joe Vrabel and Sam Rendon at the USGS in Texas

G = uc.GRAVITY
std_dev = True

def jon_swap_spectrum(freqs, wind_speed):
    
    spectrum = []
    
    g = uc.GRAVITY
    gamma = 3.3
    
    f_max = .8722 * (g/((2*np.pi)* wind_speed))
    print('fmax',f_max)
    
    #relates to wind speed and fetch(typical values range from .0081 to .01
    alpha = .0081
    
    #this is the shape parameter
    beta = -1.25
    
    for f in freqs:
        if f < f_max:
            theta = .07
        else:
            theta = .09
            
        r = np.exp(-1* (f - f_max)**2 / 2*(theta**2)*(f_max**2))
        
        #this is the peak enhancement factor
        p_e_f = gamma ** r
        
        val = alpha*(g**2) * ((2*np.pi)**-4) * (f**-5) * \
        np.exp(beta*((f/f_max)**-4)) * p_e_f
        
        spectrum.append(val)
        
    return spectrum
    

def power_spectrum(y, tstep):
    """Calculate the power spectrum of the series y"""
    spec = abs(np.fft.rfft(y))**2 / (len(y)/2)
    freqs = np.fft.rfftfreq(len(y), d=tstep)
    freqs = freqs[0:len(y)/2 + 1]
    spec = spec[1:]
    freqs = freqs[1:]
    
  
  
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


def moment(x, y, n):
    """Calculate the nth statistical moment of the x, y data."""
    return np.trapz(y * x**n, x=x)


def spec_moment(t, depth, n):
    """Calculate the nth statistical moment of the data's power spectrum."""
    tstep = t[1] - t[0]
    freqs, amps = power_spectrum(depth, tstep)
    return moment(freqs, amps, n)

def jon_swap_spec_moment(t, depth, n, wind):
    """Calculate the nth statistical moment of the data's power spectrum."""
    tstep = t[1] - t[0]
    freqs, amps = power_spectrum(depth, tstep)
    jspec = jon_swap_spectrum(freqs, wind)
    return moment(freqs, jspec, n)


def median_wave_height(t, depth):
    if not std_dev:
        return 2.36 * np.sqrt(spec_moment(t, depth, 0))
    
    return 2.36 * np.std(depth)


def rms_wave_height(t, depth):
    if not std_dev:
        return 2.83 * np.sqrt(spec_moment(t, depth, 0))
    
    return 2.83 * np.std(depth)


def significant_wave_height(t, depth):
    '''There is a discrepancy regarding the calculation sig wave height
    , will have to understand the context of the implementation better'''
    if not std_dev:
        return 4 * np.sqrt(spec_moment(t, depth, 0))
    
    return 4 * np.std(depth) 

def significant_wave_height2(t, depth, wind):
    '''There is a discrepancy regarding the calculation sig wave height
    , will have to understand the context of the implementation better'''
    if not std_dev:
        return 4 * np.sqrt(jon_swap_spec_moment(t, depth, 0, np.average(wind)))
    
    return 4 * np.std(depth) 


def maximum_wave_height(t, depth):
    if not std_dev:
        return 1.86 * 4 * np.sqrt(spec_moment(t, depth, 0))
    
    return 1.86 * 4 * np.std(depth)


def ten_percent_wave_height(t, depth):
    if not std_dev:
        return 5.091 * np.sqrt(spec_moment(t, depth, 0))
    
    return 5.091 * np.std(depth)


def one_percent_wave_height(t, depth):
    if not std_dev:
        return 6.672 * np.sqrt(spec_moment(t, depth, 0))
    
    return 6.672 * np.std(depth)


def significant_wave_height_standard(depth):
    return 4 * np.std(depth)


def average_wave_height(t, depth):
    if not std_dev:
        return 2.51 * np.sqrt(spec_moment(t, depth, 0))
    
    return 2.51 * np.std(depth)


def average_zero_crossing_period(t, depth):
    return np.sqrt(spec_moment(t, depth, 0) / spec_moment(t, depth, 2))


def mean_wave_period(t, depth):
    return spec_moment(t, depth, 0) / spec_moment(t, depth, 1)


def crest_wave_period(t, depth):
    return np.sqrt(spec_moment(t, depth, 2) / spec_moment(t, depth, 4))


def peak_wave_period(t, depth):
    '''value given in seconds; inverse of the frequency with the highest energy in the reported spectrum.'''   
    tstep = t[1] - t[0]
    freqs, amps = power_spectrum(depth, tstep)
    return 1/ freqs[np.argmax(amps)]


def significant_wave_period(depth, tstep):
    amps = np.fft.rfft(depth)
    amps[0] = 0
    freqs = np.fft.rfftfreq(len(depth), d=tstep)
    freq_max = freqs[np.argmax(np.abs(amps))]
    return .9451 / freq_max


def split_into_chunks(depth, tstep, chunk_length):
    """Split an array into chunks of size chunk_length.

    chunk_length and tstep must have the same units of time (seconds, etc)"""
    n_chunks = len(depth) * tstep / chunk_length
    return np.array_split(depth, n_chunks)

