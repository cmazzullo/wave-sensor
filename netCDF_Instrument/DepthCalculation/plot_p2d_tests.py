# import numpy as np
from numpy import fft, pi, arange, array, sin
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import newton
from DepthCalculation.pressure_to_depth import fft_method


# deeper = have to lower the cutoff
g = 9.8
rho = 1027
h = 50
z = -h/2

def make_waves(length, sample_frequency, waves):
    """Create wave pressure given frequencies, amplitudes and phases"""
    t = np.arange(length, step=1/sample_frequency)
    total_height = np.zeros_like(t)
    total_pressure = np.zeros_like(t)
    for wave in waves:
        f = wave[0]
        a = wave[1]
        phi = wave[2]
        eta = a*sin(2*pi*f*t + phi)
        total_height += eta
        k = newton(lambda k: g*k*np.tanh(k*h) - (2*pi*f)**2, 0)
        pressure = eta*rho*g*np.cosh(k*(z + h))/np.cosh(k*h)
        total_pressure += pressure
    return t, total_height, total_pressure


if __name__ == '__main__':
    hi_cut = .2
    # optimal cut amount seems to also depend on chunk size


    length = 6000 # length of the time series in seconds
    sample_frequency = 4 # time steps per second (Hz)


    # 1. MAKE WAVES
    # input format: waves are represented as [frequency, amplitude,
    # phase] where frequency is in Hz, amplitude is in dBar and phase
    # is in radians
    waves = [[.101, .09, 0],
             [.201, .2, 1],
             [.0101, .3, 2],
             [1.01, .05, 2]]

    t, y, p = make_waves(length, sample_frequency, waves)

    H = np.ones_like(t) * h
    y2 = fft_method(t, p/10000, z, H, 1/sample_frequency, window=False, gate=.02, hi_cut=hi_cut)

    plt.ion()
    plt.clf()
    plt.cla()
    plt.subplot(211)
    plt.plot(t, y, label='Original η')
    plt.xlabel('time (s)')
    plt.ylabel('η (meters)')
    plt.plot(t[:], y2, 'r', label='Reconstructed η')
    plt.plot(t, p/rho/g, 'g', label='Hydrostatic η')
    plt.legend()

    amps = fft.rfft(y2) / len(y2)
    freqs = fft.rfftfreq(len(y2), 1/sample_frequency)
    amps2 = fft.rfft(y) / len(y)
    freqs2 = fft.rfftfreq(len(y), 1/sample_frequency)

    plt.subplot(212)
    plt.grid()
    plt.plot(freqs, 2*np.absolute(amps), '.', color='red')
    plt.plot(freqs2, 2*np.absolute(amps2), color='blue')
    plt.xlabel('frequency (Hz)')
    plt.ylabel('η (meters)')

    rmse = np.sqrt(np.average((y - y2)**2))
    print('RMSE = %.4f meters' % rmse)
