# colorbar_gui_editable.py
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import simpledialog,Button,filedialog,messagebox

# palette fournie
def palette(t: float, a: np.ndarray, b: np.ndarray, c: np.ndarray, d: np.ndarray):
    return a + b * np.cos(2 * np.pi * (c * t + d))

def make_colorbar_image(a, b, c, d, width=256, height=60):
    ts = np.linspace(0.0, 1.0, 256, dtype=np.float32)
    cols = palette(ts[:, None], a[None, :], b[None, :], c[None, :], d[None, :])
    cols = np.clip(cols, 0.0, 1.0)
    cols255 = (cols * 255).astype(np.uint8)
    img_row = np.repeat(cols255, repeats=width // 256 + 1, axis=0)[:width]
    img = np.tile(img_row[None, :, :], (height, 1, 1))
    return Image.fromarray(img, mode="RGB")

class ColorbarGUI:
    def __init__(self, master):
        self.master = master
        master.title("Interactive palette")

        # NOUVEAUX DEFAULTS demandés
        self.a = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.b = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.c = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.d = np.array([0.0, 0.33, 0.67], dtype=np.float32)

        # zone image
        self.canvas = tk.Canvas(master, width=512, height=60, bd=0, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=12, padx=10, pady=10)
        self.photo = None
        self.image_id = None

        self.scales = {}
        self.value_labels = {}
        labels = ["R", "G", "B"]

        # configuration pour chaque vecteur
        vecs = [
            ("a", 0.0, 1.0, self.a),
            ("b", 0.0, 1.0, self.b),
            ("c", 0.0, 3.0, self.c),  # c a une plage plus grande
            ("d", 0.0, 1.5, self.d),
        ]

        # construction des sliders et labels
        for idx, (vecname, vmin, vmax, init) in enumerate(vecs):
            col = idx * 3
            tk.Label(master, text=vecname, font=("Arial", 10, "bold")).grid(row=1, column=col, columnspan=3)
            for i in range(3):
                s = tk.Scale(master, from_=vmax, to=vmin, resolution=0.01, orient=tk.VERTICAL,
                             length=200, showvalue=False, command=self._on_slider)
                s.set(float(init[i]))
                s.grid(row=2, column=col + i, padx=4, pady=2)
                self.scales[(vecname, i)] = s
                tk.Label(master, text=labels[i]).grid(row=3, column=col + i)

                # label pour afficher la valeur (editable en double-cliquer)
                val_label = tk.Label(master, text=f"{s.get():.3f}", width=7, relief="ridge")
                val_label.grid(row=4, column=col + i, pady=(2,6))
                # bind double-click to edit
                val_label.bind("<Double-Button-1>", lambda e, vn=vecname, jj=i, vmin=vmin, vmax=vmax: self._on_value_doubleclick(vn, jj, vmin, vmax))
                self.value_labels[(vecname, i)] = val_label

        # bouton reset / save
        btn_frame = tk.Frame(master)
        btn_frame.grid(row=6, column=0, columnspan=12, pady=(8,0))

        tk.Button(btn_frame, text="Reset valeurs",
                command=self.reset_values).pack(side=tk.LEFT, padx=6)

        tk.Button(btn_frame, text="Sauver image",
                command=self.save_image).pack(side=tk.LEFT, padx=6)

        tk.Button(btn_frame, text="Sauvegarder a,b,c,d",
                command=lambda: self.save_abcd(self.a, self.b, self.c, self.d)
                ).pack(side=tk.LEFT, padx=6)


        # initial image
        self.update_image()
        self._after_id = None

    def _on_slider(self, _=None):
        if self._after_id:
            self.master.after_cancel(self._after_id)
        self._after_id = self.master.after(50, self.update_image)

    def _on_value_doubleclick(self, vecname, i, vmin, vmax):
        # valeur courante
        cur = self.scales[(vecname, i)].get()
        prompt = f"Entrer une valeur pour {vecname}[{i}] (min {vmin}, max {vmax}) :"
        # askfloat retourne None si cancel
        val = simpledialog.askfloat("Modifier valeur", prompt, initialvalue=float(cur),
                                    minvalue=vmin, maxvalue=vmax, parent=self.master)
        if val is None:
            return
        # appliquer à l'échelle et mettre à jour
        self.scales[(vecname, i)].set(val)
        self.update_image()

    def read_values(self):
        a = np.array([self.scales[("a", i)].get() for i in range(3)], dtype=np.float32)
        b = np.array([self.scales[("b", i)].get() for i in range(3)], dtype=np.float32)
        c = np.array([self.scales[("c", i)].get() for i in range(3)], dtype=np.float32)
        d = np.array([self.scales[("d", i)].get() for i in range(3)], dtype=np.float32)
        return a, b, c, d

    def update_value_labels(self):
        for key, lbl in self.value_labels.items():
            val = self.scales[key].get()
            lbl.config(text=f"{val:.3f}")

    def update_image(self):
        a, b, c, d = self.read_values()
        img = make_colorbar_image(a, b, c, d, width=512, height=60)
        self.photo = ImageTk.PhotoImage(img)
        if self.image_id is None:
            self.image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        else:
            self.canvas.itemconfig(self.image_id, image=self.photo)
        self.update_value_labels()
        self._after_id = None

    def reset_values(self):
        defaults = {
            ("a", 0): 0.5, ("a", 1): 0.5, ("a", 2): 0.5,
            ("b", 0): 0.5, ("b", 1): 0.5, ("b", 2): 0.5,
            ("c", 0): 1.0, ("c", 1): 1.0, ("c", 2): 1.0,
            ("d", 0): 0.0, ("d", 1): 0.33, ("d", 2): 0.67,
        }
        for key, val in defaults.items():
            self.scales[key].set(val)
        self.update_image()

    def save_image(self):
        a, b, c, d = self.read_values()
        img = make_colorbar_image(a, b, c, d, width=2048, height=120)
        fname = "colorbar_saved.png"
        img.save(fname)
        print(f"Saved {fname}")
        
    def save_abcd(a, b, c, d, _):
        """Sauvegarde les tableaux a,b,c,d dans un fichier .txt"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Sauvegarder a,b,c,d"
        )
        if not file_path:
            return  # utilisateur a annulé
        
        print(a)
        print(b)
        print(c)
        print(d)

        text = (
            f"a = np.array([{a[0][0]:.2f}, {a[0][1]:.2f}, {a[0][2]:.2f}])\n"
            f"b = np.array([{b[0]:.2f}, {b[1]:.2f}, {b[2]:.2f}])\n"
            f"c = np.array([{c[0]:.2f}, {c[1]:.2f}, {c[2]:.2f}])\n"
            f"d = np.array([{d[0]:.2f}, {d[1]:.2f}, {d[2]:.2f}])\n"
        )

        with open(file_path, "w") as f:
            f.write(text)

        messagebox.showinfo("Sauvegarde", f"Paramètres enregistrés dans :\n{file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorbarGUI(root)
    root.mainloop()
