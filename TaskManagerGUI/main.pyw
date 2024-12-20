import customtkinter as ctk
from Interface import ApplicationInterface
from tkinterdnd2 import TkinterDnD, DND_FILES

class MyApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        # Set theme and mode
        ctk.set_default_color_theme("dark-blue")

        self.title("Core Dev Dashboard")
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry("%dx%d" % (width/2, height/2))
        self.lift()

        # Create an instance of ApplicationInterface
        self.sidebar = ApplicationInterface(self)


# Run the application
if __name__ == "__main__":
    app = MyApp()
    app.mainloop()

