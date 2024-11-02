import customtkinter as ctk
from tkinter import messagebox
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
        current_theme = ctk.get_appearance_mode()
        self.theme_switch.select() if current_theme.lower() == "dark" else self.theme_switch.deselect()

        # # App update button
        # self.update_button = ctk.CTkButton(body_frame, text="Check for Updates", command=self.check_for_updates)
        # self.update_button.pack(pady=(20, 10), anchor="w", padx=20)


    def change_color_mode(self):
        new_theme = "dark" if self.theme_switch.get() else "light"
        ctk.set_appearance_mode(new_theme)

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
        ctk.set_appearance_mode("light")
        self.theme_switch.deselect()
