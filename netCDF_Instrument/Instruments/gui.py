import matplotlib
matplotlib.use('TkAgg')
from numpy import arange, sin, pi

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from pytz import timezone
import os

import sys
sys.path.append('.')

import numpy as np
import time

from Instruments.sensor import Sensor
from Instruments.rbrsolo import RBRSolo
from Instruments.leveltroll import Leveltroll
from Instruments.waveguage import Waveguage

class Variable:
    def __init__(self, name, name_in_device, label=None, docs=None,
                 options=None):
        self.name = name
        self.name_in_device = name_in_device
        if label: self.label = label
        if docs: self.docs = docs
        if options: self.options = options
        self.stringvar = StringVar()
            
class Wavegui:
    """A graphical interface to the netCDF conversion program. Prompts
    the user for information about the wave sensor and converts a CSV
    file from the sensor to a properly formatted netCDF file.
    """
    def __init__(self, root):
        self.log_file = 'wavegui_log.txt'
        # Simply add a new instrument name : class pair to this dict
        # to have it included in the GUI!
        self.instruments = {'LevelTroll' : Leveltroll(),
                            'RBRSolo' : RBRSolo(),
                            'Wave Guage' : Waveguage()}
        self.root = root
        generic_sensor = Sensor()
        fill_value = str(generic_sensor.fill_value)

        self.attributes = {'in_filename': StringVar(),
                            'out_filename': StringVar(),
                            'username': StringVar(),
                            'email': StringVar(),
                            'latitude': StringVar(),
                            'longitude': StringVar(),
                            'altitude': StringVar(),
                            'altitude_units': StringVar(),
                            'salinity': StringVar(),
                            'timezone': StringVar(),
                            'instrument': StringVar(),
                            'pressure_units': StringVar(),
                            'keywords': StringVar(),
                            'project': StringVar()}

        self.setup_mainframe(root)

        def_field = self.def_field
        self._row = 1

        def_field(self.attributes['altitude_units'], "Altitude units:",
                        choices=("feet", "meters"))
        def_field(self.attributes['instrument'], "Instrument brand:",
                        choices=self.instruments.keys())
        def_field(self.attributes['timezone'], "Timezone:",
                        choices=("Central", "Eastern"))
        def_field(self.attributes['pressure_units'], "Pressure units:",
                        choices=("atm", "bar", "psi"))
        def_field(self.attributes['username'], "Your name:",
                   doc='The name of the person who ' +
                   'collected the data')
        def_field(self.attributes['email'], "Your email:")
        def_field(self.attributes['latitude'], "Latitude:")
        def_field(self.attributes['longitude'], "Longitude:")
        def_field(self.attributes['altitude'], "Altitude:")
        def_field(self.attributes['salinity'], "Salinity:")
        def_field(self.attributes['keywords'], "Keywords:",
                   doc='A comma-separated list of keywords ' +
                   'that apply to the information in the file')
        def_field(self.attributes['project'], "Project:",
                   doc='The scientific project that the ' +
                   'data was collected under.')
        self.get_filename('in', self.attributes['in_filename'])
        self.get_filename('out', self.attributes['out_filename'])
        self.process_button()
        self.quit_button()

        # TESTING STUFF        
        self.attributes['altitude_units'].set('feet')
        self.attributes['timezone'].set('Eastern')
        self.attributes['instrument'].set('RBRSolo')
        self.attributes['pressure_units'].set('atm')
        self.attributes['in_filename'].set('./Instruments/benchmark/RBR_RSK.txt')
        self.attributes['out_filename'].set('/home/chris/test.deleteme.nc')
        self.attributes['latitude'].set('10')
        self.attributes['longitude'].set('10')
        self.attributes['altitude'].set('10')
        self.attributes['salinity'].set('10')
        self.read_from_file()
        
    def write_to_file(self):
        with open(self.log_file, 'w') as f:
            for key in self.attributes:
                f.write(key + ' ' + self.attributes[key].get()
                        + '\n')

    def read_from_file(self):
        with open(self.log_file, 'r') as f:
            for line in f:
                e = line.split()
                if e[0] in self.attributes.keys() and len(e) > 2:
                    self.attributes[e[0]].set(' '.join(e[1:]))
                    
    def setup_mainframe(self, root):
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        root.title("USGS Wave Data")
        mainframe.bind('<Return>', self.process_file)
        self.mainframe = mainframe

    def get_filename(self, inorout, variable):
        def select_infile():
            fname = filedialog.askopenfilename()
        def select_outfile():
            fname = filedialog.asksaveasfilename(
                defaultextension='.nc')

        if inorout == 'in':
            label = 'Input file:'
            command = select_infile
            variable = self.attributes['in_filename']
        else:
            label = 'Output file:'
            command = select_outfile
            variable = self.attributes['out_filename']
            
        entry = ttk.Entry(self.mainframe, width=7,
                                      textvariable=variable)
        entry.grid(column=2, row=self._row, sticky=(W, E))
        ttk.Label(self.mainframe,
                  text=label).grid(column=1, row=self._row, sticky=W)
        ttk.Button(self.mainframe, text="Browse",
                   command=command).grid(column=3,
                                         row=self._row, sticky=W)
        self._row += 1
        
    def make_optionmenu(self, variable, label, option_list,
                        default_value=None, help_string=None):
        variable.set(default_value)

        ttk.Label(self.mainframe, text=label,
                  justify=LEFT).grid(column=1, row=self._row,
                                     sticky=W)

        if help_string:
            ttk.Button(self.mainframe, text='Help',
                    command=lambda: self.display_help(help_string))\
                    .grid(column=3, row=self._row, sticky=W)
        self._row += 1

    def make_entry(self, variable, label, help_string=None,
                   default_value=''):
        variable.set(default_value)
        entry = ttk.Entry(self.mainframe, width=20,
                          textvariable=variable)
        entry.grid(column=2, row=self._row, sticky=(W, E))
        ttk.Label(self.mainframe,
                  text=label).grid(column=1, row=self._row, sticky=W)
        if help_string:
            ttk.Button(self.mainframe, text='Help',
                    command=lambda: self.display_help(help_string))\
                    .grid(column=3, row=self._row, sticky=W)

        self._row += 1

    def def_field(self, variable, label, doc=None, default='',
                  choices=None):
                  
        variable.set(default)
        ttk.Label(self.mainframe,
                  text=label).grid(column=1, row=self._row, sticky=W)
        
        if choices == None:
            entry = ttk.Entry(self.mainframe, width=20,
                            textvariable=variable)
            entry.grid(column=2, row=self._row, sticky=(W, E))
        else:
            menu = OptionMenu(self.mainframe, variable, *choices)
            menu.grid(column=2, row=self._row, sticky=(W, E))
        def display_help(doc):
            d = MessageDialog(root, message=doc, title='Help')
        if doc:
            ttk.Button(self.mainframe, text='Help',
                    command=lambda: display_help(doc))\
                    .grid(column=3, row=self._row, sticky=W)

        self._row += 1
        
    def process_button(self):
        ttk.Button(self.mainframe, text="Process File",
                   command=self.process_file).grid(column=1,
                                                   row=self._row,
                                                   sticky=W)
        self._row += 1
        
    def process_file(self):

        self.write_to_file()
        
        sensor = self.attributes['instrument'].get()
        device = self.instruments[sensor]
        root = self.root
        d = MessageDialog(root, message="Processing file. "
                          "This may take a few minutes.",
                          title='Processing...',
                          nobutton=True)

        device.in_filename = self.attributes['in_filename'].get()
        device.out_filename = self.attributes['out_filename'].get()
        device.latitude = np.float32(self.attributes['latitude'].get())
        device.longitude = np.float32(self.attributes['longitude'].get())
        device.z = np.float32(self.attributes['altitude'].get())
        device.z_units = self.attributes['altitude_units'].get()
        device.salinity = np.float32(self.attributes['salinity'].get())
        device.tzinfo = timezone('US/' + self.attributes['timezone'].get().capitalize())
        device.pressure_units = self.attributes['pressure_units'].get()

        # This stuff is a bit silly but it might change
        device.geospatial_lat_min = device.latitude
        device.geospatial_lat_max = device.latitude
        device.geospatial_lon_min = device.longitude
        device.geospatial_lon_max = device.longitude
        device.geospatial_vertical_min = device.z
        device.geospatial_vertical_max = device.z

        device.read()
        d.top.destroy()
        e = EmbeddedPlot(root, device.pressure_data[:100])
        root.wait_window(e.top)
        start_time = e.get_start_time()
        print(start_time)

        if os.path.isfile(self.attributes['out_filename'].get()):
            os.remove(self.attributes['out_filename'].get())
        device.write()
        d.top.destroy()
        d = MessageDialog(root, message="Success! File saved " +
                          "in:\n%s." % self.in_filename.get(),
                          title='Success!')
        try:
            root.wait_window(d.top)
            root.destroy()
        except:
            d.top.destroy()
            d = MessageDialog(root, message="Input Error! Please " +
                              "double check your form entries.",
                              title='Error!')

    def quit_button(self):
        """Exits the application without saving anything"""
        ttk.Button(self.mainframe, text="Quit",
                   command=lambda: root.destroy()).grid(column=2,
                                                        row=21,
                                                        sticky=W)
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
        canvas.mpl_connect('key_press_event',
                           self.on_key_event)
        canvas.mpl_connect('button_press_event',
                           self.onclick)
        button = Button(master=top, text='Quit',
                        command=self._quit)
        button.pack(side=BOTTOM)

    def on_key_event(self, event):
        print('you pressed %s'%event.key)
        key_press_handler(event, self.canvas, self.toolbar)

    def _quit(self):
        self.top.destroy()  # this is necessary on Windows to prevent

    def onclick(self, event):
        print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f ' % (
            event.button, event.x, event.y, event.xdata,
            event.ydata))
        self.xdata = event.xdata
        
    def get_start_time(self):
        return self.xdata

if __name__ == "__main__":
    root = Tk()
    gui = Wavegui(root)
    root.mainloop()
