import customtkinter as ctk

class App():
    def __init__(self,root):
        self.main_root = root
        self.main_root.bind('<Escape>', lambda e: self._escape())
        
        w = self.main_root.winfo_screenwidth()
        h = self.main_root.winfo_screenheight()
        self.main_root.geometry(f"{w}x{h}")
        self.main_root.after(0, lambda: self.main_root.state("zoomed"))
        self.initWidget()
        self.main_root.mainloop()

    def initWidget(self):
        self.paramsFrame = ctk.CTkFrame(self.main_root, corner_radius=10, border_width=1, border_color="grey")
        self.paramsFrame.grid(row=0,column=0,padx=5,pady=5)
        self.gifFrame = ctk.CTkFrame(self.main_root, corner_radius=10, border_width=1, border_color="grey")
        self.gifFrame.grid(row =0,column =1,padx=5,pady=5)

        self.variablesDropdown = ctk.CTkOptionMenu(self.paramsFrame, values=["test"])
        self.variablesDropdown.grid(row=0,column=0,sticky= "nw")

    def getValues(self):
        pass 


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = App(root)