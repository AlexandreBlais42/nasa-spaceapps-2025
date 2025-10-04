import customtkinter as ctk
from GIFGenerator import GIFGenerator
import numpy as np
import netCDF4 as nc
from tkinter import filedialog
from pathlib import Path
import os
from PIL import Image, ImageTk, ImageSequence

class App():
    def __init__(self,root):
        self.main_root = root
        self.main_root.bind('<Escape>', lambda e: self._escape())
        
        w = self.main_root.winfo_screenwidth()/5
        h = self.main_root.winfo_screenheight()/5
        self.main_root.geometry(f"{w}x{h}")
        #self.main_root.after(0, lambda: self.main_root.state("zoomed"))
        self.gif_generator = None
        self.initWidget()
        self.main_root.mainloop()

    def initWidget(self):
        self.paramsFrame = ctk.CTkFrame(self.main_root, corner_radius=10, border_width=1, border_color="grey")
        self.paramsFrame.grid(row=0,column=0,padx=5,pady=5)
        self.gifFrame = ctk.CTkFrame(self.main_root, corner_radius=10, border_width=1, border_color="grey")
        self.gifFrame.grid(row =0,column =1,padx=5,pady=5)

        self.ElevationSlider = ctk.CTkSlider(self.gifFrame, command=self.displayGif,orientation="vertical")

        self.ElevationSlider.grid(row=0, column=1, padx=5, pady=5, sticky="sn")
        self.ElevationSlider.grid_remove()

        self.generateGif = ctk.CTkButton(self.paramsFrame,text="generate",command=self.verifyGifGeneration)
        self.generateGif.grid(row=1,column=0,padx=5,pady=5)

        self.selected_file = None
        self.fileSelection = ctk.CTkButton(self.paramsFrame,text="select a file",command=self.selectFile)
        self.fileSelection.grid(row=2,column=0,padx=5,pady=5)
        
        self.variablesDropdown = ctk.CTkOptionMenu(self.paramsFrame, values=["no file"],command=self.changeSlider)
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
        self.verifyGifGeneration()
        print(self.selected_file)

    def verifyGifGeneration(self):
        if self.selected_file == None :
            print("No file selected")
            return
        data_selected = os.path.join(os.path.splitext(Path(self.selected_file).name)[0],self.variablesDropdown.get())
        if os.path.isdir(data_selected):
            print("file found")
            
            self.displayGif(None)
        else:
            self.ElevationSlider.grid_remove()
            print("file not found generating gif")
            if self.gif_generator is None:
                self.gif_generator = GIFGenerator(self.selected_file, self.variablesDropdown.get())
                self.gif_generator.startGeneratingGifs()

    def displayGif(self, _):
        if self.selected_file is None:
            return

        satellite = os.path.splitext(Path(self.selected_file).name)[0]
        var = self.variablesDropdown.get().split("/")[-1].strip()  # au cas où
        elevation = int(np.ceil(self.ElevationSlider.get()))

        # --- clé composite pour éviter le faux "cache" ---
        key = (var, elevation)
        if getattr(self, "_last_key", None) == key:
            return
        self._last_key = key
        print("elevation", elevation, "var", var)

        if self.gif_generator is not None:
            self.gif_generator.setPreferedlevel(elevation)

        gifPath = os.path.join(satellite, var, f"{elevation}.0.gif")
        if hasattr(self, "gif_widget"):
            self.gif_widget.load(gifPath, keep_position=True)
        else:
            self.gif_widget = self.GifPlayer(self.gifFrame, gif_path=gifPath, delay=150, text="")
            self.gif_widget.grid(row=0, column=0, padx=5, pady=5)


        
    
    def changeSlider(self, _):
        if self.selected_file is None:
            return

        var = self.variablesDropdown.get().split("/")[-1].strip()
        base = os.path.splitext(Path(self.selected_file).name)[0]
        data_selected = os.path.join(base, var)

        if os.path.isdir(data_selected):
            files = [f for f in os.listdir(data_selected) if f.lower().endswith(".gif")]
            nb_gif = len(files)

            if nb_gif == 0:
                self.ElevationSlider.grid_remove()
                if hasattr(self, "gif_widget"):
                    self._last_key = None    # force un futur reload
                    self.gif_widget.load("loading.gif", keep_position=True)
                return

            if nb_gif == 1:
                self.ElevationSlider.grid_remove()
                if hasattr(self, "gif_widget"):
                    self._last_key = None
                    self.gif_widget.load(os.path.join(data_selected, "1.0.gif"), keep_position=False)
                return

            # nb_gif > 1
            self.ElevationSlider.configure(from_=1, to=nb_gif, number_of_steps=nb_gif-1)
            self.ElevationSlider.set(1)

            # IMPORTANT: réinitialiser la clé pour forcer le refresh
            self._last_key = None
            self.ElevationSlider.grid()
            self.displayGif(None)
        else:
            self.ElevationSlider.grid_remove()
            if hasattr(self, "gif_widget"):
                self._last_key = None
                self.gif_widget.load("loading.gif", keep_position=True)




    class GifPlayer(ctk.CTkLabel):
        def __init__(self, master, gif_path, delay=150, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.default_delay = delay
            self._after_id = None
            self.frames = []
            self.durations = []
            self.index = 0 
            self._last_ratio = 0.0
            self.load(gif_path, keep_position=False)

        def stop(self):
            if self._after_id is not None:
                try:
                    self.after_cancel(self._after_id)
                except Exception:
                    pass
                self._after_id = None

        def load(self, gif_path, keep_position=True):
            old_len = len(self.frames)
            old_index = self.index
            self.stop()

            if old_len > 0:
                self._last_ratio = old_index / max(1, old_len - 1)
            else:
                self._last_ratio = 0.0

            im = Image.open(gif_path)
            self.frames = []
            self.durations = []
            for frame in ImageSequence.Iterator(im):
                self.frames.append(ImageTk.PhotoImage(frame.copy()))
                self.durations.append(frame.info.get("duration", self.default_delay) or self.default_delay)

            if not self.frames:
                return

            if keep_position and old_len > 0:
                if len(self.frames) == old_len:
                    new_index = old_index
                else:
                    new_index = round(self._last_ratio * (len(self.frames) - 1))
            else:
                new_index = 0

            self.index = max(0, min(len(self.frames) - 1, new_index))

            self.configure(image=self.frames[self.index], text="")
            self._schedule_next()

        def _schedule_next(self):
            delay = int(self.durations[self.index]) if self.durations else self.default_delay
            self._after_id = self.after(delay, self._advance)

        def _advance(self):
            self.index = (self.index + 1) % len(self.frames)
            self.configure(image=self.frames[self.index])
            self._schedule_next()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = App(root)
