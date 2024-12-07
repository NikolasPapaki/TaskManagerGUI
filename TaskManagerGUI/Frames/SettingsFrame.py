import customtkinter as ctk
from tkinter import messagebox
import json
from cryptography.fernet import Fernet
from Update_module.Update_module import *
from custom_widgets import RestartMessageDialog
from SharedObjects import Settings

def load_or_generate_key():
    """Load the encryption key from a file or generate a new one if not found."""
    key_file = ".secret.key"
    if os.path.exists(key_file):
        with open(key_file, "rb") as file:
            return file.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as file:
            file.write(key)
        return key


class SettingsFrame(ctk.CTkFrame):
    ORDER = 98

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.updater = Update_module()
        self.settings_manager = Settings()

        self.parent = parent

        self.key = None
        self.cipher_suite = None
        # Title frame
        title_frame = ctk.CTkFrame(self)
        title_frame.pack(pady=(10, 5), padx=10, fill="x")

        # Title label
        title_label = ctk.CTkLabel(title_frame, text="Settings", font=("Arial", 24))
        title_label.pack(pady=20)

        # Body frame
        body_frame = ctk.CTkFrame(self)
        body_frame.pack(pady=(10, 5), padx=10, fill="x")

        # Theme toggle (Light/Dark mode)
        self.theme_switch = ctk.CTkSwitch(body_frame, text="Dark Mode", command=self.change_theme_mode)
        self.theme_switch.pack(pady=10, anchor="w", padx=20)

        self.sidebar_position_switch = ctk.CTkSwitch(
            body_frame,
            text="Sidebar on Right",
            command=self.change_sidebar_position
        )
        self.sidebar_position_switch.pack(pady=10, anchor="w", padx=20)

        # Healthchecks frame
        healthcheck_frame = ctk.CTkFrame(body_frame)
        healthcheck_frame.pack(pady=(10, 5), padx=10, fill="x")

        # Healthcheck label positioned above the entries
        healthcheck_label = ctk.CTkLabel(healthcheck_frame, text="Health Check Information:", font=("Arial", 12))
        healthcheck_label.pack(pady=10, padx=10, anchor='w')

        # URL Entry
        self.url_entry_frame = ctk.CTkFrame(healthcheck_frame)
        self.url_entry_frame.pack(pady=5, padx=20, fill="x")
        url_label = ctk.CTkLabel(self.url_entry_frame, text="URL:", anchor="w", width=60)
        url_label.grid(row=0, column=0, sticky="w", padx=10)
        self.url_entry = ctk.CTkEntry(self.url_entry_frame, width=300)
        self.url_entry.grid(row=0, column=1, pady=5, sticky="w")

        # Secret Id Entry
        self.secret_id_entry_frame = ctk.CTkFrame(healthcheck_frame)
        self.secret_id_entry_frame.pack(pady=5, padx=20, fill="x")
        secret_id_label = ctk.CTkLabel(self.secret_id_entry_frame, text="Secret Id:", anchor="w", width=60)
        secret_id_label.grid(row=0, column=0, sticky="w", padx=10)
        self.secret_id_entry = ctk.CTkEntry(self.secret_id_entry_frame, width=300)
        self.secret_id_entry.grid(row=0, column=1, pady=5, sticky="w")

        # Role Id Entry
        self.role_id_entry_frame = ctk.CTkFrame(healthcheck_frame)
        self.role_id_entry_frame.pack(pady=(5, 15), padx=20, fill="x")
        role_id_label = ctk.CTkLabel(self.role_id_entry_frame, text="Role Id:", anchor="w", width=60)
        role_id_label.grid(row=0, column=0, sticky="w", padx=10)
        self.role_id_entry = ctk.CTkEntry(self.role_id_entry_frame, width=300)
        self.role_id_entry.grid(row=0, column=1, pady=5, sticky="w")

        # Save button
        self.save_button = ctk.CTkButton(body_frame, text="Save Settings", command=self.save_all_settings)
        self.save_button.pack(pady=20)

        self.load_theme_mode()
        self.load_sidebar_position()
        self.load_healthcheck_data()
        # self.load_debugger_directory()

    def load_healthcheck_data(self):
        """Load the username and encrypted password from settings.json and decrypt the password."""
        if "vault_url" in self.settings_manager.settings:
            self.url_entry.insert(0, self.settings_manager.settings["vault_url"])

        if "role_id" in self.settings_manager.settings:
            self.role_id_entry.insert(0, self.settings_manager.settings["role_id"])

        if "secret_id" in self.settings_manager.settings:
            self.secret_id_entry.insert(0, self.settings_manager.settings["secret_id"])


    def set_healthcheck_data_settings(self):
        """Save the username and encrypted password to settings.json."""
        url = self.url_entry.get().strip()
        secret_id = self.secret_id_entry.get().strip()
        role_id = self.role_id_entry.get().strip()

        if url:
            self.settings_manager.add_or_update("vault_url", url)
        elif "vault_url" in self.settings_manager.settings:
                self.settings_manager.delete("vault_url")

        if secret_id:
            self.settings_manager.add_or_update("secret_id", secret_id)
        elif "secret_id" in self.settings_manager.settings:
            self.settings_manager.delete("secret_id")

        if role_id:
            self.settings_manager.add_or_update("role_id", role_id)
        elif "role_id" in self.settings_manager.settings:
            self.settings_manager.delete("role_id")

    def load_theme_mode(self):
        # Load settings and set current theme
        current_theme = self.settings_manager.get("theme", "dark")  # Default to "dark" if no theme is found
        ctk.set_appearance_mode(current_theme)
        self.theme_switch.select() if current_theme.lower() == "dark" else self.theme_switch.deselect()


    def change_theme_mode(self):
        new_theme = "dark" if self.theme_switch.get() else "light"
        ctk.set_appearance_mode(new_theme)
        self.settings_manager.add_or_update("theme", new_theme)


    def load_sidebar_position(self):
        """Load sidebar position from settings."""
        sidebar_position = self.settings_manager.get("sidebar_side", "left")  # Default to "left"
        if sidebar_position == "right":
            self.sidebar_position_switch.select()
        else:
            self.sidebar_position_switch.deselect()

    def change_sidebar_position(self):
        """Change sidebar position and save to settings."""
        sidebar_position = "right" if self.sidebar_position_switch.get() else "left"
        self.settings_manager.add_or_update("sidebar_side", sidebar_position)

        # Create and show the custom restart message dialog
        restart_dialog = RestartMessageDialog(
            self.parent,
            message="The sidebar position has been updated.\n Restart the application for the changes to take effect.\n\nWould you like to restart now?"
        )
        user_response = restart_dialog.show()

        if user_response == "restart_now":
            restart_application_executable()  # Restart the application


    def save_all_settings(self):
        # self.set_debugger_directory_settings()
        self.set_healthcheck_data_settings()
        self.settings_manager.save_settings()

        # Confirmation message
        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully.")