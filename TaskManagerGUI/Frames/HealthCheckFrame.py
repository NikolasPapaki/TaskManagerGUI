import customtkinter as ctk
from SharedObjects import Environments, Settings
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

def task_name_sanitize(task_name) -> str:
    """Sanitize the task name by replacing invalid characters with underscores."""
    return re.sub(r'[\\/:"*?<>| ]', '_', task_name)

def sanitize_password(password):
    return password.replace("^", "^^")

def _pad_names(names, max_length):
    return [name.ljust(max_length) for name in names]


class HealthCheckFrame(ctk.CTkFrame):
    ORDER = 96

    def __init__(self, parent, main_window):
        super().__init__(parent)

        self.parent = parent
        self.environment_manager = Environments(parent=self)  # Assuming this manages environment data
        self.settings_manager = Settings()
        self.client_token = None
        self.placeholder_values = None


        self.combobox_width = 350

        # Pad environment options for consistent dropdown width
        self.environments = _pad_names(
            self.environment_manager.get_environments() + ["Custom"],
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

        # Store buttons in a dictionary for easy management
        self.buttons = {}

        if os.path.exists('healthcheck.json'):
            with open('healthcheck.json', "r") as file:
                try:
                    buttons_dict = json.load(file)
                except json.JSONDecodeError:
                    print("Invalid JSON format. Starting with empty settings.")

        button_configs = []

        if buttons_dict:
            for button in buttons_dict:
                # Use a default argument to capture the current button value
                button_configs.append({
                    "command": lambda btn=button: self.run_command(buttons_dict[btn], btn),
                    "name": button
                })


        # Create and pack buttons, storing references
        for config in button_configs:
            button = ctk.CTkButton(
                master=self.button_frame,
                text=config["name"],
                command=config["command"]
            )
            button.pack(side="top", fill="x", pady=5, padx=5)
            self.buttons[config["name"]] = button

    def run_command(self, templates, name ):
        threading.Thread(target=self.run_commands_thread, args=[templates, name]).start()

    def run_commands_thread(self, templates, name):
        """Run a series of subprocesses with progress tracking and log output/errors."""
        self._configure_buttons("disabled")
        # Ensure the task_logs directory exists
        log_dir = "task_logs"
        os.makedirs(log_dir, exist_ok=True)

        # Generate a unique log file name with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
        log_file_path = f"{log_dir}/{task_name_sanitize(name)}_{timestamp}.log"

        try:
            with open(log_file_path, "w") as log_file:  # Open log file for writing
                for i, template in enumerate(templates):
                    success, command = self.build_command(template)
                    # Check if build_command was canceled due to user not giving arguments
                    if success is None:
                        break
                    # Check if build_command had errors then abort
                    if not success:
                        messagebox.showerror("Error", f"Failed to assign values to '{template}'.")
                        break

                    try:
                        # Run the command and capture output and errors
                        result = subprocess.run(
                            command,
                            shell=True,
                            check=True,
                            stdout=log_file,  # Log standard output to the file
                            stderr=log_file,  # Log errors to the same file
                            text=True,  # Ensure output is in text format
                            timeout=120
                        )

                        if result.returncode != 0:
                            log_file.write(f"Command failed with exit code {result.returncode}.\n")
                            messagebox.showerror("Error",
                                                 f"Command '{command}' failed with exit code {result.returncode}.")
                            break

                    except subprocess.TimeoutExpired as e:
                        messagebox.showerror("Error",f"Command '{command}' took more then 2 minutes")
                        break

                    except subprocess.CalledProcessError as e:
                        # Log the error to the file and show a messagebox
                        log_file.write(f"Command failed with exit code {e.returncode}.\n")
                        messagebox.showerror("Error", f"Command '{command}' failed with exit code {e.returncode}.")
                        break

                    except FileNotFoundError:
                        # Log the error to the file and show a messagebox
                        log_file.write(f"Command '{command}' not found.\n")
                        messagebox.showerror("Error", f"Command '{command}' not found.")
                        break

                    except Exception as e:
                        # Log the unexpected error to the file and show a messagebox
                        log_file.write(f"An unexpected error occurred: {str(e)}\n")
                        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
                        break
        finally:
            log_file = open(log_file_path, "r")
            log_content = log_file.read()
            if len(log_content) > 0:
                if messagebox.askyesno("Completed", f"Task {name} has been completed successfully.\n"
                                                    "Would you like to view the log output?"):
                    with open(log_file_path, "r") as log_file:
                        log_content = log_file.read()
                    # Display the log content in a popup
                    self.show_log_popup(log_content)
            else:
                log_file.close()
                os.remove(log_file_path)

            self._configure_buttons("normal")

    def build_command(self, template):
        # Fetch the current environment from the combobox
        selected_environment = self.environment_combobox.get().strip()

        if selected_environment == "Custom":
            # Prompt the user for inputs using CustomInputDialog
            fields = [field_name for _, field_name, _, _ in string.Formatter().parse(template) if field_name]

            if fields:
                dialog = CustomInputDialog(
                    title="Provide Environment Details",
                    parent=self,
                    fields=fields
                )
                result = dialog.show()

                # If the user cancels the dialog, return the original template
                if result is None:
                    return None, template

                self.placeholder_values = {field: dialog.result[idx].strip() for idx, field in enumerate(fields)}

                # Check if any required field is empty
                if any(value == "" for value in self.placeholder_values.values()):
                    return None, template
            else:
                messagebox.showerror("Error", f"There was an error trying to find the field required for template '{template}'")
                return None, template
        else:
            # Use selected environment for placeholders
            print(self.environment_manager.get_environment(selected_environment))
            self.placeholder_values = self.environment_manager.get_environment(selected_environment)

            fields = [field_name for _, field_name, _, _ in string.Formatter().parse(template) if field_name]
            if fields:

                missing_keys = [key for key in fields if key and key not in self.placeholder_values]

                if missing_keys:
                    for missing_key in missing_keys:
                        success, password = self.get_credentials(missing_key, self.placeholder_values.get("service_name"))
                        if success:
                            self.placeholder_values[missing_key] = password
                        else:
                            return None, template
            else:
                messagebox.showerror("Error", f"There was an error trying to find the field required for template '{template}'")
                return None, template

        try:
            # Use str.format() to replace placeholders in the template
            formatted_command = template.format(**self.placeholder_values)

            if "sqlplus" in formatted_command:
                formatted_command = 'echo "exit" | '+ formatted_command
            return True, formatted_command

        except KeyError as e:
            return False, template

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
        text_widget.configure(state="disabled")  # Make the textbox read-only
        text_widget.pack(side="left", fill="both", expand=True)

        # Wait for the popup to close
        log_window.wait_window()

    def get_credentials(self, username, service_name):
        if self.settings_manager.get("role_id") and self.settings_manager.get("secret_id") and self.settings_manager.get("vault_url"):

            if self.client_token is None:
                build_data = f'"role_id": "{str(self.settings_manager.get("role_id"))}", "secret_id": "{str(self.settings_manager.get("secret_id"))}"'

                client_token_response = requests.post(self.settings_manager.get("vault_url") + "/v1/auth/approle/login",
                                                      headers={"Content-Type": "application/json"},
                                                      data = build_data,
                                                      verify=False)

                if client_token_response.status_code != 200:
                    messagebox.showerror("Error",
                                         f"Failed to retrieve client token for vault. Status code {client_token_response.status_code}")
                    return False, None

                self.client_token = client_token_response.json().get("auth").get("client_token")

            user_category = "app" if "app" in username.lower() else "admin"
            url = f"{self.settings_manager.get('vault_url')}/v1//secret/tctprime%2Fdb%2Foracle%2F{user_category}%2F{service_name.lower()}%2Fprime%2F{username.lower()}"
            response = requests.get(url, headers={"X-Vault-Token": self.client_token}, verify=False)

            if response.status_code != 200:
                messagebox.showerror("Error",
                                     f"Failed to retrieve credentials for {service_name}. Status code {response.status_code}")
                return False, None

            return True, sanitize_password(response.json().get('data').get('password'))

        else:
            if messagebox.askyesno("Input Required", f"It appears that vault settings have not been configured\n Would you like to provide password manually"):
                dialog = CustomInputDialog(
                    title=f"Provide Password for {username.upper()} for {service_name}",
                    parent=self,
                    fields=["Password"]
                )
                result = dialog.show()

                # If the user cancels the dialog, return the original template
                if result is None or result == "":
                    return False, None

                else:
                    return True, result[0] # We only have password here
            else:
                return False, None
