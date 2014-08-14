from tkinter import *
from tkinter import filedialog
import script2
from tkinter import ttk


class Script2gui:
    """A frontend for script2, which takes a water and air pressure
    file and outputs a depth file."""
    def __init__(self, root):
        methods = [('Naive', 'naive'),
                   ('Linear Wave', 'fft'),
                   ('Delft Paper', 'method2')]
        self.v = StringVar()
        ttk.Label(root, text='Depth calculation:').pack(anchor=W)
        for name, kwarg in methods:
            Radiobutton(root, text=name, variable=self.v,
                            value=kwarg).pack(anchor=W)
        self.v.set('naive')
        self.sea_fname = None
        self.air_fname = None
        c1 = lambda: self.select_file('sea_fname')
        self.make_button(root, "Select Water Pressure File", c1)
        c2 = lambda: self.select_file('air_fname')
        self.make_button(root, "Select Air Pressure File", c2)
        c3 = lambda: self.select_output_file(root)
        self.b3 = self.make_button(root, "Export to File", c3,
                                   state=DISABLED)

    def select_file(self, varname):
        fname = filedialog.askopenfilename()
        setattr(self, varname, fname)
        if self.sea_fname and self.air_fname:
            self.b3['state'] = 'ENABLED'

    def make_button(self, root, text, command, state=None):
        b = ttk.Button(root, text=text, command=command, state=state)
        b.pack(anchor=W, fill=BOTH)
        return b

    def select_output_file(self, root):
        output_fname = filedialog.asksaveasfilename()
        m = self.v.get()
        script2.make_depth_file(self.sea_fname, self.air_fname,
                                output_fname, depth_method=m)
        root.destroy()


if __name__ == '__main__':
    root = Tk()
    g = Script2gui(root)
    root.mainloop()
