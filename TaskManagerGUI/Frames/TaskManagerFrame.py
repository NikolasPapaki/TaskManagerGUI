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
from tkinter import filedialog
from custom_widgets import CustomCommandDialog

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
        # Identify the item under the cursor
        item_id = self.tree.identify_row(event.y)
        selected_items = self.tree.selection()

        # If no items are selected, or the right-clicked item is not part of the selection
        if not selected_items or item_id not in selected_items:
            self.tree.selection_set(item_id)
            selected_items = self.tree.selection()

        # Clear the context menu
        self.context_menu.delete(0, tk.END)

        # If no items are selected, show general options
        if not selected_items:
            self.context_menu.add_command(label="Add New Task", command=self.add_task)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="View Logs", command=self.view_taskmanager_logs)
        else:
            # Determine the types of selected items
            parent_items = [self.tree.parent(item) for item in selected_items]
            is_task_selection = all(parent == "" for parent in parent_items)  # All are tasks
            is_command_selection = all(parent != "" for parent in parent_items)  # All are commands

            # Populate the context menu based on the selection type
            if is_task_selection:
                if len(selected_items) == 1:
                    self.context_menu.add_command(label="Add Command",
                                                  command=lambda: self.add_command(selected_items[0]))
                    self.context_menu.add_separator()
                    self.context_menu.add_command(label="Rename Task",
                                                  command=lambda: self.rename_task(selected_items[0]))
                    self.context_menu.add_separator()
                    self.context_menu.add_command(label="Delete Task",
                                                  command=lambda: self.delete_task(selected_items[0]))
                else:
                    self.context_menu.add_command(
                        label="Delete Tasks", command=lambda: self.delete_multiple_tasks(selected_items)
                    )

                self.context_menu.add_separator()
                self.context_menu.add_command(label="Export Task(s)",
                                              command=lambda: self.export_selected_tasks(selected_items))

            elif is_command_selection and len(selected_items) == 1:
                # Single command selected
                self.context_menu.add_command(label="Edit Command",
                                              command=lambda: self.edit_command(selected_items[0]))
                self.context_menu.add_separator()
                self.context_menu.add_command(label="Delete Command",
                                              command=lambda: self.delete_command(selected_items[0]))

        # Show the context menu
        self.context_menu.post(event.x_root, event.y_root)

    def export_selected_tasks(self, task_ids):
        from tkinter.filedialog import asksaveasfilename

        selected_tasks = [self.tasks_manager.get_task(self.tree.item(task_id, "text")) for task_id in task_ids]
        tasks_to_export = {"tasks": selected_tasks}

        file_path = asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Export Tasks to JSON",
        )
        if file_path:
            with open(file_path, "w") as json_file:
                json.dump(tasks_to_export, json_file, indent=4)
            messagebox.showinfo("Export Successful", f"Tasks exported to {file_path}")

    def display_tasks(self):
        """Display tasks in the treeview widget."""
        # Clear the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Sort tasks alphabetically by their name
        tasks = self.tasks_manager.get_tasks()
        tasks_sorted = sorted(tasks, key=lambda task: task["name"].lower())

        # Populate the Treeview with sorted tasks
        for task in tasks_sorted:
            task_id = self.tree.insert("", tk.END, text=task["name"], values=["Task"])
            for command_parts in task["commands"]:
                command_text = self.generate_command_from_parts(command_parts)
                self.tree.insert(task_id, tk.END, text=command_text, values=["Command"])

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
        """Add a command to a task."""
        input_dialog = CustomCommandDialog(
            title="Add Command",
            parent=self,
            fields=["Prefix (e.g., python, java)", "Executable Path", "Executable Name", "Arguments"]
        )
        command_parts = input_dialog.show()

        if command_parts:
            prefix, path, executable, arguments = map(str.strip, command_parts)
            command_dict = {
                "prefix": prefix,
                "path": path,
                "executable": executable,
                "arguments": arguments
            }

            # Retrieve the task name
            task_name = self.tree.item(task_id, "text")

            # Add the command to the task
            self.tasks_manager.add_command(task_name, command_dict)

            # Insert the new command into the Treeview under the corresponding task
            command_text = self.generate_command_from_parts(command_dict)
            self.tree.insert(task_id, tk.END, text=command_text, values=["Command"])

            # Log the addition of the command
            self.log_action("Added command", task_name, new_value=command_text)

    def edit_command(self, command_id):
        """Edit an existing command."""
        # Retrieve the task and command
        task_id = self.tree.parent(command_id)
        task_name = self.tree.item(task_id, 'text')
        command_text = self.tree.item(command_id, 'text')

        # Parse the current command using the tasks manager
        current_command = self.tasks_manager.get_command(task_name, command_text)
        print(current_command)
        # Open the CustomCommandDialog with the current values
        fields = ["Prefix", "Path", "Executable", "Arguments"]
        default_values = [
            current_command.get("prefix", ""),
            current_command.get("path", ""),
            current_command.get("executable", ""),
            current_command.get("arguments", "")
        ]
        dialog = CustomCommandDialog(title="Edit Command", parent=self, fields=fields, default_values=default_values)
        dialog_result = dialog.show()

        if dialog_result:
            new_prefix, new_path, new_executable, new_arguments = map(str.strip, dialog_result)
            new_command_dict = {
                "prefix": new_prefix,
                "path": new_path,
                "executable": new_executable,
                "arguments": new_arguments
            }

            # Confirm the edit
            new_command_text = self.generate_command_from_parts(new_command_dict)
            if new_command_text != command_text:
                confirm = messagebox.askyesno("Confirm Edit", "Are you sure you want to edit the command?")
                if confirm:
                    # Update the command in the tasks manager
                    self.tasks_manager.update_command(task_name, current_command, new_command_dict)

                    # Update the Treeview with the new command name
                    self.tree.item(command_id, text=new_command_text)

                    # Log the action
                    self.log_action("Updated command", task_name, old_value=command_text, new_value=new_command_text)

    def delete_task(self, task_id):
        """Delete an existing task."""
        task_name = self.tree.item(task_id, 'text')
        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Are you sure you want to delete the task '{task_name}' and all its commands?")
        if confirm:
            self.tree.delete(task_id)
            self.tasks_manager.delete_task(task_name)
            self.log_action("Deleted task", task_name)

    def delete_multiple_tasks(self, task_ids):
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the selected {len(task_ids)} task(s)?",
        )
        if confirm:
            # Collect task names before deletion
            task_names = [self.tree.item(task_id, 'text') for task_id in task_ids]

            # Delete tasks from Task Manager and Treeview
            for task_id in task_ids:
                task_name = self.tree.item(task_id, 'text')
                self.tasks_manager.delete_task(task_name)
                self.tree.delete(task_id)

            # Log the deletion
            self.log_action("Deleted multiple tasks", ", ".join(task_names))

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
        logs_frame = TaskManagementLogsFrame(logs_window, self.main_window)  # Use the TaskManagementLogsFrame
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

    def generate_command_from_parts(self, parts):
        """Generate a command string from its dictionary parts."""
        prefix = parts.get("prefix", "").strip()
        path = parts.get("path", "").strip()
        executable = parts.get("executable", "").strip()
        arguments = parts.get("arguments", "").strip()

        # Construct the full command
        if path:
            command = f"{prefix} {os.path.join(path, executable)} {arguments}".strip()
        else:
            command = f"{prefix} {executable} {arguments}".strip()
        return command