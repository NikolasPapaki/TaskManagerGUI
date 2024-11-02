import customtkinter as ctk
import inspect
from Frames import *  # Import all frames from the frames package
import re

def button_formating(text):
    """Add spaces before uppercase letters in camel case strings."""
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text.replace('Frame', ''))

class ApplicationInterface:
    def __init__(self, parent):
        self.parent = parent

        # Set a specific width for the sidebar (e.g., 250 pixels)
        self.sidebar_width = 250

        # Create the sidebar frame with the specified width
        self.sidebar = ctk.CTkFrame(self.parent, width=self.sidebar_width)
        self.sidebar.pack(side=ctk.LEFT, fill=ctk.Y)

        # Create the main content area to take the remaining space
        self.content_area = ctk.CTkFrame(self.parent)
        self.content_area.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)

        # Set the sidebar's minimum and maximum width to prevent resizing
        self.sidebar.pack_propagate(False)  # Prevent the frame from resizing to fit its contents

        # Create buttons for the sidebar in a custom order
        self.create_sidebar_buttons()

        # Initialize the first frame
        self.current_frame = None
        self.show_frame(HomeFrame)

    def create_sidebar_buttons(self):
        # Create a list to hold the button details
        buttons = []

        # Retrieve all classes from the frames module
        for name, obj in inspect.getmembers(inspect.getmodule(inspect.currentframe())):
            if inspect.isclass(obj) and issubclass(obj, ctk.CTkFrame):
                buttons.append((name, obj))

        # Sort the buttons based on the ORDER constant
        buttons.sort(key=lambda x: getattr(x[1], 'ORDER', float('inf')))  # Use ORDER attribute for sorting

        # Create buttons based on the sorted list
        for (text, frame_class) in buttons:
            button = ctk.CTkButton(self.sidebar, text=button_formating(text), command=lambda f=frame_class: self.show_frame(f))
            button.pack(pady=5, padx=10, fill=ctk.X)

    def show_frame(self, frame_class):
        # Destroy the current frame if it exists
        if self.current_frame is not None:
            self.current_frame.destroy()

        # Create a new frame and display it
        self.current_frame = frame_class(self.content_area)
        self.current_frame.pack(fill=ctk.BOTH, expand=True)


