import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from SharedObjects import Tasks  # Import the Tasks shared object
from custom_widgets import CustomInputDialog
import json
import os
from Frames.TaskManagementLogsFrame import TaskManagementLogsFrame
from tkinterdnd2 import TkinterDnD, DND_FILES  # Import drag-and-drop support

class TaskManagerFrame(ctk.CTkFrame):
    ORDER = 3

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.parent = parent
        self.logs = self.load_logs()

        # Initialize the shared Tasks object
        self.tasks_manager = Tasks()

        # Frame title
        title_label = ctk.CTkLabel(self, text="Task Manager", font=("Arial", 24))
        title_label.pack(pady=10)

        # Task and Command Treeview
        self.tree = ttk.Treeview(self, columns=["Type"], show='tree headings')
        self.tree.heading('#0', text='Tasks')
        self.tree.column('#0', width=250)
        self.tree.heading('Type', text='Type')
        self.tree.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        # Display tasks
        self.display_tasks()

        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Register the frame itself as a drop target
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_drop)

    def load_logs(self):
        """Load task logs from file."""
        if os.path.exists("task_logs.json"):
            with open("task_logs.json", "r") as log_file:
                return json.load(log_file)
        return []

    def show_context_menu(self, event):
        item_id = self.tree.identify_row(event.y)
        self.tree.selection_set(item_id)

        self.context_menu.delete(0, tk.END)

        if item_id:
            if self.tree.parent(item_id):
                self.context_menu.add_command(label="Edit Command", command=lambda: self.edit_command(item_id))
                self.context_menu.add_separator()
                self.context_menu.add_command(label="Delete Command", command=lambda: self.delete_command(item_id))
            else:
                self.context_menu.add_command(label="Add Command", command=lambda: self.add_command(item_id))
                self.context_menu.add_separator()
                self.context_menu.add_command(label="Rename Task", command=lambda: self.rename_task(item_id))
                self.context_menu.add_separator()
                self.context_menu.add_command(label="Delete Task", command=lambda: self.delete_task(item_id))

        else:
            self.context_menu.add_command(label="Add New Task", command=self.add_task)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="View Logs", command=self.view_taskmanager_logs)  # Add view logs option

        self.context_menu.post(event.x_root, event.y_root)

    def display_tasks(self):
        """Display tasks in the treeview widget."""
        # Clear the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Populate the Treeview with updated tasks
        for task in self.tasks_manager.get_tasks():
            task_id = self.tree.insert("", tk.END, text=task["name"], values=["Task"])
            for command in task["commands"]:
                self.tree.insert(task_id, tk.END, text=command, values=["Command"])

    def add_task(self):
        """Add a new task."""
        input_dialog = CustomInputDialog(title="Enter Task Name", initial_value="", parent=self)
        task_name = input_dialog.show()

        if task_name:
            task_name = task_name.strip()
            # Check if the task name already exists
            if any(task["name"] == task_name for task in self.tasks_manager.get_tasks()):
                messagebox.showerror("Error", "Task names must be unique.")
                return

            # Add the task if the name is unique
            self.tasks_manager.add_task(task_name)
            self.tree.insert("", tk.END, text=task_name, values=["Task"])
            self.log_action("Added task", task_name)

    def rename_task(self, item_id):
        """Rename an existing task."""
        task_name = self.tree.item(item_id, "text")

        # Prompt the user to input a new name
        input_dialog = CustomInputDialog(title="Enter New Task Name", initial_value=task_name, parent=self)
        new_task_name = input_dialog.show()

        if new_task_name:
            # Check if the new task name already exists
            if any(task["name"] == new_task_name for task in self.tasks_manager.get_tasks()):
                messagebox.showerror("Error", "Task names must be unique.")
                return

            # Update the task name in the tasks_manager and tree
            self.tasks_manager.rename_task(task_name, new_task_name)
            self.tree.item(item_id, text=new_task_name)  # Update the tree with the new name
            self.log_action("Renamed task", f"{task_name} -> {new_task_name}")

    def add_command(self, task_id):
        input_dialog = CustomInputDialog(title="Enter Command", initial_value="", parent=self)
        command_name = input_dialog.show()
        if command_name:
            task_name = self.tree.item(task_id, 'text')
            self.tasks_manager.add_command(task_name, command_name)  # Use the add_command from Tasks class

            # Insert the new command directly under the corresponding task in the Treeview
            self.tree.insert(task_id, tk.END, text=command_name, values=["Command"])

            self.log_action("Added command", task_name, new_value=command_name)

    def edit_command(self, command_id):
        """Edit an existing command."""
        command_name = self.tree.item(command_id, 'text')
        input_dialog = CustomInputDialog(title="Edit Command", initial_value=command_name, parent=self)
        new_command_name = input_dialog.show()
        if new_command_name and new_command_name != command_name:
            confirm = messagebox.askyesno("Confirm Edit", "Are you sure you want to edit the command?")
            if confirm:
                task_id = self.tree.parent(command_id)
                task_name = self.tree.item(task_id, 'text')
                self.tasks_manager.update_command(task_name, command_name, new_command_name)
                self.tree.item(command_id, text=new_command_name)
                self.log_action("Updated command", task_name, old_value=command_name, new_value=new_command_name)

    def delete_task(self, task_id):
        """Delete an existing task."""
        task_name = self.tree.item(task_id, 'text')
        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Are you sure you want to delete the task '{task_name}' and all its commands?")
        if confirm:
            self.tree.delete(task_id)
            self.tasks_manager.delete_task(task_name)
            self.log_action("Deleted task", task_name)

    def delete_command(self, command_id):
        """Delete an existing command."""
        task_id = self.tree.parent(command_id)
        task_name = self.tree.item(task_id, 'text')
        command_name = self.tree.item(command_id, 'text')
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the command?")
        if confirm:
            self.tree.delete(command_id)
            self.tasks_manager.delete_command(task_name, command_name)
            self.log_action("Deleted command", task_name, old_value=command_name)

    def log_action(self, action, task_name, old_value="", new_value=""):
        """Log changes made to tasks and commands."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "task_name": task_name,
            "old_value": old_value,
            "new_value": new_value
        }
        self.logs.append(log_entry)
        with open("task_logs.json", "w") as log_file:
            json.dump(self.logs, log_file, indent=4)

    def view_taskmanager_logs(self):
        """Show the TaskManager logs in a new window, centered on the main window."""
        # Create a new top-level window
        logs_window = ctk.CTkToplevel(self.parent)

        # Get the main window's dimensions and position
        main_window_width = self.parent.winfo_width()
        main_window_height = self.parent.winfo_height()
        main_window_x = self.parent.winfo_x()
        main_window_y = self.parent.winfo_y()

        # Set the new window size to be the same as the main window
        logs_window.geometry(f"{main_window_width}x{main_window_height}")

        # Calculate the position to center the new window on the main window
        position_x = main_window_x + (main_window_width // 2) - (main_window_width // 2)
        position_y = main_window_y + (main_window_height // 2) - (main_window_height // 2)

        # Apply the position to the new window
        logs_window.geometry(f"{main_window_width}x{main_window_height}+{position_x}+{position_y}")

        # Make sure the window stays on top of the main window
        logs_window.attributes("-topmost", True)

        # Grab the focus for the logs window and block interaction with the main window
        logs_window.grab_set()  # This prevents interaction with the main window

        # Create and pack the TaskManagementLogsFrame
        logs_frame = TaskManagementLogsFrame(logs_window)  # Use the TaskManagementLogsFrame
        logs_frame.pack(expand=True, fill=ctk.BOTH)

        # When the popup is closed, release the grab and allow interaction with the main window
        logs_window.protocol("WM_DELETE_WINDOW", lambda: self.on_logs_window_close(logs_window))

    def on_logs_window_close(self, logs_window):
        """Called when the TaskManager logs window is closed."""
        # Release the grab to allow interaction with the main window again
        logs_window.grab_release()  # Allow interaction with the main window again
        logs_window.destroy()  # Destroy the logs window

    def on_drop(self, event):
        """Handle dropped files."""
        file_path = event.data
        if file_path.endswith('.json'):
            with open(file_path, 'r') as json_file:
                new_tasks = json.load(json_file)
                self.tasks_manager.add_bulk_tasks(new_tasks)
                self.display_tasks()
                self.log_action("Imported tasks from file", file_path)
        else:
            messagebox.showerror("Invalid File", "Only JSON files are allowed.")