import tools.chopper_gui as chopper
#import tools.statviewer as statviewer
import tools.script1_gui as script1
import tools.script1_air_gui as script1_air
import tools.storm_gui_v2 as storm_gui
import tools.wind_gui as wind_gui

import tkinter as Tk
from tkinter import messagebox
from tkinter.constants import W
from PIL import Image, ImageTk
import sys

class MasterGui:
    def __init__(self, root):
       
        self.in_file_name = ''
        self.root = root
        self.root.focus_force()
        #CREATES THE GUI LOGO AT THE BEGINNING
        img = Image.open("wavelab.jpg")
        photo = ImageTk.PhotoImage(img)
        
        self.panel = Tk.Label(root, image = photo)
        self.image = photo
        self.panel.pack()
        
        self.root.title('Wavelab Tool Suite')
        self.Label = Tk.Label(self.root, text='Core Programs:')
        self.Label.pack(anchor=W,padx = 15,pady = 2)
        self.b1 = Tk.Button(self.root, text='Sea GUI', command=self.sea_gui)
        self.b1.pack(anchor=W,padx = 15,pady = 2)
        self.b2 = Tk.Button(self.root, text='Air GUI', command=self.air_gui)
        self.b2.pack(anchor=W,padx = 15,pady = 2)
        self.b3 = Tk.Button(self.root, text='Chopper', command=self.chopper)
        self.b3.pack(anchor=W,padx = 15,pady = 2)
        self.b4 = Tk.Button(self.root, text='Wind GUI', command=self.wind_gui)
        self.b4.pack(anchor=W,padx = 15,pady = 2)
        self.b5 = Tk.Button(self.root, text='Storm GUI', command=self.storm_surge)
        self.b5.pack(anchor=W,padx = 15,pady = 2)
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
    
    def wind_gui(self):
        self.root4 = Tk.Toplevel(self.root)
        gui4 = wind_gui.WindGUI(self.root4)
        self.root4.mainloop()

    def storm_surge(self):
        self.root8 = Tk.Toplevel(self.root)
        gui8 = storm_gui.StormGui(self.root8)
        self.root8.mainloop()
        
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
        
if __name__ == '__main__':  
    
                     
    root = Tk.Tk()
    gui = MasterGui(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_closing)
    root.mainloop()
    
    
# plt.close('all')

