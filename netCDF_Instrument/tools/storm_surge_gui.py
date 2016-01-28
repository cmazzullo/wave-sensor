#!/usr/bin/env python3
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

import NetCDF_Utils.nc as nc
import tools.script2 as script2
import tools.script1_gui as gc
import os
from tools.depth_grapher import make_depth_graph



class StormSurgeGui:
    def __init__(self, root):
        
        #root and selection dialogs for sea and air netCDF files
        self.root = root
        root.title('Storm Surge GUI (Pressure -> Water Level)')
        self.root.focus_force()
        
        self.chopperLabel = Label(root, text='(Please make sure Chopper is closed before making a graph)')
        self.chopperLabel.pack(anchor=W,padx = 15,pady = 2)
        
        self.sea_fname = ''
        self.sea_var = StringVar()
        self.sea_var.set('File containing water pressure...')
        self.air_fname = ''
        self.air_var = StringVar()
        self.air_var.set('File containing air pressure...')
        self.make_fileselect(root, 'Water file:',
                             self.sea_var, 'sea_fname')
        self.make_fileselect(root, 'Air file:',
                             self.air_var, 'air_fname')
        c3 = lambda: self.select_output_file(root)
        self.output_label = Label(self.root, text='Output Formats (please check at least one):')
        self.output_label.pack(anchor=W,padx = 2,pady = 2)
        
        #Initialize output selection variables
        self.netOutput = BooleanVar()
        self.csvOutput = BooleanVar()
        self.graphOutput = BooleanVar()
        self.netOutput.trace("w", self.button_state)
        self.csvOutput.trace("w", self.button_state)
        self.graphOutput.trace("w", self.hide_options)
        
        #Check boxes for output variables
        self.netCDF = Checkbutton(root, text="netCDF", variable=self.netOutput)
        self.netCDF.pack(anchor=W,padx = 15,pady = 2)
        self.csv = Checkbutton(root, text="CSV", variable=self.csvOutput)
        self.csv.pack(anchor=W,padx = 15,pady = 2)
        self.graph = Checkbutton(root, text="Graph", variable=self.graphOutput)
        self.graph.pack(anchor=W,padx = 15,pady = 2)
        
        
        #Frame for graph options (will hide unless graph output is selected)
        self.graphOptions = Frame(root)
        
        self.TzLabel = Label(self.graphOptions, text='Time zone to display dates in:')
        self.TzLabel.pack(anchor=W,padx = 15,pady = 2)
        options=('GMT',
                'US/Aleutian',
                'US/Central',
                'US/Eastern',
                'US/Hawaii',
                'US/Mountain',
                'US/Pacific')
        self.tzstringvar = StringVar()
        self.tzstringvar.set(options[0])
        
        
        self.datePickFrame = Frame(self.graphOptions)
        
        OptionMenu(self.datePickFrame, self.tzstringvar, *options).pack(side=LEFT, pady=2, padx=15)
        
        self.daylightSavings = BooleanVar()
        Checkbutton(self.datePickFrame, text="Daylight Savings", variable=self.daylightSavings).pack(side=RIGHT)
        self.datePickFrame.pack(anchor=W)
        
        #tkinter spacing
        self.emptyLabel4 = Label(self.graphOptions, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W,padx = 15,pady = 0)
        
        #variables and text boxes for air pressure limits
        self.BaroPickLabel = Label(self.graphOptions, text='Barometric Pressure Y Axis Limits: (optional)')
        self.BaroPickLabel.pack(anchor=W,padx = 15,pady = 0)
        
        self.baroPickFrame = Frame(self.graphOptions)
        self.bLowerLabel = Label(self.baroPickFrame, text="lower:").pack(side=LEFT, pady=10, padx=2)
        self.baroYlim1 = Entry(self.baroPickFrame, width=5)
        self.baroYlim1.pack(side=LEFT, pady=2, padx=15)
        self.baroYlim2 = Entry(self.baroPickFrame, width=5)
        self.baroYlim2.pack(side=RIGHT, pady=2, padx=15)
        self.bUpperLabel = Label(self.baroPickFrame, text="upper:").pack(side=RIGHT, pady=10, padx=2)
        self.baroPickFrame.pack(anchor=W, padx = 15)
        
        #tkinter spacing
        self.emptyLabel4 = Label(self.graphOptions, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W,padx = 15,pady = 0)
        
        #variables and textboxes for water level limits
        self.WaterLevelLabel = Label(self.graphOptions, text='Water Level Y Axis Limits: (optional)')
        self.WaterLevelLabel.pack(anchor=W,padx = 15,pady = 0)
        
        self.wlPickFrame = Frame(self.graphOptions)
        self.wlLowerLabel = Label(self.wlPickFrame, text="lower:").pack(side=LEFT, pady=10, padx=2)
        self.wlYlim1 = Entry(self.wlPickFrame, width=5)
        self.wlYlim1.pack(side=LEFT, pady=2, padx=15)
        self.wlYlim2 = Entry(self.wlPickFrame, width=5)
        self.wlYlim2.pack(side=RIGHT, pady=2, padx=15)
        self.wlUpperLabel = Label(self.wlPickFrame, text="upper:").pack(side=RIGHT, pady=10, padx=2)
        self.wlPickFrame.pack(anchor=W, padx = 15)
        
        #tkinter spacing
        self.emptyLabel4 = Label(self.graphOptions, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W,padx = 15,pady = 0)
        
        #variables and textbox for extra graph label
        self.GraphExtraLabel = Label(self.graphOptions, text='Extra Graph Header: (optional)')
        self.GraphExtraLabel.pack(anchor=W,padx = 15,pady = 2)
        
        self.ExtraEntry = Entry(self.graphOptions)
        self.ExtraEntry.pack(anchor=W,padx = 15,pady = 2)
        
        #tkinter spacing
        self.emptyLabel4 = Label(self.graphOptions, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W,padx = 15,pady = 0)
        
#         #variables and drop down for grid line option
#         self.GraphGridLabel = Label(self.graphOptions, text='Graph Grid Lines:')
#         self.GraphGridLabel.pack(anchor=W,padx = 15,pady = 2)
#         
#         grid_options=('Barometric Pressure',
#                 'Water Level')
#         self.gridstringvar = StringVar()
#         self.gridstringvar.set(grid_options[0])
#         
#         OptionMenu(self.graphOptions, self.gridstringvar, *grid_options).pack(anchor=W, pady=2, padx=15)
        
        #tkinter spacing
        self.emptyLabel4 = Label(self.graphOptions, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W,padx = 15,pady = 0)
        
        
        self.b3 = self.make_button(root, "Process Files", c3,
                                   state=DISABLED)
        
        self.b3.pack(anchor=W, fill=BOTH)
    
    def hide_options(self, event, arb1, arb2):
        '''Checks whether the graph option is selected to show options and whether files and one
        output is selected to enable the process files button'''
        if (self.sea_fname != '' and self.air_fname != '') and (self.graphOutput.get() or self.csvOutput.get() or self.netOutput.get()):
            self.b3['state'] = 'ENABLED'
        else:
            self.b3.config(state=DISABLED)
            
        if self.graphOutput.get() == True:
            self.b3.pack_forget()
            self.graphOptions.pack(anchor=W, padx = 2)
            self.b3.pack(anchor=W, fill=BOTH)
        else:
            self.graphOptions.pack_forget()
    
    def button_state(self, event, arb1, arb2):
        '''Checks whether files and one output is selected to enable the process files button'''
        if (self.sea_fname != '' and self.air_fname != '') and (self.graphOutput.get() or self.csvOutput.get() or self.netOutput.get()):
            self.b3['state'] = 'ENABLED'
        else:
            self.b3.config(state=DISABLED)

    def select_file(self, varname, stringvar):
        fname = filedialog.askopenfilename()
        if fname != '':
            stringvar.set(fname)
            setattr(self, varname, fname)
            if(self.sea_fname != '' and self.air_fname != '') and (self.graphOutput.get() or self.csvOutput.get() or self.netOutput.get()):
                self.b3['state'] = 'ENABLED'
        self.root.focus_force()

    def make_button(self, root, text, command, state=None):
        '''Creates a new button'''
        b = ttk.Button(root, text=text, command=command, state=state,
                       width=10)
        return b

    def make_fileselect(self, root, labeltext, stringvar, varname):
        '''Creates a file selection menu'''
        command = lambda: self.select_file(varname, stringvar)
        frame = make_frame(root)
        l = ttk.Label(frame, justify=LEFT, text=labeltext, width=10)
        l.grid(row=0, column=0, sticky=W)
        b = self.make_button(frame, 'Browse', command)
        b.grid(row=0, column=2, sticky=W)
        e = ttk.Label(frame, textvariable=stringvar, justify=LEFT,
                      width=32)
        e.grid(row=0, column=1, sticky=(W, E))
        frame.pack(anchor=W, fill=BOTH)

    def select_output_file(self, root):
        '''Processes the selected afiles and outputs in format selected'''
        
        #Format the name properly based on the input of the user
        
        og_fname = filedialog.asksaveasfilename()
        output_fname = ''
        plot_fname = ''
        
        if og_fname != None and og_fname != '' :
                
            last_index = og_fname.find('.')
            if og_fname[last_index:] != '.nc':
                
                if last_index < 0:
                    output_fname = ''.join([og_fname,'.nc'])
                    plot_fname = ''.join([og_fname,'.jpg'])
                else:
                    output_fname = ''.join([og_fname[0:last_index],'.nc'])
                    
                    if og_fname[last_index:] != '.jpg':
                        plot_fname = ''.join([og_fname[0:last_index],'.jpg'])
                    else:
                        plot_fname = og_fname
            else:
                output_fname = og_fname
                plot_fname = ''.join([og_fname[0:last_index],'.jpg'])
                
            
           
    #         dialog = gc.MessageDialog(root, message='Working, this may take up to 60 seconds.',
    #                                title='Processing...', buttons=0, wait=False)
                   
#             try:
                
                    #Get the sea time and air time and determine if there is overlap
            sea_t = nc.get_time(self.sea_fname)
            if self.air_fname != '':
                air_t = nc.get_time(self.air_fname)
                if (air_t[-1] < sea_t[0]) or (air_t[0] > sea_t[-1]):
                    message = ("Air pressure and water pressure files don't "
                               "cover the same time period!\nPlease choose "
                               "other files.")
                    gc.MessageDialog(root, message=message, title='Error!')
                    return
                elif (air_t[0] > sea_t[0] or air_t[-1] < sea_t[-1]):
                    message = ("The air pressure file doesn't span the "
                    "entire time period covered by the water pressure "
                    "file.\nThe period not covered by both files will be "
                    "chopped")
                    gc.MessageDialog(root, message=message, title='Warning')
            
            #This creates the depth file/s for storage or use in the graph
            script2.make_depth_file(self.sea_fname, self.air_fname,
                                    output_fname, method='naive', csv= self.csvOutput.get(), step= 4)
            
           
            #If graph output is selected get parameters and display graph
            if self.graphOutput.get():
                baroYLims = []
                try:
                    baroYLims.append(float(self.baroYlim1.get()))
                    baroYLims.append(float(self.baroYlim2.get()))
                except:
                    baroYLims = None
                
                wlYLims = []
                try:
                    wlYLims.append(float(self.wlYlim1.get()))
                    wlYLims.append(float(self.wlYlim2.get()))
                except:
                    wlYLims = None
                
                
                make_depth_graph(0, output_fname, \
                                         self.tzstringvar.get(), self.daylightSavings.get(),
                                         'water_level', self.ExtraEntry.get(),
                                         baroYLims, wlYLims, plot_fname)
               
                
            #if netCDF output is not selected delete the netCDF file created
            if self.netOutput.get() == False:
                if os.path.exists(output_fname):
                    os.remove(output_fname)
            
            
            gc.MessageDialog(root, message="Success! Files processed.",
                             title='Success!')
                    
#             except:
#       
#                 gc.MessageDialog(root, message="Could not process file/s, please check file type.",
#                                  title='Error')
        else:
            self.root.focus_force()

def make_frame(frame, header=None):
    """Make a frame with uniform padding."""
    return ttk.Frame(frame, padding="3 3 5 5")

 
if __name__ == '__main__':
    root = Tk()
    gui = StormSurgeGui(root)
    root.mainloop()
