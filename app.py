import customtkinter as ctk
from GIFGenerator import GIFGenerator
import numpy as np
import netCDF4 as nc
from tkinter import filedialog
from pathlib import Path
import os
from PIL import Image, ImageTk, ImageSequence


class App():
    def __init__(self, root):
        self.main_root = root
        self.main_root.bind('<Escape>', lambda e: self._escape() if hasattr(self, "_escape") else None)

        w = self.main_root.winfo_screenwidth() // 2
        h = self.main_root.winfo_screenheight() // 2
        self.main_root.geometry(f"{w}x{h}")

        self.gif_generator = None
        self._generating = False
        self._last_key = None
        self._poll_after_id = None
        self._last_poll_count = -1
        self._stable_ticks = 0
        self._poll_loops = 0

        self.initWidget()
        self.main_root.mainloop()

    # ---------------- UI init ----------------
    def initWidget(self):
        self.paramsFrame = ctk.CTkFrame(self.main_root, corner_radius=10, border_width=1, border_color="grey")
        self.paramsFrame.grid(row=0, column=0, padx=5, pady=5)

        self.gifFrame = ctk.CTkFrame(self.main_root, corner_radius=10, border_width=1, border_color="grey")
        self.gifFrame.grid(row=0, column=1, padx=5, pady=5)

        self.ElevationSlider = ctk.CTkSlider(self.gifFrame, command=self.displayGif, orientation="vertical")
        self.ElevationSlider.grid(row=0, column=1, padx=5, pady=5, sticky="sn")
        self.ElevationSlider.grid_remove()

        self.generateGif = ctk.CTkButton(self.paramsFrame, text="Generate", command=self.verifyGifGeneration)
        self.generateGif.grid(row=1, column=0, padx=5, pady=5)
        self.generateGif.grid_remove()

        self.selected_file = None
        self.fileSelection = ctk.CTkButton(self.paramsFrame, text="Select a file", command=self.selectFile)
        self.fileSelection.grid(row=2, column=0, padx=5, pady=5)

        self.variablesDropdown = ctk.CTkOptionMenu(self.paramsFrame, values=["no file"], command=self.changeSlider)
        self.variablesDropdown.grid(row=0, column=0, padx=5, pady=5)

    # ---------------- Small helpers ----------------
    def _target_dir(self) -> str:
        var = self.variablesDropdown.get().split("/")[-1].strip()
        base = os.path.splitext(Path(self.selected_file).name)[0]
        return os.path.join(base, var)

    def _count_gifs(self, folder: str) -> int:
        if not os.path.isdir(folder):
            return 0
        return len([f for f in os.listdir(folder) if f.lower().endswith(".gif")])

    def _set_loading(self, is_loading: bool, text: str = "Generating..."):
        """Centralise l'état loading: bouton, dropdown, slider, visuel."""
        if is_loading:
            self._generating = True
            self.generateGif.grid()
            self.generateGif.configure(text=text, state="disabled")
            self.variablesDropdown.configure(state="disabled")
            self.ElevationSlider.grid_remove()
            print("poopop")
            if hasattr(self, "gif_widget"):
                try:
                    self.gif_widget.load("loading.gif", keep_position=False)
                except Exception:
                    pass
            else :
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
        """Liste les variables time/lat/lon et referme le dataset proprement."""
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
            title="Sélectionner un fichier",
            filetypes=(("Fichiers NetCDF", "*.nc4;*.nc"), ("Tous les fichiers", "*.*"))
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

    def changeSlider(self, _):
        """Met l'UI dans le bon état selon l’existence/complétude des GIFs."""
        if self.selected_file is None:
            self.variablesDropdown.configure(state="normal")
            self.generateGif.grid()
            self.generateGif.configure(text="Generate", state="normal")
            self.ElevationSlider.grid_remove()
            if hasattr(self, "gif_widget"):
                self._last_key = None
                try:
                    self.gif_widget.load("loading.gif", keep_position=False)
                except Exception:
                    pass
            return

        target = self._target_dir()
        nb_gif = self._count_gifs(target)

        # Si une génération est en cours → forcer le mode loading
        if self._generating:
            self._set_loading(True, "Generating...")
            return

        if nb_gif == 0:
            # Pas encore généré → proposer Generate
            self.variablesDropdown.configure(state="normal")
            self.ElevationSlider.grid_remove()
            self.generateGif.grid()
            self.generateGif.configure(text="Generate", state="normal")
            if hasattr(self, "gif_widget"):
                self._last_key = None
                try:
                    self.gif_widget.load("loading.gif", keep_position=False)
                except Exception:
                    pass
            return

        if nb_gif == 1:
            # Dataset (de taille 1) prêt → pas de slider
            self.generateGif.grid_remove()
            self.variablesDropdown.configure(state="normal")
            self.ElevationSlider.grid_remove()
            first_path = os.path.join(target, "1.0.gif")
            if hasattr(self, "gif_widget"):
                self._last_key = None
                self.gif_widget.load(first_path, keep_position=False)
            else:
                self._last_key = None
                self.gif_widget = self.GifPlayer(self.gifFrame, gif_path=first_path, delay=150, text="")
                self.gif_widget.grid(row=0, column=0, padx=5, pady=5)
            return

        # nb_gif > 1 → slider discret 1..N
        self.generateGif.grid_remove()
        self.variablesDropdown.configure(state="normal")
        self.ElevationSlider.configure(from_=1, to=nb_gif, number_of_steps=nb_gif - 1)
        self.ElevationSlider.set(1)
        self._last_key = None
        self.ElevationSlider.grid()
        self.displayGif(None)

    def verifyGifGeneration(self):
        """Démarre la génération et n’affiche rien tant que tout n’est pas prêt."""
        if self.selected_file is None:
            print("No file selected")
            return

        # Annule un éventuel polling en cours
        if self._poll_after_id:
            try:
                self.main_root.after_cancel(self._poll_after_id)
            except Exception:
                pass
            self._poll_after_id = None

        target = self._target_dir()
        nb = self._count_gifs(target)

        # Si déjà prêt (cas limite), afficher direct
        if nb > 0 and self._is_all_ready(nb):
            self._set_loading(False)       # réactive dropdown
            self.generateGif.grid_remove() # cache le bouton
            self._last_key = None
            self._setup_slider_and_show_first(nb)
            return

        # Sinon: lancer génération & UI loading
        self._set_loading(True, "Generating...")

        var = self.variablesDropdown.get().split("/")[-1].strip()
        if (self.gif_generator is None
            or getattr(self.gif_generator, "nc_path", None) != self.selected_file
            or getattr(self.gif_generator, "var", None) != var):
            self.gif_generator = GIFGenerator(self.selected_file, var)

        # Lance la génération
        self.gif_generator.startGeneratingGifs()

        # Reset polling counters & start
        self._last_poll_count = -1
        self._stable_ticks = 0
        self._poll_loops = 0
        self._poll_generation_done()

    # ---------------- Polling ----------------
    def _poll_generation_done(self):
        """Affiche UNIQUEMENT quand tout est prêt.
        - Utilise is_done / expected / DONE si dispos,
        - Sinon, fallback: stabilisation du nombre de GIFs + timeout de sécurité.
        """
        target = self._target_dir()
        current_count = self._count_gifs(target)

        # Signaux "forts" (si dispo)
        strong_ready = self._is_all_ready(current_count)

        # Fallback stabilisation
        if current_count == self._last_poll_count:
            self._stable_ticks += 1
        else:
            self._stable_ticks = 0
        self._last_poll_count = current_count

        STABLE_TICKS_THRESHOLD = 6   # ~3s si intervalle=500ms
        TIMEOUT_TICKS = 120          # ~60s

        ready = strong_ready or (current_count > 0 and self._stable_ticks >= STABLE_TICKS_THRESHOLD)

        self._poll_loops += 1
        timeout = self._poll_loops >= TIMEOUT_TICKS
        if timeout and current_count > 0:
            ready = True  # sécurité: ne pas bloquer ad vitam si on a du contenu

        if ready:
            self._set_loading(False)       # réactive dropdown + bouton normal
            self.generateGif.grid_remove() # dataset prêt → bouton inutile (cache)

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
        """Configure le slider et affiche la première image (quand tout est prêt)."""
        target = self._target_dir()

        if nb_gif <= 0:
            self.ElevationSlider.grid_remove()
            if hasattr(self, "gif_widget"):
                try:
                    self.gif_widget.load("loading.gif", keep_position=False)
                except Exception:
                    pass
            return

        if nb_gif == 1:
            self.ElevationSlider.grid_remove()
            first_path = os.path.join(target, "1.0.gif")
            if hasattr(self, "gif_widget"):
                self._last_key = None
                self.gif_widget.load(first_path, keep_position=False)
            else:
                self._last_key = None
                self.gif_widget = self.GifPlayer(self.gifFrame, gif_path=first_path, delay=150, text="")
                self.gif_widget.grid(row=0, column=0, padx=5, pady=5)
            return

        # nb_gif > 1 → slider discret 1..N
        self.ElevationSlider.configure(from_=1, to=nb_gif, number_of_steps=nb_gif - 1)
        self.ElevationSlider.set(1)
        self._last_key = None
        self.ElevationSlider.grid()
        self.displayGif(None)

    def displayGif(self, _):
        if self.selected_file is None:
            return

        satellite = os.path.splitext(Path(self.selected_file).name)[0]
        var = self.variablesDropdown.get().split("/")[-1].strip()

        # clamp pour éviter 0 au 1er appel
        val = self.ElevationSlider.get()
        elevation = max(1, int(np.ceil(val)))

        # Empêche les reloads redondants (clé composite variable+élevation)
        key = (var, elevation)
        if self._last_key == key:
            return
        self._last_key = key

        if self.gif_generator is not None:
            try:
                self.gif_generator.setPreferedlevel(elevation)
            except Exception:
                pass

        gifPath = os.path.join(satellite, var, f"{elevation}.0.gif")
        if hasattr(self, "gif_widget"):
            self.gif_widget.load(gifPath, keep_position=True)
        else:
            self.gif_widget = self.GifPlayer(self.gifFrame, gif_path=gifPath, delay=150, text="")
            self.gif_widget.grid(row=0, column=0, padx=5, pady=5)

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
