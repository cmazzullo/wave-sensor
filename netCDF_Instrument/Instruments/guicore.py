from functools import partial
from collections import OrderedDict
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename as fileprompt
from pytz import timezone
import os
import numpy as np

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


if __name__ == '__main__':
    root = Tk()
    gui = Wavegui(root, air_pressure=False)
    root.mainloop()
