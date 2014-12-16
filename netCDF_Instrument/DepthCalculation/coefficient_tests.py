## Initialize
from numpy import *
from matplotlib.pyplot import *
ion()

from DepthCalculation.pressure_to_depth import fft_method
from DepthCalculation.testing import make_waves

# deeper = have to lower the cutoff
g = 9.8
rho = 1027

## Test whole input/output

# CHANGEABLES

h = 20
length = 6000 # length of the time series in seconds
sample_frequency = 4 # time steps per second (Hz)
z = 1-h
hi_cut = .89 / sqrt(h)
#hi_cut = .2

# MAKE WAVES

waves = [[.101,   .09,  0],
          [.201,   .2,   1],
          [.0101,  .3,   2],
          [1.01,   .05,  2]]

max_f = .2
max_a = 10
max_phase = 10
n = 5 # number of waves
waves = array([[max_f, max_a, max_phase]]*n)*random.rand(n, 3)
t, y, p = make_waves(length, sample_frequency, waves, h, 1-h)

y2 = fft_method(t, p/10000, z, ones_like(t)*h, \
                1/sample_frequency, hi_cut=hi_cut, \
                window=False, gate=0)
static = p/rho/g

## Plotting

clf()
cla()
subplot(211)
plot(t, y, label='Original η')
xlabel('time (s)')
ylabel('η (meters)')
plot(t, static, 'g', label='Hydrostatic η')
plot(t, y2, 'r', label='FFT reconstructed η')
legend()

def get_transform(seq):
    return fft.rfft(seq) / len(seq), fft.rfftfreq(len(seq), 1/sample_frequency)

fft_amps, fft_freqs = get_transform(y2)
actual_amps, actual_freqs = get_transform(y)
static_amps, static_freqs = get_transform(static)

subplot(212)
grid()
plot(actual_freqs, 2*absolute(actual_amps), color='black')

plot(static_freqs, 2*absolute(static_amps), 'x', color='blue')
plot(fft_freqs, 2*absolute(fft_amps), 'x', color='red')
xlim(0, .5)

xlabel('frequency (Hz)')
ylabel('η (meters)')

def rmse(a, b):
    return sqrt(average(absolute(a-b)**2))

fft_rmse = rmse(y2, y)
static_rmse = rmse(static, y)

fft_rmse = rmse(actual_amps,fft_amps)
static_rmse = rmse(actual_amps,static_amps)

print('FFT RMSE = %.4f meters' % fft_rmse)
print('Static RMSE = %.4f meters' % static_rmse)

if static_rmse < fft_rmse:
    print("""STATIC IS DOING BETTER
SOMETHING IS HORRIBLY WRONG""")

# dispersion relation
# ω² = gk⋅tanh(kH)

## Find coefficient
# p α ηρg cosh(k(z+H))/cosh(kH) So we want our coefficient to be C =
# 12.32, where C = cosh(kH)/cosh(kZ). What should k be?
# max frequency is 1/4 so max k is .252
# arccos(12) gives best cutoff frequency, so max_cutoff = 3.18

def k(h):
    return 3.2/h

def c(k, h, z): # where z = distance from bottom
    return cosh(k(h)*h)/cosh(k(h)*z)

max_k = .252

h = arange(0, 100, .01)
z = 1
plot(h, c(k, h, z))

## Test coefficient

f_cutoff = 0.89/sqrt(H)

## Repeatedly test cutoff, plot histogram
h = 50
length = 6000 # length of the time series in seconds
sample_frequency = 4 # time steps per second (Hz)
z = 1-h
hi_cut = .89 / sqrt(h)

static_time_rmse = []
fft_time_rmse = []
fft_freq_rmse = []
static_freq_rmse = []
for i in range(1000):
    # MAKE WAVES
    waves = [[.101,   .09,  0],
              [.201,   .2,   1],
              [.0101,  .3,   2],
              [1.01,   .05,  2]]

    max_f = .2
    max_a = 10
    max_phase = 10
    n = 10 # number of waves
    waves = array([[max_f, max_a, max_phase]]*n)*random.rand(n, 3)
    t, y, p = make_waves(length, sample_frequency, waves, h, 1-h)

    y2 = fft_method(t, p/10000, z, ones_like(t)*h, \
                    1/sample_frequency, hi_cut=hi_cut, \
                    window=False, gate=.8)
    static = p/rho/g

    def get_transform(seq):
        return fft.rfft(seq) / len(seq), fft.rfftfreq(len(seq), 1/sample_frequency)

    fft_amps, fft_freqs = get_transform(y2)
    actual_amps, actual_freqs = get_transform(y)
    static_amps, static_freqs = get_transform(static)

    def rmse(a, b):
        return sqrt(average(absolute(a-b)**2))

    fft_time_rmse.append(rmse(y2, y))
    static_time_rmse.append(rmse(static, y))
    fft_freq_rmse.append(rmse(actual_amps,fft_amps))
    static_freq_rmse.append(rmse(actual_amps,static_amps))

## Plot time space
cla()
title('RMSE comparison (H = %sm)' % h)
hist([fft_time_rmse, static_time_rmse], histtype='step', \
     color=['red','blue'], label=['FFT method RMSE', 'Hydrostatic RMSE'], bins=50)
xlabel('RMSE (m)')
ylabel('Count')
legend()
