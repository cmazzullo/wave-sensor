import numpy as np
import numpy.testing as nptest
from scipy.optimize import bisect
from unit_conversion import PASCAL_TO_DBAR
from pressure_to_depth import combo_method

G = 9.8
SEAWATER_DENSITY = 1030

def f_from_k(k, h):
    return np.sqrt(G * k * np.tanh(k * h)) / (2*np.pi)


def k_from_f(f, h):
    func = lambda k: f_from_k(k, h) - f
    return bisect(func, 0, 10)


def get_pressure(depth, k, z, h):
    return SEAWATER_DENSITY * G * depth * np.cosh(k * (z + h)) / np.cosh(k * h)


def make_known_waves(t, h, z):
    n = 25 # number of waves in the interval
    wave_freq = n / (t[-1] - t[0]) # Hz
    wave_k = k_from_f(wave_freq, h)
    wave_amp = 1.5
    known_depth = wave_amp * np.sin(2 * np.pi * wave_freq * t)
    known_p = get_pressure(known_depth, wave_k, z, h) * PASCAL_TO_DBAR
    return known_p, known_depth


def test_p2d_combo_method():
    h = 3 # water depth
    z = -2.5 # device depth
    sample_freq = 4 # Hz
    total_time = 25*60 # seconds
    t = np.linspace(0, total_time, sample_freq * total_time + 1)
    known_p, known_depth = make_known_waves(t, h, z)
    calculated_depth = combo_method(t, known_p, z, np.ones_like(t) * h,
                                    1 / sample_freq)
    nptest.assert_allclose(known_depth, calculated_depth, atol=.1)
