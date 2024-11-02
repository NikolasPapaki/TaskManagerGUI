import customtkinter as ctk
from custom_widgets import ApplicationInterface  # Adjust the import as per your structure

class MyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set theme and mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")


        self.title("My Application")
        self.geometry("1200x1000")

        # Create an instance of CustomSidebar
        self.sidebar = ApplicationInterface(self)
# Run the application
if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
