# Get pressure data from a file

# from  NetCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np

g = 9.8                         # gravity
rho = 1030                      # density of seawater in kg/m**3


def make_pressure(length):
    sample_freq = 4
    time = np.arange(length * sample_freq) / sample_freq
    start = 100600
    end = 100700
    slope = (end - start) / length
    wave_freq =.1
    ang_freq = 2 * np.pi * wave_freq
    height = 5000  # this prevents the waves from being too steep
    P = slope * time + height * np.sin(ang_freq * time) + start
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


def get_wave_data_method2(pressure_data, timestep):
    P = pressure_data
    Pstatic, Pwave = create_pwave_data(P)
    depth = Pstatic / (rho * g)

    # Find individual pressure waves

    # Downward crossing method: if the function crosses the x axis in
    # an interval and if its endpoint is below the x axis, we've found
    # a new wave.

    start = period = counter = Pmin = Pmax = 0
    periods = []                    # periods of found waves
    eta = np.zeros(len(P))
    steepness = 0.03
    Hminimum = 0.10

    H = []

    for i in range(len(Pwave) - 1):
        if (Pwave[i] * Pwave[i+1]) < 0 and Pwave[i+1] < 0:
            print(i)
            periods.append(period)
            # w**2 = g * k, the dispersion relation for deep water
            wavelength = g * period**2 / (2 * np.pi)
            # if the water is too shallow
            if depth[i] / wavelength < 0.36:
                wavelength = ((g * depth[i])**(1/2) *
                              (1 - depth[i] / wavelength) * period)
            height = (((Pmax - Pmin) / (rho * g)) *
                        np.cosh(2 * np.pi * depth[i] / wavelength))
            H.append(height)
            Hunreduced = Hreduced = height
            print('height = ' + str(height))
            print('wavelength = ' + str(wavelength))
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
        period = period + timestep
        if Pwave[i] > Pmax:
            Pmax = Pwave[i]
        if Pwave[i] < Pmin:
            Pmin = Pwave[i]
    return eta

if __name__ == '__main__':
    fname = '/home/chris/measurement-systems.nc'
    #P = get_pressure_array(fname)
    P = make_pressure(300)
    eta = get_wave_data_method2(P, .25)
    plt.plot(eta); plt.show()
