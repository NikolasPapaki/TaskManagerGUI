import customtkinter as ctk
from tkinter import messagebox
import json
import os
from cryptography.fernet import Fernet
from Update_module import *  # Assuming this import is already correct for your updater module

class SettingsFrame(ctk.CTkFrame):
    ORDER = 98

    def __init__(self, parent):
        super().__init__(parent)
        self.updater = Update_module()

        self.settings = self.load_settings()

        # Generate or load the encryption key (this key should be kept secret or stored securely)
        self.key = self.load_or_generate_key()
        self.cipher_suite = Fernet(self.key)

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
        self.theme_switch = ctk.CTkSwitch(body_frame, text="Dark Mode", command=self.change_color_mode)
        self.theme_switch.pack(pady=10, anchor="w", padx=20)

        # Credentials frame
        credential_frame = ctk.CTkFrame(body_frame)
        credential_frame.pack(pady=(10, 5), padx=10, fill="x")

        # Credential label positioned above the entries
        credential_label = ctk.CTkLabel(credential_frame, text="Credentials:", font=("Arial", 12))
        credential_label.pack(pady=10, padx=10, side="top", anchor='w', fill='x')

        # Username Entry
        self.username_entry_frame = ctk.CTkFrame(credential_frame)
        self.username_entry_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(self.username_entry_frame, text="Username").pack(side="left", anchor="w", padx=10)
        self.username_entry = ctk.CTkEntry(self.username_entry_frame, width=300)
        self.username_entry.pack(side="left", pady=5)

        # Password Entry (hidden, will be encrypted before saving)
        self.password_entry_frame = ctk.CTkFrame(credential_frame)
        self.password_entry_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(self.password_entry_frame, text="Password:").pack(side="left", anchor="w", padx=10)
        self.password_entry = ctk.CTkEntry(self.password_entry_frame, width=300, show="*")
        self.password_entry.pack(side="left", pady=5)

        # Save button
        self.save_button = ctk.CTkButton(body_frame, text="Save Settings", command=self.save_credential_data)
        self.save_button.pack(pady=20)

        # Load settings and set current theme
        settings = self.load_settings()
        current_theme = settings.get("theme", "dark")  # Default to "dark" if no theme is found
        ctk.set_appearance_mode(current_theme)
        self.theme_switch.select() if current_theme.lower() == "dark" else self.theme_switch.deselect()

        # Retrieve saved credentials if any
        self.load_credential_data()

    def load_or_generate_key(self):
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

    def save_credential_data(self):
        """Save the username and encrypted password to settings.json."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Encrypt the password
        encrypted_password = self.cipher_suite.encrypt(password.encode()).decode()

        # If username or password is in the entryboxes save it to the settings.json else
        if password:
            self.settings["password"] =encrypted_password
        else:
            if "password" in self.settings:
                del self.settings["password"]

        if username:
            self.settings["username"] = username
        else:
            if "username" in self.settings:
                del self.settings["username"]

        self.save_settings()

        # Confirmation message
        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully.")

    def save_settings(self):
        with open("settings.json", "w") as file:
            json.dump(self.settings, file, indent=4)

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as file:
                return json.load(file)
        return {}

    def load_credential_data(self):
        """Load the username and encrypted password from settings.json and decrypt the password."""
        settings = self.settings
        if "username" in settings:
            self.username_entry.insert(0, settings["username"])
        if "password" in settings:
            encrypted_password = settings["password"]
            decrypted_password = self.cipher_suite.decrypt(encrypted_password.encode()).decode()
            self.password_entry.insert(0, decrypted_password)

    def change_color_mode(self):
        new_theme = "dark" if self.theme_switch.get() else "light"
        ctk.set_appearance_mode(new_theme)
        self.settings["theme"] = new_theme
        self.save_settings()

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
