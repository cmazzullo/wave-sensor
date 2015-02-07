import numpy as np
from numpy.fft import rfft, rfftfreq

def get_transform(seq, timestep):
    return 2 * rfft(seq) / len(seq), rfftfreq(len(seq), timestep)

if __name__ == '__main__':
    # import seaborn as sns
    from matplotlib.pyplot import *
    import NetCDF_Utils.nc as nc
    ion()
    fname = '/home/chris/work/test-data/logger3.csv.nc'
    # fname = ('./tests/test_data/gui_leveltroll_test.nc')
    t = nc.get_time(fname)
    timestep = (t[1] - t[0]) / 1000
    p = nc.get_pressure(fname)
    # p = np.sin(10*t)
    # p = p*np.hamming(len(p))


    minute = 60*1000
    inc = minute * .2
    min_index = minute * 2
    max_index = min_index + inc
    p = p[min_index:max_index]
    t = t[min_index:max_index]
    t = t - t[0]
    a, f = get_transform(p, timestep)
    clf()

    min_f = 0


    subplot(211)
    semilogy(f[min_f:], np.absolute(a[min_f:]), '.')
    xlabel('Frequency (Hz)')
    ylabel('Water pressure (dbar)')

    subplot(212)
    plot(t/minute/60, p)
    xlabel('Time (hours)')
    ylabel('Water pressure (dbar)')
