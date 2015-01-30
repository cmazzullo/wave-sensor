"""
Contains a gui that interfaces with this package's netCDF-writing
modules. Also contains some convenience methods for other guis and a
general class, MessageDialog, for creating custom dialog boxes.
"""

from functools import partial
import tkinter
from tkinter import ttk
from tkinter.filedialog import askopenfilename as fileprompt
import os
from collections import OrderedDict
from tools.script1 import INSTRUMENTS, convert_to_netcdf
from Instruments.rbrsolo import RBRSolo
from Instruments.leveltroll import Leveltroll
from Instruments.waveguage import Waveguage
from Instruments.house import House
from Instruments.measuresys import MeasureSysLogger
from Instruments.hobo import Hobo


class Wavegui:
    """ GUI for csv-to-netCDF conversion. """
    def __init__(self, parent, air_pressure=False):
        self.root = parent
        if air_pressure == False:
            parent.title("Sea Water Pressure -> NetCDF")
        else:
            parent.title("Air Pressure -> NetCDF")
        if air_pressure:
            self.df_history = 'gui_df_history.txt'
        else:
            self.df_history = 'gui_df_history_air.txt'
        self.global_history = 'gui_global_history.txt'
        self.air_pressure = air_pressure
        d = OrderedDict()
        d['creator_name'] = Variable(label='Your full name:', autosave=True)
        d['creator_email'] = Variable(label='Your email address:', autosave=True)
        d['creator_url'] = Variable(label='Your personal url:', autosave=True)
        self.global_fields = d
        self.datafiles = list()
        self.filenames = set()
        self.initialize()

    def initialize(self):
        """
        Make the initial frames and entry fields.

        If no files are selected, just creates a frame where a user
        can input global variables. If some files are selected,
        creates both a frame for global variables and a frame for
        file-specific variables.
        """
        try:
            self.global_frame.destroy()
            self.file_frame.destroy()
        except AttributeError:
            pass

        self.global_frame = make_frame(self.root)
        add_label(self.global_frame, 'Global Settings:')
        entries = make_frame(self.global_frame)
        for row, key in enumerate(self.global_fields):
            self.make_widget(entries, self.global_fields[key], row)
        entries.pack(fill='both', expand=1)
        save_globals = partial(self.save_history, self.global_history,
                               self.global_fields)
        load_globals = partial(self.load_history, self.global_history,
                               self.global_fields)
        buttons = [("Add File(s)", self.add_files, 0, 0),
                   ("Save Globals", save_globals, 0, 1),
                   ("Load Globals", load_globals, 0, 2),
                   ("Quit", self.root.destroy, 0, 5)]
        if self.filenames:
            buttons += [("Load Default", self.load_per_file, 0, 3),
                        ("Process Files", self.process_files, 0, 4)]
            self.file_frame = make_frame(self.root)
            add_label(self.file_frame, 'File specific settings:')
            tabs = make_frame(self.file_frame)
            book = ttk.Notebook(tabs, width=50)
            for datafile in self.datafiles:
                tab = make_frame(tabs)
                widgets = make_frame(tab)
                for row, key in enumerate(datafile):
                    self.make_widget(widgets, datafile[key], row)
                widgets.pack(fill='both', expand=1)
                save = partial(self.save_history, self.df_history,
                               datafile)
                rm = partial(self.remove_file, datafile)
                load = partial(self.load_history, self.df_history,
                               datafile)
                buttonlist = [
                    ('Save Entries', save, 0, 1),
                    ('Remove File', rm, 0, 2),
                    ('Load Default', load, 0, 3)]
                make_buttonbox(tab, buttonlist)
                fname = os.path.basename(datafile['in_filename'].stringvar.get())
                maxlen = 7
                if len(fname) > maxlen:
                    fname = fname[:maxlen] + '...'
                book.add(tab, text=fname)
            tabs.pack(fill='both', expand=1)
            book.pack(fill='both', expand=1)

            self.file_frame.grid(row=0, column=0, sticky=('n', 'w', 'e', 's'))

        make_buttonbox(self.global_frame, buttons)
        self.global_frame.update()
        self.global_frame.grid(row=1, column=0, sticky=('n', 'w', 'e', 's'))
        self.root.update()

    def remove_file(self, datafile):
        self.filenames.remove(datafile['in_filename'].stringvar.get())
        self.datafiles.remove(datafile)
        self.initialize()

    def add_files(self):
        """Add a new file tab to the file frame."""
        new_fnames = set(fileprompt(multiple=True)) - self.filenames
        self.filenames |= new_fnames
        new_datafiles = [self.make_file_dict(fname) for fname in new_fnames]
        self.datafiles += new_datafiles
        if self.filenames:
            self.initialize()

    def make_file_dict(self, fname):
        d = OrderedDict()
        d['in_filename'] = Variable(name_in_device='in_filename',
                                    label='Input filename:',
                                    filename='in')
        d['in_filename'].stringvar.set(fname)
        d['out_filename'] = Variable(name_in_device='out_filename',
                                     label='Output filename:',
                                     filename='out')
        d['out_filename'].stringvar.set(fname + '.nc')

        d['instrument_name'] = Variable(options=INSTRUMENTS.keys(),
                                   label='Instrument:',
                                   autosave=True)
        d['latitude'] = Variable(label='Latitude (decimal degrees):',
                                 autosave=True,
                                 doc='Decimal degrees east of the Prime Meridian.')
        d['longitude'] = Variable(autosave=True,
                                  label='Longitude (decimal degrees):',
                                  doc='Decimal degrees north of the equator.')
        d['salinity'] = Variable(autosave=True,
                                 label='Salinity:',
                                 options=("Salt Water (> 30 ppt)",
                                          "Brackish Water (.5 - 30 ppt)",
                                          "Fresh Water (< .5 ppt)"),
                                 in_air_pressure=False)
        d['initial_water_depth'] = Variable(autosave=True,
                                            label='Initial water depth (meters):',
                                            in_air_pressure=False)
        d['final_water_depth'] = Variable(autosave=True,
                                          label='Final water depth (meters):',
                                          in_air_pressure=False)
        d['device_depth'] = Variable(autosave=True,
                                     label='Depth of device below surface (meters):',
                                     in_air_pressure=False)
        d['deployment_time'] = Variable(autosave=True,
                                        label='Deployment time (YYYYMMDD HHMM):',
                                        in_air_pressure=False)
        d['retrieval_time'] = Variable(autosave=True,
                                       label='Retrieval time (YYYYMMDD HHMM):',
                                       in_air_pressure=False)
        d['tzinfo'] = Variable(autosave=True,
                               label='Timezone:',
                               options=("US/Central", "US/Eastern"))
        d['sea_name'] = Variable(label='Sea Name:',
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
                                          'SW Pacific (limit-147 E to 140 W)'))
        return d

    def process_files(self):
        """Run the csv to netCDF conversion on the selected files."""
        # First, check that all fields are filled.
        for datafile in self.datafiles:
            union = dict(datafile.items() | self.global_fields.items())
            for key in union:
                if union[key].stringvar.get() == '':
                    MessageDialog(self.root, message="Incomplete entries,"
                                  " please fill out all fields.",
                                  title='Incomplete!', wait=True)
                    return False
        message = ('Processing files, this may take a few minutes.')
        d = MessageDialog(self.root, message=message,
                          title='Processing...', buttons=0,
                          wait=False)
        self.root.update()
        for datafile in self.datafiles:
            union = dict(datafile.items() | self.global_fields.items())
            inputs = {key : union[key].stringvar.get() for key in union}
            inputs['sea_pressure'] = not self.air_pressure
            convert_to_netcdf(inputs)
        d.destroy()
        MessageDialog(self.root, message="Success! Files saved.",
                      title='Success!')
        self.datafiles = list()
        self.filenames = set()
        self.initialize()

    def save_history(self, filename, vardict):
        """Save per-file entries to a history file for later use"""
        with open(filename, 'w') as f:
            for key in vardict:
                if vardict[key].autosave:
                    f.write(vardict[key].stringvar.get() + '\n')

    def load_per_file(self):
        for dfile in self.datafiles:
            self.load_history(self.df_history, dfile)

    def load_history(self, filename, datafile):
        """Load saved per-file entries into a file's tab"""
        # if any fields are filled, ask first
        any_fields_filled = (
            any(self.global_fields[v].stringvar.get()
                for v in self.global_fields
                if not self.global_fields[v].filename))
        message = 'This will overwrite your entries. Are you sure?'
        def proceed():
            d = MessageDialog(self.root, message=message,
                              title='Confirm', buttons=2, wait=True)
            return d.boolean

        if not any_fields_filled or proceed():
            if os.path.isfile(filename):
                with open(filename, 'r') as f:
                    l = [v for v in datafile if datafile[v].autosave]
                    for line, key in zip(f, l):
                        print('line:', line, 'key:', key)
                        datafile[key].stringvar.set(line.rstrip())

    def make_widget(self, frame, var, row):
        """Make a widget based on the properties of a Variable."""
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
            tkinter.OptionMenu(frame, var.stringvar, *var.options)\
                .grid(column=2, row=row, sticky=('w', 'e'))
        else:
            ttk.Entry(frame, width=20, textvariable=var.stringvar)\
                .grid(column=2, row=row, sticky=('w', 'e'))
        if var.doc:
            c = lambda: MessageDialog(self.root, message=var.doc,
                                      title='Help')
            add_button(frame, 'Help', c, row, 3)


def make_frame(frame, header=None):
    """Make a frame with uniform padding."""
    return ttk.Frame(frame, padding="3 3 5 5")


def add_button(frame, text, command, row, column):
    """Make and grid a button in a uniform way."""
    b = ttk.Button(frame, text=text, command=command)
    b.grid(column=column, row=row, sticky='w')
    return b


def make_buttonbox(frame, buttonlist):
    """Expects button tuples: (text, command, row, column)"""
    box = make_frame(frame)
    for b in buttonlist:
        text, command, row, column = b
        add_button(box, text, command, row, column)
    box.pack(fill='both', expand=1)
    return box


def add_label(frame, text, pos=None):
    """Make a label and pack/grid it"""
    label = ttk.Label(frame, text=text)
    if pos:
        row, column = pos
        label.grid(column=column, row=row, sticky='w')
    else:
        label.pack(fill='both', expand=1)
    return label


class MessageDialog(tkinter.Toplevel):
    """ A template for nice dialog boxes. """

    def __init__(self, parent, message="", title="", buttons=1,
                 wait=True):
        tkinter.Toplevel.__init__(self, parent)
        body = ttk.Frame(self)
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
    """
    Stores data about each attribute to be added to the netCDF file.

    Also contains metadata that allows the GUI to build widgets from
    the Variable and use the data inside it in the csv-to-netCDF
    converters.
    """
    def __init__(self, name_in_device=None, label=None, doc=None,
                 options=None, filename=False, autosave=False,
                 in_air_pressure=True, in_water_pressure=True):
        self.name_in_device = name_in_device
        self.label = label
        self.doc = doc
        self.options = options
        self.stringvar = tkinter.StringVar()
        self.stringvar.set('')
        self.filename = filename
        self.autosave = autosave
        self.in_air_pressure = in_air_pressure
        self.in_water_pressure = in_water_pressure

if __name__ == '__main__':
    root = tkinter.Tk()
    gui = Wavegui(root, air_pressure=False)
    root.mainloop()
