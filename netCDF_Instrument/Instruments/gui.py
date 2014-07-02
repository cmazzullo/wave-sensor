#!/usr/bin/env python3
import matplotlib
matplotlib.use('TkAgg')
import collections
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
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
sys.path.append('.')

from Instruments.sensor import Sensor
from Instruments.rbrsolo import RBRSolo
from Instruments.leveltroll import Leveltroll
from Instruments.waveguage import Waveguage

class Variable:
    def __init__(self, name_in_device=None, label=None,
                 docs=None, options=None, required=True,
                 filename=False, default_value='',
                 valtype=str):
        self.name_in_device = name_in_device
        self.label = label
        self.docs = docs
        self.options = options
        self.stringvar = StringVar()
        self.required = required
        self.filename = filename
        self.default_value = default_value
        self.stringvar.set(default_value)
        self.valtype = valtype

    def getvalue(self):
        val = self.stringvar.get()
        return self.valtype(val)

class Wavegui:
    """A graphical interface to the netCDF conversion program. Prompts
    the user for information about the wave sensor and converts a CSV
    file from the sensor to a properly formatted netCDF file.
    """
    def __init__(self, root):
        self.log_file = 'wavegui_log.txt'

        self.instruments = {'LevelTroll' : Leveltroll(),
                            'RBRSolo' : RBRSolo(),
                            'Wave Guage' : Waveguage()}
        self.root = root
        generic_sensor = Sensor()
        fill_value = str(generic_sensor.fill_value)
        
        self.fields = fields = collections.OrderedDict()
        fields['username'] = Variable(label='Your full name:',
                                         name_in_device='creator_name')
        fields['email'] = Variable(label='Your email address:')
        fields['latitude'] = Variable(name_in_device='latitude',
                  label='Latitude:', valtype=np.float32)
        fields['longitude'] = Variable(name_in_device='longitude',
                  label='Longitude:', valtype=np.float32)
        fields['altitude'] = Variable(name_in_device='z',
                  label='Altitude:',
                  docs="Altitude in meters with respect to the "\
                  " WGS 84 ellipsoid.", valtype=np.float32)
        fields['salinity'] = Variable(name_in_device='salinity',
                  label='Salinity:', valtype=np.float32)
        fields['timezone'] = Variable(name_in_device='tzinfo',
                  label='Timezone:',
                  options=("US/Central", "US/Eastern"),
                  valtype=timezone)
        fields['instrument'] = Variable(options=self.instruments.keys(),
                  label='Instrument:')
        fields['pressure_units'] = Variable(name_in_device='pressure_units',
                  label='Pressure units:',
                  options=("atm", "bar", "psi"))
        # fields['keywords'] = Variable(label='Comma-separated keywords:',
        #           required=False)
        fields['project'] = Variable(label='Project name:')
        fields['in_filename'] = Variable(name_in_device='in_filename',
                  label='Input filename:', filename='in')
        fields['out_filename'] = Variable(name_in_device='out_filename',
                  label='Output filename:', filename='out')

        self.setup_mainframe(root)

        for row, var in enumerate(fields.values()):
            self.make_widget(var, row) 

        self.process_button(len(fields))
        self.quit_button(len(fields))

        self.read_from_file(fields)
        
    def write_to_file(self, fields):
        with open(self.log_file, 'w') as f:
            for var in fields.values():
                f.write(var.stringvar.get() + '\n')

    def read_from_file(self, fields):
        if os.path.isfile(self.log_file):
            with open(self.log_file, 'r') as f:
                for line, var in zip(f, fields.values()):
                    var.stringvar.set(line.rstrip())

    def setup_mainframe(self, root):
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        root.title("USGS Wave Data")
        mainframe.bind('<Return>', self.process_file)
        self.mainframe = mainframe

    def get_filename(self, var, row):
        def select_infile():
            fname = filedialog.askopenfilename()
            var.stringvar.set(fname)
        def select_outfile():
            fname = filedialog.asksaveasfilename(
                defaultextension='.nc')
            var.stringvar.set(fname)
        if var.filename == 'in':
            command = select_infile
        else:
            command = select_outfile
            
        entry = ttk.Entry(self.mainframe, width=7,
                                      textvariable=var.stringvar)
        entry.grid(column=2, row=row, sticky=(W, E))
        ttk.Button(self.mainframe, text="Browse",
                   command=command).grid(column=3, row=row, sticky=W)
        
    def make_widget(self, var, row):

        label = ('' if var.required else '(*)') + var.label
        ttk.Label(self.mainframe, text=label).\
          grid(column=1, row=row, sticky=W)
        if var.filename:
            self.get_filename(var, row)
        elif var.options:
            menu = OptionMenu(self.mainframe, var.stringvar,
                              *var.options)
            menu.grid(column=2, row=row, sticky=(W, E))
        else:
            entry = ttk.Entry(self.mainframe, width=20,
                              textvariable=var.stringvar)
            entry.grid(column=2, row=row, sticky=(W, E))
        def display_help(docs):
            d = MessageDialog(root, message=docs, title='Help')
        if var.docs:
            ttk.Button(self.mainframe, text='Help',
                    command=lambda: display_help(var.docs))\
                    .grid(column=3, row=row, sticky=W)
        
    def process_button(self, row):
        ttk.Button(self.mainframe, text="Process File",
                   command=self.process_file).\
                   grid(column=1, row=row, sticky=W)
        
    def process_file(self):
        root = self.root
        for var in self.fields.values():
            if var.required and var.stringvar.get() == '':
                d = MessageDialog(root, message="Incomplete "\
                                  "entries, please fill out all "\
                                  "fields.", title='Incomplete!')
                root.wait_window(d.top)
                return 
        
        self.write_to_file(self.fields)
        device = self.instruments[self.fields['instrument'].getvalue()]

        d = MessageDialog(root, message="Processing file. "
                          "This may take a few minutes.",
                          title='Processing...', nobutton=True)
        for var in self.fields.values():
            if var.name_in_device:
                setattr(device, var.name_in_device, var.getvalue())

        device.geospatial_lat_min = device.latitude
        device.geospatial_lat_max = device.latitude
        device.geospatial_lon_min = device.longitude
        device.geospatial_lon_max = device.longitude
        device.geospatial_vertical_min = device.z
        device.geospatial_vertical_max = device.z
        device.z_units = 'meters'
        device.read()
        d.top.destroy()
        e = EmbeddedPlot(root, device.pressure_data[:100])
        root.wait_window(e.top)
        start_time = e.get_start_time()

        out_file = self.fields['out_filename'].getvalue()
        if os.path.isfile(out_file): os.remove(out_file)
        device.write()
        d.top.destroy()
        d = MessageDialog(root, message="Success! File saved " +
                          "in:\n%s." % out_file,
                          title='Success!')
        try:
            root.wait_window(d.top)
            root.destroy()
        except:
            d.top.destroy()
            d = MessageDialog(root, message="Input Error! Please " +
                              "double check your form entries.",
                              title='Error!')

    def quit_button(self, row):
        """Exits the application without saving anything"""
        ttk.Button(self.mainframe, text="Quit",
                   command=lambda: root.destroy()).\
                   grid(column=2, row=row, sticky=W)
                   
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
        print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f ' % (
            event.button, event.x, event.y, event.xdata, event.ydata))
        self.xdata = event.xdata
        
    def get_start_time(self):
        return self.xdata

if __name__ == "__main__":
    root = Tk()
    gui = Wavegui(root)
    root.mainloop()
