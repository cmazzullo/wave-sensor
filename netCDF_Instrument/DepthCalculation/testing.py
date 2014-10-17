import numpy as np
import matplotlib.pyplot as plt


def make_waves(length, sample_frequency, waves):
    """Create waves given frequencies, amplitudes and phases"""
    t = np.arange(length, step=1/sample_frequency)
    return t, sum(wave[1] * np.sin(2*np.pi * t * wave[0] + wave[2])
                  for wave in waves)

if __name__ == '__main__':
    length = 3000 # length of the time series in seconds
    sample_frequency = 4 # time steps per second (Hz)

    # input format: waves are represented as [frequency, amplitude,
    # phase] where frequency is in Hz, amplitude is in dBar and phase
    # is in radians
    waves = [[1, .5, np.pi/3],
             [.01, 2.2, np.pi/2],
             [.005, 3.5, np.pi/5],
             [.5, .23, np.pi/6]]

    t, y = make_waves(length, sample_frequency, waves)
    plt.plot(t, y)
    plt.show()
