import customtkinter as ctk
import ImageGenerator as IG
import numpy as np
import netCDF4 as nc
from tkinter import filedialog
from pathlib import Path

class App():
    def __init__(self,root):
        self.main_root = root
        self.main_root.bind('<Escape>', lambda e: self._escape())
        
        w = self.main_root.winfo_screenwidth()/5
        h = self.main_root.winfo_screenheight()/5
        self.main_root.geometry(f"{w}x{h}")
        #self.main_root.after(0, lambda: self.main_root.state("zoomed"))
        self.initWidget()
        self.main_root.mainloop()

    def initWidget(self):
        self.paramsFrame = ctk.CTkFrame(self.main_root, corner_radius=10, border_width=1, border_color="grey")
        self.paramsFrame.grid(row=0,column=0,padx=5,pady=5)
        self.gifFrame = ctk.CTkFrame(self.main_root, corner_radius=10, border_width=1, border_color="grey")
        self.gifFrame.grid(row =0,column =1,padx=5,pady=5)

        self.generateGif = ctk.CTkButton(self.paramsFrame,text="generate")
        self.generateGif.grid(row=1,column=0,padx=5,pady=5)

        self.selected_file = None
        self.fileSelection = ctk.CTkButton(self.paramsFrame,text="select a file",command=self.selectFile)
        self.fileSelection.grid(row=2,column=0,padx=5,pady=5)
        
        self.variablesDropdown = ctk.CTkOptionMenu(self.paramsFrame, values=["no file"])
        self.variablesDropdown.grid(row=0,column=0,padx=5,pady=5)

    def getValues(self)->list:
        if self.selected_file == None : return []
        goodlist = []
        ds = nc.Dataset(self.selected_file)
        for v in ds.variables.keys() :
            list = ds.variables[str(v)].dimensions
            if "time" in list and "lat" in list and "lon"in list :
                goodlist.append(v)
        return goodlist
    
    def selectFile(self):
        self.selected_file = filedialog.askopenfilename(
            title="Sélectionner un fichier",
            filetypes=(("Fichiers NetCDF", "*.nc4"), ("Tous les fichiers", "*.*")))
        values = self.getValues()
        self.variablesDropdown.set(values[0])
        self.variablesDropdown.configure(values=self.getValues())
    
        filename = Path(self.selected_file).name
        self.fileSelection.configure(text=filename)
        print(self.selected_file)
        



if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = App(root)