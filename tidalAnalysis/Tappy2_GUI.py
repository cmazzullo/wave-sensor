from netCDF4 import Dataset
import pandas as pd
import matplotlib.pyplot as plt
from tappy2 import *

import Tkinter as Tk
import Tkinter
import tkFileDialog as filedialog
from Tkinter import StringVar, BooleanVar
from Tkinter import W, E, LEFT, BOTH, DISABLED, ACTIVE

class TappyGui:
    def __init__(self, root):
       
        self.in_file_name = ''
        self.root = root
        self.root.title('Tappy (Tidal Analysis Package)')
        
        
        #gets the tappy_filter method
        methods = [('None', 'none'),
                   ('Transform', 'transform'),
                   ('USGS', 'usgs')]

        self.methodvar = StringVar()
        self.methodvar.set('none')
        
        Tk.Label(root, text='Filter:').pack(anchor=W,pady=2, padx=15)
        for name, kwarg in methods:
            Tk.Radiobutton(root, text=name, variable=self.methodvar,
                            value=kwarg).pack(anchor=W,pady=2, padx=15)
        
        Tk.Label(root, text='Options:').pack(anchor=W,pady=2, padx=15)
        
        #choose linear trend
        self.linearTrend = BooleanVar()
        Tk.Checkbutton(root, text="Linear Trend", variable = self.linearTrend) \
        .pack(anchor=W,pady= 2,padx=15)
        
        #reads the input file name chosen in file upload
        self.in_file_name = StringVar()
        self.make_fileselect(root,"Tide File:",self.in_file_name,"tide_fname")
        
        #chooses output file directory and begins the analysis of the input file
        c3 = lambda: self.select_output_file(root)                    
        self.b1 = Tk.Button(self.root, text='Export File', 
                            state = DISABLED, command=c3)
        self.b1.pack(anchor=W,pady=2, padx=15)
         
    def make_fileselect(self, root, labeltext, stringvar, varname):
        '''create frame and file upload button for a variable'''
        command = lambda: self.select_file(varname, stringvar)
        frame = make_frame(root)
        l = Tk.Label(frame, justify=LEFT, text=labeltext, width=10)
        l.grid(row=0, column=0, sticky=W)
        b = make_button(frame, 'Browse', command)
        b.grid(row=0, column=2, sticky=W)
        e = Tk.Label(frame, textvariable=stringvar, justify=LEFT,
                      width=32)
        e.grid(row=0, column=1, sticky=(W,E))
        frame.pack(anchor=W, fill=BOTH)

    def select_output_file(self, root):
        '''Name output file and process results'''
        
        #name the output file
        output_fname = filedialog.asksaveasfilename()
       
        #gets the tappy_filter name if there was a tappy_filter applied and re-applies analysis
        filter_filename = analysis(self.in_file_name.get(),filter=self.methodvar.get(), output_filename=output_fname, linear_trend=self.linearTrend.get())
        if filter_filename != None:
            for x in filter_filename:
                dotIndex = x.find('.')
                out_filename = "%s_filtered.nc" % x[0:dotIndex]
                filter_subtraction(self.in_file_name.get(),x,out_filename)
                analysis(out_filename, output_filename=output_fname, linear_trend=self.linearTrend.get())
                
        #success message
        MessageDialog(root, message="Success! Tappy Results saved.",
                         title='Success!')
        
        
    def select_file(self, varname, stringvar):
        fname = filedialog.askopenfilename()
        if fname != '':
            stringvar.set(fname)
            setattr(self, varname, fname)
            if self.in_file_name:
                self.b1['state'] = ACTIVE

def make_button(root, text, command, state=None):
        b = Tk.Button(root, text=text, command=command, state=state,
                       width=10)
        return b
         
def make_frame(frame, header=None):
    """Make a frame with uniform padding."""
#     return Tk.Frame(frame, padding="3 3 5 5")
    return Tk.Frame(frame, width=20)

class MessageDialog(Tkinter.Toplevel):
    """ A template for nice dialog boxes. """

    def __init__(self, parent, message="", title="", buttons=1,
                 wait=True):
        Tkinter.Toplevel.__init__(self, parent)
        body = Tk.Frame(self)
        self.title(title)
        self.boolean = None
        self.parent = parent
        self.transient(parent)
        Tk.Label(body, text=message).pack()
        if buttons == 1:
            b = Tk.Button(body, text="OK", command=self.destroy)
            b.pack(pady=5)
        elif buttons == 2:
            buttonframe = make_frame(body)

            def event(boolean):
                self.boolean = boolean
                self.destroy()

            b1 = Tk.Button(buttonframe, text='YES',
                            command=lambda: event(True))
            b1.grid(row=0, column=0)
            b2 = Tk.Button(buttonframe, text='NO',
                            command=lambda: event(False))
            b2.grid(row=0, column=1)
            buttonframe.pack()

        body.pack()
        self.grab_set()
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        if wait:
            self.wait_window(self)




root = Tk.Tk()
gui = TappyGui(root)
root.mainloop()

    
