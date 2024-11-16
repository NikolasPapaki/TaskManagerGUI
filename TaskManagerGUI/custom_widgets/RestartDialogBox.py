import customtkinter as ctk
import tkinter as tk

class RestartMessageDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Restart Required", message="", width=450, height=200):
        super().__init__(parent)
        self.title(title)

        # Set the dialog size
        self.geometry(f"{width}x{height}")

        # Center the dialog on the parent window
        self.center_dialog(parent, width, height)

        # Create the message label
        self.message_label = ctk.CTkLabel(self, text=message, font=("Arial", 12), justify="center")
        self.message_label.pack(pady=20, padx=20)

        # Create buttons for "Restart Now" and "Restart Later"
        # Use fg_color instead of bg_color
        self.button_frame = ctk.CTkFrame(self, fg_color=self.cget("fg_color"))  # Match the parent fg_color
        self.button_frame.pack(pady=(10, 20))

        # Make sure the button frame background color matches the dialog background
        self.button_frame.configure(fg_color=self.cget("fg_color"))  # Set the frame's background color

        self.restart_button = ctk.CTkButton(self.button_frame, text="Restart Now", command=self.on_restart)
        self.restart_button.pack(side="left", padx=10)

        self.later_button = ctk.CTkButton(self.button_frame, text="Restart Later", command=self.on_later)
        self.later_button.pack(side="left", padx=10)

        # To capture the result of the dialog
        self.result = None

        # Close dialog when the window's close button is clicked
        self.protocol("WM_DELETE_WINDOW", self.on_later)

        # Make sure the dialog is always on top
        self.attributes("-topmost", True)
        self.grab_set()  # Make the window modal (blocks interaction with parent window)

    def center_dialog(self, parent, width, height):
        """Center the dialog on the parent window or screen."""
        if parent:
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()
            x = parent_x + (parent_width - width) // 2
            y = parent_y + (parent_height - height) // 2
        else:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
        self.geometry(f"+{x}+{y}")

    def on_restart(self):
        """Handle Restart Now button click."""
        self.result = "restart_now"
        self.destroy()  # Close the dialog

    def on_later(self):
        """Handle Restart Later button click."""
        self.result = "restart_later"
        self.destroy()  # Close the dialog

    def show(self):
        """Show the dialog and wait for user input."""
        self.wait_window()  # Block until the dialog is closed
        return self.result
