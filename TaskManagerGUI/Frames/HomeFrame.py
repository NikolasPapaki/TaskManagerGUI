import customtkinter as ctk

class HomeFrame(ctk.CTkFrame):
    ORDER = 1
    def __init__(self, parent, main_window):
        super().__init__(parent)

        self.parent = parent

        label = ctk.CTkLabel(self, text="Welcome to Core Dev Dashboard", font=("Arial", 24))
        label.pack(pady=20)
