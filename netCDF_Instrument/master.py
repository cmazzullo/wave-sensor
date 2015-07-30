import tools.chopper as chopper
import tools.statviewer as statviewer
import tools.script1_gui as script1
import tools.script1_air_gui as script1_air
import tools.script2_gui as script2
import tools.average_gui as average
import tools.depth_grapher_gui as depth_grapher

import tkinter as Tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from tkinter.constants import W
from PIL import Image, ImageTk

class MasterGui:
    def __init__(self, root):
       
        self.in_file_name = ''
        self.root = root
        
        #CREATES THE GUI LOGO AT THE BEGINNING
        img = Image.open("wavelab.jpg")
        photo = ImageTk.PhotoImage(img)
        
        self.panel = Tk.Label(root, image = photo)
        self.image = photo
        self.panel.pack()
        
        self.root.title('Wave Lab Tool Suite')
        self.Label = Tk.Label(self.root, text='Core Programs:')
        self.Label.pack(anchor=W,padx = 15,pady = 2)
        self.b1 = Tk.Button(self.root, text='Sea GUI', command=self.sea_gui)
        self.b1.pack(anchor=W,padx = 15,pady = 2)
        self.b2 = Tk.Button(self.root, text='Air GUI', command=self.air_gui)
        self.b2.pack(anchor=W,padx = 15,pady = 2)
        self.b3 = Tk.Button(self.root, text='Chopper', command=self.chopper)
        self.b3.pack(anchor=W,padx = 15,pady = 2)
        self.b4 = Tk.Button(self.root, text='Averager', command=self.averager)
        self.b4.pack(anchor=W,padx = 15,pady = 2)
        self.b5 = Tk.Button(self.root, text='Water Level GUI', command=self.water_level)
        self.b5.pack(anchor=W,padx = 15,pady = 2)
        self.emptyLabel = Tk.Label(self.root, text='', font=("Helvetica", 2))
        self.emptyLabel.pack(anchor=W,padx = 15,pady = 0)
        self.Label2 = Tk.Label(self.root, text='Graphing Utilities:')
        self.Label2.pack(anchor=W,padx = 15,pady = 2)
        self.b6 = Tk.Button(self.root, text='Water Level Graph', command=self.water_level_graph)
        self.b6.pack(anchor=W,padx = 15,pady = 2)
        self.b7 = Tk.Button(self.root, text='Statistics Viewer', command=self.stat_viewer)
        self.b7.pack(anchor=W,padx = 15,pady = 2)
        self.emptyLabel2 = Tk.Label(self.root, text='', font=("Helvetica", 2))
        self.emptyLabel2.pack(anchor=W,padx = 15,pady = 0)
        
    def sea_gui(self):
        self.root1 = Tk.Toplevel(self.root)
        gui1 = script1.Wavegui(self.root1, air_pressure=False)
        self.root1.mainloop()
    
    def air_gui(self):
        self.root2 = Tk.Toplevel(self.root)
        gui2 = script1_air.Wavegui(self.root2)
        self.root2.mainloop()
    
    def chopper(self):
        self.root3 = Tk.Toplevel(self.root)
        gui3 = chopper.Chopper(self.root3)
        self.root3.mainloop()
    
    def averager(self):
        self.root4 = Tk.Toplevel(self.root)
        gui4 = average.AverageGui(self.root4)
        self.root4.mainloop()
    
    def water_level(self):
        self.root5 = Tk.Toplevel(self.root)
        gui5 = script2.Script2gui(self.root5)
        self.root5.mainloop()
    
    def water_level_graph(self):
        self.root6 = Tk.Toplevel(self.root)
        gui6 = depth_grapher.DepthGui(self.root6)
        self.root6.mainloop()
        
    def stat_viewer(self):
        self.root7 = Tk.Toplevel(self.root)
        gui7 = statviewer.StatsViewer(self.root7)
        self.root7.mainloop()
        
def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
        
if __name__ == '__main__':  
    
                     
    root = Tk.Tk()
    gui = MasterGui(root)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
    
    
# plt.close('all')

