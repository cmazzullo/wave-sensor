import numpy as np
from pytz import timezone
from Instruments.rbrsolo import RBRSolo
from Instruments.leveltroll import Leveltroll
from Instruments.waveguage import Waveguage
from Instruments.house import House
from Instruments.measuresys import MeasureSysLogger
from Instruments.hobo import Hobo

sea_pressure = True

inputs = { 'instrument_name' : 'Measurement Specialties',
           'in_filename' : '/home/chris/work/wave-sensor/data_files/logger1.csv',
           'out_filename' : '/home/chris/testfile.nc',
           'latitude' : '20',
           'longitude' : '20',
           'salinity' : '100',
           'initial_water_depth' : '11',
           'final_water_depth' : '10',
           'device_depth' : '9.5',
           'deployment_time' : '20140101 0000',
           'retrieval_time' : '20140102 0000',
           'tzinfo' : 'US/Central',
           'sea_name' : 'Atlantic Ocean',
           'creator_name' : 'Chris Mazzullo',
           'creator_email' : 'stuff@gmail.com',
           'creator_url' : 'zombo.com' }

DATATYPES = { 'latitude': np.float32,
              'longitude': np.float32,
              'salinity': np.float32,
              'initial_water_depth': np.float32,
              'final_water_depth': np.float32,
              'device_depth': np.float32,
              'tzinfo': timezone }

for key in inputs: # cast everything to the right type
    if key in DATATYPES:
        inputs[key] = DATATYPES[key](inputs[key])

INSTRUMENTS = {'LevelTroll': Leveltroll,
               'RBRSolo': RBRSolo,
               'Wave Guage': Waveguage,
               'USGS Homebrew': House,
               'Measurement Specialties': MeasureSysLogger,
               'HOBO': Hobo}

instrument = INSTRUMENTS[inputs['instrument_name']]()

instrument.user_data_start_flag = 0
for key in inputs:
    setattr(instrument, key, inputs[key])

instrument.read()
instrument.write(sea_pressure=sea_pressure)

# if os.path.isfile(out_file):
#     os.remove(out_file)
