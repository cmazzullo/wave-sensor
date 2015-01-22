"""
@author: Chris Mazzullo

Converts pressure to depth and plots the result. Complete with knobs
and buttons!
"""
import sys
sys.path.append('.')
from DepthCalculation.depth_methods import chunked_p2d
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

import NetCDF_Utils.nc as nc
import tools.script2 as script2
import tools.script1_gui as gc


class Script2gui:
    def __init__(self, root):
        root.title('Pressure -> Water Height')
        self.methodvar = StringVar()
        self.methodvar.set('both')
        methods = [('Hydrostatic (purple)', 'naive'),
                   ('Linear Wave (blue)', 'fft'),
                   ('Both', 'both')]
        self.make_radiobutton(root, self.methodvar, 'Depth method:',
                              methods)
        self.sea_fname = None
        self.sea_var = StringVar()
        self.sea_var.set('File containing water pressure...')
        self.air_fname = None
        self.air_var = StringVar()
        self.no_air = 'File containing air pressure...'
        self.air_var.set(self.no_air)
        self.make_fileselect(root, 'Water file:',
                             self.sea_var, 'sea_fname')
        self.make_fileselect(root, 'Air file:',
                             self.air_var, 'air_fname')
        # c3 = lambda: self.select_output_file(root)
        # self.b3 = self.make_button(root, "Export to File", c3,
        #                            state=DISABLED)
        # self.b3.pack(anchor=W, fill=BOTH)
        c3 = self.plot_depth

        self.chunk_size = self.make_field(root, 'Chunk Size (s)')
        self.chunk_size.set('-1')
        self.lo_cut = self.make_field(root, 'Low Cut (Hz)')
        self.lo_cut.set('-1')
        self.hi_cut = self.make_field(root, 'High Cut (Hz)')
        self.hi_cut.set('inf')
        self.noise_gate = self.make_field(root, 'Noise Gate (dbar)')
        self.noise_gate.set('-1')
        self.avg_len = self.make_field(root, 'Avg. Length (data points)')
        self.avg_len.set('-1')
        self.b3 = self.make_button(root, "Go!", c3, state=DISABLED)
        self.b3.pack(anchor=W, fill=BOTH)


    def make_field(self, root, name):
        frame = gc.make_frame(root)
        var = StringVar()
        l = ttk.Label(frame, justify=LEFT, text=name, width=20)
        l.grid(row=0, column=0, sticky=W)
        e = ttk.Entry(frame, textvariable=var, justify=LEFT, width=16)
        e.grid(row=0, column=1, sticky=(W, E))
        frame.pack(anchor=W, fill=BOTH)
        return var

    def plot_depth(self):
        if self.air_fname == self.no_air:
            self.air_fname = None
        method = self.methodvar.get()
        print(method == 'naive')
        print(method)
        print(repr(method))
        frequency = nc.get_frequency(self.sea_fname)
        if int(self.chunk_size.get()) == -1:
            self.chunk_size.set(-1)
        else:
            self.chunk_size.set(int(int(self.chunk_size.get()) * frequency))
        # FFT
        if method != 'naive':
            print('plotting fft')
            time1, depth_fft = chunked_p2d(self.sea_fname, self.air_fname, 'fft',
                                           chunk_size=int(self.chunk_size.get()),
                                           lo_cut=float(self.lo_cut.get()),
                                           hi_cut=float(self.hi_cut.get()),
                                           noise_gate=float(self.noise_gate.get()),
                                           avg_len=float(self.avg_len.get()))
            print(len(time1), len(depth_fft))
            plt.plot(time1/1e3, depth_fft, 'b', label='Chunked spectral')

        if method != 'fft':
            print('plotting naive')
            time2, depth_static = chunked_p2d(self.sea_fname,
                                              self.air_fname,
                                              'hydrostatic',
                                              chunk_size=int(self.chunk_size.get()),
                                              avg_len=int(self.avg_len.get()))
            plt.plot(time2/1e3, depth_static, 'm', label='Hydrostatic')

        if method == 'both':
            # error = np.absolute(depth_fft - depth_static)
            plt.plot(time1/1e3, depth_fft - depth_static, 'r', label='Difference')

        plt.legend()
        plt.ylabel('water height (m)')
        plt.xlabel('time (seconds)')
        plt.grid(which='both')
        plt.show()


    def select_file(self, varname, stringvar):
        fname = filedialog.askopenfilename()
        stringvar.set(fname)
        setattr(self, varname, fname)
        if self.sea_fname:
            self.b3['state'] = 'ENABLED'

    def make_button(self, root, text, command, state=None):
        b = ttk.Button(root, text=text, command=command, state=state,
                       width=10)
        return b

    def make_radiobutton(self, root, var, text, options):
        ttk.Label(root, text=text).pack(anchor=W)
        for name, kwarg in options:
            ttk.Radiobutton(root, text=name, variable=var,
                            value=kwarg).pack(anchor=W)


    def make_fileselect(self, root, labeltext, stringvar, varname):
        command = lambda: self.select_file(varname, stringvar)
        frame = gc.make_frame(root)
        l = ttk.Label(frame, justify=LEFT, text=labeltext, width=10)
        l.grid(row=0, column=0, sticky=W)
        e = ttk.Label(frame, textvariable=stringvar, justify=RIGHT,
                      width=40)
        e.grid(row=0, column=1, sticky=(W, E))
        b = self.make_button(frame, 'Browse', command)
        b.grid(row=0, column=2, sticky=W)

        frame.pack(anchor=W, fill=BOTH)

    def select_output_file(self, root):
        output_fname = filedialog.asksaveasfilename()
        method = self.methodvar.get()
        sea_t = nc.get_time(self.sea_fname)
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
            "set to the fill value:%d" % nc.FILL_VALUE)
            gc.MessageDialog(root, message=message, title='Warning')
        script2.make_depth_file(self.sea_fname, self.air_fname,
                                output_fname, method=method)
        gc.MessageDialog(root, message="Success! Files saved.",
                         title='Success!')

def evenify(n):
    if n % 2 != 0:
        return n + 1
    else: return n

if __name__ == '__main__':
    root = Tk()
    g = Script2gui(root)


    root.mainloop()
