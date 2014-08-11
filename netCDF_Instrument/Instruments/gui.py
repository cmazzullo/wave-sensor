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

import sys
sys.path.append('..')

from Instruments.rbrsolo import RBRSolo
from Instruments.leveltroll import Leveltroll
from Instruments.waveguage import Waveguage
from Instruments.house import House
from Instruments.measuresys import MeasureSysLogger
from Instruments.hobo import Hobo


class Wavegui:


    def __init__(self, root, air_pressure=False):
        self.instruments = {'LevelTroll': Leveltroll,
                            'RBRSolo': RBRSolo,
                            'Wave Guage': Waveguage,
                            'USGS Homebrew': House,
                            'Measurement Specialties': MeasureSysLogger,
                            'HOBO': Hobo}
        self.root = root
        self.per_file_history = 'gui_per_file_history.txt'
        self.global_history = 'gui_global_history.txt'
        root.title("USGS Wave Data")
        
        self.air_pressure = air_pressure
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
        self.global_frame.grid(row=1, column=0, sticky=(N, W, E, S))

        self.file_frame = self.make_file_frame(root)
        self.file_frame.grid(row=0, column=0, sticky=(N, W, E, S))

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
            tab = ttk.Frame(tabs)
            widgets = ttk.Frame(tab, padding="3 3 12 12")

            for row, var in enumerate(datafile.fields.values()):
                self.make_widget(widgets, var, row)

            widgets.pack(fill=BOTH, expand=1)

            buttons = ttk.Frame(tab, padding="3 3 12 12")

            save = partial(self.save_entries, datafile)
            ttk.Button(buttons, text='Save Entries', command=save).\
                grid(column=1, row=0, sticky=W)

            rm = partial(self.remove_file, datafile)
            ttk.Button(buttons, text='Remove File', command=rm).\
                grid(column=2, row=0, sticky=W)

            load = partial(self.load_entries, datafile)
            ttk.Button(buttons, text='Load Default',
                       command=load).grid(column=3, row=0, sticky=W)
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

        entries = ttk.Frame(f, padding="3 3 12 12", relief='raised')

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
        ttk.Button(b, text="Load Default in All Files",
                   command=self.load_per_file).grid(column=4, row=0)
        ttk.Button(b, text="Process Files",
                   command=self.process_files).grid(column=5, row=0)
        ttk.Button(b, text="Quit",
                   command=root.destroy).grid(column=6, row=0)
        return b


    def make_global_fields(self):

        l = [Variable('username', label='Your full name:',
                      name_in_device='creator_name'),
             Variable('email',
                      label='Your email address:',
                      name_in_device='creator_email'),
             Variable('url',
                      label='Your personal url:',
                      name_in_device='creator_url'),
             Variable('project',
                      label='Project name:')]

        d = OrderedDict([(v.name, v) for v in l])
        return d


    def select_files(self):
        fnames = filedialog.askopenfilename(multiple=True)
        if fnames:
            self.datafiles = [Datafile(fname, self.instruments)
                              for fname in fnames]
            self.initialize_somefiles(self.root)


    def add_files(self):
        old_fnames = [d.fields['in_filename'].get()
                      for d in self.datafiles]
        print(old_fnames)
        new_fnames = filedialog.askopenfilename(multiple=True)
        new_fnames = [f for f in new_fnames if f not in old_fnames]

        new_datafiles = [Datafile(fname, self.instruments)
                         for fname in new_fnames]

        self.datafiles += new_datafiles
        self.initialize_somefiles(self.root)


    def remove_all(self):
        self.datafiles = []
        self.initialize_nofiles(self.root)


    def proceed(self, datafiles):
        message = 'This will overwrite your entries. Are you sure?'
        d = MessageDialog(root, message=message, title='Confirm',
                          buttons=2)

        self.root.wait_window(d.top)
        return d.boolean


    def process_files(self):
        devices = [self.read_file(datafile) for datafile in
                   self.datafiles]

        if not all(devices):
            return

     # start_points = [self.plot_pressure(d) for d in devices]
        start_points = [0 for d in devices]
        print('writing files...')
        [self.write_file(d, s) for d, s in zip(devices, start_points)]

        d = MessageDialog(self.root, message="Success! Files saved.",
                          title='Success!')

        self.root.wait_window(d.top)
        d.top.destroy()
        self.root.destroy()


    def plot_pressure(self, device):

        e = EmbeddedPlot(self.root, device.pressure_data[:])
        self.root.wait_window(e.top)
        return e.xdata


    def read_file(self, datafile):
        print('reading file')        
        fields = self.global_fields
        fields.update(datafile.fields)

        # if the variable is required for the type of file, make sure it's 
        # filled out
        for var in fields.values():
            if ((var.in_air_pressure and self.air_pressure) or \
                (var.in_water_pressure and (not self.air_pressure))) and \
                var.required and var.stringvar.get() == '':
                d = MessageDialog(self.root, message="Incomplete "
                                  "entries, please fill out all "
                                  "fields.", title='Incomplete!')
                self.root.wait_window(d.top)
                return False

        device_class = self.instruments[fields['instrument'].get()]
        device = device_class()
        message = ('Processing file:\n\n%s\n\n'
                   'This may take a few minutes.')
        fname = datafile.fields['in_filename'].get()
        message = message % os.path.basename(fname)
        d = MessageDialog(self.root, message=message,
                          title='Processing...', buttons=0)

        for var in fields.values():
            if ((var.in_air_pressure and self.air_pressure) or 
            (var.in_water_pressure and not self.air_pressure) and
            var.name_in_device):
                print(var.label)
                print('> ', var.name_in_device)
                print('$ ', var.get())
                if var.name_in_device != None:
                    setattr(device, var.name_in_device, var.get())

        print('filename: %s' % device.in_filename)
        device.read()
        d.top.destroy()
        return device


    def write_file(self, device, start_point):
        device.user_data_start_flag = start_point
        out_file = device.out_filename
        if os.path.isfile(out_file):
            os.remove(out_file)
        sea_pressure = not self.air_pressure
        device.write(sea_pressure=sea_pressure)


    def load_per_file(self):
        # if none of the entries have been filled out...
        b = not any(v.stringvar.get() for d in self.datafiles
                    for v in d.fields.values() if not v.filename)

        if b or self.proceed(self.datafiles):
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
        b = not any(v.stringvar.get()
                    for v in self.global_fields.values()
                    if not v.filename)

        if b or self.proceed(self.global_fields):
            l = [v for v in self.global_fields.values() if v.autosave]

            if os.path.isfile(self.global_history):
                with open(self.global_history, 'r') as f:
                    for line, var in zip(f, l):
                        var.stringvar.set(line.rstrip())


    def load_entries(self, datafile):
        b = not any(v.stringvar.get()
                    for v in datafile.fields.values()
                    if not v.filename)

        if b or self.proceed([datafile]):
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
        self.datafiles.remove(datafile)
        if self.datafiles:
            self.initialize_somefiles(self.root)
        else:
            self.initialize_nofiles(self.root)


    def make_widget(self, frame, var, row):
        if (not var.in_air_pressure) and self.air_pressure:
            print('firstif')
            return
        if (not var.in_water_pressure) and (not self.air_pressure):
            print('secondif')            
            return
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

    def __init__(self, filename, instruments):

        l = [Variable('in_filename',
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
                      label='Latitude (decimal degrees):',
                      valtype=np.float32,
                      autosave=False,
                      doc='Decimal degrees east of the Prime Meridian.'),
             Variable('longitude (decimal degrees)',
                      name_in_device='longitude',
                      label='Longitude (decimal degrees):',
                      valtype=np.float32,
                      autosave=False,
                      doc='Decimal degrees north of the equator.'),
             Variable('altitude',
                      name_in_device='z',
                      label='Altitude (meters):',
                      doc="Depth below reference point",
                      valtype=np.float32,
                      autosave=False,
                      in_air_pressure=False),
             Variable('salinity',
                      name_in_device='salinity',
                      label='Salinity (ppm):',
                      valtype=np.float32,
                      autosave=False,
                      in_air_pressure=False),
             Variable('initial_pressure',
                      name_in_device='initial_pressure',
                      label='Pressure inside device (dbar):',
                      valtype=np.float32,
                      autosave=False),
             Variable('water_depth',
                      name_in_device='water_depth',
                      label='Water depth (meters):',
                      valtype=np.float32,
                      autosave=False,
                      in_air_pressure=False),
             Variable('device_depth',
                      name_in_device='device_depth',
                      label='Depth of device below surface (meters):',
                      valtype=np.float32,
                      autosave=False,
                      in_air_pressure=False),
             Variable('timezone',
                      name_in_device='tzinfo',
                      label='Timezone:',
                      options=("US/Central", "US/Eastern"),
                      valtype=timezone),
             Variable('instrument',
                      options=instruments.keys(),
                      label='Instrument:'),
             Variable('sea_name',
                      name_in_device='sea_name',
                      label='Sea Name:',
                      in_air_pressure=False,
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


class MessageDialog:

    def __init__(self, parent, message="", title="",  buttons=1):
        top = self.top = Toplevel(parent)
        top.transient(parent)
        top.title(title)
        Label(top, text=message).pack()

        if buttons == 1:
            b = Button(top, text="OK", command=top.destroy)
            b.pack(pady=5)
            top.initial_focus = top
        elif buttons == 2:
            buttonframe = ttk.Frame(top, padding="3 3 12 12")

            def event(boolean):
                self.boolean = boolean
                top.destroy()
            b1 = Button(buttonframe, text='YES',
                        command=lambda: event(True))
            b1.grid(row=0, column=0)
            b2 = Button(buttonframe, text='NO',
                        command=lambda: event(False))
            b2.grid(row=0, column=1)
            buttonframe.pack()
            top.initial_focus = top

        top.grab_set()


class Variable:

    def __init__(self, name, name_in_device=None, label=None,
                 doc=None, options=None, required=True,
                 filename=False, valtype=str, autosave=True, 
                 in_air_pressure=True, in_water_pressure=True):
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


if __name__ == '__main__':
    root = Tk()
    gui = Wavegui(root, air_pressure=True)
    root.mainloop()
