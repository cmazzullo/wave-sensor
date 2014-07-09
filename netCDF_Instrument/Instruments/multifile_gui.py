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

import sys
sys.path.append('..')

from Instruments.sensor import Sensor
from Instruments.rbrsolo import RBRSolo
from Instruments.leveltroll import Leveltroll
from Instruments.waveguage import Waveguage
from Instruments.house import House

class Variable:

    def __init__(self, name, name_in_device=None, label=None,
                 doc=None, options=None, required=True,
                 filename=False, valtype=str):

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

    def get(self):

        val = self.stringvar.get()
        return self.valtype(val)

class Datafile:

    def __init__(self, filename, instruments):

        l = [ Variable('latitude',
                       name_in_device='latitude',
                       label='Latitude:',
                       valtype=np.float32),
              Variable('longitude',
                       name_in_device='longitude',
                       label='Longitude:',
                       valtype=np.float32),
              Variable('altitude',
                       name_in_device='z',
                       label='Altitude:',
                       doc="Altitude in meters with respect to the "
                           "NAVD88 geoid.", 
                       valtype=np.float32),
              Variable('salinity',
                       name_in_device='salinity',
                       label='Salinity:', 
                       valtype=np.float32),
              Variable('timezone',
                       name_in_device='tzinfo',
                       label='Timezone:',
                       options=("US/Central", "US/Eastern"),
                       valtype=timezone),
              Variable('instrument',
                       options=instruments.keys(),
                       label='Instrument:'),
              Variable('pressure_units',
                       name_in_device='pressure_units',
                       label='Pressure units:',
                       options=("atm", "bar", "psi")),
              Variable('in_filename',
                       name_in_device='in_filename',
                       label='Input filename:',
                       filename='in'),
              Variable('out_filename',
                       name_in_device='out_filename',
                       label='Output filename:',
                       filename='out'),
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

class Wavegui:
    """A graphical interface to the netCDF conversion program. Prompts
    the user for information about the wave sensor and converts a CSV
    file from the sensor to a properly formatted netCDF file.
    """

    def __init__(self, root):

        self.instruments = {'LevelTroll' : Leveltroll(),
                            'RBRSolo' : RBRSolo(),
                            'Wave Guage' : Waveguage(),
                            'USGS Homebrew' : House()}
        
        self.log_file = 'autoload.txt'
#        self.autoload()
        self.global_fields = global_fields = self.make_global_fields()

        self.root = root
        root.title("USGS Wave Data")

        bookframe = ttk.Frame(root, padding="3 3 12 12")
        bookframe.grid(column=0, row=1, sticky=(N, W, E, S))
        book = ttk.Notebook(bookframe)
        book.grid(column=0, row=0)

        buttonframe = ttk.Frame(root, padding="3 3 12 12")
        b1 = ttk.Button(buttonframe, text="Process File(s)",
                        command=self.process_files)
        b1.grid(column=0, row=0)
        b2 = ttk.Button(buttonframe, text="Quit",
                        command=root.destroy)
        b2.grid(column=1, row=0)
        b3 = ttk.Button(buttonframe, text="Select File(s)",
                        command=lambda: 
                        self.get_files(bookframe, book))
        b3.grid(column=2, row=0)
        b4 = ttk.Button(buttonframe, text="Load (in all tabs)",
                        command=self.load_template)
        b4.grid(column=3, row=0)

        buttonframe.grid(column=0, row=2, sticky=(N, W, E, S))
        
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        for row, var in enumerate(global_fields.values()):
            self.make_widget(mainframe, var, row)

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
    
    def save_template(self, datafile):

        with open(self.log_file, 'w') as f:
            for var in self.global_fields.values():
                f.write(var.stringvar.get() + '\n')
            for var in datafile.fields.values():
                f.write(var.stringvar.get() + '\n')


    def load_template(self):

        for datafile in self.datafiles:

            l = [v for v in self.global_fields.values()]
            l += [v for v in datafile.fields.values()]

            if os.path.isfile(self.log_file):
                with open(self.log_file, 'r') as f:
                    for line, var in zip(f, l):
                        var.stringvar.set(line.rstrip())
    
    def get_files(self, frame, book):
        
        for tab in book.tabs(): book.forget(tab) 
        fnames = filedialog.askopenfilename(multiple=True)
        self.datafiles = [Datafile(fname, self.instruments) \
                              for fname in fnames]
        for datafile in self.datafiles:
            tab =  ttk.Frame(frame)
            for row, var in enumerate(datafile.fields.values()):
                self.make_widget(tab, var, row)
            row += 1
            
            save = lambda: self.save_template(datafile)
            ttk.Button(tab, text='Save as Template', command=save).\
                grid(column=1, row=row, sticky=W)
            load = lambda: self.load_template()
            ttk.Button(tab, text='Load Template', command=load).\
                grid(column=2, row=row, sticky=W)
            fname = datafile.fields['in_filename'].stringvar.get()
            fname = os.path.basename(fname)
            book.add(tab, text=fname)
        self.root.update()

    def make_widget(self, frame, var, row):

        label = var.label
        # label = ('(*) ' if var.required else '') + label
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

    def process_files(self):
        
#        self.autosave()

        if not hasattr(self, 'datafiles'):
            
            d = MessageDialog(self.root, 
                              message='No file selected! Please '
                              'select the file that you\'d like to '
                              'convert.', title='Error!')
            return
        
        success = False
        for datafile in self.datafiles:
            success = self.process_file(datafile)
            if not success: break

        if success:
            d = MessageDialog(root, message="Success! File saved.",
                              title='Success!')

            root.wait_window(d.top)
            d.top.destroy()
            root.destroy()
                        
    def process_file(self, datafile):

        fields = self.global_fields
        fields.update(datafile.fields)
        for var in fields.values():
            if var.required and var.stringvar.get() == '':
                d = MessageDialog(self.root, message="Incomplete "
                                  "entries, please fill out all "
                                  "fields.", title='Incomplete!')
                self.root.wait_window(d.top)
                return False

        device = self.instruments[fields['instrument'].get()]

        d = MessageDialog(self.root, message="Processing file. "
                          "This may take a few minutes.",
                          title='Processing...', nobutton=True)

        for var in fields.values():
            if var.name_in_device:
                setattr(device, var.name_in_device, var.get())

        device.read()

        # e = EmbeddedPlot(self.root, device.pressure_data)
        # self.root.wait_window(e.top)
        # start_time = e.get_start_time()

        out_file = fields['out_filename'].get()
        if os.path.isfile(out_file): os.remove(out_file)

        device.write()
        d.top.destroy()
        return True


class MessageDialog:

    def __init__(self, parent, message="", title="",  nobutton=False):

        top = self.top = Toplevel(parent)
        top.transient(parent)
        top.title(title)
        Label(top, text=message).pack()
        if not nobutton:
            b = Button(top, text="OK", command=self.ok)
            b.pack(pady=5)
            top.initial_focus = top
        parent.update()
        parent.grab_set()

    def ok(self):

        self.top.destroy()

class EmbeddedPlot:

    def __init__(self, root, data):

        top = self.top = Toplevel(root)
        f = Figure(figsize=(5,4), dpi=100)
        self.a = a = f.add_subplot(111)
        a.plot(data)
        a.plot(np.arange(len(data)), 100000 * np.ones(len(data)))

        self.canvas = canvas = FigureCanvasTkAgg(f, master=top)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.toolbar = toolbar = NavigationToolbar2TkAgg(canvas, top)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        canvas.mpl_connect('button_press_event',
                           self.onclick)
        button = Button(master=top, text='Accept',
                        command=self._quit)
        button.pack(side=BOTTOM)

    def _quit(self):

        self.top.destroy()  # this is necessary on Windows to prevent

    def onclick(self, event):

        print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f ' % 
              (event.button, event.x, event.y, event.xdata, 
               event.ydata))
        self.xdata = event.xdata

    def get_start_time(self):

        return self.xdata

if __name__ == "__main__":

    root = Tk()
    gui = Wavegui(root)
    root.mainloop()
