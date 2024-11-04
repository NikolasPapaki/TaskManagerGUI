import customtkinter as ctk

class CustomInputDialog(ctk.CTkToplevel):
    def __init__(self, title,initial_value, width=450, height=150, parent=None):
        super().__init__(parent)
        self.title(title)

        # Set the dialog size
        self.geometry(f"{width}x{height}")

        # Create an entry for user input with the initial value
        self.input_entry = ctk.CTkEntry(self)
        self.input_entry.insert(0, initial_value)  # Set initial value
        self.input_entry.pack(pady=10, padx=10, fill=ctk.X)

        # Create OK and Cancel buttons
        self.ok_button = ctk.CTkButton(self, text="OK", command=self.on_ok)
        self.ok_button.pack(side='left', padx=(10, 5), pady=10)

        self.cancel_button = ctk.CTkButton(self, text="Cancel", command=self.on_cancel)
        self.cancel_button.pack(side='right', padx=(5, 10), pady=10)

        self.result = None
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)  # Handle window close

    def on_ok(self):
        """Handle OK button click."""
        self.result = self.input_entry.get()
        self.destroy()  # Close the dialog

    def on_cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.destroy()  # Close the dialog

    def show(self):
        """Show the dialog and wait for user input."""
        self.wait_window()  # Block until the dialog is closed
        return self.result