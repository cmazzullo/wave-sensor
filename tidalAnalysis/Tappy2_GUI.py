from netCDF4 import Dataset
import pandas as pd
import matplotlib.pyplot as plt
from tappy2 import *

import Tkinter as Tk
import Tkinter
import tkFileDialog as filedialog
from Tkinter import StringVar
from Tkinter import W, E, LEFT, BOTH

class TappyGui:
    def __init__(self, root):
       
        self.in_file_name = ''
        self.root = root
        self.root.title('Tappy (Tidal Analysis Package)')
        
        methods = [('None', 'none'),
                   ('Transform', 'transform'),
                   ('USGS', 'usgs')]

        self.methodvar = StringVar()
        self.methodvar.set('none')

        Tk.Label(root, text='Filter:').pack(anchor=W,pady=2, padx=15)
        for name, kwarg in methods:
            Tk.Radiobutton(root, text=name, variable=self.methodvar,
                            value=kwarg).pack(anchor=W,pady=2, padx=15)
                            
        self.b1 = Tk.Button(self.root, text='Select File', command=self.select_input)
        self.b1.pack(anchor=W,pady=2, padx=15)
         
    def select_input(self):
        self.in_file_name = filedialog.askopenfilename()
        filter_filename = analysis(self.in_file_name,filter=self.methodvar.get())
        if filter_filename != None:
            for x in filter_filename:
                print(x)
                dotIndex = x.find('.')
                out_filename = "%s_filtered.nc" % x[0:dotIndex]
                filter_subtraction(self.in_file_name,x,out_filename)
                analysis(out_filename)
        MessageDialog(root, message="Success! Tappy Results saved.",
                         title='Success!')
                
    def make_fileselect(self, root, labeltext, stringvar, varname):
        command = lambda: self.select_file(varname, stringvar)
        frame = make_frame(root)
        l = Tk.Label(frame, justify=LEFT, text=labeltext, width=10)
        l.grid(row=0, column=0, sticky=W)
        b = self.make_button(frame, 'Browse', command)
        b.grid(row=0, column=2, sticky=W)
        e = Tk.Label(frame, textvariable=stringvar, justify=LEFT,
                      width=32)
        e.grid(row=0, column=1, sticky=(W, E))
        frame.pack(anchor=W, fill=BOTH)

    def select_output_file(self, root):
        output_fname = filedialog.asksaveasfilename()
        
def make_frame(frame, header=None):
    """Make a frame with uniform padding."""
    return Tk.Frame(frame, padding="3 3 5 5")
       
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

    
