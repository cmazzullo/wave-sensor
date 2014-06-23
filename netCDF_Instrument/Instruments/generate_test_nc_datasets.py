import os
from datetime import datetime
import pytz
import numpy as np
import pylab
import blackbox

start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
data_start = datetime(year=2014,month=3,day=20,tzinfo=pytz.utc)
dt = 1.0 #seconds
npts = 100000 #number of points in the series
#--use the last amplitude-period pair as the "baro" signal
amplitudes = np.array([0.1,1.0,10,100]) #psi
periods = np.array([10.0,100.0,1000.0,10000.0]) #seconds

offset = (data_start - start).total_seconds()
print offset
t = np.arange(offset,offset+(npts*dt),dt) #time
freqs = 1.0 / periods
omegas = 2.0 * np.pi * freqs
print freqs
pres_signal = np.zeros_like(t)
for o,a in zip(omegas,amplitudes):
	pres_signal += a * np.sin(t*o)
baro_signal = amplitudes[-1] * np.sin(t*omegas[-1])

lt_pres = blackbox.leveltroll()		
lt_pres.is_baro = False
lt_pres.pressure_units = "psi"
lt_pres.z_units = "meters"
lt_pres.longitude = np.float32(0.0)
lt_pres.latitude = np.float(0.0)
lt_pres.salinity_ppm = np.float32(0.0)
lt_pres.z = np.float32(0.0)

lt_baro = blackbox.leveltroll()		
lt_baro.is_baro = False
lt_baro.pressure_units = "psi"
lt_baro.z_units = "meters"
lt_baro.longitude = np.float32(0.0)
lt_baro.latitude = np.float(0.0)
lt_baro.salinity_ppm = np.float32(0.0)
lt_baro.z = np.float32(0.0)

lt_pres.timezone_string = "fake_utc"
lt_baro.timezone_string = "fake_utc"
lt_pres.in_filename = "fake"
lt_baro.in_filename = "fake"

millsecond = t * 1000.0
lt_pres.utc_millisecond_data = millsecond
lt_baro.utc_millisecond_data = millsecond
lt_pres.pressure_data = pres_signal
lt_baro.pressure_data = baro_signal
lt_pres.data_start = start
lt_baro.data_start = start



#--write noise-less test files
lt_pres.out_filename = os.path.join("benchmark","testdata.nc")
if os.path.exists(lt_pres.out_filename):
		os.remove(lt_pres.out_filename)
lt_baro.out_filename = os.path.join("benchmark","testbaro.nc")
if os.path.exists(lt_baro.out_filename):
		os.remove(lt_baro.out_filename)
lt_pres.write()
lt_baro.write()

#--add some noise
noise = np.random.normal(loc=0.0,scale=np.min(amplitudes)*0.1,size=t.shape)
lt_pres.pressure_data += noise

#--write noisy pressure files
lt_pres.out_filename = os.path.join("benchmark","testdata_noise.nc")
if os.path.exists(lt_pres.out_filename):
		os.remove(lt_pres.out_filename)
lt_pres.write()



fig = pylab.figure(figsize=(10,10))
ax = pylab.subplot(111)
ax.plot(t,pres_signal,'b',label="signal")
pylab.show()
