#!/usr/bin/env python3
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

import tools.script1_gui as gc
from tools.storm_options import StormOptions
from tools.storm_graph import StormGraph
from tools.storm_csv import StormCSV
from tools.storm_netCDF import Storm_netCDF
import traceback
from tools.storm_statistics import StormStatistics
from tools.multi_series_options import MultiOptions
from tools.multi_series import MultiSeries


class MultiSeriesGui:
    def __init__(self, root):
        
        self.file_opt = options = {}
        options['filetypes'] = [('netCDF files', '.nc')]
        options['initialdir'] = '~\\Desktop'
        #root and selection dialogs for sea and air netCDF files
        self.root = root
        
        self.top = Frame(self.root)
#       
        root.title('Multiple Time Series GUI')
        self.root.focus_force()
        
        self.stormLabel = Label(self.top, text='(Please make sure Chopper is closed before making a graph)')
        self.stormLabel.pack(anchor=W,pady = 2)
        
        self.sea_fnames, self.sea_vars = [], []
        self.air_fnames, self.air_vars = [], []
        
        for x in range(0,10):
            self.sea_fnames.append('')
            self.sea_vars.append(StringVar())
            self.sea_vars[x].set('No file selected...')
            self.air_fnames.append('')
            self.air_vars.append(StringVar())
            self.air_vars[x].set('No file selected...')

        open_file = lambda: self.open_file_selection(self.root)

        
        self.b3 = ttk.Button(self.top,text="Browse Files", command=open_file)
        self.b3.pack(anchor=W, pady=2)
         
        
        self.mo = MultiOptions()
        
        self.top.grid(row=0, columnspan=2, sticky=W, padx = 15, pady=10)
        
        self.side1 = Frame(self.root)
        
        #Check boxes for output variables
        self.netCDFLabel = Label(self.side1, text='Graph Options:')
        self.netCDFLabel.pack(anchor=W,padx = 2,pady = 2)
        
        for x in sorted(self.mo.graph):
            self.mo.graph[x] = BooleanVar()
            button = Checkbutton(self.side1, text=x, variable=self.mo.graph[x])
            button.pack(anchor=W,padx = 0,pady = 2)
        
        self.TzLabel = Label(self.side1, text='Time zone to display dates in:')
        self.TzLabel.pack(anchor=W,padx = 2,pady = 2)
        
        options=('GMT',
                'US/Aleutian',
                'US/Central',
                'US/Eastern',
                'US/Hawaii',
                'US/Mountain',
                'US/Pacific')
        self.tzstringvar = StringVar()
        self.tzstringvar.set(options[0])

        self.datePickFrame = Frame(self.side1)
        
        OptionMenu(self.datePickFrame, self.tzstringvar, *options).pack(side=LEFT, pady=2, padx=15)
        self.daylightSavings = BooleanVar()
        Checkbutton(self.datePickFrame, text="Daylight Savings", variable=self.daylightSavings).pack(side=RIGHT)
        self.datePickFrame.pack(anchor=W)
        
        self.emptyLabel4 = Label(self.side1, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W,padx = 15,pady = 0)
        
        #variables and text boxes for air pressure limits
        self.BaroPickLabel = Label(self.side1, text='Barometric Pressure Y Axis Limits: (optional)')
        self.BaroPickLabel.pack(anchor=W,padx = 15,pady = 0)
        
        self.baroPickFrame = Frame(self.side1)
        self.bLowerLabel = Label(self.baroPickFrame, text="lower:").pack(side=LEFT, pady=10, padx=2)
        self.baroYlim1 = Entry(self.baroPickFrame, width=5)
        self.baroYlim1.pack(side=LEFT, pady=2, padx=15)
        self.baroYlim2 = Entry(self.baroPickFrame, width=5)
        self.baroYlim2.pack(side=RIGHT, pady=2, padx=15)
        self.bUpperLabel = Label(self.baroPickFrame, text="upper:").pack(side=RIGHT, pady=10, padx=2)
        self.baroPickFrame.pack(anchor=W, padx = 15)
        
        #tkinter spacing
        self.emptyLabel4 = Label(self.side1, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W,padx = 15,pady = 0)
        
        #variables and textboxes for water level limits
        self.WaterLevelLabel = Label(self.side1, text='Water Level Y Axis Limits: (optional)')
        self.WaterLevelLabel.pack(anchor=W,padx = 15,pady = 0)
        
        self.wlPickFrame = Frame(self.side1)
        self.wlLowerLabel = Label(self.wlPickFrame, text="lower:").pack(side=LEFT, pady=10, padx=2)
        self.wlYlim1 = Entry(self.wlPickFrame, width=5)
        self.wlYlim1.pack(side=LEFT, pady=2, padx=15)
        self.wlYlim2 = Entry(self.wlPickFrame, width=5)
        self.wlYlim2.pack(side=RIGHT, pady=2, padx=15)
        self.wlUpperLabel = Label(self.wlPickFrame, text="upper:").pack(side=RIGHT, pady=10, padx=2)
        self.wlPickFrame.pack(anchor=W, padx = 15)
        
        self.side1.grid(row=1, column=0, sticky=W, padx = 15)
        
    
        self.final = Frame(self.root)
        c3 = lambda: self.select_output_file(self.root)
        self.b3 = ttk.Button(self.final,text="Process Files", command=c3,width=50)
        
        self.b3.pack(fill='both')

        self.final.grid(row=2, columnspan=2)
    

    def open_file_selection(self, root):
        self.file_root = Toplevel(root)
        self.file_select_grid1 = Frame(self.file_root)
        self.file_select_grid2 = Frame(self.file_root)
        self.close_frame = Frame(self.file_root)
        
        self.stormLabel = Label(self.file_select_grid1, text='Water netCDF Files')
        self.stormLabel.pack(anchor=W,pady = 2)
        self.stormLabel = Label(self.file_select_grid2, text='Air netCDF Files')
        self.stormLabel.pack(anchor=W,pady = 2)
        
        for x in range(0,10):
            self.make_fileselect(self.file_select_grid1, ''.join([str(x + 1),': ']),
                                 self.sea_vars, self.sea_fnames,x)
            self.make_fileselect(self.file_select_grid2, ''.join([str(x + 1),': ']),
                                 self.air_vars, self.air_fnames,x)
        
        self.file_select_grid1.grid(row=0, column=0,padx = 15)
        self.file_select_grid2.grid(row=0, column=1,padx = 15)
        
        close = lambda: self.file_root.destroy()
        self.b3 = ttk.Button(self.close_frame,text="Done", command=close)
        self.b3.pack()
        
        self.close_frame.grid(row=1, column=1,padx = 15)
        
        self.file_root.mainloop()  
         
        
            
    def select_file(self, var, stringvar, index):
        fname = filedialog.askopenfilename(**self.file_opt)
        if fname != '':
            stringvar.set(fname)
            var[index] = fname
            
            print(fname)
            index = fname.rfind('/')
            if index == -1:
                self.file_opt['initialdir'] = '\\'
            else:  
                self.file_opt['initialdir'] = fname[0:index]
#             if(self.air_fname != ''):
#                 self.b3['state'] = 'ENABLED'
        self.file_root.focus_force()
        
    def clear_file(self, var, stringvar, index):
        
        stringvar.set('No file selected...')
        var[index] = ''
#         if(self.air_fname == ''):
#                 self.b3.config(state='disabled')

    def make_button(self, root, text, command, state=None):
        '''Creates a new button'''
        b = ttk.Button(root, text=text, command=command, state=state,
                       width=10)
        return b

    def make_fileselect(self, root, labeltext, stringvar, var, index):
        '''Creates a file selection menu'''
        command = lambda: self.select_file(var, stringvar[index], index)
        command2 = lambda: self.clear_file(var, stringvar[index], index)
        frame = make_frame(root)
        l = ttk.Label(frame, justify=LEFT, text=labeltext, width=10)
        l.grid(row=0, column=0, sticky=W)
        b = self.make_button(frame, 'Browse', command)
        b.grid(row=0, column=2, sticky=W)
        b2 = self.make_button(frame, 'Clear', command2)
        b2.grid(row=0, column=3, sticky=W)
        e = ttk.Label(frame, textvariable=stringvar[index], justify=LEFT,
                      width=32)
        e.grid(row=0, column=1, sticky=(W, E))
        frame.pack(anchor=W, fill=BOTH)

    def select_output_file(self, root):
        '''Processes the selected afiles and outputs in format selected'''
        
        self.mo.clear_data()
        self.mo.sea_fnames = self.sea_fnames
        self.mo.air_fnames = self.air_fnames
        
        if self.mo.check_selected() == False:
            message = ("Please select at least one option")
            gc.MessageDialog(root, message=message, title='Error!')
            return
        
        if self.mo.file_check() == False:
            message = ("Please upload at least one file")
            gc.MessageDialog(root, message=message, title='Error!')
            return
        
        if self.mo.option_check_selected() == False:
            message = ("Please upload at least one sea file or air file or \n \
            uncheck options that require it")
            gc.MessageDialog(root, message=message, title='Error!')
            return
        
        
        og_fname = filedialog.asksaveasfilename()
        
        if og_fname is None or og_fname == '':
            self.root.focus_force()
            return
        
#         try:
        self.mo.format_output_fname(og_fname)
        self.mo.timezone = self.tzstringvar.get()
        self.mo.daylight_savings = self.daylightSavings.get()
        self.mo.create_storm_objects()
        
        self.mo.baroYLims = []
        try:
            self.mo.baroYLims.append(float(self.baroYlim1.get()))
            self.mo.baroYLims.append(float(self.baroYlim2.get()))
        except:
            self.mo.baroYLims = None
            
        self.mo.wlYLims = []
        try:
            self.mo.wlYLims.append(float(self.wlYlim1.get()))
            self.mo.wlYLims.append(float(self.wlYlim2.get()))
        except:
            self.mo.wlYLims = None
        
        if self.mo.sea_fnames[0] != '':
            
            for x in range(0,len(self.mo.storm_objects)):
                
                overlap = self.mo.storm_objects[x].time_comparison()
                    
                if overlap == 2:
                    message = ("Air pressure and water pressure of files in pair %d do not "
                               "cover the same time period!\nPlease choose "
                               "other files." % (x+1))
                    gc.MessageDialog(root, message=message, title='Error!')
                    return
            
        
        ms = MultiSeries()
        ms.process_graphs(self.mo)
        
        gc.MessageDialog(root, message="Success! Files processed.",
                                 title='Success!')
                
#         except:
#             exc_type, exc_value, exc_traceback = sys.exc_info()
#        
#             message = traceback.format_exception(exc_type, exc_value,
#                                           exc_traceback)
# #             message = 'Could not process files, please check file type.'
#             gc.MessageDialog(root, message=message,
#                              title='Error')

def make_frame(frame, header=None):
    """Make a frame with uniform padding."""
    return ttk.Frame(frame, padding="3 3 5 5")

 
if __name__ == '__main__':
    root = Tk()
    gui = MultiSeriesGui(root)
    root.mainloop()
