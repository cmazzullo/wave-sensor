# Get pressure data from a file

# from  NetCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np

# def get_pressure_array(fname):
#     f = Dataset(fname, 'r', format='NETCDF4_CLASSIC')
#     v = f.variables
#     P = v['sea_water_pressure'][:]
#     return P

# Constants
g = 9.8                         # gravity
rho = 1030                      # density of seawater in kg/m**3

def compress_np(arr, c=10):
    final = np.zeros(math.floor(len(arr) / c))
    summed = 0
    for i, e in enumerate(arr):
        summed += np.float64(e)
        if i % c == c - 1:
            final[math.floor(i / c)] = summed / c
            summed = 0
    return final

def compress(P):
    M = 500
    c = math.ceil(len(P) / M)
    p = compress_np(P, c)
    return p

def make_pressure(length):
    time = np.arange(length)
    slope = 0.1
    intercept = 30
    frequency = .01
    ang_freq = 2 * np.pi * frequency
    m = .1
    P = slope * time + m * np.sin(ang_freq * time) + intercept
    plt.plot(P)
    plt.show()
    return P
    
def create_pwave_data(P):
    freq = 4    
    t = np.arange(0, len(P)) / freq
    slope, intercept =  np.polyfit(t, P, 1)
    Pstatic = slope * t + intercept
    Pwave = P - Pstatic
    return Pstatic, Pwave
    
fname = '/home/chris/measurement-systems.nc'
#P = get_pressure_array(fname)
P = make_pressure(100)
P = P * 1e4
Pstatic, Pwave = create_pwave_data(P)
depth = Pstatic / (rho * g)
# Find individual pressure waves

# Downward crossing method: if the function crosses the x axis in
# an interval and if its endpoint is below the x axis, we've found
# a new wave.

start = period = counter = Pmin = Pmax = 0
periods = []                    # periods of found waves
eta = np.zeros(len(P))
interval = 1 / 4
steepness = 0.03
Hminimum = 0.10

H = []


for i in range(len(Pwave) - 1):
    if (Pwave[i] * Pwave[i+1]) < 0 and Pwave[i+1] < 0:
        print(i)
        periods.append(period)
        # apply w**2 = g * k, the dispersion relation for deep water 
        wavelength = g * period**2 / (2 * np.pi)
        # if the water is too shallow
        if depth[i] / wavelength < 0.36:
            wavelength = ((g * depth[i])**(1/2) *
                          (1 - depth[i] / wavelength) * period)
        height = (np.cosh(2 * np.pi * depth[i] / wavelength)
                  * (Pmax - Pmin) / (rho * g))
        H.append(height)
        Hunreduced = Hreduced = height
        if height / wavelength > steepness:
            print('Wave is too steep!')
            Hreduced = steepness * wavelength
            H.pop()
            H.append(Hreduced)
        if height < Hminimum:
            print('Wave is too small!')    
            Hreduced = Hminimum
            counter -= 1
        reduction = Hreduced / Hunreduced
        for j in range(start, i):
            eta[j] = ((Pwave[j] * reduction) / (rho * g)) * \
                     np.cosh(2 * np.pi * depth[j] / wavelength)
        start = i + 1
        period = Pmax = Pmin = 0
        counter += 1
    period = period + interval
    if Pwave[i] > Pmax:
        Pmax = Pwave[i]
    if Pwave[i] < Pmin:
        Pmin = Pwave[i]
        

                
