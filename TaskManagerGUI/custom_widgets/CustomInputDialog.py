import customtkinter as ctk
import tkinter as tk  # Ensure tk is imported if needed for focus handling



class CustomInputDialog(ctk.CTkToplevel):
    def __init__(self, title, parent, fields, default_values=None):
        super().__init__(parent)

        # Set the title of the dialog
        self.title(title)
        self.entries = {}
        self.result = None

        if default_values is None:
            default_values = ['' for _ in fields]

        # Calculate dynamic dimensions
        min_width = 450
        padding = 20  # Additional width padding
        max_field_length = max(len(field) for field in fields) if fields else 0
        dialog_width = max(min_width, max_field_length * 10 + padding)  # Approx. 10px per character + padding
        dialog_height = len(fields) * 40 + 80  # 40px per field row + 80px for buttons and padding

        # Set the dialog size
        self.geometry(f"{dialog_width}x{dialog_height}")

        # Center the dialog on the parent window
        self.center_dialog(parent, dialog_width, dialog_height)

        # Configure grid layout for responsive resizing
        self.columnconfigure(0, weight=1)  # For labels
        self.columnconfigure(1, weight=3)  # For entry widgets

        # Create labels and entry widgets for each field using customtkinter
        for idx, (field, default_value) in enumerate(zip(fields, default_values)):
            label = ctk.CTkLabel(self, text=field)
            label.grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            entry = ctk.CTkEntry(self)
            entry.grid(row=idx, column=1, padx=10, pady=5, sticky="ew")  # Expand horizontally
            entry.insert(0, default_value)
            self.entries[field] = entry

        # Create a frame for the buttons
        button_frame = ctk.CTkFrame(self, fg_color=self.cget('bg'))  # Set background color to parent window's bg
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10, sticky="ew")

        # Add OK and Cancel buttons with spacing between them
        ok_button = ctk.CTkButton(button_frame, text="OK", command=self._on_ok)
        ok_button.pack(side=ctk.LEFT, padx=10)  # Add horizontal spacing
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self._on_cancel)
        cancel_button.pack(side=ctk.RIGHT, padx=10)  # Add horizontal spacing

        # Make the dialog window modal and wait for a response
        self.lift()
        self.transient(parent)
        self.grab_set()
        self.wait_window()


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

    def _on_ok(self):
        # Collect all field values
        self.result = [entry.get().strip() for entry in self.entries.values()]
        self.destroy()

    def _on_cancel(self):
        self.destroy()

    def show(self):
        return self.result
