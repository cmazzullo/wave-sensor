"""
Takes in pressure data, outputs frequency information.

When given an array of sea pressure readings, the script method of
this module will print out the moments of the data and draw a
graph of the frequency of the waves.

This module assumes that p is a numpy array! Regular python arrays
won't work!
"""
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import Analysis.fourier as fourier


rho = 1030  # Density of water in kg / m**3
g = 9.8  # gravitational acceleration


def get_mean_depth(t, p):
    slope, intercept = np.polyfit(t, p, 1)
    static_p = slope * t + intercept
    mean_p = np.mean(static_p)
    mean_depth = mean_p / (rho * g)
    return mean_depth


def script(p, M, sample_freq=4):
    t = np.arange(0, len(p)) / sample_freq
    DT = 1 / sample_freq
    mean_depth = get_mean_depth(t, p)
    P, F = crosgk(p, p, len(p), M, DT, 1)
    energy = np.zeros_like(F)
    # Moments:
    m0 = m1 = m2 = m01 = 0
    deltaF = F[2] - F[1]
    emax = prmax = 0  # maximum value of pressure energy

    cutoff = .95
    # Calculates energy spectrum and calculates the moments of the
    # spectrum
    prmax = max(P[1][50:2000])
    print(prmax)
    print(np.shape(p))
    for i in range(50, 2000):
    # prmax = max(P[1])
    # for i in range(len(P)):
        T = 1 / F[i]
        pr = np.sqrt(P[0][i])
        L = 1.56 * T**2
        if mean_depth / L < 0.36:
            L = np.sqrt(g * mean_depth) * (1 - mean_depth / L) * T
        energy[i] = (np.cosh(2 * np.pi * mean_depth / L)**2 *
                     pr / (rho * g))
        if pr / prmax < cutoff:
            energy[i] = 0
        if energy[i] > emax:
            emax = energy[i]
        m0 = m0 + energy[i] * deltaF
        m1 = m1 + energy[i] * deltaF * F[i]
        m2 = m2 + energy[i] * deltaF * F[i]**2
        if F[i] > 0:
            m01 = m01 + energy[i] * deltaF / F[i]
    return energy

def crosgk(X, Y, N, M, DT, DW):
    '''Takes two signals and outputs their power cross-spectrum with
some smoothing in the frequency domain.

INPUT:
X - signal 1
Y - signal 2
N - number of samples per data segment
M - number of frequency bins to smooth over
DT - time step
DW - data window type (1 for hann, else rectangle)
'''
    df = 1 / (N * DT)
    if DW == 1:
        # Hann window
        w = np.hanning(N)
        dj = N / 2
    else:
        w = np.ones(N, 1)
        dj = N

    varw = sum(w**2) / N

    nx = len(X)
    ny = len(Y)
    avgx = sum(X) / nx
    avgy = sum(Y) / ny
    px = np.zeros(len(w))
    py = np.zeros(len(w))
    Pxx = np.zeros(len(w))
    Pxy = np.zeros(len(w))
    Pyy = np.zeros(len(w))
    ns = 1

    px = X - avgx;
    px = w * px
    px = np.fft.fft(px)

    py = Y - avgy
    py = w * py
    py = np.fft.fft(py)

    Pxx = Pxx + px * np.conj(px)
    Pyy = Pyy + py * np.conj(py)
    Pxy = Pxy + py * np.conj(px)

    Pxx = (2 / (ns * (N**2) * varw * df)) * Pxx
    Pyy = (2 / (ns * (N**2) * varw * df)) * Pyy
    Pxy = (2 / (ns * (N**2) * varw * df)) * Pxy

    if M > 1:
        w = np.hamming(M)
        w = w / sum(w)
        w1 = np.array(w[np.ceil((M + 1) / 2) : M])
        w2 = np.zeros(N - M)
        w3 = np.array(w[0 : np.ceil((M + 1) / 2)])
        w = np.hstack((w1, w2, w3))
        w = np.fft.fft(w)
        Pxx = np.fft.fft(Pxx)
        Pyy = np.fft.fft(Pyy)
        Pxy = np.fft.fft(Pxy)
        Pxx = np.fft.ifft (w * Pxx)
        Pyy = np.fft.ifft(w * Pyy)
        Pxy = np.fft.ifft (w * Pxy)

    Pxx = Pxx[0 : N / 2]
    Pyy = Pyy[0 : N / 2]
    Pxy = Pxy[0 : N / 2]

    F = np.arange(0, N / 2) * df

    if DW == 1:
        nn = (ns + 1) * N / 2
    else:
        nn = ns * N

    avgx = sum(X[0:nn]) / nn
    varx = sum((X[0 : nn] - avgx)**2) / (nn - 1)

    avgy = sum(Y[0:nn]) / nn
    vary = sum((Y[0 : nn] - avgy)**2) / (nn - 1)
    covxy = sum((X[0 : nn] - avgx) * (Y[0 : nn] - avgy)) / (nn - 1)

    m0xx = (0.5 * Pxx[0] + sum(Pxx[1 : N / 2 - 1]) +
            0.5 * Pxx[N / 2 - 1]) * df

    m0yy = (0.5 * Pyy[0] + sum(Pyy[1 : N / 2 - 1]) +
            0.5 * Pyy[N / 2 - 1]) * df
    m0xy = (0.5 * Pxy[0] + sum(Pxy[1 : N / 2 - 1]) +
            0.5 * Pxy[N / 2 - 1]) * df

    Pxx = Pxx * (varx / m0xx)
    Pyy = Pyy * (vary / m0yy)
    Pxy = Pxy * (covxy / np.real(m0xy))

    P = [Pxx, Pyy, Pxy]

    return P, F


def make_test_data():
    T = 300  # total time in seconds
    f = 4  # sample frequency in Hz
    t = np.arange(T * f) / f
    periods = (3, 10)  # wave periods in seconds
    amps = (.5, 1)  # amplitudes in meters
    noise = np.random.normal(.5, .03, (len(t),))
    Pwave = sum([amp * np.sin(2 * np.pi * t / period)
                 for amp, period in zip(amps, periods)]) + noise
    return Pwave


def demonstration():
    #    p = make_test_data()
    fname = '/home/chris/measurement-systems.nc'
    p = get_pressure_array(fname)
    P, F = crosgk(p, p, len(p), 1, .25, 1)
    plt.plot(fourier.compress(P[2]), 'b')
    plt.xticks(np.arange(0, 1, .1), rotation=30, size='small')
    plt.xlim((0, 1))

    plt.ylim((0, .000001))
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power spectrum (Pa**2 / Hz)')
    plt.show()

    
def get_pressure_array(fname):
    f = Dataset(fname, 'r', format='NETCDF4_CLASSIC')
    v = f.variables
    P = v['sea_water_pressure'][:]
    P -= sum(P) / len(P)
    return P

fname = ('C:\\Users\\cmazzullo\\wave-sensor-test-data\\'
         'wave-guage-14-07-2014.csv.nc')
p = get_pressure_array(fname)

energy = script(p, 10)

#demonstration()

if __name__ == '__main__':
    pass
