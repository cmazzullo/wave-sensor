from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import sys
sys.path.append('.')
import RBRTroll
import numpy as np

class WaveGui:
    """A graphical interface to the netCDF conversion program. Prompts
    the user for information about the wave sensor and converts a CSV
    file from the sensor to a properly formatted netCDF file.
    """
    def __init__(self, root):
        generic_sensor = RBRTroll.pressure()
        fill_value = str(generic_sensor.fill_value)

        self.in_filename = StringVar()
        self.out_filename = StringVar()
        self.username = StringVar()
        self.latitude = StringVar(value=fill_value)
        self.longitude = StringVar(value=fill_value)
        self.altitude = StringVar(value=fill_value)
        self.altitude_units = StringVar()
        self.barometric = StringVar()
        self.salinity = StringVar(value=fill_value)
        self.timezone = StringVar()
        self.instrument = StringVar()
        self.pressure_units = StringVar()

        # Sets of widgets to hide for particular devices:
        self.suppress_dict = {'LevelTroll' :
                                  (self.select_is_barometric,
                                   self.enter_salinity)}

        self.setup_mainframe(root)
        self.select_instrument(root)
        self.widgets = (self.get_in_filename,
                        self.get_out_filename,
                        self.enter_username,
                        self.enter_latitude,
                        self.enter_longitude,
                        self.enter_altitude,
                        self.select_altitude_units,
                        self.select_timezone,
                        self.select_is_barometric,
                        self.enter_salinity,
                        self.select_pressure_units,
                        self.process_button,
                        self.quit_button)

    def setup_mainframe(self, root):
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        root.title("USGS Wave Data")
        mainframe.bind('<Return>', self.process_file)
        self.mainframe = mainframe

    def select_instrument(self, root):
        # Option Menu for Self.Instrument selection
        ttk.Label(self.mainframe, text="Sensor brand:",
                  justify=LEFT).grid(column=1, row=1, sticky=W)
#        self.instrument.set("LevelTroll") # default value

        def setup_for_instrument(instrument_name):
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

        imenu = OptionMenu(self.mainframe, self.instrument,
                           "LevelTroll",
                           "RBRVirtuoso",
                           "SomeInstrument",
                           command=setup_for_instrument)
        imenu.grid(column=2, row=1, sticky=(W, E))


    def get_in_filename(self):
        # Input Filename
        in_filename_entry = ttk.Entry(self.mainframe, width=7,
                                      textvariable=self.in_filename)
        in_filename_entry.grid(column=2, row=2, sticky=(W, E))
        ttk.Label(self.mainframe, text="In Filename:").grid(column=1,
                                                            row=2,
                                                            sticky=W)
        def select_infile():
            fname = filedialog.askopenfilename()
            if fname is None:
                pass
            else:
                self.in_filename.set(fname)
        ttk.Button(self.mainframe, text="Browse",
                   command=select_infile).grid(column=3, row=2,
                                               sticky=W)
        in_filename_entry.focus()

    def get_out_filename(self):
        # Output Filename
        out_filename_entry = ttk.Entry(self.mainframe, width=7,
                                       textvariable=self.out_filename)
        out_filename_entry.grid(column=2, row=3, sticky=(W, E))
        ttk.Label(self.mainframe, text="Out Filename:").grid(column=1,
                                                             row=3,
                                                             sticky=W)
        def select_outfile():
            fname = filedialog.asksaveasfilename(defaultextension='.nc')
            if fname is None:
                pass
            else:
                self.out_filename.set(fname)
        ttk.Button(self.mainframe, text="Browse",
                   command=select_outfile).grid(column=3, row=3,
                                                sticky=W)

    def enter_username(self):
        # Operator's name
        username_entry = ttk.Entry(self.mainframe, width=7,
                                   textvariable=self.username)
        username_entry.grid(column=2, row=4, sticky=(W, E))
        ttk.Label(self.mainframe, text="Your name:").grid(column=1,
                                                          row=4,
                                                          sticky=W)

    def enter_latitude(self):
        # Latitude
        latitude_entry = ttk.Entry(self.mainframe, width=7,
                                   textvariable=self.latitude)
        latitude_entry.grid(column=2, row=5, sticky=(W, E))
        ttk.Label(self.mainframe, 
                  text="Latitude:").grid(column=1, row=5, sticky=W)

    def enter_longitude(self):
        # Longitude
        longitude_entry = ttk.Entry(self.mainframe, width=7, 
                                    textvariable=self.longitude)
        longitude_entry.grid(column=2, row=6, sticky=(W, E))
        ttk.Label(self.mainframe, 
                  text="Longitude:").grid(column=1, row=6, sticky=W)

    def enter_altitude(self):
        # Altitude
        altitude_entry = ttk.Entry(self.mainframe, width=7, 
                                   textvariable=self.altitude)
        altitude_entry.grid(column=2, row=7, sticky=(W, E))
        ttk.Label(self.mainframe, 
                  text="Altitude:").grid(column=1, row=7, sticky=W)

    def select_altitude_units(self):
        # Altitude units
        ttk.Label(self.mainframe, text="Altitude units:",
                  justify=LEFT).grid(column=1, row=8, sticky=W)
        self.altitude_units.set("meters") # default value
        amenu = OptionMenu(self.mainframe, self.altitude_units, 
                           "feet", "meters")
        amenu.grid(column=2, row=8, sticky=(W, E))

    def select_timezone(self):
        # Timezone option menu
        ttk.Label(self.mainframe, text="Timezone:",
                  justify=LEFT).grid(column=1, row=9, sticky=W)
        self.timezone.set("Eastern") # default value
        tmenu = OptionMenu(self.mainframe, self.timezone, 
                           "Central", "Eastern")
        tmenu.grid(column=2, row=9, sticky=(W, E))

    def select_is_barometric(self):
        # Barometric option menu
        ttk.Label(self.mainframe, 
                  text="Barometric correction dataset?:", 
                  justify=LEFT).grid(column=1, row=10, sticky=W)
        self.barometric.set("No") # default value
        bmenu = OptionMenu(self.mainframe, self.barometric, 
                           "Yes", "No")
        bmenu.grid(column=2, row=10, sticky=(W, E))

    def enter_salinity(self):
        # Salinity
        ttk.Label(self.mainframe, 
                  text="Salinity:").grid(column=1, row=11, sticky=W)
        salinity_entry = ttk.Entry(self.mainframe, width=7, 
                                   textvariable=self.salinity)
        salinity_entry.grid(column=2, row=11, sticky=(W, E))



    def select_pressure_units(self):
        # Option Menu for Pressure Units
        ttk.Label(self.mainframe, text="Pressure units:",
                  justify=LEFT).grid(column=1, row=13, sticky=W)
        self.pressure_units.set("pascals") # default value
        pressures = OptionMenu(self.mainframe, self.pressure_units,
                               "atm",
                               "bar",
                               "pascals",
                               "psi")
        pressures.grid(column=2, row=13, sticky=(W, E))

    def process_button(self):
        # 'Process File' Button
        ttk.Button(self.mainframe, text="Process File",
                   command=self.process_file).grid(column=1, row=21,
                                                   sticky=W)

    def process_file(self):
        print('processing file...')
        sensor = self.instrument.get()
        print(sensor)
        if sensor == 'LevelTroll':
            device = RBRTroll.leveltroll()
        elif sensor == 'RBRVirtuoso':
            # The rbr and leveltroll subclasses are mixed up in
            # the current file
            device = RBRTroll.leveltroll()

        # TODO: Check for missing inputs
        # Progress bar while processing file
        try:
            device.in_filename = self.in_filename.get()
            device.out_filename = self.out_filename.get()
            device.latitude = np.float32(self.latitude.get())
            device.longitude = np.float32(self.longitude.get())
            device.z = np.float32(self.altitude.get())
            device.z_units = self.altitude_units.get()
            device.is_baro = self.barometric.get() == 'Yes'
            device.salinity = np.float32(self.salinity.get())
            device.tz = timezone('US/' + 
                                 self.timezone.get().capitalize())
            device.pressure_units = self.pressure_units.get()

            device.read()
            device.write()
        except:
            # TODO: dialog boxes
            pass
    def quit_button(self):
        """Exits the application without saving anything"""
        ttk.Button(self.mainframe, text="Quit",
                   command=lambda: root.destroy()).grid(column=2, 
                                                        row=21, 
                                                        sticky=W)
        
if __name__ == "__main__":
    root = Tk()
    gui = WaveGui(root)
    root.mainloop()
