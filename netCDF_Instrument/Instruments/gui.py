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

class Wavegui:
    """A graphical interface to the netCDF conversion program. Prompts
    the user for information about the wave sensor and converts a CSV
    file from the sensor to a properly formatted netCDF file.
    """
    def __init__(self, root):

        # Simply add a new instrument name : class pair to this dict
        # to have it included in the GUI!
        self.instruments = {'LevelTroll' : Leveltroll(),
                            'RBRSolo' : RBRSolo(),
                            'Wave Guage' : Waveguage()}

        self.root = root
        generic_sensor = Sensor()
        fill_value = str(generic_sensor.fill_value)
        self.in_filename = StringVar(value='./Instruments/benchmark/RBR_RSK.txt')
        self.out_filename = StringVar(value='/home/chris/test.deleteme.nc')
        self.username = StringVar()
        self.email = StringVar()
        self.latitude = StringVar(value=fill_value)
        self.longitude = StringVar(value=fill_value)
        self.altitude = StringVar(value=fill_value)
        self.altitude_units = StringVar()
        self.salinity = StringVar(value=fill_value)
        self.timezone = StringVar()
        self.instrument = StringVar()
        self.pressure_units = StringVar()

        self.setup_mainframe(root)

        make_entry = self.make_entry
        make_optionmenu = self.make_optionmenu
        self._row = 1

        make_optionmenu(self.altitude_units, "Altitude units:",
                        ("feet", "meters"))
        make_optionmenu(self.instrument, "Instrument brand:",
                        self.instruments.keys())
        make_optionmenu(self.timezone, "Timezone:",
                        ("Central", "Eastern"))
        make_optionmenu(self.pressure_units, "Pressure units:",
                        ("atm", "bar", "psi"))

        make_entry(self.username, "Your name:")
        make_entry(self.email, "Your email:")
        make_entry(self.latitude, "Latitude:")
        make_entry(self.longitude, "Longitude:")
        make_entry(self.altitude, "Altitude:")
        make_entry(self.salinity, "Salinity:")
        self.get_filename(self.in_filename, 'Input filename:', 'in')
        self.get_filename(self.out_filename, 'Output filename', 'out')
        self.process_button()
        self.quit_button()

        # TESTING STUFF        
        self.altitude_units.set('feet')
        self.timezone.set('Eastern')
        self.instrument.set('RBRSolo')
        self.pressure_units.set('atm')

    def setup_mainframe(self, root):
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        root.title("USGS Wave Data")
        mainframe.bind('<Return>', self.process_file)
        self.mainframe = mainframe

    def setup_for_instrument(self, instrument_name):
        self.mainframe.destroy()
        self.setup_mainframe(root)
        self.select_instrument(root)
        for w in self.widgets:
            try:
                if w not in self.suppress_dict[instrument_name]:
                    w()
            except KeyError:
                w()
        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        root.minsize(root.winfo_width(), root.winfo_height())

    def get_filename(self, variable, label, inorout):
        def select_infile():
            fname = filedialog.askopenfilename()
            self.in_filename.set(fname)
        def select_outfile():
            fname = filedialog.asksaveasfilename(
                defaultextension='.nc')
            self.out_filename.set(fname)
        commands = {'in': select_infile, 'out': select_outfile}
        
        entry = ttk.Entry(self.mainframe, width=7,
                                      textvariable=variable)
        entry.grid(column=2, row=self._row, sticky=(W, E))
        ttk.Label(self.mainframe,
                  text=label).grid(column=1, row=self._row, sticky=W)
        ttk.Button(self.mainframe, text="Browse",
                   command=commands[inorout]).grid(column=3,
                                                   row=self._row, sticky=W)
        entry.focus()
        self._row += 1
        
    def make_optionmenu(self, variable, label, option_list,
                        default_value=None):
        variable.set(default_value)
        menu = OptionMenu(self.mainframe, variable, *option_list)
        menu.grid(column=2, row=self._row, sticky=(W, E))
        ttk.Label(self.mainframe, text=label,
                  justify=LEFT).grid(column=1, row=self._row,
                                     sticky=W)
        self._row += 1

    def make_entry(self, variable, label):
        entry = ttk.Entry(self.mainframe, width=7,
                          textvariable=variable)
        entry.grid(column=2, row=self._row, sticky=(W, E))
        ttk.Label(self.mainframe,
                  text=label).grid(column=1, row=self._row, sticky=W)
        self._row += 1

    def process_button(self):
        # 'Process File' Button
        ttk.Button(self.mainframe, text="Process File",
                   command=self.process_file).grid(column=1,
                                                   row=self._row,
                                                   sticky=W)
        self._row += 1
        
    def process_file(self):
        sensor = self.instrument.get()
        device = self.instruments[sensor]
        root = self.root
        d = MessageDialog(root, message="Processing file. "
                          "This may take a few minutes.",
                          title='Processing...',
                          nobutton=True)

        device.in_filename = self.in_filename.get()
        device.out_filename = self.out_filename.get()
        device.latitude = np.float32(self.latitude.get())
        device.longitude = np.float32(self.longitude.get())
        device.z = np.float32(self.altitude.get())
        device.z_units = self.altitude_units.get()
        device.salinity = np.float32(self.salinity.get())
        device.tzinfo = timezone('US/' +
                                 self.timezone.get().capitalize())
        device.pressure_units = self.pressure_units.get()

        device.read()

        e = EmbeddedPlot(root, device.pressure_data[:100])
        root.wait_window(e.top)
        start_time = e.get_start_time()
        print(start_time)

        if os.path.isfile(self.out_filename.get()):
            os.remove(self.out_filename.get())
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

        t = arange(0.0,3.0,0.01)
        s = sin(2*pi*t)
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
#        self.top.quit()     # stops mainloop
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
