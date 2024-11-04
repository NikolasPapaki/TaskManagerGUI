import customtkinter as ctk
from Interface import ApplicationInterface

class MyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set theme and mode
        ctk.set_default_color_theme("blue")


        self.title("Task Manager")
        self.geometry("1200x1000")

        # Create an instance of ApplicationInterface
        self.sidebar = ApplicationInterface(self)
# Run the application
if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
