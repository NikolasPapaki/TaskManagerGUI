import threading
import time

import customtkinter as ctk
import json
from custom_widgets import CustomInputDialog
from SharedObjects import *
import requests
from tkinter import messagebox
from cryptography.fernet import Fernet
import os
import re
import tkinter as tk

def _pad_names(names, max_length):
    return [name.ljust(max_length) for name in names]


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

#
# def create_right_click_menu(tabview):
#     def on_right_click(event):
#         # Identify the tab that was right-clicked
#         clicked_tab = tabview.winfo_containing(event.x_root, event.y_root)
#         if clicked_tab:
#             menu = tk.Menu(tabview, tearoff=0)
#             menu.add_command(label="Close Tab", command=lambda: close_tab(tabview, clicked_tab))
#             menu.post(event.x_root, event.y_root)
#
#     # Get the underlying tkinter widget from the customtkinter Tabview widget
#     tkinter_tabview = tabview.winfo_toplevel()
#
#     tkinter_tabview.bind("<Button-3>", on_right_click)  # Bind right-click (Button-3) to the tabview
#
# def close_tab(tabview, tab):
#     """Close the given tab."""
#     tabview.delete(tab)  # Use the tabview's delete method

class PasswordRetrieverFrame(ctk.CTkFrame):
    ORDER = 4

    def __init__(self, parent, main_window):
        super().__init__(parent)

        self.parent = parent
        self.environment_manager = Environments(parent=self)
        self.settings_manager = Settings()
        self.credential_manager = EnvironmentCredentials()

        self.users = []
        self.client_token = None
        self.key = load_or_generate_key()
        self.cipher_suite = Fernet(self.key)

        # Frame title
        title_label = ctk.CTkLabel(self, text="Password Retriever", font=("Arial", 24))
        title_label.pack(pady=10)

        self.combobox_width = 350
        # Pad environment options for consistent dropdown width
        self.environments = _pad_names(
            self.environment_manager.get_all_rds(),
            int(self.combobox_width // 4.3)
        )

        # Create an environment frame
        self.environment_frame = ctk.CTkFrame(self, fg_color=self.cget("fg_color"))
        self.environment_frame.pack(pady=20, padx=20, fill="x", expand=False)

        # Add a label above the combobox
        self.environment_label = ctk.CTkLabel(
            self.environment_frame,
            text="Select RDS Environment:",
            font=("Arial", 14)
        )
        self.environment_label.pack(pady=(10, 5), padx=10)

        # Create and configure the combobox inside the environment frame
        self.environment_combobox = ctk.CTkComboBox(
            master=self.environment_frame,
            values=self.environments,
            width=self.combobox_width,
            state="readonly"
        )
        if self.environments:
            self.environment_combobox.set(self.environments[0])
        self.environment_combobox.pack(pady=10, padx=10)

        # Frame for buttons
        self.button_frame = ctk.CTkFrame(self, fg_color=self.cget("fg_color"))
        self.button_frame.pack(fill="x", pady=5, padx=10, anchor="w")

        # Buttons (next to each other)
        self.app_users_button = ctk.CTkButton(self.button_frame, text="App Users", command=lambda: self.get_app_users_password())
        self.app_users_button.pack(side="left", padx=5)

        self.admin_users_button = ctk.CTkButton(self.button_frame, text="Admin Users", command=lambda: self.get_admin_users_password())
        self.admin_users_button.pack(side="left", padx=5)

        self.specific_user_button = ctk.CTkButton(self.button_frame, text="Specific User", command=lambda: self.get_specific_user_password())
        self.specific_user_button.pack(side="left", padx=5)

        # Create a Tabview on the right side of the result_textbox for service selection
        self.tabview_frame = ctk.CTkFrame(self, fg_color=self.cget("fg_color"))
        self.tabview_frame.pack(fill='both', expand=True)

        # Create a CTkTabview inside the tabview_frame
        self.tabview = ctk.CTkTabview(self.tabview_frame)
        self.tabview.pack(padx=5, pady=5, expand=True, fill="both")

    def load_json_file(self, filepath):
        """Load JSON file and display it in the text box."""
        try:
            with open(filepath, "r") as file:
                data = json.load(file)
                self.users = data
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
           pass

    def get_app_users_password(self):
        """Load app users JSON."""
        self.load_json_file("users/app.json")
        self.get_passwords()

    def get_admin_users_password(self):
        """Load admin.json users JSON."""
        self.load_json_file("users/admin.json.json")

    def get_specific_user_password(self):
        """Show a dialog to add a specific user and display placeholder JSON."""
        dialog = CustomInputDialog(parent=self, fields=["Username"], title="Add Specific User")
        username = dialog.show()
        if username:
            self.users = username
            self.get_passwords()

    def get_passwords(self):
        threading.Thread(target=self.get_passwords_thread).start()

    def get_passwords_thread(self):
        if not self.vault_defined():
            messagebox.showwarning("Warning!", "Vault settings have not been configured!\nAborting action!")
            return

        self.toggle_buttons()
        self.environment_combobox.configure(state="disabled")

        """Retrieve and display passwords for the selected service."""
        selected_environment = self.environment_combobox.get().strip()
        environment_details = self.environment_manager.get_environment(selected_environment)
        host = environment_details.get("host", None)
        service = environment_details.get("service_name", None)
        unique_name = str(host) + "_" + str(service)

        # Check if the tab for the service exists, if not, add it
        try:
            self.tabview.tab(selected_environment)
            self.tabview.delete(selected_environment)
        except ValueError:
            # Tabview for service does not exist, so we will add a new one
            pass
        finally:
            tab = self.tabview.add(selected_environment)

        try:
            if tab:
                # create_right_click_menu(self.tabview)  # Bind right-click menu to the new tab

                textbox = ctk.CTkTextbox(tab, height=10)
                textbox.pack(padx=10, pady=10, fill="both", expand=True)
                textbox.delete("1.0", ctk.END)
                # Create content for the tab
                for user in self.users:
                    success, password, _ = self.get_credentials(user, service, unique_name)
                    if success:
                        formatted_data = json.dumps({"username": user, "password": password}, indent=4)
                        textbox.insert("1.0", formatted_data + ",\n")
                    else:
                        # Something went wrong break the loop
                        break

                self.tabview.set(selected_environment)
        finally:
            self.toggle_buttons()
            self.environment_combobox.configure(state="normal")

    def get_credentials(self, username, service_name, unique_name):
        if self.client_token is None:

            decrypted_role_id = self.cipher_suite.decrypt(self.settings_manager.settings["role_id"].encode()).decode()
            decrypted_secret_id = self.cipher_suite.decrypt(self.settings_manager.settings["secret_id"].encode()).decode()

            build_data = f'"role_id": "{str(decrypted_role_id)}", "secret_id": "{str(decrypted_secret_id)}"'

            client_token_response = requests.post(self.settings_manager.get("vault_url") + "/v1/auth/approle/login",
                                                  headers={"Content-Type": "application/json"},
                                                  data="{" + build_data + "}",
                                                  verify=False)

            if client_token_response.status_code != 200:
                messagebox.showerror("Error",
                                     f"Failed to retrieve client token for vault. Status code {client_token_response.status_code}")
                return False, None, None

            self.client_token = client_token_response.json().get("auth").get("client_token")

        user_category = "app" if "app" in username.lower() else "admin"
        prime_pattern = r"\w+pd\d+"
        system = "prime" if re.match(prime_pattern, service_name.lower()) else "online"
        url = f"{self.settings_manager.get('vault_url')}/v1/secret/tct{system}%2Fdb%2Foracle%2F{user_category}%2Feu-central-1-{service_name.lower()}%2F{system}%2F{username.lower()}"
        response = requests.get(url, headers={"X-Vault-Token": self.client_token}, verify=False)

        if response.status_code != 200:
            messagebox.showerror("Error",
                                 f"Failed to retrieve credentials for {service_name}. Status code {response.status_code}")
            return False, None, None

        password = response.json().get('data').get('password')

        if self.settings_manager.get("save_healthcheck_credentials_locally", False):
            self.credential_manager.add_or_update(unique_name, username, password)

        return True, password, False

    def toggle_buttons(self):
        for widget in self.button_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                current_state = widget.cget("state")
                new_state = "disabled" if current_state == "normal" else "normal"
                widget.configure(state=new_state)

    def vault_defined(self) -> bool:
        return self.settings_manager.exists("role_id") and self.settings_manager.exists("secret_id") and self.settings_manager.exists("vault_url")
