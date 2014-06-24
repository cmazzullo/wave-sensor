from tkinter import *
from tkinter import ttk
from tkinter import filedialog

class WaveGui:

    def __init__(self):
        root = Tk()
        root.title("USGS Wave Data")
        
        in_filename = StringVar()
        out_filename = StringVar()
        username = StringVar()
        latitude = StringVar()
        longitude = StringVar()
        altitude = StringVar()
        altitude_units = StringVar()
        barometric = StringVar()
        salinity = StringVar()
        timezone = StringVar()
        instrument = StringVar()
        pressure_units = StringVar()
        
        vars = [in_filename,
                out_filename,
                username,
                latitude,
                longitude,
                altitude,
                altitude_units,
                barometric,
                salinity,
                timezone,
                instrument,
                pressure_units]
        
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        
        # Input Filename
        in_filename_entry = ttk.Entry(mainframe, width=7, textvariable=in_filename)
        in_filename_entry.grid(column=2, row=1, sticky=(W, E))
        ttk.Label(mainframe, text="In Filename:").grid(column=1, row=1, sticky=W)
        
        # Output Filename
        out_filename_entry = ttk.Entry(mainframe, width=7, textvariable=out_filename)
        out_filename_entry.grid(column=2, row=2, sticky=(W, E))
        ttk.Label(mainframe, text="Out Filename:").grid(column=1, row=2, sticky=W)
        
        # Operator's name
        username_entry = ttk.Entry(mainframe, width=7, textvariable=username)
        username_entry.grid(column=2, row=3, sticky=(W, E))
        ttk.Label(mainframe, text="Your name:").grid(column=1, row=3, sticky=W)
        
        # Latitude
            latitude_entry = ttk.Entry(mainframe, width=7, textvariable=latitude)
            latitude_entry.grid(column=2, row=4, sticky=(W, E))
            ttk.Label(mainframe, text="Latitude:").grid(column=1, row=4, sticky=W)
            
        # Longitude
            longitude_entry = ttk.Entry(mainframe, width=7, textvariable=longitude)
            longitude_entry.grid(column=2, row=5, sticky=(W, E))
            ttk.Label(mainframe, text="Longitude:").grid(column=1, row=5, sticky=W)
            
        # Altitude
            altitude_entry = ttk.Entry(mainframe, width=7, textvariable=altitude)
            altitude_entry.grid(column=2, row=6, sticky=(W, E))
            ttk.Label(mainframe, text="Altitude:").grid(column=1, row=6, sticky=W)
            
        # Altitude units
            ttk.Label(mainframe, text="Altitude units:", 
                      justify=LEFT).grid(column=1, row=7, sticky=W)
            altitude_units.set("meters") # default value
            amenu = OptionMenu(mainframe, altitude_units, "feet", "meters")
            amenu.grid(column=2, row=7, sticky=(W, E))
            
        # Timezone option menu
            ttk.Label(mainframe, text="Timezone:", 
                      justify=LEFT).grid(column=1, row=8, sticky=W)
            timezone.set("Eastern") # default value
            tmenu = OptionMenu(mainframe, timezone, "Central", "Eastern")
            tmenu.grid(column=2, row=8, sticky=(W, E))
            
        # Barometric option menu
            ttk.Label(mainframe, text="Is this a barometric correction dataset?:",
                      justify=LEFT).grid(column=1, row=9, sticky=W)
            barometric.set("No") # default value
            bmenu = OptionMenu(mainframe, barometric, "Yes", "No")
            bmenu.grid(column=2, row=9, sticky=(W, E))
            
        # Salinity
            salinity_entry = ttk.Entry(mainframe, width=7, textvariable=salinity)
            salinity_entry.grid(column=2, row=10, sticky=(W, E))
            ttk.Label(mainframe, text="Salinity:").grid(column=1, row=10, sticky=W)
            
        # Option Menu for Instrument selection
            ttk.Label(mainframe, text="Sensor brand:", 
                      justify=LEFT).grid(column=1, row=11, sticky=W)
            instrument.set("LevelTroll") # default value
            imenu = OptionMenu(mainframe, instrument, "LevelTroll", "RBRVirtuoso",
                               "SomeInstrument")
            imenu.grid(column=2, row=11, sticky=(W, E))
            
        # Option Menu for Pressure Units
            ttk.Label(mainframe, text="Pressure units:", 
                      justify=LEFT).grid(column=1, row=12, sticky=W)
            pressure_units.set("pascals") # default value
            pressures = OptionMenu(mainframe, pressure_units, "atm", "bar", 
                                   "pascals", "psi")
            pressures.grid(column=2, row=12, sticky=(W, E))
            
        # File dialog
            def select_file():
                d = filedialog.FileDialog(root)
                fname = d.go()
                if fname is None:
                    pass
                else:
                    pass
                print(fname)
                
                ttk.Label(mainframe, text="Input file:", 
                          justify=LEFT).grid(column=1, row=19, sticky=W)
                ttk.Button(mainframe, text="Browse", 
                           command=select_file).grid(column=2, row=19, sticky=W)
                
                
            # 'Process File' Button
                ttk.Button(mainframe, text="Process File", 
                           command=process_file).grid(column=2, row=20, sticky=W)
                
                for child in mainframe.winfo_children(): child.grid_configure(padx=5, 

        def process_file(*args):
            try:
                print(timezone.get())
            # TODO: Send user-submitted info to the netCDF generator
            except ValueError:
                pass

in_filename_entry.focus()
root.bind('<Return>', process_file)
root.mainloop()
