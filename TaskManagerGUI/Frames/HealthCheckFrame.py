import customtkinter as ctk
from SharedObjects import Environments
import re
import threading
import os
import subprocess
from datetime import datetime
from tkinter import messagebox
from custom_widgets import CustomInputDialog
import string


def task_name_sanitize(task_name) -> str:
    """Sanitize the task name by replacing invalid characters with underscores."""
    return re.sub(r'[\\/:"*?<>| ]', '_', task_name)


def _pad_names(names, max_length):
    return [name.ljust(max_length) for name in names]


class HealthCheckFrame(ctk.CTkFrame):
    ORDER = 96

    def __init__(self, parent, main_window):
        super().__init__(parent)

        self.parent = parent
        self.environment_manager = Environments()  # Assuming this manages environment data

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
        )
        self.environment_combobox.pack(pady=10, padx=10)

        # Create a button frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10, padx=20, fill="x", expand=False)

        # Store buttons in a dictionary for easy management
        self.buttons = {}

        # Button configurations
        button_configs = [
            {"command": lambda: self.run_command(["connect {user}/{password}@{tns}"], "Button 1"), "name": "Button 1"},
            {"command": lambda: self.run_command(["template2"], "Button 2"), "name": "Button 2"},
            {"command": lambda: self.run_command(["template3"], "Button 3"), "name": "Button 3"},
            {"command": lambda: self.run_command(["template4"], "Button 4"), "name": "Button 4"},
            {"command": lambda: self.run_command(["template5"], "Button 5"), "name": "Button 5"},
        ]

        # Create and pack buttons, storing references
        for config in button_configs:
            button = ctk.CTkButton(
                master=self.button_frame,
                text=config["name"],
                command=config["command"]
            )
            button.pack(side="top", fill="x", pady=5, padx=5)
            self.buttons[config["name"]] = button

    def run_command(self, templates, name):
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
                            text=True  # Ensure output is in text format
                        )

                        if result.returncode != 0:
                            log_file.write(f"Command failed with exit code {result.returncode}.\n")
                            messagebox.showerror("Error",
                                                 f"Command '{command}' failed with exit code {result.returncode}.")
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
            self._configure_buttons("normal")

    def build_command(self, template):
        # Fetch the current environment from the combobox
        selected_environment = self.environment_combobox.get().strip()

        if selected_environment == "Custom":
            # Prompt the user for inputs using CustomInputDialog
            fields = [field_name for _, field_name, _, _ in string.Formatter().parse(template) if field_name]
            dialog = CustomInputDialog(
                title="Provide Environment Details",
                parent=self,
                fields=fields
            )
            result = dialog.show()

            # If the user cancels the dialog, return the original template
            if result is None:
                return None, template

            placeholder_values = {field: dialog.result[idx].strip() for idx, field in enumerate(fields)}
            print(placeholder_values)

            # Check if any required field is empty
            if any(value == "" for value in placeholder_values.values()):
                return None, template
        else:
            # Use selected environment for placeholders
            placeholder_values = self.environment_manager.get_environment(selected_environment)

        try:
            # Use str.format() to replace placeholders in the template
            formatted_command = template.format(**placeholder_values)
            return True, formatted_command
        except KeyError as e:
            print(f"Error: Missing placeholder {e} in template.")
            return False, template

    def _configure_buttons(self, state):
        """Configure all buttons to the specified state."""
        for button in self.buttons.values():
            button.configure(state=state)
