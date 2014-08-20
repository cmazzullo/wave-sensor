#!/usr/bin/env python3
from functools import partial
import matplotlib
matplotlib.use('TkAgg')
from collections import OrderedDict
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from pytz import timezone
import os
import numpy as np
from tkinter.filedialog import askopenfilename as fileprompt
import sys
sys.path.append('..')


from datetime import datetime
import pytz
import netCDF4
import netCDF4_utils
import netcdftime

from bitarray import bitarray as bit
import pandas

class Wavegui:


    def __init__(self, root, air_pressure=False):
        self.instruments = {'LevelTroll': Leveltroll,
                            'RBRSolo': RBRSolo,
                            'Wave Guage': Waveguage,
                            'USGS Homebrew': House,
                            'Measurement Specialties': MeasureSysLogger,
                            'HOBO': Hobo}
        self.root = root
        self.df_history = 'gui_df_history.txt'
        self.global_history = 'gui_global_history.txt'
        self.root.title("USGS Wave Data")
        self.air_pressure = air_pressure
        self.global_fields = [
            Variable(label='Your full name:', autosave=True,
                     name_in_device='creator_name'),
            Variable(label='Your email address:', autosave=True,
                     name_in_device='creator_email'),
            Variable(label='Your personal url:', autosave=True,
                     name_in_device='creator_url'),
            Variable(label='Project name:',  autosave=True,)]
        self.datafiles = list()
        self.filenames = set()
        self.initialize()


    def initialize(self):
        try:
            self.global_frame.destroy()
            self.file_frame.destroy()
        except AttributeError:
            pass
        self.global_frame = make_frame(self.root)
        add_label(self.global_frame, 'Global Settings:')
        entries = make_frame(self.global_frame)
        for row, var in enumerate(self.global_fields):
            self.make_widget(entries, var, row)
        entries.pack(fill=BOTH, expand=1)
        def save_globals():
            self.save_history(self.global_history, self.global_fields)
        def load_globals():
            self.load_history(self.global_history, self.global_fields)
        buttons = [("Add File(s)", self.add_files, 0 , 0),
                   ("Save Globals", save_globals, 0 , 1),
                   ("Load Globals", load_globals, 0 , 2),
                   ("Quit", self.root.destroy, 0 , 5)]
        if self.filenames:
            def load_per_file():
                for df in self.datafiles:
                    self.load_history(self.df_history, df.fields)
            buttons += [("Load Default", load_per_file, 0 , 3),
                        ("Process Files", self.process_files, 0 , 4)]
            self.file_frame = make_frame(self.root)
            add_label(self.file_frame, 'File specific settings:')
            tabs = make_frame(self.file_frame)
            book = ttk.Notebook(tabs, width=50)
            for df in self.datafiles:
                tab = make_frame(tabs)
                widgets = make_frame(tab)
                for row, var in enumerate(df.fields):
                    self.make_widget(widgets, var, row)
                widgets.pack(fill=BOTH, expand=1)
                save = partial(self.save_history, self.df_history,
                               df.fields)
                def remove_file(datafile):
                    self.filenames.remove(datafile.in_filename.get())
                    self.datafiles.remove(datafile)
                    self.initialize()
                rm = partial(remove_file, df)
                load = partial(self.load_history, self.df_history,
                               df.fields)
                buttonlist = [
                    ('Save Entries', save, 0, 1),
                    ('Remove File', rm, 0, 2),
                    ('Load Default', load, 0, 3)]
                make_buttonbox(tab, buttonlist)
                fname = os.path.basename(df.in_filename.stringvar.get())
                maxlen = 7
                if len(fname) > maxlen:
                    fname = fname[:maxlen] + '...'
                book.add(tab, text=fname)
            tabs.pack(fill=BOTH, expand=1)
            book.pack(fill=BOTH, expand=1)

            self.file_frame.grid(row=0, column=0, sticky=(N, W, E, S))

        make_buttonbox(self.global_frame, buttons)
        self.global_frame.update()
        self.global_frame.grid(row=1, column=0, sticky=(N, W, E, S))
        self.root.update()


    def add_files(self):
        new_fnames = set(fileprompt(multiple=True)) - self.filenames
        self.filenames |= new_fnames
        new_datafiles = [Datafile(fname, self.instruments)
                         for fname in new_fnames]
        self.datafiles += new_datafiles
        if self.filenames:
            self.initialize()


    def process_files(self):
        message = ('Processing files, this may take a few minutes.')
        d = MessageDialog(self.root, message=message,
                          title='Processing...', buttons=0,
                          wait=False)
        root.update()
        devices = [self.read_file(datafile, d) for datafile in
                   self.datafiles]
        if not all(devices):
            return
        start_points = [0 for d in devices]
        for device, s in zip(devices, start_points):
            self.write_file(device, s)
        d.destroy()
        MessageDialog(self.root, message="Success! Files saved.",
                      title='Success!')
        self.datafiles = list()
        self.filenames = set()
        self.initialize()


    def read_file(self, datafile, dialog):
        fields = self.global_fields + datafile.fields
        for var in fields:
            if ((var.in_air_pressure and self.air_pressure) or \
                (var.in_water_pressure and (not self.air_pressure))) \
                and var.required and not var.stringvar.get():
                dialog.destroy()
                MessageDialog(self.root, message="Incomplete entries,"
                              " please fill out all fields.",
                              title='Incomplete!', wait=True)
                return False
        device = self.instruments[datafile.instrument.get()]()
        for var in fields:
            if ((var.in_air_pressure and self.air_pressure) or
                (var.in_water_pressure and not self.air_pressure) and
                var.name_in_device):
                setattr(device, var.name_in_device, var.get())
        device.read()
        return device


    def write_file(self, device, start_point):
        device.user_data_start_flag = start_point
        out_file = device.out_filename
        if os.path.isfile(out_file):
            os.remove(out_file)
        sea_pressure = not self.air_pressure
        device.write(sea_pressure=sea_pressure)


    def save_history(self, filename, varlist):
        with open(filename, 'w') as f:
            for var in varlist:
                if var.autosave:
                    f.write(var.stringvar.get() + '\n')


    def load_history(self, filename, fields):
        any_fields_filled = (
            any(v.stringvar.get()
                for v in self.global_fields
                if not v.filename))
        l = [v for v in fields if v.autosave]
        message = 'This will overwrite your entries. Are you sure?'
        def proceed():
            d = MessageDialog(self.root, message=message,
                              title='Confirm', buttons=2, wait=True)
            return d.boolean
        if not any_fields_filled or proceed():
            if os.path.isfile(filename):
                with open(filename, 'r') as f:
                    for line, var in zip(f, l):
                        var.stringvar.set(line.rstrip())


    def make_widget(self, frame, var, row):
        air = self.air_pressure
        air_var = var.in_air_pressure
        water_var = var.in_water_pressure
        if ((not air_var) and air) or ((not water_var and not air)):
            return
        add_label(frame, var.label, pos=(row, 1))
        if var.filename:
            fname = os.path.basename(var.stringvar.get())
            add_label(frame, text=fname, pos=(row, 2))
        elif var.options:
            OptionMenu(frame, var.stringvar, *var.options)\
                .grid(column=2, row=row, sticky=(W, E))
        else:
            ttk.Entry(frame, width=20, textvariable=var.stringvar)\
                .grid(column=2, row=row, sticky=(W, E))
        if var.doc:
            c = lambda: MessageDialog(self.root, message=var.doc,
                                      title='Help')
            add_button(frame, 'Help', c, row, 3)


def make_frame(frame, header=None):
    return ttk.Frame(frame, padding="3 3 5 5")


def add_button(frame, text, command, row, column):
    b = ttk.Button(frame, text=text, command=command)
    b.grid(column=column, row=row, sticky=W)
    return b


def make_buttonbox(frame, buttonlist):
    """Expects button tuples: (text, command, row, column)"""
    box = make_frame(frame)
    for b in buttonlist:
        text, command, row, column = b
        add_button(box, text, command, row, column)
    box.pack(fill=BOTH, expand=1)
    return box


def add_label(frame, text, pos=None):
    label = ttk.Label(frame, text=text)
    if pos:
        row, column = pos
        label.grid(column=column, row=row, sticky=W)
    else:
        label.pack(fill=BOTH, expand=1)
    return label


class Datafile:

    def __init__(self, filename, instruments):
        self.in_filename = Variable(name_in_device='in_filename',
                                    label='Input filename:',
                                    filename='in')
        self.out_filename = Variable(name_in_device='out_filename',
                                     label='Output filename:',
                                     filename='out')
        self.instrument = Variable(options=instruments.keys(),
                                   label='Instrument:',
                                   autosave=True)
        self.fields = [
            self.in_filename,
            self.out_filename,
            self.instrument,
            Variable(name_in_device='latitude',
                     label='Latitude (decimal degrees):',
                     valtype=np.float32,
                     autosave=True,
                     doc='Decimal degrees east of the Prime Meridian.'),
            Variable(name_in_device='longitude',
                     autosave=True,
                     label='Longitude (decimal degrees):',
                     valtype=np.float32,
                     doc='Decimal degrees north of the equator.'),
            Variable(name_in_device='salinity',
                     autosave=True,
                     label='Salinity (ppm):',
                     valtype=np.float32,
                     in_air_pressure=False),
            Variable(name_in_device='initial_water_depth',
                     autosave=True,
                     label='Initial water depth (meters):',
                     valtype=np.float32,
                     in_air_pressure=False),
            Variable(name_in_device='final_water_depth',
                     autosave=True,
                     label='Final water depth (meters):',
                     valtype=np.float32,
                     in_air_pressure=False),
            Variable(name_in_device='device_depth',
                     autosave=True,
                     label='Depth of device below surface (meters):',
                     valtype=np.float32,
                     in_air_pressure=False),
            Variable(name_in_device='deployment_time',
                     autosave=True,
                     label='Deployment time (YYYYMMDD HHMM):',
                     in_air_pressure=False),
            Variable(name_in_device='retrieval_time',
                     autosave=True,
                     label='Retrieval time (YYYYMMDD HHMM):',
                     in_air_pressure=False),
            Variable(name_in_device='tzinfo',
                     autosave=True,
                     label='Timezone:',
                     options=("US/Central", "US/Eastern"),
                     valtype=timezone),
            Variable(name_in_device='sea_name',
                     label='Sea Name:',
                     in_air_pressure=False,
                     autosave=True,
                     options=('Chesapeake Bay',
                              'Great Lakes',
                              'Gulf of Alaska',
                              'Gulf of California',
                              'Gulf of Maine',
                              'Gulf of Mexico',
                              'Hudson Bay',
                              'Massachusetts Bay',
                              'NE Atlantic (limit-40 W)',
                              'NE Pacific (limit-180)',
                              'North American Coastline-North',
                              'North American Coastline-South',
                              'North Atlantic Ocean',
                              'North Pacific Ocean',
                              'NW Atlantic (limit-40 W)',
                              'NW Pacific (limit-180)',
                              'SE Atlantic (limit-20 W)',
                              'SE Pacific (limit-140 W)',
                              'SW Atlantic (limit-20 W)',
                              'SW Pacific (limit-147 E to 140 W)'))]
        self.in_filename.stringvar.set(filename)
        self.out_filename.stringvar.set(filename + '.nc')


class MessageDialog(Toplevel):

    def __init__(self, parent, message="", title="",  buttons=1,
                 wait=True):
        Toplevel.__init__(self, parent)
        body = Frame(self)
        self.title(title)
        self.boolean = None
        self.parent = parent
        self.transient(parent)
        ttk.Label(body, text=message).pack()
        if buttons == 1:
            b = ttk.Button(body, text="OK", command=self.destroy)
            b.pack(pady=5)
        elif buttons == 2:
            buttonframe = make_frame(body)
            def event(boolean):
                self.boolean = boolean
                self.destroy()
            b1 = ttk.Button(buttonframe, text='YES',
                        command=lambda: event(True))
            b1.grid(row=0, column=0)
            b2 = ttk.Button(buttonframe, text='NO',
                        command=lambda: event(False))
            b2.grid(row=0, column=1)
            buttonframe.pack()

        body.pack()
        self.grab_set()
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                 parent.winfo_rooty()+50))
        if wait:
            self.wait_window(self)


class Variable:

    def __init__(self, name_in_device=None, label=None,
                 doc=None, options=None, required=True,
                 filename=False, valtype=str, autosave=False,
                 in_air_pressure=True, in_water_pressure=True):
        self.name_in_device = name_in_device
        self.label = label
        self.doc = doc
        self.options = options
        self.stringvar = StringVar()
        self.stringvar.set('')
        self.required = required
        self.filename = filename
        self.valtype = valtype
        self.autosave = autosave
        self.in_air_pressure = in_air_pressure
        self.in_water_pressure = in_water_pressure

    def get(self):
        val = self.stringvar.get()
        return self.valtype(val)


class EmbeddedPlot:

    def __init__(self, root, data):
        top = self.top = Toplevel(root)
        message = ('Please select the point that you think is the '
                   'start of the useful data - probably when the '
                   'device was put in the water.')
        header = ttk.Label(top, text=message)
        header.pack(fill=BOTH, expand=1)

        f = Figure(figsize=(5, 4), dpi=100)
        self.a = a = f.add_subplot(111)
        a.plot(data)

        self.canvas = canvas = FigureCanvasTkAgg(f, master=top)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.toolbar = toolbar = NavigationToolbar2TkAgg(canvas, top)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        canvas.mpl_connect('button_press_event',
                           self.onclick)
        button = Button(master=top, text='Accept',
                        command=self.top.destroy)
        button.pack(side=BOTTOM)
        top.update()
        top.grab_set()
        self.dot = None
        self.xdata = 0

    def onclick(self, event):
        if self.dot:
            self.dot = self.a.plot(event.xdata, event.ydata, 'ro')
            self.canvas.show()

        self.xdata = event.xdata

epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)

def convert_to_milliseconds(series_length, datestring, date_format_string, frequency,date_seconds = None):
        if date_seconds == None:
            return  np.arange(series_length, dtype='int64') * (1000 / frequency)\
                + convert_date_to_milliseconds(datestring,date_format_string)
        else:
            return  np.arange(series_length, dtype='int64') * (1000 / frequency)\
                + date_seconds



def convert_date_to_milliseconds(datestring, date_format_string, date_time = None):
        if date_time == None:
            first_date = pytz.utc.localize(datetime.strptime(datestring, date_format_string))
            return (first_date - epoch_start).total_seconds() * 1000
        else:
            #pandas index will not take a long so I cannot multiply by 1000
            first_date = date_time
            return (first_date - epoch_start).total_seconds()
        
def convert_milliseconds_to_datetime(milliseconds, tzinfo):
        date = datetime.fromtimestamp(milliseconds / 1000)
        new_dt = tzinfo.localize(date)
        final_date = new_dt.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        return(final_date)
    
def get_time_duration(seconds_difference):

        days = int((((seconds_difference / 1000) / 60) / 60) / 24)
        hours =  int((((seconds_difference / 1000) / 60) / 60) % 24)
        minutes =  int(((seconds_difference / 1000) / 60)  % 60)
        seconds = (seconds_difference / 1000) % 60

        data_duration_time = "P%sDT%sH%sM%sS" % (days, hours, minutes, seconds)
        print(data_duration_time)


import uuid

class DataStore(object):
    '''Use this as an abstract data store, then pass a netcdf write stream to send data method'''
    def __init__(self, grouping):
        self.utc_millisecond_data = None
        self.data_start_date = None
        self.data_end_date = None
        self.data_duration = None
        self.pressure_data = None
        self.pressure_qc_data = None
        self.pressure_range = [-1000,1000]
        self.pressure_name = None
        self.temperature_data = None
        self.temperature_qc_data = None
        self.temperature_range = [-20,50]
        self.z_data = 0
        self.z_qc_data = None
        self.z_range = [-1000,1000]
        self.z_name = None
        self.latitude = 0
        self.latitude_range = [-90,90]
        self.longitude = 0
        self.longitude_range = [-180,180]
        self.z = 0
        self.salinity = 35
        self.data_grouping = grouping
        self.epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
        self.fill_value = np.float64(-1.0e+10)
        self.instrument_var = { 'long_name': 'Attributes for instrument 1',
                                'make_model': '',
                                'serial_number': '',
                                'calibration_date': '',
                                'factory_calibration': '',
                                'user_calibrated': '',
                                'calibration_report': '',
                                'accuracy': '',
                                'valid_range': [0,1],
                                'precision': '',
                                'comment': '',
                                'ancillary_variables': ''}
        self.time_var = {
                        'long_name': 'Time',
                        'short_name': 'time',
                        'standard_name': "time",
                        'units': "milliseconds since " + self.epoch_start.strftime("%Y-%m-%d %H:%M:%S"),
                        'calendar': "gregorian",
                        'axis': 'T',
                        'ancillary_variables': '',
                        'comment': "Original time zone future gui",
                        'ioos_category': "Time",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time"}
        self.lon_var = {
                        'long_name': "longitude of sensor",
                        'standard_name': "longitude",
                        'short_name': 'longitude',
                        'units': "degrees",
                        'axis': 'X',
                        'valid_min': self.longitude,
                        'valid_max': self.longitude,
                        'ancillary_variables': '',
                        'comment': "longitude 0 equals prime meridian",
                        'ioos_category': "Location",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time",
                        }
        self.lat_var = {
                        'long_name': "latitude of sensor",
                        'standard_name': "latitude",
                        'short_name': 'latitude',
                        'units': "degrees",
                        'axis': 'Y',
                        'valid_min': self.latitude,
                        'valid_max': self.latitude,
                        'ancillary_variables': '',
                        'comment': "latitude 0 equals equator",
                        'ioos_category': "Location",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time",
                        }
        self.z_var = {
                        'long_name': "altitude of sensor",
                        'standard_name': "altitude",
                        'short_name': 'altitude',
                        'units': "degrees",
                        'axis': 'Z',
                        'valid_min': self.z_range[0],
                        'valid_max': self.z_range[1],
                        'ancillary_variables': '',
                        'comment': "altitude of instrument",
                        'ioos_category': "Location",
                        'add_offset': 0.0,
                        'scale_factor': 1.0,
                        'compression': "not used at this time",
                      }
        self.z_var_qc = {
                                'flag_masks': '1111 1110 1101 1011',
                                'flag_meanings': "no_known_bad_data last_five_vals_identical, outside_valid_range, invalid_rate_of_change",
                                'comment': '1 signifies the value passed the test while a 0 flags a failed test, leading 1 is a placeholder'
                                }
        self.pressure_var = {
                             'long_name': "sensor pressure record",
                             'standard_name': "sea_water_pressure",
                             'short_name': "pressure",
                             'nodc_name': "pressure".upper(),
                             'units': "decibar",
                             'scale_factor': np.float32(1.0),
                             'add_offset': np.float32(0.0),
                             'compression': "not used at this time",
                             'min': self.pressure_range[0],
                             'max': self.pressure_range[1],
                             'ancillary_variables': '',
                             'coordinates': "time latitude longitude altitude",
                             'ioos_category': "Pressure",
                             'comment': "",
                             } 
        self.pressure_var_qc = {
                                'flag_masks': '1111 1110 1101 1011',
                                'flag_meanings': "no_bad_data last_five_vals_identical, outside_valid_range, invalid_rate_of_change",
                                 'comment': '1 signifies the value passed the test while a 0 flags a failed test, leading 1 is a placeholder'
                                }
        self.temp_var= {
                             'long_name': "sensor temperature record",
                             'standard_name': "temperature",
                             'short_name': "temp",
                             'nodc_name': "temperature".upper(),
                             'units': "degree_Celsius",
                             'scale_factor': np.float32(1.0),
                             'add_offset': np.float32(0.0),
                             'compression': "not used at this time",
                             'min': self.temperature_range[0],
                             'max': self.temperature_range[1],
                             'ancillary_variables': '',
                             'coordinates': "time latitude longitude altitude",
                             'ioos_category': "Temperature",
                             'comment': "",
                             } 
        self.temp_var_qc = {
                             'flag_masks': '111 110 101 011',
                             'flag_meanings': "no_bad_data last_five_vals_identical, outside_valid_range, invalid_rate_of_change",
                             'comment': '1 signifies the value passed the test while a 0 flags a failed test, leading 1 is a placeholder'
                            }
       
        self.global_vars_dict = {"cdm_data_type": "station",
                                 "comment": "not used at this time",
                                 "contributor_name": "USGS",
                                 "contributor_role": "data collector",
                                 "Conventions": "CF-1.6",
                                 "creator_email": "gui email",
                                 "creator_name": "gui name",
                                 "creator_url": "gui url",
                                 "date_created": datetime.strftime(datetime.now(tz=pytz.utc), "%Y-%m-%dT%H:%M:%SZ"),
                                 "date_modified": datetime.strftime(datetime.now(tz=pytz.utc), "%Y-%m-%dT%H:%M:%SZ"),
                                 "distance_from_referencepoint_to_transducer": None,
                                 "distance_from_transducer_to_seabed": None,
                                 "geospatial_lat_min": self.latitude_range[0],
                                 "geospatial_lat_max": self.latitude_range[1],
                                 "geospatial_lon_min": self.longitude_range[0],
                                 "geospatial_lon_max": self.longitude_range[1],
                                 "geospatial_lat_units": "degrees_north",
                                 "geospatial_lat_resolution": "point",
                                 "geospatial_lon_units": "degrees_east",
                                 "geospatial_lon_resolution": "point",
                                 "geospatial_vertical_min": self.z,
                                 "geospatial_vertical_max": self.z,
                                 "geospatial_vertical_units": "meters",
                                 "geospatial_vertical_resolution": "point",
                                 "geospatial_vertical_positive": "up",
                                 "history": "not used at this time",
                                 "id": "not used at this time",
                                 "institution": "USGS",
                                 "keywords": "not used at this time",
                                 "keywords_vocabulary": "not used at this time",
                                 "license": "This data may only be used upon the consent of the USGS",
                                 "Metadata_Conventions": "Unidata Dataset Discovery v1.0",
                                 "metadata_link": "http://54.243.149.253/home/webmap/viewer.html?webmap=c07fae08c20c4117bdb8e92e3239837e",
                                 "naming_authority": "not used at this time",
                                 "processing_level": "deferred with intention to implement",
                                 "project": "deferred with intention to implement",
                                 "publisher_email": "deferred with intention to implement",
                                 "publisher_name": "deferred with intention to implement",
                                 "publisher_url": "deferred with intention to implement",
                                 "readme": "file created by "+ "gui creator " +str(datetime.now()) +" with files " + "gui filenames",
                                 "salinity_ppm": self.salinity,
                                 "sea_name": "gui sea name",
                                 "standard_name_vocabulary": "CF-1.6",
                                 "summary": "This is data collected by a pressure instrument used for extrapolating information regarding weather patterns",
                                 "time_coverage_start": "utilitiy coverage start",
                                 "time_coverage_end": "utility coverage end",
                                 "time_coverage_duration": "utility coverage duration",
                                 "time_coverage_resolution": "P0.25S",
                                 "time_of_deployment": None,
                                 "time_of_retrieval": None,
                                 "time_zone": "UTC",
#                                  "title": 'Measure of pressure at %s degrees latitude, %s degrees longitude' \
#                                  ' from the date range of %s to %s' % (self.latitude, self.longitude,self.creator_name, \
#                                                                        self.data_start_date, self.data_end_date),
                                 "uuid": str(uuid.uuid4())
                                 }
    def send_data(self,ds):
        print('in VarDatastore.send_data')
        self.get_time_var(ds)
        self.get_pressure_var(ds)
        self.get_pressure_qc_var(ds)
        if self.temperature_data != None:
            self.get_temp_var(ds) 

        print('getting z var')            
        if type(self.z_data) != list:
            self.get_z_var(ds, False)
        else:
            self.get_z_var(ds, True)
            self.get_z_qc_var(ds)
        print('getting lat var')
        self.get_lat_var(ds)
        print('getting lon var')
        self.get_lon_var(ds)
        print('getting global_vars')
        self.get_global_vars(ds)
        print('getting time duration')
        self.get_time_duration()
        print('done write')
        
    def get_instrument_var(self,ds):
        instrument = ds.createVariable("instrument","i4")
        for x in self.instrument_var:
            instrument.setncattr(x,self.instrument_var[x])
        
    def get_time_var(self,ds):
        time = ds.createVariable("time","f8",("time",))
        for x in self.time_var:
            time.setncattr(x,self.time_var[x]) 
        time[:] = self.utc_millisecond_data
        
    def get_lat_var(self,ds):
        lat = ds.createVariable("latitude","f8",fill_value=self.fill_value)
        for x in self.lat_var:
            lat.setncattr(x,self.lat_var[x])
        lat[:] = self.latitude
            
    def get_lon_var(self,ds):
        lon = ds.createVariable("longitude","f8",fill_value=self.fill_value)
        for x in self.lon_var:
            lon.setncattr(x,self.lon_var[x])
        lon[:] = self.longitude
          
    def get_z_var(self,ds,time_dimen_bool = False):
        print('in get_z_var')
        print(time_dimen_bool)
        if time_dimen_bool == False:
            z = ds.createVariable("altitude", "f8",
                                  fill_value=self.fill_value)
        else:
            z = ds.createVariable("altitude", "f8",("time",),
                                  fill_value=self.fill_value)
        print('setting attributes')
        for x in self.z_var:
            z.setncattr(x,self.z_var[x])
        print('assigning to slice')
        z[:] = self.z_data
           
    def get_z_qc_var(self,ds):
        if self.z_name != None:
            z_qc = ds.createVariable(self.z_name,'i4',('time'))
        else:
            z_qc = ds.createVariable("altitude_qc",'i4',('time'))
        for x in self.z_var_qc:
            z_qc.setncattr(x,self.z_var_qc[x])
        z_qc[:] = self.z_qc_data
                   
    def get_pressure_var(self,ds):
        if self.pressure_name != None:
            pressure = ds.createVariable(self.pressure_name,"f8",("time",))
        else:
            pressure = ds.createVariable("sea_water_pressure","f8",("time",))
        for x in self.pressure_var:
            pressure.setncattr(x,self.pressure_var[x])
        pressure[:] = self.pressure_data
            
    def get_pressure_qc_var(self,ds):
        pressure_qc = ds.createVariable("pressure_qc",'i4',('time'))
        for x in self.pressure_var_qc:
            pressure_qc.setncattr(x,self.pressure_var_qc[x])
        pressure_qc[:] = self.pressure_qc_data
        
    def get_temperature_var(self,ds):
        temperature = ds.createVariable("temperature_at_transducer","f8", ("time",))
        for x in self.temperature_var:
            temperature.setncattr(x,self.temp_var[x])
        temperature[:] = self.temperature_data
            
    def get_temperature_qc_var(self,ds):
        temperature_qc = ds.createVariable("temperature_qc",'i4',('time'))
        for x in self.temp_var_qc:
            temperature_qc.setncattr(x,self.temp_var_qc[x])
        temperature_qc[:] = self.temperature_qc_data
            
    def get_global_vars(self, ds):
        for x in self.global_vars_dict:
            if self.global_vars_dict[x] is not None:
                ds.setncattr(x,self.global_vars_dict[x])
        
    def get_time_duration(self):
        print(type(self.utc_millisecond_data))
        first_milli = self.utc_millisecond_data[0]
        print(first_milli)
        second_milli = self.utc_millisecond_data[-1]
        print(second_milli)
        self.global_vars_dict["time_coverage_start"] = \
        convert_milliseconds_to_datetime(first_milli, pytz.utc)
        
        self.global_vars_dict["time_coverage_end"] = \
        convert_milliseconds_to_datetime(second_milli, pytz.utc)
        
        self.global_vars_dict["time_coverage_duration"] = \
        get_time_duration(second_milli - first_milli)
        
        self.global_vars_dict['title'] = 'Measure of pressure at %s degrees latitude, %s degrees longitude  by %s' \
        ' from the date range of %s to %s' % (self.latitude, self.longitude, self.global_vars_dict["creator_name"], \
                                                  self.global_vars_dict["time_coverage_start"], \
                                                  self.global_vars_dict["time_coverage_end"])
            
    
    def set_attributes(self, var_dict):
        """Sets attributes in script
        
        var_dict -- key- attr name value- attr value"""
        
        for x in var_dict:
            for y in var_dict[x]:
                var1 = self.__dict__[x]
                var1[y] = var_dict[x][y]
        print('done set')
        
sys.path.append('..')
class DataTests(object):
    """QC tests are performed on any data written to a netcdf file"""
     
    def __init__(self):
        self.five_count_list = list()
        self.pressure_data = None
        self.valid_pressure_range = [-10000,10000]
        self.pressure_max_rate_of_change = 10
        self.depth_data = None
        self.valid_depth_range = [-1000,1000]
        self.depth_max_rate_of_change = 20
        self.temperature_data = None
        self.valid_temperature_range = [-20,50]
        self.temperature_max_rate_of_change = None
        self.prev_value = np.NaN
        
       
    def select_tests(self, data_selection):
        '''Runs all of the netcdf Tests on the selected data, then performs an or binary mask (and) for
        those that passed, 1 for pass 0 for fail, and returns an unisgned 4bit integer, leading 1 is just a placeholder'''  
        
        if data_selection == 'depth':
            return self.run_tests(self.depth_data, self.valid_depth_range, self.depth_max_rate_of_change)
        elif data_selection == 'temperature':
            return self.run_tests(self.temperature_data, self.valid_temperature_range \
                                  , self.temperature_max_rate_of_change)
        else:
            return self.run_tests(self.pressure_data, self.valid_pressure_range, \
                                   self.pressure_max_rate_of_change)
        
  
    def run_tests(self, data, data_range, rate_of_change):
        """Runs all of the data tests"""
        
        bit_array1 = [self.get_1_value(x) for x in data]
        bit_array2 = [self.get_2_value(x, data_range) for x in data]
        bit_array3 = [self.get_3_value(x, rate_of_change) for x in data]
       
        final_bits = [bit_array1[x] & bit_array2[x] & bit_array3[x] for x in range(0,len(data))]
        
        return [x.to01() for x in final_bits]
    
   
    def get_1_value(self,x):
        """Checks to see if the sensor recorded 5 identical measurements previous the the current measurement, if so
        indicate an issue with a zero in the 1 bit"""
           
        if len(self.five_count_list) > 5:
            self.five_count_list.pop()
            
        flags = np.count_nonzero(np.equal(x,self.five_count_list))
        self.five_count_list.insert(0,x)
        
        if flags <= 4:
            return bit('1111')
        else:
            return bit('1110')  
            
    def get_2_value(self, x, data_range):
        '''Checks if the data point is within a valid range'''
        
        if np.greater_equal(x,data_range[0]) and \
        np.less_equal(x,data_range[1]):
            return bit('1111')
        else:
            return bit('1101')
        
    def get_3_value(self, x, rate_of_change):
        '''Checks to see if rate of change is within valid range'''
        
        if np.isnan(self.prev_value) or \
        np.less_equal(np.abs(np.subtract(x,self.prev_value)), rate_of_change):
            self.prev_value = x
            return bit('1111')
        else:
            self.prev_value = x
            return bit('1011')
                        
class NetCDFWriter(object):

    def __init__(self):
        self.pressure_comments = None
        self.temperature_comments = None
        self.depth_comments = None
        self.out_filename = os.path.join("..\Instruments",'benchmark','DepthTest.nc')
        self.in_filename = None
        self.is_baro = None
        self.pressure_units = None
        self.z_units = 'meters'
        self.latitude = 0
        self.longitude = 0
        self.z = 0
        self.salinity_ppm = -1.0e+10
        self.utc_millisecond_data = None
        self.pressure_data = None
        self.presure_data_flags = None
        self.epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
        self.data_start = None
        self.timezone_string = None
        self.tz_info = pytz.timezone('US/Eastern')
        self.date_format_string = None
        self.frequency = None
        self.valid_pressure_units = ["psi","pascals","atm"]
        self.valid_z_units = ["meters","feet"]
        self.valid_latitude = (np.float32(-90),np.float32(90))
        self.valid_longitude = (np.float32(-180),np.float32(180))
        self.valid_z = (np.float32(-10000),np.float32(10000))
        self.valid_salinity = (np.float32(0.0),np.float32(40000))
        self.valid_pressure = (np.float32(-10000),np.float32(10000))
        self.valid_temp = (np.float32(-10000), np.float32(10000))
        self.fill_value = np.float64(-1.0e+10)
        self.creator_name = ""
        self.creator_email = ""
        self.creator_url = ""
        self.sea_name = "The Red Sea"
        self.user_data_start_flag = None
        self.vstore = DataStore(1)
        self.vdict = dict()
        self.data_tests = DataTests()

        self.initial_water_depth = 0
        self.final_water_depth = 0
        self.device_depth = 0
        self.deployment_time = 0
        self.retrieval_time = 0

    def write_netCDF(self,var_datastore,series_length):
        ds = netCDF4.Dataset(os.path.join(self.out_filename),'w',format="NETCDF4_CLASSIC")
        time_dimen = ds.createDimension("time",series_length)
        var_datastore.set_attributes(self.var_dict())
        var_datastore.send_data(ds)

    def var_dict(self):
        var_dict = dict()

        lat_dict = {'valid_min': self.latitude, 'valid_max': self.latitude}
        var_dict['lat_var'] = lat_dict
        lon_dict = {'valid_min': self.longitude, 'valid_max': self.longitude}
        var_dict['lon_var'] = lon_dict
        global_vars = {'creator_name': self.creator_name, 'creator_email': self.creator_email,
                       'creator_eamil': self.creator_email, 'geospatial_lat_min': self.latitude,
                       'geospatial_lat_max': self.latitude, 'geospatial_lon_min': self.longitude,
                       'geospatial_lon_max': self.longitude, 'geospatial_vertical_min': self.z,
                       'geospatial_vertical_max': self.z, 'sea_name': self.sea_name,
                       'initial_water_depth': self.initial_water_depth, 'final_water_depth': self.final_water_depth,
                       'deployment_time': self.deployment_time, 'retrieval_time': self.retrieval_time,
                       'device_depth': self.device_depth}
        var_dict['global_vars_dict'] = global_vars

        return var_dict

class Hobo(NetCDFWriter):
    '''derived class for hobo csv files
    '''
    def __init__(self):
        self.timezone_marker = "time zone"      
        super().__init__()
        
        self.tz_info = pytz.timezone("US/Eastern")
        self.frequency = 1.0/30.0
        self.date_format_string = '%m/%d/%y %I:%M:%S %p'  
        self.data_tests = DataTests()
        self.transducer_distance_from_seabed = [0,0]
        self.reference_point_distance_to_transducer = [0,0]
        self.deployment_time = datetime.now(tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.retrieval_time = datetime.now(tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        
    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        skip_index = self.read_start('"#"',',')
        #for skipping lines in case there is calibration header data
        df = pandas.read_table(self.in_filename,skiprows=skip_index, header=None, engine='c', sep=',')
       
        self.utc_millisecond_data = convert_to_milliseconds(df.shape[0], df[1][0], \
                                                            self.date_format_string, self.frequency)
        
        self.pressure_data = [x for x in np.divide(df[2], 1.45037738)]
       
        print(len(self.pressure_data))
        
    def read_start(self, expression, delimeter):
        skip_index = 0;
        with open(self.in_filename,'r') as fileText:
            for x in fileText:
                file_string = x.split(delimeter)[0].strip()
                if expression == file_string:
                    print('Success! Index %s' % skip_index)
                    break
                skip_index += 1   
        return skip_index + 1 
    
    def write(self, sea_pressure = True):
        '''Write netCDF files
        
        sea_pressure - if true write sea_pressure data, otherwise write air_pressure data'''
        if sea_pressure == False:
            self.vstore.pressure_name = "air_pressure"
            self.vstore.pressure_var['standard_name'] = "air_pressure"
        else:
            self.vstore.global_vars_dict['distance_from_referencepoint_to_transducer'] = \
            'When Deployed: %s - When Retrieved: %s' % (self.reference_point_distance_to_transducer[0], \
                                                        self.reference_point_distance_to_transducer[1])
            self.vstore.global_vars_dict['distance_from_transducer_to_seabed'] = \
            'When Deployed: %s - When Retrieved: %s' % (self.transducer_distance_from_seabed[0],self.transducer_distance_from_seabed[1])
            self.vstore.global_vars_dict['time_of_deployment'] = self.deployment_time
            self.vstore.global_vars_dict['time_of_retrieval'] = self.retrieval_time
            
        self.vstore.pressure_data = self.pressure_data
        self.vstore.utc_millisecond_data = self.utc_millisecond_data
        self.vstore.latitutde = self.latitude
        self.vstore.longitude = self.longitude
       
        #Tests#
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')
        
        self.write_netCDF(self.vstore, len(self.pressure_data))  
        
class House(NetCDFWriter):
    '''derived class for house csv files
    '''
    def __init__(self):
        self.timezone_marker = "time zone"   
        self.temperature_data = None   
        super(House,self).__init__()
        self.tz_info = pytz.timezone("US/Eastern")
        self.frequency = 4
       
        self.date_format_string = '%Y.%m.%d %H:%M:%S '
        self.data_tests = DataTests() 
        self.transducer_distance_from_seabed = [0,0]
        self.reference_point_distance_to_transducer = [0,0]
        self.deployment_time = datetime.now(tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.retrieval_time = datetime.now(tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    

    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
       
        skip_index = self.read_start('^[0-9]{4},[0-9]{4}$',' ') 
        df = pandas.read_table(self.in_filename,skiprows=skip_index, header=None, engine='c', sep=',', names=('a','b'))
       
        self.pressure_data = [self.pressure_convert(np.float64(x)) for x in df[df.b.isnull() == False].a]
        self.temperature_data = [self.temperature_convert(np.float64(x)) for x in df[df.b.isnull() == False].b]
            
        with open(self.in_filename, 'r') as wavelog:
            for x in wavelog:
                if re.match('^[0-9]{4}.[0-9]{2}.[0-9]{2}', x):
                    self.utc_millisecond_data = convert_to_milliseconds(len(self.pressure_data), x, \
                                                                        self.date_format_string, self.frequency) #second arg has extra space that is unnecessary
                    break
       
        print(len(self.pressure_data))
        
    def pressure_convert(self, x):
        # gets volt to psig
        # gets psig to pascals
        return ((x * (30 / 8184) - 6) + 14.7) / 1.45037738
    
    def temperature_convert(self, x):
        # gets volts to farenheit
        # gets farenheit to celsius
        return (x * (168 / 8184) - 32) * (5.0/9)
    
    def read_start(self, expression, delimeter):
        skip_index = 0;
        with open(self.in_filename,'r') as fileText:
            for x in fileText:
                file_string = x.split(delimeter)[0]
                if re.match(expression, file_string):
                    print('Success! Index %s' % skip_index)
                    break
                skip_index += 1   
        return skip_index  
    
    def write(self, sea_pressure = True):
        '''Write netCDF files
        
        sea_pressure - if true write sea_pressure data, otherwise write air_pressure data'''
        
        if sea_pressure == False:
            self.vstore.pressure_name = "air_pressure"
            self.vstore.pressure_var['standard_name'] = "air_pressure"
        else:
            self.vstore.global_vars_dict['distance_from_referencepoint_to_transducer'] = \
            'When Deployed: %s - When Retrieved: %s' % (self.reference_point_distance_to_transducer[0], \
                                                        self.reference_point_distance_to_transducer[1])
            self.vstore.global_vars_dict['distance_from_transducer_to_seabed'] = \
            'When Deployed: %s - When Retrieved: %s' % (self.transducer_distance_from_seabed[0],self.transducer_distance_from_seabed[1])
            self.vstore.global_vars_dict['time_of_deployment'] = self.deployment_time
            self.vstore.global_vars_dict['time_of_retrieval'] = self.retrieval_time
        self.vstore.pressure_data = self.pressure_data
        self.vstore.utc_millisecond_data = self.utc_millisecond_data
        self.vstore.latitutde = self.latitude
        self.vstore.longitude = self.longitude
       
        #Tests#
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')
        
        self.write_netCDF(self.vstore, len(self.pressure_data))

class Leveltroll(NetCDFWriter):
    '''derived class for leveltroll ascii files
    '''
    def __init__(self):
        self.numpy_dtype = np.dtype([("seconds",np.float32),("pressure",np.float32)])
        self.record_start_marker = "date and time,seconds"
        self.timezone_marker = "time zone" 
        super(Leveltroll,self).__init__()
        self.date_format_string = "%m/%d/%Y %I:%M:%S %p "
        self.temperature_data = None
        self.data_tests = DataTests()
        self.transducer_distance_from_seabed = [0,0]
        self.reference_point_distance_to_transducer = [0,0]
        self.deployment_time = datetime.now(tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.retrieval_time = datetime.now(tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        
    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        f = open(self.in_filename,'rb')
        
        self.read_header(f)
        self.read_datetime(f)

        data = np.genfromtxt(f,dtype=self.numpy_dtype,delimiter=',',usecols=[1,2,3])     
        f.close()
        
        
        long_seconds = data["seconds"]
        print(long_seconds[::-1])
        self.utc_millisecond_data = [(x * 1000) + self.data_start for x in long_seconds]
        
        self.pressure_data = np.divide(data["pressure"], 1.45037738)
#         self.temperature_data = [x for x in data["temperature"]]
        
        print(len(self.pressure_data))

    def read_header(self,f):
        ''' read the header from the level troll ASCII file
        '''
        line = ""
        line_count = 0    
        while not line.lower().startswith(self.record_start_marker):
            bit_line = f.readline() 
            line = bit_line.decode()
            line_count += 1
            if line.lower().startswith(self.timezone_marker):
                self.timezone_string = line.split(':')[1].strip()        
        if self.timezone_string is None:
            raise Exception("ERROR - could not find time zone in file "+\
                self.in_filename+" header before line "+str(line_count)+'\n') 
        self.set_timezone()        
        

    def read_datetime(self,f):
        '''read the first datetime and cast
        '''        
        dt_fmt = "%m/%d/%Y %I:%M:%S %p "
#         dt_converter = lambda x: datetime.strptime(str(x),dt_fmt)\
#             .replace(tzinfo=self.tzinfo)
        reset_point = f.tell()  
        bit_line = f.readline()          
        line = bit_line.decode()  

        raw = line.strip().split(',')
        dt_str = raw[0]
        try:
            self.data_start = convert_date_to_milliseconds(dt_str,self.date_format_string)
#             self.data_start_date = datetime.strftime(self.data_start, "%Y-%m-%dT%H:%M:%SZ")
#             print('Datetime', self.data_start, self.data_start_date)
        except Exception as e:
            raise Exception("ERROR - cannot parse first date time stamp: "+str(self.td_str)+" using format: "+dt_fmt+'\n')
        f.seek(reset_point)
        


    def set_timezone(self):
        '''set the timezone from the timezone string found in the header - 
        needed to get the times into UTC
        '''
        tz_dict = {"central":"US/Central","eastern":"US/Eastern"}
        for tz_str,tz in tz_dict.items():
            if self.timezone_string.lower().startswith(tz_str):
                self.tzinfo = timezone(tz)
                return               
        raise Exception("could not find a timezone match for " + self.timezone_string)  
    
    @property    
    def offset_seconds(self):
        '''offsets seconds from specified epoch using UTC time
        '''        
        offset = self.data_start - self.epoch_start            
        return offset.total_seconds()       
    
    def write(self, sea_pressure = True):
        '''Write netCDF files
        
        sea_pressure - if true write sea_pressure data, otherwise write air_pressure data'''
        
        if sea_pressure == False:
            self.vstore.pressure_name = "air_pressure"
            self.vstore.pressure_var['standard_name'] = "air_pressure"
        else:
            self.vstore.global_vars_dict['distance_from_referencepoint_to_transducer'] = \
            'When Deployed: %s - When Retrieved: %s' % (self.reference_point_distance_to_transducer[0], \
                                                        self.reference_point_distance_to_transducer[1])
            self.vstore.global_vars_dict['distance_from_transducer_to_seabed'] = \
            'When Deployed: %s - When Retrieved: %s' % (self.transducer_distance_from_seabed[0],self.transducer_distance_from_seabed[1])
            self.vstore.global_vars_dict['time_of_deployment'] = self.deployment_time
            self.vstore.global_vars_dict['time_of_retrieval'] = self.retrieval_time
        self.vstore.pressure_data = self.pressure_data
        self.vstore.utc_millisecond_data = self.utc_millisecond_data
        self.vstore.latitutde = self.latitude
        self.vstore.longitude = self.longitude
       
        #Tests#
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')
        
        self.write_netCDF(self.vstore, len(self.pressure_data))   

class MeasureSysLogger(NetCDFWriter):
    '''derived class for Measurement Systems cvs files
    '''
    def __init__(self):
        self.timezone_marker = "time zone"      
        super(MeasureSysLogger,self).__init__()
        self.tz_info = pytz.timezone("US/Eastern")
        self.frequency = 4
        self.date_format_string = '%m/%d/%Y %H:%M:%S.%f %p' 
        self.data_tests = DataTests() 
        self.transducer_distance_from_seabed = [0,0]
        self.reference_point_distance_to_transducer = [0,0]
        self.deployment_time = datetime.now(tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.retrieval_time = datetime.now(tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        
    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        skip_index = self.read_start('^ID$',',')
        #for skipping lines in case there is calibration header data
        df = pandas.read_table(self.in_filename,skiprows=skip_index + 1, header=None, engine='c', sep=',', usecols=[3,4,5,6])
       
        first_date = df[3][0][1:]
        self.data_start = convert_date_to_milliseconds(first_date, self.date_format_string)
        self.utc_millisecond_data = [(x * 1000) + self.data_start for x in df[4]]
  
        self.pressure_data = [x / 1.45037738 for x in df[5]]
       
        if re.match('^[0-9]{1,3}.[0-9]+$', str(df[6][0])):
            self.temperature_data = [x for x in df[6]]
            
        print(len(self.pressure_data))
        
    def read_start(self, expression, delimeter):
        skip_index = 0;
        with open(self.in_filename,'r') as fileText:
            for x in fileText:
                file_string = x.split(delimeter)[0]
                if re.match(expression, file_string):
                    print('Success! Index %s' % skip_index)
                    break
                skip_index += 1   
        return skip_index 
    
    def write(self, sea_pressure = True):
        '''Write netCDF files
        
        sea_pressure - if true write sea_pressure data, otherwise write air_pressure data'''
        
        if sea_pressure == False:
            self.vstore.pressure_name = "air_pressure"
            self.vstore.pressure_var['standard_name'] = "air_pressure"
        else:
            self.vstore.global_vars_dict['distance_from_referencepoint_to_transducer'] = \
            'When Deployed: %s - When Retrieved: %s' % (self.reference_point_distance_to_transducer[0], \
                                                        self.reference_point_distance_to_transducer[1])
            self.vstore.global_vars_dict['distance_from_transducer_to_seabed'] = \
            'When Deployed: %s - When Retrieved: %s' % (self.transducer_distance_from_seabed[0],self.transducer_distance_from_seabed[1])
            self.vstore.global_vars_dict['time_of_deployment'] = self.deployment_time
            self.vstore.global_vars_dict['time_of_retrieval'] = self.retrieval_time
        
        self.vstore.pressure_data = self.pressure_data
        self.vstore.utc_millisecond_data = self.utc_millisecond_data
        self.vstore.latitutde = self.latitude
        self.vstore.longitude = self.longitude
       
        #Tests#
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')
        
        self.write_netCDF(self.vstore, len(self.pressure_data))
        
class RBRSolo(NetCDFWriter):
    '''derived class for RBR solo engineer text files, (exported via ruskin software)
    '''
    def __init__(self):
        self.timezone_marker = "time zone"      
        super().__init__()
        
        self.tz_info = pytz.timezone("US/Eastern")
        self.frequency = 4
        self.date_format_string = '%d-%b-%Y %H:%M:%S.%f'  
        self.data_tests = DataTests()
        self.transducer_distance_from_seabed = [0,0]
        self.reference_point_distance_to_transducer = [0,0]
        self.reference_point_distance_to_transducer = [0,0]
        self.deployment_time = datetime.now(tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.retrieval_time = datetime.now(tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        
    def read(self):
        '''load the data from in_filename
        only parse the initial datetime = much faster
        '''
        skip_index = self.read_start('^[0-9]{2}-[A-Z]{1}[a-z]{2,8}-[0-9]{4}$',' ')
        #for skipping lines in case there is calibration header data
        df = pandas.read_csv(self.in_filename,skiprows=skip_index, delim_whitespace=True, \
                            header=None, engine='c', usecols=[0,1,2])
        
        #This gets the date and time since they are in two separate columns
        self.utc_millisecond_data = convert_to_milliseconds(df.shape[0] - 1, \
                                                            ('%s %s' % (df[0][0],df[1][0])), \
                                                            self.date_format_string, self.frequency)
               
        self.pressure_data = [x for x in df[2][:-1]]
       
        print(len(self.pressure_data))
        
    def read_start(self, expression, delimeter):
        skip_index = 0;
        with open(self.in_filename,'r') as fileText:
            for x in fileText:
                file_string = x.split(delimeter)[0]
                if re.match(expression, file_string):
                    print('Success! Index %s' % skip_index)
                    break
                skip_index += 1   
        return skip_index  
    
    def write(self, sea_pressure = True):
        '''Write netCDF files
        
        sea_pressure - if true write sea_pressure data, otherwise write air_pressure data'''
        
        if sea_pressure == False:
            self.vstore.pressure_name = "air_pressure"
            self.vstore.pressure_var['standard_name'] = "air_pressure"
        else:
            self.vstore.global_vars_dict['distance_from_referencepoint_to_transducer'] = \
            'When Deployed: %s - When Retrieved: %s' % (self.reference_point_distance_to_transducer[0], \
                                                        self.reference_point_distance_to_transducer[1])
            self.vstore.global_vars_dict['distance_from_transducer_to_seabed'] = \
            'When Deployed: %s - When Retrieved: %s' % (self.transducer_distance_from_seabed[0],self.transducer_distance_from_seabed[1])
            self.vstore.global_vars_dict['time_of_deployment'] = self.deployment_time
            self.vstore.global_vars_dict['time_of_retrieval'] = self.retrieval_time
        self.vstore.pressure_data = self.pressure_data
        self.vstore.utc_millisecond_data = self.utc_millisecond_data
        self.vstore.latitutde = self.latitude
        self.vstore.longitude = self.longitude
#       
        #Tests#
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')
        
        self.write_netCDF(self.vstore, len(self.pressure_data))        
        
class Waveguage(NetCDFWriter):
    """Reads in an ASCII file output by a Waveguage pressure sensor
    from Ocean Sensor Systems Inc.

    This class reads in data from a plaintext output file into a
    pandas Dataframe. This is then translated into numpy ndarrays
    and written to a netCDF binary file."""

    def __init__(self):
        self.tz_info = pytz.timezone("US/Eastern")
        super(Waveguage, self).__init__()
        self.data_tests = DataTests()
        self.transducer_distance_from_seabed = [0,0]
        self.reference_point_distance_to_transducer = [0,0]
        self.deployment_time = datetime.now(tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.retrieval_time = datetime.now(tz=pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        

    def read(self):
        """Sets start_time to a datetime object, utc_millisecond_data
        to a numpy array of dtype=int64 and pressure_data to a numpy
        array of dtype float64."""

        data = self.get_data()
        chunks = self.get_pressure_chunks(data)
        timestamps = self.get_times(data)
        self.data_start_date = datetime.\
            strftime(timestamps[0], "%Y-%m-%dT%H:%M:%SZ")
        self.data_duration_time = timestamps[-1] - timestamps[0]
        self.frequency = self._get_frequency()
        self.utc_millisecond_data = self.get_ms_data(timestamps, chunks)
        self.pressure_data = np.add(np.multiply(self.make_pressure_array(timestamps, chunks),10.0),10.1325)

        #Test and utility methods
        ms = self.utc_millisecond_data[::-1][0]
        

    def make_pressure_array(self, t, chunks):
        def press_entries(t2, t1):
            seconds = self._ms_time_difference(t2, t1) / 1000
            return seconds * self.frequency

        final = np.zeros(0, dtype=np.float64)
        prev_stamp = None
        prev_press = None
        for stamp, press in zip(t, chunks):
            if prev_stamp:
                n = press_entries(stamp, prev_stamp) - len(prev_press)
                print(n)
                narr = np.zeros(n, dtype=np.float64) + self.fill_value
                print('narr = %d' % narr[1])
                final = np.hstack((final, prev_press, narr))
            prev_stamp = stamp
            prev_press = press
        final = np.hstack((final, chunks[-1]))
        return final

    def get_pressure_chunks(self, data):
        master = [[]]
        i = 0
        for e in data:
            if (e.startswith('+') or e.startswith('-')):
                if len(e) == 7:
                    master[i].append(np.float64(e))
            else:
                if master[i] != []:
                    master.append([])
                    i += 1
        master.pop()
        return master

    def get_ms_data(self, timestamps, chunks):
        """Generates the time data using the initial timestamp in the
        file and the length of the pressure data array."""
        first_stamp = timestamps[0]
        last_stamp = timestamps[-1]

        def del_t_ms(t2, t1):
            return (t2 - t1).total_seconds() * 1000

        total_stamp_ms = del_t_ms(last_stamp, first_stamp)
        last_chunk = chunks[-1]
        last_chunk_ms = 1000 * len(last_chunk) / self.frequency
        total_ms = total_stamp_ms + last_chunk_ms

        first_date = timestamps[0]
        epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)
        offset = self._ms_time_difference(first_date, epoch_start)

        utc_ms_data = np.arange(total_ms, step=(1000 / self.frequency),
                                dtype='int64')
        utc_ms_data += offset
        return utc_ms_data

    def _ms_time_difference(self, t2, t1):
        return (t2 - t1).total_seconds() * 1000

    def _get_frequency(self):
        with open(self.in_filename) as f:
            line = f.readline()
        freq = int(line[25:27])
        return freq

    def get_times(self, p):
        """Returns the time that the device started reading as a
        datetime object."""
        def make_stamps(p):
            added = ''
            result = []
            for i, s in enumerate(p):
                added += s
                if i % 6 == 5:
                    result.append(added)
                    added = ''
            return result

        def test2(x):
            return not  (x.startswith('+') or x.startswith('-'))
        c = p.map(test2)
        p = p[c]
        p = p[14:-1]
        stamps = make_stamps(p)

        date_format = 'Y%yM%mD%dH%HM%MS%S'
        stamps = [datetime.strptime(stamp, date_format).\
                      replace(tzinfo=self.tzinfo)
                  for stamp in stamps]
        return stamps

    def get_data(self):
        """Reads the pressure data from the current file and returns
        it in a numpy array of dtype float64."""

        data = pandas.read_csv(self.in_filename, skiprows=0, header=None,
                          lineterminator=',', sep=',', engine='c',
                          names='p')
        data.p = data.p.apply(lambda x: x.strip())
        return data.p
    
    def write(self, sea_pressure = True):
        '''Write netCDF files
        
        sea_pressure - if true write sea_pressure data, otherwise write air_pressure data'''
        
        if sea_pressure == False:
            self.vstore.pressure_name = "air_pressure"
            self.vstore.pressure_var['standard_name'] = "air_pressure"
        else:
            self.vstore.global_vars_dict['distance_from_referencepoint_to_transducer'] = \
            'When Deployed: %s - When Retrieved: %s' % (self.reference_point_distance_to_transducer[0], \
                                                        self.reference_point_distance_to_transducer[1])
            self.vstore.global_vars_dict['distance_from_transducer_to_seabed'] = \
            'When Deployed: %s - When Retrieved: %s' % (self.transducer_distance_from_seabed[0],self.transducer_distance_from_seabed[1])
            self.vstore.global_vars_dict['time_of_deployment'] = self.deployment_time
            self.vstore.global_vars_dict['time_of_retrieval'] = self.retrieval_time
        self.vstore.pressure_data = self.pressure_data
        self.vstore.utc_millisecond_data = self.utc_millisecond_data
        self.vstore.latitutde = self.latitude
        self.vstore.longitude = self.longitude
       
        #Tests#
        self.data_tests.pressure_data = self.pressure_data
        self.vstore.pressure_qc_data = self.data_tests.select_tests('pressure')
        
        self.write_netCDF(self.vstore, len(self.pressure_data)) 

if __name__ == '__main__':
    root = Tk()
    gui = Wavegui(root, air_pressure=True)
    root.mainloop()
