import tkinter as Tk
from tkinter import filedialog
from tkinter import ttk
from tkinter.constants import W, LEFT, RIGHT

from tools.depth_grapher import make_depth_graph
import easygui


class DepthGui:
    def __init__(self, root):
       
        self.in_file_name = ''
        self.root = root
        self.root.title('Water Level vs. Pressure Grapher')
        self.root.focus_force()
        #Date time options
        
        self.TzLabel = Tk.Label(self.root, text='Time zone to display dates in:')
        self.TzLabel.pack(anchor=W,padx = 15,pady = 2)
        options=('GMT',
                'US/Aleutian',
                'US/Central',
                'US/Eastern',
                'US/Hawaii',
                'US/Mountain',
                'US/Pacific')
        self.tzstringvar = Tk.StringVar()
        self.tzstringvar.set(options[0])
        
        
        self.datePickFrame = Tk.Frame(root)
        
        Tk.OptionMenu(self.datePickFrame, self.tzstringvar, *options).pack(side=LEFT, pady=2, padx=15)
        
        self.daylightSavings = Tk.BooleanVar()
        Tk.Checkbutton(self.datePickFrame, text="Daylight Savings", variable=self.daylightSavings).pack(side=RIGHT)
        self.datePickFrame.pack()
        
        #tkinter spacing
        self.emptyLabel4 = Tk.Label(self.root, text='', font=("Helvetica", 2))
        self.emptyLabel4.pack(anchor=W,padx = 15,pady = 0)
        
        self.Label = Tk.Label(self.root, text='Averaged Points:')
        self.Label.pack(anchor=W,padx = 15,pady = 2)
        
        
        self.AveragedPoints = Tk.Entry(self.root)
        self.AveragedPoints.pack(anchor=W,padx = 15,pady = 2)
        self.AveragedPoints.insert(0, "1")
        self.b1 = Tk.Button(self.root, text='Select File', command=self.select_input)
        self.b1.pack(anchor=W,padx = 15,pady = 2)
        
    def select_input(self):
        self.in_file_name = filedialog.askopenfilename()
        
        try:
            make_depth_graph(int(self.AveragedPoints.get()), self.in_file_name, \
                                 self.tzstringvar.get(), self.daylightSavings.get())
        except:
            easygui.msgbox('Could not plot file, check file type', 'Error')

class Variable:
    """
    Stores data about each attribute to be added to the netCDF file.

    Also contains metadata that allows the GUI to build widgets from
    the Variable and use the data inside it in the csv-to-netCDF
    converters.
    """
    def __init__(self, name_in_device=None, label=None, doc=None,
                 options=None, filename=False, autosave=False,
                 in_air_pressure=True, in_water_pressure=True):
        self.name_in_device = name_in_device
        self.label = label
        self.doc = doc
        self.options = options
        self.stringvar = Tk.StringVar()
        self.stringvar.set('')
        self.filename = filename
        self.autosave = autosave
        self.in_air_pressure = in_air_pressure
        self.in_water_pressure = in_water_pressure

if __name__ == '__main__':       
    root = Tk.Tk()
    gui = DepthGui(root)
    root.mainloop()
# plt.close('all')