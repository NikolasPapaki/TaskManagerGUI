import customtkinter as ctk
import subprocess
import threading
import tkinter.messagebox as messagebox
import time
from datetime import datetime
import re
from SharedObjects import Tasks  # Import the shared Tasks object


def task_name_sanitize(task_name) -> str:
    """Sanitize the task name by replacing invalid characters with underscores."""
    return re.sub(r'[\\/:"*?<>|]', '_', task_name)


class TaskRunnerFrame(ctk.CTkFrame):
    ORDER = 2

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        label = ctk.CTkLabel(self, text="Task Runner", font=("Arial", 24))
        label.pack(pady=20)

        # Initialize the shared Tasks object and pass a callback to it
        self.tasks_manager = Tasks()

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
        self.progress_bar = ctk.CTkProgressBar(self, height=15)
        self.progress_bar.pack(fill=ctk.X, padx=10, pady=(5, 10))
        self.progress_bar.set(0)

        self.create_task_buttons()

        # Debounce mechanism
        self.last_search_time = time.time()
        self.debounce_delay = 0.3  # 300 ms delay after the user stops typing

    def on_search_input(self, *args):
        """Handle the search input with debounce."""
        current_time = time.time()
        if current_time - self.last_search_time >= self.debounce_delay:
            self.last_search_time = current_time
            self.create_task_buttons()
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
        # Get tasks from the shared Tasks object
        tasks = self.tasks_manager.get_tasks()

        # Filter tasks based on the search text
        filtered_tasks = [task for task in tasks if search_text in task["name"].lower()]

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

    def run_commands(self, args, name):
        threading.Thread(target=self.run_commands_thread, args=[args, name]).start()

    def run_commands_thread(self, commands, name):
        """Run a series of subprocesses with progress tracking and log output/errors."""
        self.disable_buttons()

        # Generate a unique log file name with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
        log_file_path = f"{task_name_sanitize(name)}_{timestamp}.log"

        try:
            with open(log_file_path, "w") as log_file:  # Open log file for writing
                for i, command in enumerate(commands):
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

                        self.update_progress_bar(i + 1, len(commands))
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

                else:
                    if messagebox.askyesno("Completed", f"Task {name} has been completed successfully.\n"
                                                        "Would you like to view the log output?"):
                        with open(log_file_path, "r") as log_file:
                            log_content = log_file.read()
                        # Display the log content in a popup
                        self.show_log_popup(log_content)

        finally:
            self.update_progress_bar(len(commands), len(commands))
            self.enable_buttons()

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

        # Add a scrollbar
        scrollbar = ctk.CTkScrollbar(frame, command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.configure(yscrollcommand=scrollbar.set)

        # Add a Close button
        close_button = ctk.CTkButton(log_window, text="Close", command=log_window.destroy)
        close_button.pack(pady=10)

        # Wait for the popup to close
        log_window.wait_window()

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

    def on_show(self):
       self.create_task_buttons()
