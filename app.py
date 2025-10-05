import customtkinter as ctk
from GIFGenerator import GIFGenerator
import numpy as np
import netCDF4 as nc
from tkinter import filedialog
from pathlib import Path
import os
from PIL import Image, ImageTk, ImageSequence

colorPalette ={
    "luminosity":[0.5,0.5,0.5],
    "contrast":[0.5,0.5,0.5],
    "phase":[0.5,0.5,0.5],
    "colorRange":[0.5,0.5,0.5]
}

class App():
    def __init__(self, root):
        self.main_root = root
        self.main_root.bind('<Escape>', self._escape)

        w = self.main_root.winfo_screenwidth() // 2
        h = self.main_root.winfo_screenheight() // 2
        self.main_root.geometry(f"{w}x{h}")

        self.main_root.state("zoomed")
        self.gif_generator = None
        self._generating = False
        self._last_key = None
        self._poll_after_id = None
        self._last_poll_count = -1
        self._stable_ticks = 0
        self._poll_loops = 0

        self.initWidget()
        #background
        self.background = self.set_background(frame= self.main_root,image_path="bg2.webp")
        self.main_root.bind("<Configure>",self._on_configure_gate)
        self.main_root.mainloop()

    # ---------------- UI init ----------------
    def initWidget(self):
        self.paramsFrame = ctk.CTkFrame(self.main_root, corner_radius=2, border_width=1, border_color="grey")
        self.paramsFrame.grid(row=0, column=0, padx=5, pady=5)

        self.gifFrame = ctk.CTkFrame(self.main_root, corner_radius=2, border_width=1, border_color="grey")
        self.gifFrame.grid(row=0, column=1, padx=5, pady=5)

        #slider
        self.elevatorFrame = ctk.CTkFrame(self.gifFrame,border_width=1,corner_radius=5)
        self.elevatorFrame.grid(row=0,column=1,padx=5,pady=5)
        self.elevationTitle = ctk.CTkLabel(self.elevatorFrame,text="Elevation")
        self.elevationTitle.grid(row=2,column=0,padx=5,pady=5)
        self.ElevationSlider = ctk.CTkSlider(self.elevatorFrame, command=self.displayGif, orientation="vertical")
        self.ElevationSlider.grid(row=0, column=0, padx=5, pady=5, sticky="sn")
        self.elevationLabel = ctk.CTkLabel(self.elevatorFrame,text = self.ElevationSlider._value)
        self.elevationLabel.grid(row=1,column=0,padx=5,pady=5)
        self.elevatorFrame.grid_remove()

        self.djTable = []
        self.djTableFrame = ctk.CTkFrame(self.gifFrame,border_width=1)
        self.djTableFrame.grid(row=0,column=2,padx=5,pady=5)


        #luminosity
        self.luminosityFrame,self.luminositySliders = self.createDJTable(colorPalette['luminosity'],"luminosity")
        self.luminosityFrame.grid(row=0,column=0,padx=5,pady=5)
        #contrast
        self.contrastFrame,self.contrastSliders = self.createDJTable(colorPalette['contrast'],"contrast")
        self.contrastFrame.grid(row=0,column=1,padx=5,pady=5)
        #phase
        self.phaseFrame,self.phaseSliders = self.createDJTable(colorPalette['phase'],"phase")
        self.phaseFrame.grid(row=0,column=2,padx=5,pady=5)
        #color range
        self.colorRangeFrame,self.colorRangeSliders = self.createDJTable(colorPalette['colorRange'],"color range")
        self.colorRangeFrame.grid(row=0,column=3,padx=5,pady=5)

        #gif button
        self.generateGif = ctk.CTkButton(self.paramsFrame, text="Generate", command=self.verifyGifGeneration)
        self.generateGif.grid(row=1, column=0, padx=5, pady=5)
        #self.generateGif.grid_remove()

        self.selected_file = None
        self.fileSelection = ctk.CTkButton(self.paramsFrame, text="Select a file", command=self.selectFile)
        self.fileSelection.grid(row=2, column=0, padx=5, pady=5)

        self.variablesDropdown = ctk.CTkOptionMenu(self.paramsFrame, values=["no file"], command=self.changeSlider)
        self.variablesDropdown.grid(row=0, column=0, padx=5, pady=5)

        #self.method = ctk.CTkCheckBox(self.paramsFrame,text="method")
        #self.method.grid(row=3,column=0,padx=5,pady=5)

    # ---------------- Small helpers ----------------
    def _fit_window_to_content(self, content_widget, marginx=-100,marginy=-50, include_padding=True, thresh=6):
        if getattr(self, "_sizing_internally", False):
            return

        try:
            is_zoomed = (str(self.root.state()) == "zoomed")  # Windows
        except Exception:
            is_zoomed = False
        is_full = bool(self.main_root.attributes("-fullscreen")) if hasattr(self.main_root, "attributes") else False
        if is_zoomed or is_full:
            return

        self.main_root.update_idletasks()
        target_w = content_widget.winfo_reqwidth()
        target_h = content_widget.winfo_reqheight()

        if include_padding:
            try:
                gi = content_widget.grid_info()
                if gi:
                    padx = gi.get("padx") or 0
                    pady = gi.get("pady") or 0
                    def _to_int_sum(v):
                        if isinstance(v, tuple):
                            return int(v[0]) + int(v[1])
                        return int(v)
                    target_w += _to_int_sum(padx)
                    target_h += _to_int_sum(pady)
            except Exception:
                pass

        target_w += int(marginx)
        target_h += int(marginy)

        cur_w = self.main_root.winfo_width()
        cur_h = self.main_root.winfo_height()

        if abs(target_w - cur_w) <= thresh and abs(target_h - cur_h) <= thresh:
            return
        self._sizing_internally = True
        try:
            x, y = self.main_root.winfo_x(), self.main_root.winfo_y()
            self.main_root.geometry(f"{int(target_w)}x{int(target_h)}+{x}+{y}")
        finally:
            self.main_root.after(1, lambda: setattr(self, "_sizing_internally", False))

    def _on_configure_gate(self,event=None):
        win = self.main_root.winfo_toplevel()
        if event is not None and event.widget is not win:
            return
        self._fit_window_to_content(self.main_root)

    def set_background(self,frame, image_path, keep_aspect=True):
        frame.update_idletasks()
        W = max(1, frame.winfo_width())
        H = max(1, frame.winfo_height())

        pil = Image.open(image_path).convert("RGB")

        def _fit_size(img, w, h):
            if not keep_aspect:
                return (w, h)
            iw, ih = img.size
            s = min(w/iw, h/ih) if iw and ih else 1
            return (max(1, int(iw*s)), max(1, int(ih*s)))

        size = _fit_size(pil, W, H)
        bg_img = ctk.CTkImage(light_image=pil, dark_image=pil, size=size)
        bg_lbl = ctk.CTkLabel(frame, text="", image=bg_img)
        bg_lbl.place(relx=0, rely=0, relwidth=1, relheight=1)
        bg_lbl.lower()
        frame._bg_pil = pil
        frame._bg_img = bg_img
        frame._bg_lbl = bg_lbl
        def _on_resize(_=None):
            w = max(1, frame.winfo_width())
            h = max(1, frame.winfo_height())
            new_size = _fit_size(frame._bg_pil, w, h)
            frame._bg_img.configure(size=new_size)

        frame.bind("<Configure>", _on_resize)
        return bg_lbl

    def getDJValues(self):
        luminosity =self.getSliderVal(self.luminositySliders)
        contrast = self.getSliderVal(self.contrastSliders)
        phase = self.getSliderVal(self.phaseSliders)
        colorRange =self.getSliderVal(self.colorRangeSliders)
        return luminosity,contrast,phase,colorRange

    def getSliderVal(self,sliders):
        val = [None,None,None]
        for i,slider in enumerate(sliders):
            val[i] = slider._value
        return val

    def createDJTable(self,vector,label,func =None):
        frame = ctk.CTkFrame(self.djTableFrame)
        label = ctk.CTkLabel(frame,text=label)
        label.grid(row=1,column=0,padx=5,pady=5,sticky="ew",columnspan=3)
        djTable = [None,None,None]
        for i,val in enumerate(vector):
            djTable[i] = ctk.CTkSlider(frame,orientation="vertical",from_=0,to=1)#,)
            djTable[i].grid(row=0,column=i,padx=5,pady=5)
            djTable[i].set(val)
        return frame,djTable

    def _target_dir(self) -> str:
        var = self.variablesDropdown.get().split("/")[-1].strip()
        base = os.path.splitext(Path(self.selected_file).name)[0]
        return os.path.join(base, var)

    def _count_gifs(self, folder: str) -> int:
        if not os.path.isdir(folder):
            return 0
        return len([f for f in os.listdir(folder) if f.lower().endswith(".gif")])

    def _set_loading(self, is_loading: bool, text: str = "Generating..."):

        if is_loading:
            self._generating = True
            self.generateGif.grid()
            #self.generateGif.configure(text=text, state="disabled")
            self.variablesDropdown.configure(state="disabled")
            self.ElevationSlider.grid_remove()

            if hasattr(self, "gif_widget"):
                try:
                    self.gif_widget.load("loading.gif", keep_position=False)
                except Exception:
                    pass
            else:
                self._last_key = None
                self.gif_widget = self.GifPlayer(self.gifFrame, gif_path="loading.gif", delay=150, text="")
                self.gif_widget.grid(row=0, column=0, padx=5, pady=5)
        else:
            self._generating = False
            self.generateGif.configure(text="Generate", state="normal")
            self.variablesDropdown.configure(state="normal")

    def _is_all_ready(self, current_count: int) -> bool:
        """Vrai uniquement si la génération est terminée (is_done / expected / DONE)."""
        # 1) Flag explicite fourni par le générateur
        if bool(getattr(self.gif_generator, "is_done", False)):
            return True
        # 2) Nombre total attendu
        expected = getattr(self.gif_generator, "expected", None)
        if isinstance(expected, int) and expected > 0 and current_count >= expected:
            return True
        # 3) Fichier sentinelle
        done_path = os.path.join(self._target_dir(), "DONE")
        if os.path.exists(done_path):
            return True
        return False

    # ---------------- Data helpers ----------------
    def getValues(self) -> list:
        if self.selected_file is None:
            return []
        goodlist = []
        ds = nc.Dataset(self.selected_file)
        try:
            for v in ds.variables.keys():
                dims = ds.variables[str(v)].dimensions
                if "time" in dims and "lat" in dims and "lon" in dims:
                    goodlist.append(v)
        finally:
            ds.close()
        return goodlist

    # ---------------- Main actions ----------------
    def selectFile(self):
        self.selected_file = filedialog.askopenfilename(
            title="select file",
            filetypes=(("NetCDF files", "*.nc4;*.nc"), ("all files", "*.*"))
        )
        if not self.selected_file:
            return


        values = self.getValues()
        if values:
            self.variablesDropdown.configure(values=values)
            self.variablesDropdown.set(values[0])
        else:
            self.variablesDropdown.configure(values=["no var"])
            self.variablesDropdown.set("no var")

        self.fileSelection.configure(text=Path(self.selected_file).name)
        self._last_key = None

        self.changeSlider(None)
        self._fit_window_to_content(self.main_root)

    def changeSlider(self, _):
        #if no file, remove slider from UI
        print(self.selected_file)
        if self.selected_file is None or self.variablesDropdown.get() == "no var":
            self.variablesDropdown.configure(state="normal")
            self.generateGif.grid()
            self.generateGif.configure(text="Generate", state="normal")
            self.elevatorFrame.grid_remove()

            if hasattr(self, "gif_widget"):
                self._last_key = None
                try:
                    self.gif_widget.load("loading.gif", keep_position=False)
                except Exception:
                    pass
            return

        #get gif path
        target = self._target_dir()
        nb_gif = self._count_gifs(target)

        #if in generation force loading
        if self._generating:
            self._set_loading(True, "Generating...")
            return

        #no gif, set UI
        if nb_gif == 0:
            self.variablesDropdown.configure(state="normal")
            self.elevatorFrame.grid_remove()
            self.generateGif.grid()
            self.generateGif.configure(text="Generate", state="normal")
            if hasattr(self, "gif_widget"):
                self._last_key = None
                try:
                    self.gif_widget.load("loading.gif", keep_position=False)
                except Exception:
                    pass
            return

        #1 gif no slider
        if nb_gif == 1:
            #self.generateGif.grid_remove()
            self.variablesDropdown.configure(state="normal")
            self.elevatorFrame.grid_remove()
            first_path = os.path.join(target, "1.0.gif")
            if hasattr(self, "gif_widget"):
                self._last_key = None
                self.gif_widget.load(first_path, keep_position=False)
            else:
                self._last_key = None
                self.gif_widget = self.GifPlayer(self.gifFrame, gif_path=first_path, delay=150, text="")
                self.gif_widget.grid(row=0, column=0, padx=5, pady=5)
            return

        # nb_gif > 1
        #self.generateGif.grid_remove()
        self.variablesDropdown.configure(state="normal")
        self.ElevationSlider.configure(from_=nb_gif, to=0, number_of_steps=nb_gif)
        self.ElevationSlider.set(nb_gif)
        self._last_key = None
        self.elevatorFrame.grid()
        self.displayGif(None)

    def verifyGifGeneration(self):
        print("iakfhoaidhasoidhasod")
        if self.variablesDropdown.get() == "no var":
            print("no var")
            return
        if self.selected_file is None:
            print("No file selected")
            return

        #stop process if one is started
        if self._poll_after_id:
            try:
                self.main_root.after_cancel(self._poll_after_id)
            except Exception:
                pass
            self._poll_after_id = None

        target = self._target_dir()
        nb = self._count_gifs(target)

        #already ready
        print(nb)

        if nb > 0:
            self._set_loading(False)
            self._last_key = None
            self._setup_slider_and_show_first(nb)                
            return

        #no gif
        #set loading
        self._set_loading(True, "Generating...")

        #init data for Gif gen
        var = self.variablesDropdown.get().split("/")[-1].strip()
        if (self.gif_generator is None
            or getattr(self.gif_generator, "nc_path", None) != self.selected_file
            or getattr(self.gif_generator, "var", None) != var):
            self.gif_generator = GIFGenerator(self.selected_file, var)

        #start gen
        self.gif_generator.startGeneratingGifs()

        # Reset polling counters & start
        self._last_poll_count = -1
        self._stable_ticks = 0
        self._poll_loops = 0
        self._poll_generation_done()

    # ---------------- Polling ----------------
    def _poll_generation_done(self):
        """Updates UI if polling is done.
        """
        target = self._target_dir()
        current_count = self._count_gifs(target)

        #True if done
        strong_ready = self._is_all_ready(current_count)

        #verify if gif are still generating given a time lapse
        if current_count == self._last_poll_count:
            self._stable_ticks += 1
        else:
            self._stable_ticks = 0
        self._last_poll_count = current_count

        STABLE_TICKS_THRESHOLD = 6
        TIMEOUT_TICKS = 120

        ready = strong_ready or (current_count > 0 and self._stable_ticks >= STABLE_TICKS_THRESHOLD)

        self._poll_loops += 1
        timeout = self._poll_loops >= TIMEOUT_TICKS
        if timeout and current_count > 0:
            ready = True

        #ready to update UI
        if ready:
            self._set_loading(False)
            #self.generateGif.grid_remove()

            current_var = self.variablesDropdown.get().split("/")[-1].strip()
            gen_var = getattr(self.gif_generator, "var", current_var)

            if current_var == gen_var:
                self._last_key = None
                nb = self._count_gifs(target)  # recalc final
                self._setup_slider_and_show_first(nb)

            # Stop polling & reset
            if self._poll_after_id:
                try:
                    self.main_root.after_cancel(self._poll_after_id)
                except Exception:
                    pass
            self._poll_after_id = None
            self._stable_ticks = 0
            self._poll_loops = 0
            self._last_poll_count = -1
            return

        # Continue polling
        self._poll_after_id = self.main_root.after(500, self._poll_generation_done)

    # ---------------- Display ----------------
    def _setup_slider_and_show_first(self, nb_gif: int):

        #get directory
        target = self._target_dir()

        #if no gif set loading image
        if nb_gif <= 0:
            self.ElevationSlider.grid_remove()
            if hasattr(self, "gif_widget"):
                try:
                    self.gif_widget.load("loading.gif", keep_position=False)
                except Exception:
                    pass
            return

        #if 1 gif, remove slider
        if nb_gif == 1:
            self.ElevationSlider.grid_remove()
            first_path = os.path.join(target, "1.0.gif")
            if hasattr(self, "gif_widget"):
                self._last_key = None
                self.gif_widget.load(first_path, keep_position=False)
            #not sure this is usefull
            else:
                self._last_key = None
                self.gif_widget = self.GifPlayer(self.gifFrame, gif_path=first_path, delay=150, text="")
                self.gif_widget.grid(row=0, column=0, padx=5, pady=5)
            return

        # nb_gif > 1 setup slider
        self.ElevationSlider.configure(from_=nb_gif, to=0, number_of_steps=nb_gif - 1)
        self.ElevationSlider.set(nb_gif-1)
        self._last_key = None
        self.ElevationSlider.grid()
        #show gif
        self.displayGif(None)

    def displayGif(self, _):
        #no file for whatever reason
        if self.selected_file is None:
            return

        #data from UI
        satellite = os.path.splitext(Path(self.selected_file).name)[0]
        var = self.variablesDropdown.get().split("/")[-1].strip()

        # clamp to min 1
        val = self.ElevationSlider.get()
        elevation = max(1, int(np.ceil(val)))

        #Reload each n e Z
        key = (var, elevation)
        if self._last_key == key:
            return
        self._last_key = key
        #change 
        
        self.elevationLabel.configure(text=np.abs(self.ElevationSlider.cget("from_")-elevation))
        #define prefered level
        if self.gif_generator is not None:
            try:
                self.gif_generator.setPreferedlevel(elevation)
            except Exception:
                pass

        #load gif into a gif player or start a new gif player
        gifPath = os.path.join(satellite, var, f"{elevation}.0.gif")
        if hasattr(self, "gif_widget"):
            self.gif_widget.load(gifPath, keep_position=True)
        else:
            self.gif_widget = self.GifPlayer(self.gifFrame, gif_path=gifPath, delay=150, text="")
            self.gif_widget.grid(row=0, column=0, padx=5, pady=5)

    def _escape(self,_):
        pass

    # ---------------- GIF player ----------------
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
