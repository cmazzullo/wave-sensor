#!/usr/bin/env python3
"""
Contains a GUI that interfaces with this package's netCDF-writing
modules. Also contains some convenience methods for other GUIs and a
general class, MessageDialog, for creating custom dialog boxes.
"""

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import os
from collections import OrderedDict
from tools.script1 import INSTRUMENTS, convert_to_netcdf
import json
from pip._vendor.html5lib import inputstream
import re

GLOBAL_HISTFILE = 'history.json'
LOCAL_HISTFILE = 'history2_sea.json'
GLOBAL_FIELDS = OrderedDict([
    ('creator_name', ['Your full name:', '']),
    ('creator_email', ['Your email address:', '']),
    ('creator_url', ['Your personal url:', ''])])
LOCAL_FIELDS = OrderedDict([
    ('instrument_name', ['Instrument:', [
        'MS TruBlue 255', 'Onset Hobo U20', #'LevelTroll','RBRSolo', 'USGS Homebrew'
        ], True]),
    ('stn_station_number', ['STN Station Number:', '']),
    ('stn_instrument_id', ['STN Instrument Id:', '']),
    ('latitude', ['Latitude (decimal degrees):', '', True]),
    ('longitude', ['Longitude (decimal degrees):', '', True]),
    ('tzinfo', ['Time zone the instrument recorded time in:', ['GMT',
                'US/Aleutian',
                'US/Central',
                'US/Eastern',
                'US/Hawaii',
                'US/Mountain',
                'US/Pacific'], True]),
    ('daylightSavings', ['Daylight Savings',False]),
    ('datum', ['Datum:', ['NAVD88',
                            'NGVD29',
                            'Above Ground Level',
                            'Local Control Point'], True])])
WATER_ONLY_FIELDS = OrderedDict([
    ('salinity', ['Salinity:', [
        'Salt Water (> 30 ppt)', 'Brackish Water (.5 - 30 ppt)',
        'Fresh Water (< .5 ppt)'], False]),
    ('initial_land_surface_elevation', ['Initial land surface elevation (feet):', '', False]),
    ('final_land_surface_elevation', ['Final land surface elevation (feet):', '', False]),
    ('device_depth', ['Sensor orifice elevation at deployment time(feet):', '', False]),
    ('device_depth2', ['Sensor orifice elevation at retrieval time(feet):', '', False]),
    ('deployment_time', ['Deployment time (YYYYMMDD HHMM):', '', False]),
    ('retrieval_time', ['Retrieval time (YYYYMMDD HHMM):', '', False]),
    ('sea_name', ['Sea Name:', [
        'Chesapeake Bay', 'Great Lakes', 'Gulf of Alaska', 'Gulf of California',
        'Gulf of Maine', 'Gulf of Mexico', 'Hudson Bay', 'Massachusetts Bay',
        'NE Atlantic (limit-40 W)', 'NE Pacific (limit-180)',
        'North American Coastline-North', 'North American Coastline-South',
        'North Atlantic Ocean', 'North Pacific Ocean',
        'NW Atlantic (limit-40 W)', 'NW Pacific (limit-180)',
        'SE Atlantic (limit-20 W)', 'SE Pacific (limit-140 W)',
        'SW Atlantic (limit-20 W)', 'SW Pacific (limit-147 E to 140 W)'],
                  False])])

class Wavegui:
    """ GUI for csv-to-netCDF conversion. """
    def __init__(self, parent, air_pressure=False):
        self.parent = parent
        self.parent.focus_force()
        self.air_pressure = air_pressure
        self.local_fields = LOCAL_FIELDS
        if not air_pressure:
            self.local_fields.update(WATER_ONLY_FIELDS)
        parent.title("Sea GUI (CSV -> NetCDF)")
        self.air_pressure = air_pressure
        self.datafiles = OrderedDict()
        self.book = ttk.Notebook(self.parent)
        self.book.grid(row=1, column=0)
        self.global_form = Form(self.parent, list(GLOBAL_FIELDS.values()),
                                GLOBAL_HISTFILE)
        self.global_form.grid(row=2, column=0)
        self.summary = "These data were collected by an unvented pressure logger deployed in the water."
        add = lambda: [self.add_file(fname)
                       for fname in askopenfilename(multiple=True)]
        self.error_message = ""
        
        buttons = [
            ("Add File(s)", add),
            ("Save Globals", self.global_form.dump),
            ("Load Globals", self.global_form.load),
            ("Process Files", self.process_files),
            ("Quit", self.parent.destroy)]
        ButtonBar(self.parent, buttons).grid(row=3, column=0)

    def add_file(self, fname):
        """Add a new file tab to the file frame."""
        tab = tk.Frame(self.book)
        self.book.add(tab, text=os.path.basename(fname))
        datafile = Form(tab, list(LOCAL_FIELDS.values()), LOCAL_HISTFILE)
        datafile.pack()
        self.datafiles[fname] = datafile
        removef = lambda: self.remove_file(fname)
        ButtonBar(tab, (('Remove File', removef),
                        ('Save Entries', datafile.dump),
                        ('Load Entries', datafile.load))).pack()
        self.parent.update()
        self.parent.focus_force()

    def process_files(self):
        """Run the csv to netCDF conversion on the selected files."""
        message = ('Working, this may take a few minutes.')

#         try:
        dialog = MessageDialog(self.parent, message=message,
                               title='Processing...', buttons=0, wait=False)
        globs = dict(zip(GLOBAL_FIELDS.keys(),
                         self.global_form.export_entries()))
        bad_data = None

        for fname, datafile in self.datafiles.items():
            inputs = dict(zip(LOCAL_FIELDS.keys(), datafile.export_entries()))
            inputs.update(globs)
            inputs['sea_pressure'] = not self.air_pressure
            inputs['in_filename'] = fname
            inputs['out_filename'] = fname + '.nc'
            inputs['initial_water_depth'] = 1.98
            inputs['final_water_depth'] = 1.98
            
            process_files = self.validate_entries(inputs)
            
            if process_files == True:
                bad_data = convert_to_netcdf(inputs)
                self.remove_file(fname)
                dialog.destroy()
                if bad_data == True:
                    MessageDialog(self.parent, message="There were some bad data points in the file, please cut them using chopper\n and/or" \
                                  " use the \"Hydrostatic\" method in the Water Level GUI",
                              title='Data Issues!')
                else:
                    MessageDialog(self.parent, message="There were no bad data points in the file",
                              title='No Data Issues!')
            
                MessageDialog(self.parent, message="Success! Files saved.",
                              title='Success!') 
            else:
                dialog.destroy()
                MessageDialog(self.parent, message= self.error_message,
                              title='Error')
            
            self.error_message = ''
                
        
        
#         except:
#             dialog.destroy()
#             MessageDialog(self.parent, message="Could not process files, please check file type.",
#                           title='Error')
    
    def validate_entries(self, inputs):
        '''Check if the GUI entries are filled out and in the proper format'''
        
        ignore = [
                  'in_filename',
                  'tzinfo', 
                  'sea_name',
                  'sea_pressure',
                  'salinity',
                  'out_filename',
                  'datum',
                  'instrument_name'
                  ]
        
        message_names = {
        "creator_name": "Full Name",
        "creator_email": "Email Address",
        "creator_url": "Personal Url",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "stn_station_number": "STN Station Number",
        "stn_instrument_id": "STN Instrument Id",
        "initial_land_surface_elevation": "Initial Land Surface Elevation",
        "final_land_surface_elevation": "Final Land Surface Elevation",
        "device_depth": "Sensor Orifice Elevation at Deployment Time",
        "device_depth2": "Sensor Orifice Elevation at Retrieval Time",
        "deployment_time": "Deployment Time",
        "retrieval_time": "Retrieval Time"
         }
        
        #Iterate through all of the dictionary inputs, check if blank or check proper ret/deploy time format
        for x in sorted(inputs):
            if x not in ignore:
                if inputs[x] != None:
                    if x == 'deployment_time' or x == 'retrieval_time':
                       
                        if re.fullmatch('^[0-9]{8}\s[0-9]{4}$', str(inputs[x])) == None:
                            self.error_message += "%s input invalid \n" % message_names[x]
                    else:
                        if inputs[x] == '':
                            self.error_message += "%s input invalid \n" % message_names[x]
                else:
                    self.error_message += "%s input invalid \n" % message_names[x]
                    
        if self.error_message != '':
            return False
        else:
            return True
        
    def remove_file(self, fname):
        """Remove the current file's tab from the window."""
        self.book.forget('current')
        self.datafiles.pop(fname)

#what do you want me to do?  I'll never understand
#please stop bullying me
class Form(tk.Frame):
    """A widget that contains form fields that users can fill"""
    def __init__(self, root, fields, histfile):
        """Create all the tk.Entry widgets and populate the widget with them."""
        tk.Frame.__init__(self, root)
        self.root = root
        self.histfile = histfile
        self.entries = [self.make_entry_row(field, row)
                        for row, field in enumerate(fields)]

    def make_entry_row(self, field, row):
        """Create an Entry based on a field and return its StringVar."""
        label = tk.Label(self, text=field[0], width=40, anchor='w')
        label.grid(row=row, column=0, sticky='W')
        
        value = field[1]
         
        if isinstance(value, bool):
            content = tk.BooleanVar()
        else:
            content = tk.StringVar()
            
        if isinstance(value, str):
            content.set(value)
            widget = tk.Entry(self, textvariable=content, width=40)
        elif isinstance(value, bool):
            content.set(value)
            widget = tk.Checkbutton(self, variable=content, width=40)
        else:
            content.set(value[0])
            widget = tk.OptionMenu(self, content, *value)
        widget.grid(row=row, column=1, sticky=('W', 'E'))
        return content

    def export_entries(self):
        """Export the user's input as a list of strings."""
        return [entry.get() for entry in self.entries]

    def import_entries(self, in_entries):
        """Populate the form fields with a list of strings."""
        for ein, current in zip(in_entries, self.entries):
            current.set(ein)

    def dump(self):
        """Write the user's inputs to a file."""
        with open(self.histfile, 'w') as fname:
            json.dump(self.export_entries(), fname)

    def load(self):
        """Populate the form fields with a list from a file."""
        try:
            with open(self.histfile) as fname:
                self.import_entries(json.load(fname))
        except:
            MessageDialog(self.root, message="No entry file found, fill in fields and click save to create one.",
                      title='Error')


class ButtonBar(tk.Frame):
    """A widget containing buttons arranged horizontally."""
    def __init__(self, root, buttonlist):
        """Create a Button for each entry in buttonlist"""
        tk.Frame.__init__(self, root)
        for i, props in enumerate(buttonlist):
            button = tk.Button(self, text=props[0], command=props[1], width=12)
            button.grid(row=0, column=i, sticky=('W', 'E'))


class MessageDialog(tk.Toplevel):
    """ A template for nice dialog boxes. """
    def __init__(self, parent, message="", title="", buttons=1, wait=True):
        tk.Toplevel.__init__(self, parent)
        body = tk.Frame(self)
        self.title(title)
        self.boolean = None
        self.parent = parent
        self.transient(parent)
        tk.Label(body, text=message).pack()
        if buttons == 1:
            b = tk.Button(body, text="OK", command=self.destroy)
            b.pack(pady=5)
        elif buttons == 2:
            buttonframe = tk.Frame(body, padding="3 3 5 5")
            def event(boolean):
                self.boolean = boolean
                self.destroy()
            b1 = tk.Button(buttonframe, text='YES',
                           command=lambda: event(True))
            b1.grid(row=0, column=0)
            b2 = tk.Button(buttonframe, text='NO',
                           command=lambda: event(False))
            b2.grid(row=0, column=1)
            buttonframe.pack()
        body.pack()
        self.grab_set()
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        if wait:
            self.wait_window(self)

if __name__ == '__main__':
    root = tk.Tk()
    gui = Wavegui(root, air_pressure=False)
    root.mainloop()
