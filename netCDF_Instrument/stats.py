from matplotlib.pyplot import *
import numpy as np


def significant_wave_height(depth):
    return 4 * np.std(depth)


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
