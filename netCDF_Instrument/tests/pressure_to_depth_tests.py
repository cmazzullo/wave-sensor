# Now with cells!

## Initialize
from numpy import *
from matplotlib.pyplot import *
ion()

from scipy.optimize import newton
from pressure_to_depth import fft_method
from pressure_to_depth import combo_method

g = 9.8
rho = 1027

def rmse(a, b):
    return sqrt(average(absolute(a-b)**2))

def print_rmse(y, static_y, fft_y):
    fft_rmse = rmse(fft_y, y)
    static_rmse = rmse(static_y, y)

    print('FFT RMSE = %.4f meters' % fft_rmse)
    print('Static RMSE = %.4f meters' % static_rmse)

    if static_rmse < fft_rmse:
        print("""STATIC IS DOING BETTER
    SOMETHING IS HORRIBLY WRONG""")

def make_waves(length, sample_frequency, waves, h, z):
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
    c = random.rand()*20
    total_height += c*arange(len(total_height)) / len(total_height)
    total_pressure += rho*g*c * arange(len(total_height)) / len(total_height)
    return t, total_height, total_pressure

def random_waves(length, sample_frequency, h, z, max_f, max_a, n):
    waves = array([[max_f, max_a, 2*pi]]*n)*random.rand(n, 3)
    return make_waves(length, sample_frequency, waves, h, z)

def easy_waves(length, h, z, n):
    return random_waves(length, 4, h, z, .2, z/4, n)

if __name__ == '__main__':
    # CHANGEABLES

    h = 20
    length = 6000 # length of the time series in seconds
    sample_frequency = 4 # time steps per second (Hz)
    z = 1-h
    hi_cut = .89 / sqrt(h)

    max_f = .2
    max_a = 10
    max_phase = 10
    n = 5 # number of waves
    waves = array([[max_f, max_a, max_phase]]*n)*random.rand(n, 3)
    t, y, p = make_waves(length, sample_frequency, waves, h, 1-h)

    z_increase = 100

    y += z_increase * arange(len(y)) / len(y) # Linear trend
    p += rho*g*z_increase * arange(len(y)) / len(y) # Linear trend
    y2 = combo_method(t, p/10000, z, ones_like(t)*h, 1/sample_frequency)
    static = p/rho/g

    ## Plotting
    clf()
    subplot(211)
    plot(t, y, label='Original η')
    xlabel('time (s)')
    ylabel('η (meters)')
    plot(t, static, label='Hydrostatic η')
    plot(t, y2, label='FFT reconstructed η')
    legend()

    def get_transform(seq):
        return fft.rfft(seq) / len(seq), fft.rfftfreq(len(seq), 1/sample_frequency)

    fft_amps, fft_freqs = get_transform(y2)
    actual_amps, actual_freqs = get_transform(y)
    static_amps, static_freqs = get_transform(static)

    subplot(212)
    grid()
    plot(actual_freqs, 2*absolute(actual_amps), color='black')

    plot(static_freqs, 2*absolute(static_amps), '.', color='blue')
    plot(fft_freqs, 2*absolute(fft_amps), '.', color='red')
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

    # p α ηρg cosh(k(z+H))/cosh(kH) So we want our coefficient to be C =
    # 12.32, where C = cosh(kH)/cosh(kZ). What should k be?
    # max frequency is 1/4 so max k is .252
    # arccos(12) gives best cutoff frequency, so max_cutoff = 3.18

    ## Monte Carlo
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

        y += 10 * arange(len(y)) / len(y) #Linear trend

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

    ## Plot RMSE
    cla()
    title('RMSE comparison (H = %sm)' % h)
    hist([fft_time_rmse, static_time_rmse], histtype='step', \
         color=['red','blue'], label=['FFT method RMSE', 'Hydrostatic RMSE'], bins=50)
    xlabel('RMSE (m)')
    ylabel('Count')
    legend()

    ## Remove linear trend
    # get linear trend
    clf()
    coeff = polyfit(t, p, 1)
    plot(t, p, 'b')
    plot(t, coeff[1] + coeff[0]*t, 'r')
    show()

    ## math stuff
    h = 10
    z = -9
    k = lambda z, h: .1

    z = arange(-10, 10, .01)
    h = arange(-10, 10, .01)
    f = lambda z, h: cosh(k(z, h)*(z+h))/cosh(k(z, h)*h)
    clf()
    fig = figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(z, h, f(z, h))

    ## Outliers
    length = 300
    h = 10
    z = -9.5
    n = 10
    t, y, p = easy_waves(length, h, z, n)

    # Add outliers
    n_out = 10 # number of outliers
    outlier_val = 0
    p[random.randint(0, len(p), n_out)] = outlier_val
    combo_y = combo_method(t, p/10000, z, ones_like(t)*h, t[1] - t[0])
    clf()
    plot(t, y, label='Real y')
    plot(t, combo_y, label='Combo y')
    # plot(t, p, label='Combo y')
    legend()
