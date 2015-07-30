from matplotlib.pyplot import *
import numpy as np


def power_spectrum(y, tstep):
    """Calculate the power spectrum of the series y"""
    spec = abs(np.fft.rfft(y))**2 / (len(y)/2)
    freqs = np.fft.rfftfreq(len(y), d=tstep)
    return freqs[1:], spec[1:]


def moment(x, y, n):
    """Calculate the nth statistical moment of the x, y data."""
    return np.trapz(y * x**n, x=x)


def spec_moment(t, depth, n):
    """Calculate the nth statistical moment of the data's power spectrum."""
    tstep = t[1] - t[0]
    freqs, amps = power_spectrum(depth, tstep)
    return moment(freqs, amps, n)


def median_wave_height(t, depth):
    return 2.36 * np.sqrt(spec_moment(t, depth, 0))


def rms_wave_height(t, depth):
    return 2.83 * np.sqrt(spec_moment(t, depth, 0))


def significant_wave_height(t, depth):
    return 4 * np.sqrt(spec_moment(t, depth, 0))


def maximum_wave_height(t, depth):
    return 1.86 * 4 * np.sqrt(spec_moment(t, depth, 0))


def ten_percent_wave_height(t, depth):
    return 5.091 * np.sqrt(spec_moment(t, depth, 0))


def one_percent_wave_height(t, depth):
    return 6.672 * np.sqrt(spec_moment(t, depth, 0))


def significant_wave_height(depth):
    return 4 * np.std(depth)


def average_wave_height(t, depth):
    return 2.51 * np.sqrt(spec_moment(t, depth, 0))


def average_zero_crossing_period(t, depth):
    return np.sqrt(spec_moment(t, depth, 0) / spec_moment(t, depth, 1))


def mean_wave_period(t, depth):
    return spec_moment(t, depth, 0) / spec_moment(t, depth, 1)


def crest_wave_period(t, depth):
    return np.sqrt(spec_moment(t, depth, 2) / spec_moment(t, depth, 2))


def peak_wave_period(t, depth):
    tstep = t[1] - t[0]
    freqs, amps = power_spectrum(depth, tstep)
    return freqs[np.argmax(amps)]


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
