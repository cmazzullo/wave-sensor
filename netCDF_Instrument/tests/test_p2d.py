from nose.tools import *
from numpy import *
from matplotlib.pyplot import *
from scipy.optimize import bisect
from unit_conversion import PASCAL_TO_DBAR
from pressure_to_depth import combo_method, rmse

G = 9.8
SEAWATER_DENSITY = 1030

def f_from_k(k, h):
    return sqrt(G * k * tanh(k * h)) / (2*pi)


def k_from_f(f, h):
    func = lambda k: f_from_k(k, h) - f
    return bisect(func, 0, 10)


def get_pressure(depth, k, z, h):
    return SEAWATER_DENSITY * G * depth * cosh(k * (z + h)) / cosh(k * h)



def make_known_waves(t, h, z):
    wave_freq = .25 # Hz
    wave_k = k_from_f(wave_freq, h)
    wave_amp = 1.5
    known_depth = wave_amp * sin(2 * pi * wave_freq * t)
    known_p = get_pressure(known_depth, wave_k, z, h) * PASCAL_TO_DBAR
    return known_p, known_depth

def test_p2d_combo_method():
    h = 3 # water depth
    z = -2.5 # device depth
    total_time = 5 * 60 # seconds
    sample_freq = 4 # Hz
    t = linspace(0, total_time, sample_freq * total_time + 1)
    known_p, known_depth = make_known_waves(t, h, z)
    calculated_depth = combo_method(t, known_p, z, ones_like(t) * h,
                                    1 / sample_freq)
    err = rmse(known_depth, calculated_depth)
    print(err)
    err2 = rmse(known_depth, zeros_like(t))
    print(err2)