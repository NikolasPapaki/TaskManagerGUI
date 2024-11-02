from logging import exception

import customtkinter as ctk
import subprocess
import threading
import tkinter.messagebox as messagebox
import json
import os


def load_tasks():
    """Load tasks from the JSON file and return a list of tasks."""
    if not os.path.exists("tasks.json"):
        return []

    try:
        with open("tasks.json", "r") as file:
            data = json.load(file)
            return data.get("tasks", [])
    except json.JSONDecodeError:
        messagebox.showerror("Error", "There was an error loading the task file")
        return []


class TaskRunnerFrame(ctk.CTkFrame):
    ORDER = 2

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        label = ctk.CTkLabel(self, text="Task Runner", font=("Arial", 24))
        label.pack(pady=20)

        # Load tasks from the JSON file
        self.tasks = load_tasks()

        # Create an inner frame to hold the buttons
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill=ctk.X, padx=10, pady=(5, 10))
        self.progress_bar.set(0)  # Initialize progress bar to 0

        # Dynamically create buttons for each task
        self.create_task_buttons()

    def create_task_buttons(self):
        for task in self.tasks:
            task_name = task["name"]
            commands = task["commands"]

            if commands:
                button = ctk.CTkButton(
                    self.button_frame,
                    text=task_name,
                    command=lambda cmds=commands, name=task_name: self.run_commands(cmds, name)
                )
                button.pack(pady=5, padx=10, fill=ctk.X)


    def run_commands(self, args, name):
        threading.Thread(target=self.run_commands_thread, args=[args, name,] ).start()

    def run_commands_thread(self, commands, name):
        """Patch the database by running a series of subprocesses with progress tracking."""
        self.disable_buttons()

        try:
            for i, command in enumerate(commands):
                try:
                    result = subprocess.run(command, shell=True, check=True)

                    self.update_progress_bar(i + 1, len(commands))

                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Command '{command}' failed with exit code {e.returncode}.")
                    break

                except FileNotFoundError:
                    messagebox.showerror("Error", f"Command '{command}' not found.")
                    break  # Stop processing on error

                except Exception as e:
                    messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
                    break

            else:
                # Show a completion message only if all commands succeed
                messagebox.showinfo("Completed", f"Task {name} has been completed successfully.")

        finally:
            # Finalize progress bar and re-enable buttons regardless of errors
            self.update_progress_bar(len(commands), len(commands))
            self.enable_buttons()

    def update_progress_bar(self, completed, total):
        if total > 0:
            progress = completed / total  # Calculate progress as a fraction
            self.progress_bar.set(progress)  # Update the progress bar
            self.update_idletasks()


    def disable_buttons(self):
        for button in self.button_frame.winfo_children():
            button.configure(state="disabled")

    def enable_buttons(self):
        for button in self.button_frame.winfo_children():
            button.configure(state="normal")
