from tkinter import *
from tkinter import ttk
from tkinter import filedialog

class WaveGui:
    """A graphical interface to the netCDF conversion program. Prompts
    the user for information about the wave sensor and converts a CSV 
    file from the sensor to a properly formatted netCDF file.
    """
    def __init__(self, root):

        self.in_filename = StringVar()
        self.out_filename = StringVar()
        self.username = StringVar()
        self.latitude = StringVar()
        self.longitude = StringVar()
        self.altitude = StringVar()
        self.altitude_units = StringVar()
        self.barometric = StringVar()
        self.salinity = StringVar()
        self.timezone = StringVar()
        self.instrument = StringVar()
        self.pressure_units = StringVar()

        root.title("USGS Wave Data")
        # vars = [in_filename,
        #     self.out_filename,
        #     self.username,
        #     self.latitude,
        #     self.longitude,
        #     self.altitude,
        #     self.self.altitude_units,
        #     self.barometric,
        #     self.salinity,
        #     self.timezone,
        #     self.instrument,
        #     self.pressure_units]
        
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        
        # Input Filename
        in_filename_entry = ttk.Entry(mainframe, width=7, 
                                      textvariable=self.in_filename)
        in_filename_entry.grid(column=2, row=1, sticky=(W, E))
        ttk.Label(mainframe, text="In Filename:").grid(column=1, 
                                                       row=1, 
                                                       sticky=W)
        def select_infile():
            fname = filedialog.askopenfilename()
            if fname is None:
                pass
            else:
                self.in_filename.set(fname)
        ttk.Button(mainframe, text="Browse", 
                   command=select_infile).grid(column=3, row=1, 
                                               sticky=W)
        
        # Output Filename
        out_filename_entry = ttk.Entry(mainframe, width=7, textvariable=self.out_filename)
        out_filename_entry.grid(column=2, row=2, sticky=(W, E))
        ttk.Label(mainframe, text="Out Filename:").grid(column=1, row=2, sticky=W)
        def select_outfile():
            fname = filedialog.asksaveasfilename(defaultextension='.nc')
            if fname is None:
                pass
            else:
                self.out_filename.set(fname)
        ttk.Button(mainframe, text="Browse", 
                   command=select_outfile).grid(column=3, row=2, 
                                                sticky=W)
        
        # Operator's name
        username_entry = ttk.Entry(mainframe, width=7, textvariable=self.username)
        username_entry.grid(column=2, row=3, sticky=(W, E))
        ttk.Label(mainframe, text="Your name:").grid(column=1, row=3, sticky=W)
        
        # Latitude
        latitude_entry = ttk.Entry(mainframe, width=7, textvariable=self.latitude)
        latitude_entry.grid(column=2, row=4, sticky=(W, E))
        ttk.Label(mainframe, text="Latitude:").grid(column=1, row=4, sticky=W)
        
        # Longitude
        longitude_entry = ttk.Entry(mainframe, width=7, textvariable=self.longitude)
        longitude_entry.grid(column=2, row=5, sticky=(W, E))
        ttk.Label(mainframe, text="Longitude:").grid(column=1, row=5, sticky=W)
        
        # Altitude
        altitude_entry = ttk.Entry(mainframe, width=7, textvariable=self.altitude)
        altitude_entry.grid(column=2, row=6, sticky=(W, E))
        ttk.Label(mainframe, text="Altitude:").grid(column=1, row=6, sticky=W)
        
        # Altitude units
        ttk.Label(mainframe, text="Altitude units:", 
                  justify=LEFT).grid(column=1, row=7, sticky=W)
        self.altitude_units.set("meters") # default value
        amenu = OptionMenu(mainframe, self.altitude_units, "feet", "meters")
        amenu.grid(column=2, row=7, sticky=(W, E))
        
        # Timezone option menu
        ttk.Label(mainframe, text="Timezone:", 
                  justify=LEFT).grid(column=1, row=8, sticky=W)
        self.timezone.set("Eastern") # default value
        tmenu = OptionMenu(mainframe, self.timezone, "Central", "Eastern")
        tmenu.grid(column=2, row=8, sticky=(W, E))
        
        # Barometric option menu
        ttk.Label(mainframe, text="Barometric correction dataset?:",
                  justify=LEFT).grid(column=1, row=9, sticky=W)
        self.barometric.set("No") # default value
        bmenu = OptionMenu(mainframe, self.barometric, "Yes", "No")
        bmenu.grid(column=2, row=9, sticky=(W, E))
        
        # Salinity
        salinity_entry = ttk.Entry(mainframe, width=7, textvariable=self.salinity)
        salinity_entry.grid(column=2, row=10, sticky=(W, E))
        ttk.Label(mainframe, text="Salinity:").grid(column=1, row=10, sticky=W)
        
        # Option Menu for Self.Instrument selection
        ttk.Label(mainframe, text="Sensor brand:", 
                  justify=LEFT).grid(column=1, row=11, sticky=W)
        self.instrument.set("LevelTroll") # default value
        imenu = OptionMenu(mainframe, self.instrument, "LevelTroll", "RBRVirtuoso",
                           "SomeInstrument")
        imenu.grid(column=2, row=11, sticky=(W, E))
        
        # Option Menu for Pressure Units
        ttk.Label(mainframe, text="Pressure units:", 
                  justify=LEFT).grid(column=1, row=12, sticky=W)
        self.pressure_units.set("pascals") # default value
        pressures = OptionMenu(mainframe, self.pressure_units, "atm", "bar", 
                               "pascals", "psi")
        pressures.grid(column=2, row=12, sticky=(W, E))
        
        
        # 'Process File' Button
        ttk.Button(mainframe, text="Process File", 
                   command=self.process_file).grid(column=2, row=20, sticky=W)
        
        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
        in_filename_entry.focus()                    
        root.bind('<Return>', self.process_file)            
        
    def process_file(self):
        try:
            print(self.timezone.get())
        # TODO: Send user-submitted info to the netCDF generator
        except ValueError:
            pass

root = Tk()
gui = WaveGui(root)
root.mainloop()
