import customtkinter as ctk

class HomeFrame(ctk.CTkFrame):
    ORDER = 1
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        label = ctk.CTkLabel(self, text="Welcome to my Application", font=("Arial", 24))
        label.pack(pady=20)

