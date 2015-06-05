import pdb
import seaborn as sns
from matplotlib.pyplot import *
from numpy import *
import NetCDF_Utils.nc as nc
import pandas as pd
from scipy.optimize import curve_fit
from plotting import myplot

# Given a particular stevens data set and a particular instrument data
# set, we want to find the index at which the sets seem to match up.

# Constants

INCH_TO_METER = 0.0254

stevens_fold = '/home/chris/work/test-data/stevens_data/Stevens Acoustic & Wave Wire/'
fnames = ['A5763.001', 'A5763.002', 'A5763.003', 'A5763.004',
          'A5763.005', 'A5763.006', 'A5763.007', 'A5763.008',
          'A5763.009', 'A5763.010', 'A5763.011', 'A5763.012',
          'A5763.013', 'A5763.014', 'A5763.015', 'A5763.016',
          'A5763.017', 'A5763.018', 'A5763.019', 'A5763.020',
          'A5763.021', 'A5763.022', 'A5763.023', 'A5763.024',
          'A5763.025', 'A5763.026', 'A5763.027', 'A5763.028',
          'A5763.029', 'A5763.030', 'A5763.031', 'A5763.032',
          'A5763.033', 'A5763.034', 'A5763.035', 'A5763.036',
          'A5763.037', 'A5763.038', 'A5763.039', 'A5763.040',
          'A5763.041']
fnames = [stevens_fold + fname for fname in fnames]
blacklist = (3, 4, 11, 12, 13, 20, 21, 22, 29, 30, 31, 38)

day1_times = 1429527600 + array([
    (9300, 9600),
    (10500, 10800),
    (13500, 13700),
    (nan, nan),
    (nan, nan),
    (14500, 14900),
    (14900, 15300),
    (15300, 15600),
    (15600, 15900),
    (15800, 16100),
    (16100, 16300),
    (16300, 16700)])

day2_times = 1429609879 + array([
    (nan, nan),
    (nan, nan),
    (6000, 6500),
    (6500, 7000),
    (7000, 7500),
    (7500, 7900),
    (7900, 8150),
    (8150, 8400),
    (8400, 8700),
    (nan, nan),
    (nan, nan),
    (14000, 14500),
    (14600, 15200),
    (15200, 15700),
    (15700, 16200),
    (16200, 16600),
    (16600, 16850),
    (16850, 17200),
    (nan, nan),
    (nan, nan),
    (18700, 19200),
    (19200, 19500),
    (19500, 19900),
    (19900, 20150),
    (20150, 20350),
    (20350, 20600),
    (20600, 21000),
    (21000, 21500),
    (21500, 22000)])
run_times = concatenate((day1_times, day2_times))
expected_periods = array([2, 2.5, 3.03, 1, 1.49, 2, 2.5, 3.03, 3.58, 3.99, 4.56, 2.88])
expected_freqs = 1 / expected_periods

stevens_interval = .02
data_fold = '/home/chris/work/test-data/stevens_data/'
hobo1 = data_fold + 'Hobo/ncs/StevensDay1Run1G.csv.nc.depth'
hobo2 = data_fold + 'Hobo/ncs/StevensDay1Run1H.csv.nc.depth'
tru1 = data_fold + 'TruBlue/ncs/4-20 1100-536PM.csv.nc.depth'
tru2 = data_fold + 'TruBlue/ncs/4-20 11PM-454PM.csv.nc.depth'
troll1 = data_fold + 'LevelTROLL/LevelTroll F/Day 1 Run 1_2015-04-20_23-56-20-912.csv.nc.depth'
troll2 = data_fold + 'LevelTROLL/LevelTroll E/Day 1 run 1_2015-04-20_23-21-29-039.csv.nc.depth'
house1 = data_fold + 'USGS Prototype/ncs/WaveLog #1 - J Run 1 Day 1.csv.nc.depth'
house2 = data_fold + 'USGS Prototype/ncs/WaveLog #1 - J Run 1 Day 2.csv.nc.depth'
house3 = data_fold + 'USGS Prototype/ncs/WaveLog #2 - K Run 1 Day1.csv.nc.depth'
house4 = data_fold + 'USGS Prototype/ncs/WaveLog #2 - K Run 1 Day2.csv.nc.depth'

# Functions

def get_stevens_wire_data(fname):
    meters = []
    time = []
    with open(fname) as f:
        for i, l in enumerate(f):
            if i != 0:
                level_inches = float(l.split()[2])
                meters.append(level_inches * INCH_TO_METER)
                time.append(float(l.split()[1]))
    return pd.Series(meters, time)


def get_instrument_data(f):
    """Get time, pressure and depth from a netCDF file f.
    t is in seconds, p is in dbar(?) and d is in meters"""
    t = nc.get_time(f) / 1000
    d = nc.get_depth(f)
    print('Sample interval: ', t[1] - t[0])

    t_interp = arange(t[0], t[-1], stevens_interval)
    d_interp = interp(t_interp, t, d)
    return pd.Series(d_interp, t_interp)


def get_difference(clean_series, start_time, instrument_s):
    t = clean_series.index
    end_time = start_time + t[-1] - t[0] + t[1] - t[0]
    window = instrument_s[start_time:end_time]
    d_window = remove_mean(window.values)
    return rmse(d_window, clean_series.values)


def find_likely_time(stevens_series, instrument_s, interval):
    """Match the stevens series to the instrument and return the start
    time.
    """
    clean_series = remove_mean(stevens_series)
    end_time = interval[1] - stevens_series.index[-1] + stevens_series[0]
    time = interval[0]
    min_time = time
    min_dif = False
    while time < end_time:
        dif = get_difference(clean_series, time, instrument_s)
        if min_dif == False:
            min_dif = dif
        elif dif < min_dif:
            min_dif = dif
            min_time = time
        time += stevens_interval
    return min_time


def rmse(a, b):
    n = len(a)
    return sqrt(sum((a - b)**2) / n)


def remove_mean(series):
    return series - average(series)


def swh(series):
    """Return the significant wave height of a series of water elevation."""
    return 4 * series.std()


def plot_stevens_over_instrument(instrument_s, stevens_fnames,
                                 runs, blacklist, indices, stevens_series,
                                 plot_title=''):
    instrument_s.plot(label='Instrument readings (m)', color='black')
    for file_number, idx in zip(runs, indices):
        stevens_fname = fnames[file_number]
        if file_number in blacklist:
            continue
        stevens_series = get_stevens_wire_data(stevens_fname)
        t = stevens_series.index
        d = stevens_series.values
        offset = average(instrument_s[idx:idx + t[-1] - t[0]])
        print('plotting', stevens_fname)
        plot(t + idx, d + offset, label=stevens_fname)
    legend()
    xlabel('Time (s)')
    ylabel('Depth of Sensor (m)')
    title(plot_title)
    show()


def describe_window(window_number, stevens_series, windows):
    if window_number in blacklist:
        print('Data set not processed')
        return
    test = remove_mean(stevens_series[window_number])
    w = remove_mean(windows[window_number])
    plot(test, label='Wavewire', color='blue')
    plot(w, label='Instrument', color='red')
    xlabel('Time (s)')
    ylabel('Depth of Sensor (m)')
    title('Stevens Wavewire and Instrument Data')
    legend()
    show()
    def printcm(name, q):
        format_string = '{:8.4}'
        print(name, '=\t', format_string.format(q * 100), 'cm')
    print('Instrument data:')
    printcm('Hₛ', swh(w))
    printcm('RMS', swh(w) / 1.4)
    print('\nWavewire data:')
    printcm('Hₛ', swh(test))
    printcm('RMS', swh(test) / 1.4)


describe = lambda n: describe_window(n, stevens_series, windows)


# Find where all runs of Stevens data matches the instrument data
instrument_fname = house1
runs = range(0, 12)
instrument_s = get_instrument_data(instrument_fname)
instrument_s.index += 510

stevens_series = []
indices = []
windows = []

for file_number, guess, fname, in zip(runs, run_times, fnames):
    if file_number in blacklist:
        stevens_series.append(False)
        indices.append(nan)
        windows.append(())
        continue
    print('Processing file', file_number)
    s = get_stevens_wire_data(fname)
    s_len = s.index[-1] - s.index[0]
    stevens_series.append(s)
    t = find_likely_time(s, instrument_s, guess)
    w = instrument_s[t:t + s_len]
    windows.append(w)
    indices.append(t)


## plot all series
plot_stevens_over_instrument(instrument_s, fnames, runs,
                             blacklist, indices, stevens_series,
                             plot_title='LevelTroll 1 Second Data')


## power spectrum
from power_spectrum import get_transform
from plotting import myplot

def get_main_frequency(series):
    series = remove_mean(series)
    timestep = series.index[1] - series.index[0]
    amps, freqs = get_transform(series.values, stevens_interval)
    return freqs[argmax(amps)]

stevens_freqs = array([get_main_frequency(remove_mean(s))
                       for i, s in enumerate(stevens_series)
                       if i not in blacklist])

window_freqs = array([get_main_frequency(remove_mean(s))
                      for i, s in enumerate(windows)
                      if i not in blacklist])

run_number = 6
s = stevens_series[run_number]
amps, freqs = get_transform(s.values, stevens_interval)

subplot(121)
myplot('Stevens Data Run {}'.format(run_number),
       s,
       'Frequency (Hz)',
       'Wave height (cm)')

subplot(122)
myplot('Spectrum of Stevens Run {}'.format(run_number),
       (freqs, amps * 100),
       'Frequency (Hz)',
       'Wave height (cm)')
xlim(0, 2)
show()
max_freq = freqs[argmax(amps)]


## curve fitting
def fit_amplitude_and_phase(series):
    freq_guess = get_main_frequency(series)
    phase_guess = 1
    series = remove_mean(series)
    amp_guess = series.max()
    f = lambda t, amp, freq, phase: amp * sin(2*pi*freq*t - phase)
    popt, pcov = curve_fit(f, series.index, series.values,
                           p0=(amp_guess, freq_guess, phase_guess))
    return popt


wave_props = []

for i in range(12):
    if i in blacklist:
        continue
    run_number = i
    s = remove_mean(stevens_series[run_number])
    s.index -= s.index[0] # large time values swamp the fit, causing failure
    # freq_guess = 1 / expected_periods[run_number]
    amp, freq, phase = fit_amplitude_and_phase(s)
    # wave_props.append({'Run': run_number,
    #                    'Amplitude': amp,
    #                    'Frequency': freq,
    #                    'Phase': phase,
    #                    'Expected frequency': expected_freqs[i]})
    y = amp * sin(2*pi*freq*s.index-phase)
    myplot('Best Fit Sine Wave, Data Set {}'.format(run_number+1),
           {'Stevens data': (s.index, s.values),
            'Best fit':(s.index, y)},
           'Time (s)', 'Wave height (m)')
    show()
