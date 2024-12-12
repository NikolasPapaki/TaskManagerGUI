import customtkinter as ctk
from Interface import ApplicationInterface
from tkinterdnd2 import TkinterDnD, DND_FILES

class MyApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        # Set theme and mode
        ctk.set_default_color_theme("dark-blue")

        self.title("Prime Core Dashboard")
        self.geometry("1280x720")

        # Create an instance of ApplicationInterface
        self.sidebar = ApplicationInterface(self)


# Run the application
if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
