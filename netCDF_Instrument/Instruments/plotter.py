import sys
sys.path.append('..')

import numpy as np

from Instruments.house import House
import matplotlib.pyplot as plt

def getdata(fname):
    lt = House()
    lt.creator_email = "a@aol.com"
    lt.creator_name = "Jurgen Klinnsmen"
    lt.creator_url = "www.test.com"
    lt.in_filename = fname
    lt.out_filename = './plotter-output.nc'
    lt.is_baro = True
    lt.pressure_units = "bar"
    lt.z_units = "meters"
    lt.longitude = np.float32(0.0)
    lt.latitude = np.float(0.0)
    lt.salinity_ppm = np.float32(0.0)
    lt.z = np.float32(0.0)
    lt.read()    
    return lt

def compress(data, n):
    """Averages every group of n points in the data"""
    result = []
    summed = 0
    for i, e in enumerate(data):
        summed += e
        if i % n == n - 1:
            result.append(summed / n)
            summed = 0
    return result

fname1 = (r'/home/chris/Documents/'
          r'Neag Sensor 1 Atmospheric Pressure Test 071414.csv')

fname2 = (r'/home/chris/Documents/'
          r'Neag Sensor 2 Atmospheric Pressure Test 071414.csv')

lt1 = getdata(fname1)
lt2 = getdata(fname2)
press1 = lt1.pressure_data
press2 = lt2.pressure_data
temp1 = lt1.temperature_data
temp2 = lt2.temperature_data

sum = 0
plt.vlines()
for x in press1:
    sum += x

mean = sum / len(press1)

print('press11: mean = ' + str(mean))
print('len press1 = ' + str(len(press1)))
print('len press2 = ' + str(len(press2)))

plt.plot(press2[:7200])
plt.plot(press1[:7200])
print(len(press1))

list1 = []



plt.show()


        
