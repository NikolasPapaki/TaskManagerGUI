from logging import exception
import customtkinter as ctk
import subprocess
import threading
import tkinter.messagebox as messagebox
import json
import os
import time

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

        # Create a label for the search entry
        search_label = ctk.CTkLabel(self, text="Search tasks by name:", font=("Arial", 14))
        search_label.pack(pady=5, padx=10, anchor="w")

        # Create a search bar
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.on_search_input)

        search_entry = ctk.CTkEntry(self, textvariable=self.search_var, placeholder_text="Search tasks")
        search_entry.pack(pady=10, padx=10, fill=ctk.X)

        # Create an inner frame to hold the task buttons
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill=ctk.X, padx=10, pady=(5, 10))
        self.progress_bar.set(0)  # Initialize progress bar to 0

        # Dynamically create buttons for each task
        self.create_task_buttons()

        # Debounce mechanism
        self.last_search_time = time.time()
        self.debounce_delay = 0.3  # 300 ms delay after the user stops typing

    def on_search_input(self, *args):
        """Handle the search input with debounce."""
        current_time = time.time()
        if current_time - self.last_search_time >= self.debounce_delay:
            self.last_search_time = current_time
            self.update_task_buttons()
        else:
            # If the user is typing too fast, just wait
            pass

    def create_task_buttons(self):
        """Create task buttons based on the current tasks and search filter."""
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        search_text = self.search_var.get().lower()

        # Use a background thread to update buttons
        threading.Thread(target=self.create_buttons_thread, args=(search_text,)).start()

    def create_buttons_thread(self, search_text):
        """Create buttons in a background thread to avoid blocking the UI."""
        filtered_tasks = [task for task in self.tasks if search_text in task["name"].lower()]

        # Create the buttons in the UI thread
        self.after(0, self.update_buttons_in_ui, filtered_tasks)

    def update_buttons_in_ui(self, filtered_tasks):
        """Update the task buttons in the main UI thread."""
        for task in filtered_tasks:
            task_name = task["name"]
            commands = task["commands"]
            if commands:
                button = ctk.CTkButton(
                    self.button_frame,
                    text=task_name,
                    command=lambda cmds=commands, name=task_name: self.run_commands(cmds, name)
                )
                button.pack(pady=5, padx=10, fill=ctk.X)

    def update_task_buttons(self):
        """Update the displayed task buttons based on search criteria."""
        self.create_task_buttons()

    def run_commands(self, args, name):
        threading.Thread(target=self.run_commands_thread, args=[args, name]).start()

    def run_commands_thread(self, commands, name):
        """Run a series of subprocesses with progress tracking."""
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
                    break

                except Exception as e:
                    messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
                    break

            else:
                messagebox.showinfo("Completed", f"Task {name} has been completed successfully.")

        finally:
            self.update_progress_bar(len(commands), len(commands))
            self.enable_buttons()

    def update_progress_bar(self, completed, total):
        if total > 0:
            progress = completed / total
            self.progress_bar.set(progress)
            self.update_idletasks()

    def disable_buttons(self):
        for button in self.button_frame.winfo_children():
            button.configure(state="disabled")

    def enable_buttons(self):
        for button in self.button_frame.winfo_children():
            button.configure(state="normal")
