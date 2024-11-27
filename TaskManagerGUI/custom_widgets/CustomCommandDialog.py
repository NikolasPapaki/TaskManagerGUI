import customtkinter as ctk
import tkinter as tk  # Ensure tk is imported if needed for focus handling

class CustomCommandDialog(ctk.CTkToplevel):
    def __init__(self, title, parent, fields, default_values=None):
        super().__init__(parent)
        # Set the title of the dialog
        self.title(title)
        self.entries = {}
        self.result = None

        if default_values is None:
            default_values = ['' for _ in fields]

        # Calculate the position of the dialog to center it in the parent window
        dialog_width = 350  # Set the desired width of the dialog
        dialog_height = 200  # Set the desired height of the dialog
        # Set the dialog size
        self.geometry(f"{dialog_width}x{dialog_height}")

        # Center the dialog on the parent window
        self.center_dialog(parent, dialog_width, dialog_height)

        # Create labels and entry widgets for each field using customtkinter
        for idx, (field, default_value) in enumerate(zip(fields, default_values)):
            label = ctk.CTkLabel(self, text=field)
            label.grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            entry = ctk.CTkEntry(self, width=250)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entry.insert(0, default_value)
            self.entries[field] = entry

        # Create a frame for the buttons
        button_frame = ctk.CTkFrame(self, fg_color=self.cget('bg'))  # Set background color to parent window's bg
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        # Add OK and Cancel buttons with spacing between them
        ok_button = ctk.CTkButton(button_frame, text="OK", command=self._on_ok)
        ok_button.pack(side=ctk.LEFT, padx=10)  # Add horizontal spacing
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self._on_cancel)
        cancel_button.pack(side=ctk.LEFT, padx=10)  # Add horizontal spacing

        # Make the dialog window modal and wait for a response
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
