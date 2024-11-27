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

        # App update button
        self.update_button = ctk.CTkButton(body_frame, text="Check for Updates", command=self.check_for_updates)
        self.update_button.pack(pady=(20, 10), anchor="w", padx=20)

        # Credentials frame
        credential_frame = ctk.CTkFrame(body_frame)
        credential_frame.pack(pady=(10, 5), padx=10, fill="x")

        # Credential label positioned above the entries
        credential_label = ctk.CTkLabel(credential_frame, text="Credentials:", font=("Arial", 12))
        credential_label.pack(pady=10, padx=10, anchor='w')

        # Username Entry
        self.username_entry_frame = ctk.CTkFrame(credential_frame)
        self.username_entry_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(self.username_entry_frame, text="Username").pack(side="left", anchor="w", padx=10)
        self.username_entry = ctk.CTkEntry(self.username_entry_frame, width=300)
        self.username_entry.pack(side="left", pady=5)

        # Password Entry (hidden, will be encrypted before saving)
        self.password_entry_frame = ctk.CTkFrame(credential_frame)
        self.password_entry_frame.pack(pady=(5, 15), padx=20,
                                       fill="x")  # Added more padding below the password entry frame
        ctk.CTkLabel(self.password_entry_frame, text="Password:").pack(side="left", anchor="w", padx=10)
        self.password_entry = ctk.CTkEntry(self.password_entry_frame, width=300, show="*")
        self.password_entry.pack(side="left", pady=5)

        # # Debugger Root Directory frame
        # debugger_frame = ctk.CTkFrame(body_frame)
        # debugger_frame.pack(pady=(10, 5), padx=10, fill="x")
        #
        # # Debugger Root Directory label
        # debugger_label = ctk.CTkLabel(debugger_frame, text="Debugger Root Directory:", font=("Arial", 12))
        # debugger_label.pack(pady=10, padx=10, anchor='w')
        #
        # # Debugger Root Directory Entry
        # self.debugger_root_entry_frame = ctk.CTkFrame(debugger_frame)
        # self.debugger_root_entry_frame.pack(pady=(5,15), padx=20, fill="x")
        # ctk.CTkLabel(self.debugger_root_entry_frame, text="Path").pack(side="left", anchor="w", padx=10)
        # self.debugger_root_entry = ctk.CTkEntry(self.debugger_root_entry_frame, width=300)
        # self.debugger_root_entry.pack(side="left", pady=5, anchor="w", expand=True)

        # Save button
        self.save_button = ctk.CTkButton(body_frame, text="Save Settings", command=self.save_all_settings)
        self.save_button.pack(pady=20)

        self.load_theme_mode()
        self.load_sidebar_position()
        self.load_credential_data()
        # self.load_debugger_directory()

    def load_credential_data(self):
        """Load the username and encrypted password from settings.json and decrypt the password."""
        if "username" in self.settings_manager.settings:
            self.username_entry.insert(0, self.settings_manager.settings["username"])
        if "password" in self.settings_manager.settings:
            if not self.key and not self.cipher_suite:
                self.key = load_or_generate_key()
                self.cipher_suite = Fernet(self.key)
            encrypted_password = self.settings_manager.settings["password"]
            decrypted_password = self.cipher_suite.decrypt(encrypted_password.encode()).decode()
            self.password_entry.insert(0, decrypted_password)

    def set_credential_data_settings(self):
        """Save the username and encrypted password to settings.json."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if password:
            if not self.key and not self.cipher_suite:
                self.key = load_or_generate_key()
                self.cipher_suite = Fernet(self.key)
            # Encrypt the password
            encrypted_password = self.cipher_suite.encrypt(password.encode()).decode()
            self.settings_manager.add_or_update("password",encrypted_password)
        else:
            if "password" in self.settings_manager.settings:
                self.settings_manager.delete("password")

        if username:
            self.settings_manager.add_or_update("username", username)
        else:
            if "username" in self.settings_manager.settings:
                self.settings_manager.delete("username")

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


    def check_for_updates(self):
        needs_update, latest_version = self.updater.check_for_updates()
        print(needs_update)
        if needs_update:
            user_response = messagebox.askyesno(
                "Update Available",
                f"A new version ({latest_version}) is available."
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

    # def load_debugger_directory(self):
    #     if "debugger_root_directory" in self.settings_manager.settings:
    #         self.debugger_root_entry.insert(0, self.settings_manager.get("debugger_root_directory"))
    #
    # def set_debugger_directory_settings(self):
    #     # Save the debugger root directory setting
    #     debugger_root = self.debugger_root_entry.get().strip()
    #     if debugger_root:
    #         self.settings_manager.add_or_update("debugger_root_directory", debugger_root)
    #     else:
    #         if "debugger_root_directory" in self.settings_manager.settings:
    #             self.settings_manager.delete("debugger_root_directory")

    def save_all_settings(self):
        # self.set_debugger_directory_settings()
        self.set_credential_data_settings()
        self.settings_manager.save_settings()

        # Confirmation message
        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully.")