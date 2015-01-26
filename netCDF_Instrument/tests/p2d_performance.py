import pressure_to_depth as p2d
import timeit as ti
from numpy.random import rand
# We want to create datasets full of noise with different lengths and
# see how the pressure to depth conversion performs on them.

# Maybe come up with a pressure to depth algorithm without an explicit
# for loop?

import seaborn as sns
from matplotlib.pyplot import *
ion()

def time_combo(length, times):
    setup='''import numpy as np
import pressure_to_depth as p2d
length = %d
t = np.arange(length)
data = np.random.rand(length)''' % length
    combo = 'p2d.combo_method(t, data, 10, 11*np.ones(length), 1)'
    return ti.timeit(stmt=combo, setup=setup, number=times) / times


lengths = range(100, 10100, 500)
time_arr = []
for length in lengths:
    times = 10
    time_arr.append(time_combo(length, times))

plot(lengths, time_arr)
