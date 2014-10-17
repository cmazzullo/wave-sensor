import numpy as np
import matplotlib.pyplot as plt
import NetCDF_Utils.make_default as md
import NetCDF_Utils.nc as nc

def make_waves(length, sample_frequency, waves):
    """Create waves given frequencies, amplitudes and phases"""
    t = np.arange(length, step=1/sample_frequency)
    return t, sum(wave[1] * np.sin(2*np.pi * t * wave[0] + wave[2])
                  for wave in waves)

if __name__ == '__main__':
    # TEST OVERVIEW:
    # 1. Make waves with known amplitude, frequency and phase
    # 2. Record them as pressure in a netCDF
    # 3. Read them in
    # 4. Do a spectral analysis and compare with known quantities

    length = 3000 # length of the time series in seconds
    sample_frequency = 4 # time steps per second (Hz)

    # 1. MAKE WAVES
    # input format: waves are represented as [frequency, amplitude,
    # phase] where frequency is in Hz, amplitude is in dBar and phase
    # is in radians
    waves = [[1, .5, np.pi/3],
             [.01, 2.2, np.pi/2],
             [.005, 3.5, np.pi/5],
             [.5, .23, np.pi/6]]

    t, y = make_waves(length, sample_frequency, waves)

    # 2. WRITE TO NETCDF
    filename = 'blah.nc'
    md.make_default_netcdf(filename, t, y)

    # 3. READ PRESSURE BACK IN
    p = nc.get_pressure(filename)

    # 4. SPECTRAL ANALYSIS
    amps = fft.rfft(p) / len(p)
    freqs = fft.rfftfreq(len(p), 1/sample_frequency)
    plot(freqs, amps)
    show()
