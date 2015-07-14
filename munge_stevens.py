import seaborn as sns
from matplotlib.pyplot import *
from numpy import *
import NetCDF_Utils.nc as nc
import pandas as pd
from scipy.optimize import curve_fit
from plotting import myplot
from power_spectrum import get_transform
import pressure_to_depth as p2d
# Given a particular stevens data set and a particular instrument data
# set, we want to find the index at which the sets seem to match up.

# Constants

INCH_TO_METER = 0.0254

stevens_fold = '/home/chris/work/stevens_data/Stevens Acoustic & Wave Wire/'
fnames = [
    'A5763.001', 'A5763.002', 'A5763.003', 'A5763.004',
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

# this was done with house4 but it should have been done with house2
temp_times = array([(1429615056.263425, 1429615566.858695),
                    (1429615350.837619, 1429615900.709449),
                    (1429615841.794610, 1429616450.581278),
                    (1429616372.028160, 1429617039.729667),
                    (1429616941.538269, 1429617452.133539),
                    (1429617393.218700, 1429617844.899132),
                    (1429617805.622572, 1429618178.749885),
                    (1429618002.005368, 1429618375.132681),
                    (1429618316.217842, 1429618689.345155),
                    (1429622715.192478, 1429623265.064308),
                    (1429623068.681511, 1429623854.212696),
                    (1429623520.361943, 1429624443.361085),
                    (1429624600.467322, 1429625032.509474),
                    (1429625130.700872, 1429625896.593777),
                    (1429625739.487540, 1429626210.806251),
                    (1429626132.253133, 1429626603.571844),
                    (1429626466.103886, 1429626858.869479),
                    (1429626701.763242, 1429627153.443673),
                    (1429627938.974858, 1429628194.272493),
                    (1429628096.081095, 1429628371.017010),
                    (1429628685.229484, 1429629038.718517),
                    (1429628999.441958, 1429629490.398948),
                    (1429629372.569271, 1429629765.334863),
                    (1429629726.058304, 1429630118.823896),
                    (1429630020.632498, 1429630315.206692),
                    (1429630177.738735, 1429630531.227768),
                    (1429630550.866048, 1429630865.078522),
                    (1429630943.631640, 1429631316.758953),
                    (1429631414.950351, 1429631807.715944)])


house2_times = array([
    (1429614382, 1429615147),
    (1429614277, 1429615599),
    (1429615251, 1429616155),
    (1429615912, 1429616712),
    (1429616468, 1429617198),
    (1429616990, 1429617546),
    (1429617303, 1429617859),
    (1429617546, 1429618103),
    (1429617824, 1429618450),
    (1429622902, 1429623423),
    (1429623110, 1429623632),
    (1429623458, 1429624258),
    (1429624119, 1429624849),
    (1429624745, 1429625510),
    (1429625336, 1429626031),
    (1429625857, 1429626310),
    (1429626136, 1429626622),
    (1429626310, 1429626970),
    (1429627561, 1429628083),
    (1429627735, 1429628257),
    (1429628257, 1429628918),
    (1429628709, 1429629335),
    (1429629126, 1429629648),
    (1429629474, 1429629926),
    (1429629717, 1429630135),
    (1429629926, 1429630378),
    (1429629996, 1429630726),
    (1429630517, 1429631178),
    (1429630969, 1429631700),
    (1429633265, 1429633890)])


# run_times = concatenate((day1_times, day2_times))
run_times = concatenate((day1_times, house2_times))
expected_periods = array([2, 2.5, 3.03, 1, 1.49, 2, 2.5, 3.03, 3.58, 3.99, 4.56, 2.88])
expected_freqs = 1 / expected_periods

stevens_interval = .02
data_fold = '/home/chris/work/stevens_data/'
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

stevens_series = [get_stevens_wire_data(f) for f in fnames]


def get_instrument_pressure(f):
    """Get time, pressure and depth from a netCDF file f.
    t is in seconds, p is in dbar(?) and d is in meters"""
    t = nc.get_time(f) / 1000
    d = nc.get_pressure(f)
    t_interp = arange(t[0], t[-1], stevens_interval)
    d_interp = interp(t_interp, t, d)
    return pd.Series(d_interp, t_interp)


def get_instrument_data(f):
    """Get time, pressure and depth from a netCDF file f.
    t is in seconds, p is in dbar(?) and d is in meters"""
    t = nc.get_time(f) / 1000
    p = nc.get_pressure(f)
    z = -nc.get_device_depth(f)
    H = nc.get_water_depth(f)
    # DELETE THIS STUFF
    # z = -100
    # H = 200 * ones_like(H)
    d = p2d.combo_method(t, p, z, H, t[1] - t[0])
    t_interp = arange(t[0], t[-1], stevens_interval)
    d_interp = interp(t_interp, t, d)
    return pd.Series(d_interp, t_interp)


def find_likely_time(stevens_series, instrument_s, interval):
    """Match the stevens series to the instrument and return the start
    time.
    """
    clean_series = remove_mean(stevens_series)
    tlen = clean_series.index[-1] - clean_series.index[0]
    end_time = interval[1] - stevens_series.index[-1] + stevens_series[0]
    time = interval[0]
    min_time = time
    min_dif = False
    while time < end_time:
        window = remove_mean(instrument_s[time:time + tlen + stevens_interval])
        dif = rmse(clean_series.values, window.values)
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
    plot(instrument_s.index, instrument_s.values,
         label='Instrument readings (m)', color='black')
    for file_number, idx in zip(runs, indices):
        s = stevens_series[file_number]
        stevens_fname = fnames[file_number]
        if file_number in blacklist:
            continue
        t = s.index
        d = s.values
        offset = average(instrument_s[idx:idx + t[-1] - t[0]])
        plot(t + idx, d + offset, label=stevens_fname)
    legend()
    xlabel('Time (s)')
    ylabel('Depth of Sensor (m)')
    title(plot_title)
    show()


def get_windows(instrument_fname, stevens_series, runs, time_offset=0):
    instrument_s = get_instrument_data(instrument_fname)
    instrument_s.index += time_offset
    indices = []
    windows = []
    for file_number, in zip(runs):
        s = stevens_series[file_number]
        if file_number in blacklist:
            indices.append(nan)
            windows.append(())
            continue
        guess = run_times[file_number]
        fname = fnames[file_number]
        print('Processing file', file_number)
        s_len = s.index[-1] - s.index[0]
        t = find_likely_time(s, instrument_s, guess)
        w = instrument_s[t:t + s_len]
        windows.append(w)
        indices.append(t)
    return indices, windows


def get_main_frequency(series):
    timestep = series.index[1] - series.index[0]
    amps, freqs = get_transform(series.values, stevens_interval)
    return freqs[argmax(amps[1:]) + 1] # find largest frequency > 0


def fit_sine(series):
    series = remove_mean(series)
    freq_guess = get_main_frequency(series)
    phase_guess = 1
    amp_guess = series.max()
    f = lambda t, amp, freq, phase: amp * sin(2*pi*freq*t - phase)
    popt, pcov = curve_fit(f, series.index, series.values,
                           p0=(amp_guess, freq_guess, phase_guess))
    return popt

def get_stats(stevens_series, windows, runs):
    window_stats = []
    stevens_stats = []
    for i, w in zip(runs, windows):
        s = stevens_series[i]
        if i in blacklist:
            continue
        s.index -= s.index[0] # large time values swamp the fit, causing failure
        w.index -= w.index[0]
        s_stats = fit_sine(s)
        w_stats = fit_sine(w)
        window_stats.append(w_stats)
        stevens_stats.append(s_stats)
    data = concatenate((array(window_stats), array(stevens_stats)), 1)
    df = pd.DataFrame(data, columns=['instrument_amp',
                                     'instrument_freq',
                                     'instrument_phase',
                                     'stevens_amp',
                                     'stevens_freq',
                                     'stevens_phase'])
    df['instrument_amp'] = absolute(df['instrument_amp'])
    df['stevens_amp'] = absolute(df['stevens_amp'])
    df['instrument_freq'] = absolute(df['instrument_freq'])
    df['stevens_freq'] = absolute(df['stevens_freq'])
    return df


# runs = range(0, 12)
# instrument_f = house1
# indices, windows = get_windows(tru1, stevens_series, runs)
# indices2, windows2 = get_windows(tru2, stevens_series, runs)
# indices3, windows3 = get_windows(house1, stevens_series, runs, time_offset=510)
# data = {tru1: get_stats(stevens_series, windows, runs),
#         tru2: get_stats(stevens_series, windows2, runs),
#         house1: get_stats(stevens_series, windows3, runs)}


runs = range(12, 41)
runs = range(0, 12)
offset = 0
fname = tru1
indices, windows = get_windows(fname, stevens_series, runs, time_offset=offset)
wp = pd.Panel(data)

instrument_s = get_instrument_data(fname)
plot_stevens_over_instrument(instrument_s, fnames, runs, blacklist,
                             array(indices) - offset, stevens_series)
# def plot_stevens_over_instrument(instrument_s, stevens_fnames,
#                                  runs, blacklist, indices, stevens_series,
#                                  plot_title=''):


print(average(wp.minor_xs('instrument_amp') - wp.minor_xs('stevens_amp')))


# ## sldkfj
# offset=0
# indices = array(indices) - offset
# p = get_instrument_pressure(fname)
# depth = get_instrument_data(fname)
# d_static = p2d.hydrostatic_method(p)
# for file_number, idx in zip(runs, indices):
#     s = stevens_series[file_number]
#     stevens_fname = fnames[file_number]
#     if file_number in blacklist:
#         continue
#     t = s.index
#     d = s.values
#     offset = average(depth[idx:idx + t[-1] - t[0]])
#     if file_number==1:
#         plot(t + idx, d + offset, color=sns.color_palette()[2], label='Real depth')
#     else:
#         plot(t + idx, d + offset, color=sns.color_palette()[2])
# plot(depth.index, depth.values, label='FFT (m)')
# plot(d_static.index, d_static.values, label='Hydrostatic (m)')
# legend()
# xlabel('Time (s)')
# ylabel('Depth of Sensor (m)')
# title('Hydrostatic and FFT comparison for 2.5 second waves')
# show()
