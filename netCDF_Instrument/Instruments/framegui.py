#!/usr/bin/env python3
import matplotlib
matplotlib.use('TkAgg')
from collections import OrderedDict
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from pytz import timezone
import os
import numpy as np
import time

from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import sys
sys.path.append('..')

from Instruments.sensor import Sensor
from Instruments.rbrsolo import RBRSolo
from Instruments.leveltroll import Leveltroll
from Instruments.waveguage import Waveguage
from Instruments.house import House
from Instruments.measuresys import MeasureSysLogger

class Wavegui:

    def __init__(self, root):

        self.root = root
        self.per_file_history = 'gui_per_file_history.txt'
        self.global_history = 'gui_global_history.txt'
        root.title("USGS Wave Data")
        self.global_fields = self.make_global_fields()
        self.initialize_nofiles(root)

    def initialize_nofiles(self, root):

        try:
            self.global_frame.destroy()
            self.file_frame.destroy()
        except AttributeError:
            pass

        self.global_frame = self.make_global_frame(root, files=False)
        self.global_frame.grid(row=0, column=0, sticky=(N, W, E, S))

        root.update()
        root.minsize(root.winfo_width(), root.winfo_height())

    def initialize_somefiles(self, root):

        self.global_frame.destroy()

        self.global_frame = self.make_global_frame(root, files=True)
        self.global_frame.grid(row=1, column=0, sticky=(N,W,E,S))

        self.file_frame = self.make_file_frame(root)
        self.file_frame.grid(row=0, column=0, sticky=(N,W,E,S))

        root.update()
        root.minsize(root.winfo_width(), root.winfo_height())
        
    def make_file_frame(self, root):

        f = ttk.Frame(root, padding="3 3 12 12")

        # Populate file_frame
        section_header = ttk.Label(f,
                                   text='File specific settings:')
        section_header.pack(fill=BOTH, expand=1)

        tabs = ttk.Frame(f, padding="3 3 12 12")
        book = ttk.Notebook(tabs, width=50)

        for datafile in self.datafiles:
            tab =  ttk.Frame(tabs)
            widgets = ttk.Frame(tab, padding="3 3 12 12")

            for row, var in enumerate(datafile.fields.values()):
                self.make_widget(widgets, var, row)

            widgets.pack(fill=BOTH, expand=1)

            buttons = ttk.Frame(tab, padding="3 3 12 12")

            save = lambda: self.save_entries(datafile)
            ttk.Button(buttons, text='Save Entries', command=save).\
                grid(column=1, row=0, sticky=W)

            rm = lambda: self.remove_file(datafile)
            ttk.Button(buttons, text='Remove File', command=rm).\
                grid(column=2, row=0, sticky=W)

            load = lambda: self.load_entries(datafile)
            ttk.Button(buttons, text='Load Default',
                       command=load).\
                       grid(column=3, row=0, sticky=W)
            buttons.pack(fill=BOTH, expand=1)
            fname = datafile.fields['in_filename'].stringvar.get()
            fname = os.path.basename(fname)
            maxlen = 7
            if len(fname) > maxlen:
                fname = fname[:maxlen] + '...'
            book.add(tab, text=fname)

        book.enable_traversal()
        book.pack(fill=BOTH, expand=1)
        tabs.pack(fill=BOTH, expand=1)

        f.update()

        return f

    def make_global_frame(self, root, files=False):

        f = ttk.Frame(root, padding="3 3 12 12")

        section_header = ttk.Label(f, text='Global settings:')
        section_header.pack(fill=BOTH, expand=1)

        # Subframes

        entries = ttk.Frame(f, padding="3 3 12 12", relief='sunken')

        for row, var in enumerate(self.global_fields.values()):
            self.make_widget(entries, var, row)

        entries.pack(fill=BOTH, expand=1)

        if files:
            buttons = self.make_global_buttons_somefiles(f)
        else:
            buttons = self.make_global_buttons_nofile(f)

        buttons.pack(fill=BOTH, expand=1)
        f.update()
        return f


    def make_global_buttons_nofile(self, f):
        """This makes the frame containing buttons and populates it.
        This is for the case when there are no files selected by the
        user."""

        buttons = ttk.Frame(f, padding="3 3 12 12")

        ttk.Button(buttons, text="Select File(s)",
                   command=self.select_files).grid(column=0, row=0)
        ttk.Button(buttons, text="Save Globals",
                   command=self.save_globals).grid(column=1, row=0)
        ttk.Button(buttons, text="Load Globals",
                   command=self.load_globals).grid(column=2, row=0)
        ttk.Button(buttons, text="Quit",
                   command=root.destroy).grid(column=3, row=0)

        return buttons

    def make_global_buttons_somefiles(self, f):
        """This makes the frame containing buttons and populates it.
        This is for the case when there are some files selected by the
        user."""

        b = ttk.Frame(f, padding="3 3 12 12")

        ttk.Button(b, text="Add File(s)",
                   command=self.add_files).grid(column=0, row=0)
        ttk.Button(b, text="Save Globals",
                   command=self.save_globals).grid(column=1, row=0)
        ttk.Button(b, text="Load Globals",
                   command=self.load_globals).grid(column=2, row=0)
        ttk.Button(b, text="Remove All Files",
                   command=self.remove_all_files).\
                   grid(column=3, row=0)
        ttk.Button(b, text="Load Default in All Files",
                   command=self.load_per_file).grid(column=4, row=0)
        ttk.Button(b, text="Quit",
                   command=root.destroy).grid(column=5, row=0)

        return b

    def make_global_fields(self):

        l = [ Variable('username',
                       label='Your full name:',
                       name_in_device='creator_name'),
              Variable('email',
                       label='Your email address:',
                       name_in_device='creator_email'),
              Variable('url',
                       label='Your personal url:',
                       name_in_device='creator_url'),
              Variable('project',
                       label='Project name:') ]

        d = OrderedDict([(v.name, v) for v in l])
        return d

# Methods on buttons
# Global

    def select_files(self):

        fnames = filedialog.askopenfilename(multiple=True)

        self.datafiles = [Datafile(fname) for fname in fnames]
        self.initialize_somefiles(self.root)

    def add_files(self):

        fnames = filedialog.askopenfilename(multiple=True)

        new_datafiles = [Datafile(fname) for fname in fnames]
        self.datafiles += new_datafiles
        print(self.datafiles)
        self.initialize_somefiles(self.root)

    def remove_all_files(self):
        self.datafiles = []
        self.initialize_nofiles(self.root)

    def load_per_file(self):
        
        for datafile in self.datafiles:

            l = [v for v in datafile.fields.values() if v.autosave]

            if os.path.isfile(self.per_file_history):
                with open(self.per_file_history, 'r') as f:
                    for line, var in zip(f, l):
                        var.stringvar.set(line.rstrip())

    def save_globals(self):
                            
        with open(self.global_history, 'w') as f:

            for var in self.global_fields.values():
                if var.autosave:
                    print(var.stringvar.get())
                    f.write(var.stringvar.get() + '\n')

    def load_globals(self):
        
        l = [v for v in self.global_fields.values() if v.autosave]

        if os.path.isfile(self.global_history):
            with open(self.global_history, 'r') as f:
                for line, var in zip(f, l):
                    var.stringvar.set(line.rstrip())

# Per-file

    def load_entries(self, datafile):

        l = [v for v in datafile.fields.values() if v.autosave]

        if os.path.isfile(self.per_file_history):
            with open(self.per_file_history, 'r') as f:
                for line, var in zip(f, l):
                    var.stringvar.set(line.rstrip())

    def save_entries(self, datafile):

        with open(self.per_file_history, 'w') as f:

            for var in datafile.fields.values():
                if var.autosave:
                    print(var.stringvar.get())
                    f.write(var.stringvar.get() + '\n')

    def remove_file(self, datafile):
        print('before = ')
        print(self.datafiles)

        for d in datafiles:
            if d.
        self.datafiles.remove(datafile)

        print('after = ')
        print(self.datafiles)
        
        if self.datafiles:
            self.initialize_somefiles(self.root)
        else:
            self.initialize_nofiles(self.root)
            
    def make_widget(self, frame, var, row):

        label = var.label
        ttk.Label(frame, text=label).\
            grid(column=1, row=row, sticky=W)

        if var.filename:
            fname = os.path.basename(var.stringvar.get())
            w = ttk.Label(frame, text=fname)
            w.grid(column=2, row=row, sticky=W)
        elif var.options:
            w = OptionMenu(frame, var.stringvar,
                           *var.options)
            w.grid(column=2, row=row, sticky=(W, E))
        else:
            w = ttk.Entry(frame, width=20,
                          textvariable=var.stringvar)
            w.grid(column=2, row=row, sticky=(W, E))

        if var.doc:
            c = lambda: MessageDialog(root, message=var.doc,
                                      title='Help')

            ttk.Button(frame, text='Help', command=c).\
                grid(column=3, row=row, sticky=W)

class Datafile:

    def __init__(self, filename):

        instruments = {'LevelTroll': Leveltroll(),
                       'RBRSolo': RBRSolo(),
                       'Wave Guage': Waveguage(),
                       'USGS Homebrew': House(),
                       'Measurement Systems': MeasureSysLogger()}

        l = [ Variable('in_filename',
                       name_in_device='in_filename',
                       label='Input filename:',
                       filename='in',
                       autosave=False),
              Variable('out_filename',
                       name_in_device='out_filename',
                       label='Output filename:',
                       filename='out',
                       autosave=False),
              Variable('latitude',
                       name_in_device='latitude',
                       label='Latitude:',
                       valtype=np.float32,
                       autosave=False),
              Variable('longitude',
                       name_in_device='longitude',
                       label='Longitude:',
                       valtype=np.float32,
                       autosave=False),
              Variable('altitude',
                       name_in_device='z',
                       label='Altitude:',
                       doc="Altitude in meters with respect to the "
                       "NAVD88 geoid.",
                       valtype=np.float32,
                       autosave=False),
              Variable('salinity',
                       name_in_device='salinity',
                       label='Salinity:',
                       valtype=np.float32,
                       autosave=False),
              Variable('timezone',
                       name_in_device='tzinfo',
                       label='Timezone:',
                       options=("US/Central", "US/Eastern"),
                       valtype=timezone),
              Variable('instrument',
                       options=instruments.keys(),
                       label='Instrument:'),
              # Variable('pressure_units',
              #          name_in_device='pressure_units',
              #          label='Pressure units:',
              #          options=("atm", "bar", "psi")),
              Variable('sea_name',
                       name_in_device='sea_name',
                       label='Sea Name:',
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

        self.fields = OrderedDict([(v.name, v) for v in l])

        self.fields['in_filename'].stringvar.set(filename)
        self.fields['out_filename'].stringvar.set(filename + '.nc')

class Variable:

    def __init__(self, name, name_in_device=None, label=None,
                 doc=None, options=None, required=True,
                 filename=False, valtype=str, autosave=True):

        self.name = name
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

    def get(self):

        val = self.stringvar.get()
        return self.valtype(val)

if __name__ == "__main__":

    root = Tk()
    gui = Wavegui(root)
    root.mainloop()
