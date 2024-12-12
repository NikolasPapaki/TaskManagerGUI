import customtkinter as ctk
from SharedObjects import Environments, Settings, EnvironmentCredentials, OracleDB, HealthCheck
import re
import threading
import os
import subprocess
from datetime import datetime
from tkinter import messagebox
from custom_widgets import CustomInputDialog
import string
import requests
import json
from cryptography.fernet import Fernet

def task_name_sanitize(task_name) -> str:
    """Sanitize the task name by replacing invalid characters with underscores."""
    return re.sub(r'[\\/:"*?<>| ]', '_', task_name)

def sanitize_password(password):
    return password

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


class HealthCheckFrame(ctk.CTkFrame):
    ORDER = 95

    def __init__(self, parent, main_window):
        super().__init__(parent)

        self.parent = parent
        self.environment_manager = Environments(parent=self)
        self.settings_manager = Settings()
        self.credential_manager = EnvironmentCredentials()
        self.database_manager = OracleDB()
        self.healthcheck_manager = HealthCheck()

        self.client_token = None
        self.key = load_or_generate_key()
        self.cipher_suite = Fernet(self.key)

        # Store buttons in a dictionary for easy management
        self.buttons = {}
        self.button_configs = []

        self.combobox_width = 350
        # Pad environment options for consistent dropdown width
        self.environments = _pad_names(
            self.environment_manager.get_environments(),
            int(self.combobox_width // 4.3)
        )

        # Create an environment frame
        self.environment_frame = ctk.CTkFrame(self)
        self.environment_frame.pack(pady=20, padx=20, fill="x", expand=False)

        # Add a label above the combobox
        self.environment_label = ctk.CTkLabel(
            self.environment_frame,
            text="Select Environment:",
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
        self.environment_combobox.set(self.environments[0])
        self.environment_combobox.pack(pady=10, padx=10)

        # Create a button frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10, padx=20, fill="x", expand=False)
        # Create buttons
        self.create_buttons_in_ui()

    def run_command(self, name, config):
        print(name)
        print(config)
        threading.Thread(target=self.run_commands_thread, args=[name, config]).start()

    def run_commands_thread(self, name, config):
        """Run a series of subprocesses with progress tracking and log output/errors."""
        self._configure_buttons("disabled")
        # Ensure the task_logs directory exists
        log_dir = "task_logs"
        os.makedirs(log_dir, exist_ok=True)

        # Generate a unique log file name with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
        log_file_path = f"{log_dir}/{task_name_sanitize(name)}_{timestamp}.log"

        selected_environment = self.environment_combobox.get().strip()
        environment_details = self.environment_manager.get_environment(selected_environment)
        host = environment_details.get("host", None)
        service = environment_details.get("service_name", None)
        port = environment_details.get("port", None)
        unique_name = str(host) + "_" + str(service)
        loop_complete = True
        log_file = open(log_file_path, "w")

        try:
            for user in config.get("users", None).split(","):
                # Get Password for user
                success, password = self.get_credentials(username=user, service_name=environment_details.get("service_name"), unique_name=unique_name)
                # Check if we retrived password
                print(user)
                print(password)
                if not success:
                    loop_complete = False
                    break
                else:
                    errormsg = self.database_manager.connect(username=user, password=password, host=host, port=port, service_name=service)
                    if errormsg:
                        if errormsg == self.database_manager.INVALID_PASS:
                            if self.credential_manager.exists(unique_name, user):
                                messagebox.showerror("Error", "Incorrect password. Deleting local entry!")
                                self.credential_manager.delete(unique_name)
                            else:
                                messagebox.showerror("Error", "Incorrect password. Something went wrong!")
                        else:
                            messagebox.showerror("Error", f"Something went wrong!\n {errormsg}")

                        loop_complete = False
                        break
                    else:
                        result = self.database_manager.execute(config.get("plsql_block", None))
                        if result:
                            for line in result:
                                log_file.write(line + "\n")

                        self.database_manager.disconnect()
        finally:
            log_file = open(log_file_path, "r")
            log_content = log_file.read()
            log_file.close()

            if loop_complete:

                if len(log_content) > 0:
                    if messagebox.askyesno("Finished!", f"Would you like to view the log output?"):
                        # Display the log content in a popup
                        self.show_log_popup(log_content)
                else:
                    messagebox.showinfo("Finished!", f"{name} has finished!")
                    os.remove(log_file_path)
            else:
                if len(log_content) > 0:
                    if messagebox.askyesno("Finished!", f"{name} has finished with errors. Would you like to view the log output?"):
                        # Display the log content in a popup
                        self.show_log_popup(log_content)
                else:
                    messagebox.showwarning("Finished!", f"{name} has finished with errors.")
                    os.remove(log_file_path)

            self._configure_buttons("normal")

    def _configure_buttons(self, state):
        """Configure all buttons to the specified state."""
        for button in self.buttons.values():
            button.configure(state=state)

    def show_log_popup(self, log_content):
        """Display the log content in a modal, scrollable popup window using CustomTkinter."""
        log_window = ctk.CTkToplevel(self)
        log_window.title("Log Output")

        # Center the popup in the parent window
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        popup_width = 600
        popup_height = 400
        position_x = parent_x + (parent_width - popup_width) // 2
        position_y = parent_y + (parent_height - popup_height) // 2

        log_window.geometry(f"{popup_width}x{popup_height}+{position_x}+{position_y}")

        # Make the popup modal
        log_window.transient(self)  # Set the popup as a child of the parent window
        log_window.grab_set()  # Disable interaction with the parent window

        # Create a frame to hold the Textbox and scrollbar
        frame = ctk.CTkFrame(log_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create the CTkTextbox
        text_widget = ctk.CTkTextbox(frame, wrap="word", font=("Arial", 12))
        text_widget.insert("0.0", log_content)  # Insert the log content at the start
        text_widget.configure(state="disabled")
        text_widget.pack(side="left", fill="both", expand=True)

        # Wait for the popup to close
        log_window.wait_window()

    def get_credentials(self, username, service_name, unique_name):
        if self.credential_manager.exists(unique_name, username):
            return True, sanitize_password(self.credential_manager.get(unique_name).get(username))

        elif self.vault_defined() and self.is_rds():

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
                    return False, None

                self.client_token = client_token_response.json().get("auth").get("client_token")

            user_category = "app" if "app" in username.lower() else "admin"
            prime_pattern = r"\w+pd\d+"
            system = "prime" if re.match(prime_pattern, service_name.lower()) else "online"
            url = f"{self.settings_manager.get('vault_url')}/v1/secret/tct{system}%2Fdb%2Foracle%2F{user_category}%2Feu-central-1-{service_name.lower()}%2F{system}%2F{username.lower()}"
            response = requests.get(url, headers={"X-Vault-Token": self.client_token}, verify=False)

            if response.status_code != 200:
                messagebox.showerror("Error",
                                     f"Failed to retrieve credentials for {service_name}. Status code {response.status_code}")
                return False, None

            password = response.json().get('data').get('password')

            if self.settings_manager.get("save_healthcheck_credentials_locally", False):
                self.credential_manager.add_or_update(unique_name, username, password)

            return True, sanitize_password(password)

        elif self.is_rds():
            if messagebox.askyesno("Input Required", f"It appears that neither vault settings or default passwords have not been configured\n Would you like to provide password manually"):
                dialog = CustomInputDialog(
                    title=f"Provide Password for {username.upper()} of {service_name}",
                    parent=self,
                    fields=["Password"]
                )
                result = dialog.show()

                # If the user cancels the dialog, return the original template
                if result is None or result == "":
                    return False, None

                else:
                    if self.settings_manager.get("save_healthcheck_credentials_locally", False):
                        self.credential_manager.add_or_update(unique_name, username, result[0])
                    return True, sanitize_password(result[0]) # We only have password here
            else:
                return False, None
        else:
            if messagebox.askyesno("Input Required", f"It appears this is not an RDS instance and default passwords have not been configured\n Would you like to provide password manually"):
                dialog = CustomInputDialog(
                    title=f"Provide Password for {username.upper()} of {service_name}",
                    parent=self,
                    fields=["Password"]
                )
                result = dialog.show()

                # If the user cancels the dialog, return the original template
                if result is None or result == "":
                    return False, None

                else:
                    if self.settings_manager.get("save_healthcheck_credentials_locally", False):
                        self.credential_manager.add_or_update(unique_name, username, result[0])
                    return True, sanitize_password(result[0]) # We only have password here
            else:
                return False, None


    def vault_defined(self) -> bool:
        return self.settings_manager.exists("role_id") and self.settings_manager.exists("secret_id") and self.settings_manager.exists("vault_url")

    def is_rds(self) -> bool:
        return True if "rds.amazonaws.com" in self.environment_manager.get_environment(self.environment_combobox.get().strip()).get("host") else False

    def is_localdb(self, selected_environment) -> bool:
        return True if any(env in self.environment_manager.get_environment(selected_environment.strip()).get("host") for env in ["localhost", "127.0.0.1"]) else False

    def create_buttons_in_ui(self):
        threading.Thread(target=lambda: self.create_buttons_in_ui_thread(), daemon=True).start()

    def create_buttons_in_ui_thread(self):
        for button in self.buttons.values():
            button.destroy()

        self.button_configs = []

        for name in self.healthcheck_manager.get_options():
            # Use a default argument to capture the current button value
            self.button_configs.append({
                "command": lambda btn=name, conf=self.healthcheck_manager.get_config(name): self.run_command(btn, conf),
                "name": name
            })

        # Create and pack buttons, storing references
        for config in self.button_configs:
            button = ctk.CTkButton(
                master=self.button_frame,
                text=config["name"],
                command=config["command"]
            )
            button.pack(side="top", fill="x", pady=5, padx=5)
            self.buttons[config["name"]] = button

        # Let's call the update_buttons in case we loaded with non-local environment to remove buttons
        # self.update_buttons_in_ui(self.environment_combobox.get().strip())

    def on_show(self):
        self.create_buttons_in_ui()

    # def update_buttons_in_ui(self, selected_value):
    #     buttons_to_add = []
    #     buttons_to_remove = []
    #     if self.is_localdb(selected_value):
    #        pass
    #     else:
    #         pass
    #
    #     threading.Thread(target=lambda: self.update_buttons_in_ui_thread(buttons_to_add, buttons_to_remove), daemon=True).start()
    #
    # def update_buttons_in_ui_thread(self, buttons_to_add, buttons_to_remove):
    #     # Remove unnecessary buttons
    #     for button_name in buttons_to_remove:
    #         self.buttons[button_name].destroy()
    #         del self.buttons[button_name]
    #
    #     # Add buttons
    #     for config in self.button_configs:
    #         if config["name"] in buttons_to_add:
    #             button = ctk.CTkButton(
    #                 master=self.button_frame,
    #                 text=config["name"],
    #                 command=config["command"]
    #             )
    #             button.pack(side="top", fill="x", pady=5, padx=5)
    #             self.buttons[config["name"]] = button