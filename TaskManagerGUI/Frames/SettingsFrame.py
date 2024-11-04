import customtkinter as ctk
from tkinter import messagebox
import json
import os
from Update_module import *

class SettingsFrame(ctk.CTkFrame):
    ORDER = 98

    def __init__(self, parent):
        super().__init__(parent)
        self.updater = Update_module()

        # Title frame
        title_frame = ctk.CTkFrame(self)
        title_frame.pack(pady=(10, 5), padx=10, fill="x")

        # Title label
        label = ctk.CTkLabel(title_frame, text="Settings", font=("Arial", 24))
        label.pack(pady=20)

        # Body frame
        body_frame = ctk.CTkFrame(self)
        body_frame.pack(pady=(10, 5), padx=10, fill="x")

        # Theme toggle (Light/Dark mode)
        self.theme_switch = ctk.CTkSwitch(body_frame, text="Dark Mode", command=self.change_color_mode)
        self.theme_switch.pack(pady=10, anchor="w", padx=20)

        # Load settings and set current theme
        settings = self.load_settings()
        current_theme = settings.get("theme", "dark")  # Default to "dark" if no theme is found
        ctk.set_appearance_mode(current_theme)
        self.theme_switch.select() if current_theme.lower() == "dark" else self.theme_switch.deselect()

    def change_color_mode(self):
        new_theme = "dark" if self.theme_switch.get() else "light"
        ctk.set_appearance_mode(new_theme)
        self.save_settings("theme", new_theme)

    def save_settings(self, key, value):
        """Save or update a specific setting in the JSON file."""
        settings = self.load_settings()  # Load existing settings
        settings[key] = value  # Update the specific setting

        with open("settings.json", "w") as file:
            json.dump(settings, file, indent=4)

    def load_settings(self):
        """Load settings from the JSON file, or return an empty dictionary if the file does not exist."""
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as file:
                return json.load(file)
        return {}

    def check_for_updates(self):
        needs_update, latest_version = self.updater.check_for_updates()

        if needs_update:
            user_response = messagebox.askyesno(
                "Update Available",
                f"A new version ({latest_version}) is available. Would you like to download the update?"
            )
            if user_response:
                self.download_update()
        else:
            messagebox.showinfo("Up to Date", "Your application is already up to date.")

    def download_update(self):
        try:
            self.updater.update_application()
        except Exception as e:
            messagebox.showerror("Error!", "Error checking for updates.")
            print(f"Error: {e}")

    def reset_settings(self):
        print("Settings have been reset to defaults.")
        self.theme_switch.deselect()
        self.save_settings("theme", "light")
