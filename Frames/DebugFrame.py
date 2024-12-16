import os
import re
import subprocess
import json
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from SharedObjects import Settings

class DebugFrame(ctk.CTkFrame):
    ORDER = 4
    def __init__(self, parent, main_window):
        super().__init__(parent)

        # Load the settings to get the root directory
        self.settings_manager = Settings()

        # Title for the Debugger tool
        title_label = ctk.CTkLabel(self, text="Error Debugger", font=("Arial", 24))
        title_label.pack(pady=20)

        # Label for the Root Directory Entry
        root_directory_label = ctk.CTkLabel(self, text="Root Directory:", font=("Arial", 14))
        root_directory_label.pack(pady=(10, 5), anchor="w", padx=20)  # Add some padding on top and bottom for spacing

        self.root_directory = ""
        # Root Directory Entry
        self.root_directory_entry = ctk.CTkEntry(self, width=400)
        self.root_directory_entry.pack(padx=20, pady=10, fill='x')

        # Label for the Root Directory Entry
        errstack_label = ctk.CTkLabel(self, text="Error Stack:", font=("Arial", 14))
        errstack_label.pack(pady=(10, 5), anchor="w", padx=20)

        # Error Message Entry
        self.error_message_entry = ctk.CTkTextbox(self, height=10, width=400)
        self.error_message_entry.pack(padx=20, pady=10, fill="both", expand=True)


        # Submit Button
        submit_button = ctk.CTkButton(self, text="Submit", command=self.submit_error_message)
        submit_button.pack(pady=20)


    def submit_error_message(self):
        """Parse the error message and open relevant files in VS Code."""
        error_message = self.error_message_entry.get("1.0", "end-1c").strip()

        if not error_message:
            messagebox.showerror("Input Error", "Please enter an error message.")
            return

        # Get root directory from the entry widget
        self.root_directory = self.root_directory_entry.get().strip()

        # Specify schema (you can change this to be dynamic if needed)
        schema = "TCTCD1"

        # Step 1: Parse the error message to extract file names and line numbers
        files_and_lines = parse_error_message(error_message, schema)

        if not files_and_lines:
            messagebox.showinfo("No Matches", "No files found in the error message.")
            return

        # Step 2: Open the files in VS Code at the specified line numbers
        open_files_in_vscode(files_and_lines, self.root_directory)

    def on_show(self):
        if not self.root_directory_entry.get().strip():
            settings_root_directory = self.settings_manager.get("debugger_root_directory", "")
            if settings_root_directory:
                self.root_directory_entry.insert(0, settings_root_directory)

def parse_error_message(error_message, schema="TCTCD1"):
    """Parse an error message to find the file names and line numbers."""
    pattern = re.compile(rf'ORA-06512: at "{schema}\.(.*?)", line (\d+)')
    matches = pattern.findall(error_message)

    return [(match[0], int(match[1])) for match in matches]


def find_file_in_subfolders(file_name, root_directory):
    """Search for a file in the root directory and its subdirectories."""
    for root, dirs, files in os.walk(root_directory):
        if f"{file_name}.sql" in files:
            return os.path.join(root, f"{file_name}.sql")
    return None


def open_files_in_vscode(files_and_lines, root_directory):
    """Open files in VS Code at the specified line numbers."""
    for file_name, line_number in files_and_lines:
        file_path = find_file_in_subfolders(file_name, root_directory)
        if file_path:
            subprocess.run(['code', '--goto', f"{file_path}:{line_number}"])
        else:
            print(f"File {file_name}.sql not found in {root_directory} or its subfolders.")


