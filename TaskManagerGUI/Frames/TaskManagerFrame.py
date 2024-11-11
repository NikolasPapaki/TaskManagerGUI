import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime
from custom_widgets import CustomInputDialog


class TaskManagerFrame(ctk.CTkFrame):
    ORDER = 2

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Frame title
        title_label = ctk.CTkLabel(self, text="Task Manager", font=("Arial", 24))
        title_label.pack(pady=10)

        # Configuration frame for task name and commands
        self.configuration_frame = ctk.CTkFrame(self)
        self.configuration_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Task Name Label and Entry
        task_name_label = ctk.CTkLabel(self.configuration_frame, text="Task Name:")
        task_name_label.pack(pady=(5, 0), padx=10, anchor=tk.W)

        self.task_name_var = ctk.StringVar()
        self.task_name_entry = ctk.CTkEntry(self.configuration_frame, textvariable=self.task_name_var,
                                            state=tk.DISABLED)
        self.task_name_entry.pack(pady=5, padx=10, fill=ctk.X)

        # Commands Label and Treeview
        command_label = ctk.CTkLabel(self.configuration_frame, text="Commands:")
        command_label.pack(pady=(5, 0), padx=10, anchor=tk.W)

        self.command_tree = ttk.Treeview(self.configuration_frame, columns=("Commands"), show='headings', height=6)
        self.command_tree.heading("Commands", text="Commands")
        self.command_tree.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        # Right-click menu for commands
        self.command_menu = tk.Menu(self.command_tree, tearoff=0)
        self.command_menu.add_command(label="Add Command", command=self.add_command)
        self.command_menu.add_command(label="Edit Command", command=self.edit_command)
        self.command_menu.add_command(label="Remove Command", command=self.remove_command)

        self.command_tree.bind("<Button-3>", self.show_command_menu)

        # Tasks Frame for Existing Tasks and Delete Task Button
        self.tasks_frame = ctk.CTkFrame(self)
        self.tasks_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        task_list_label = ctk.CTkLabel(self.tasks_frame, text="Existing Tasks:")
        task_list_label.pack(pady=(10, 0), padx=10, anchor=tk.W)

        self.task_listbox = tk.Listbox(self.tasks_frame)
        self.task_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.task_listbox.bind("<<ListboxSelect>>", self.on_task_select)

        # Right-click menu for tasks
        self.task_menu = tk.Menu(self.task_listbox, tearoff=0)
        self.task_menu.add_command(label="Add Task", command=self.add_task)
        self.task_menu.add_command(label="Delete Task", command=self.delete_task)

        self.task_listbox.bind("<Button-3>", self.show_task_menu)

        # Load existing tasks
        self.load_tasks()

    def show_command_menu(self, event):
        """Display the context menu for the Command Treeview."""
        self.command_menu.post(event.x_root, event.y_root)

    def show_task_menu(self, event):
        """Display the context menu for the Task Listbox."""
        self.task_menu.post(event.x_root, event.y_root)

    def log_action(self, action, task_name, old_value="", new_value=""):
        """Log actions performed on tasks."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "task_name": task_name,
            "old_value": old_value,
            "new_value": new_value
        }
        print(log_entry)

        # Load existing logs
        logs = self.load_logs()

        # Append the new log entry
        logs.append(log_entry)

        # Save the updated logs back to the file
        with open("task_logs.json", "w") as log_file:
            json.dump(logs, log_file, indent=4)

    def load_logs(self):
        """Load existing logs from the log file."""
        if os.path.exists("task_logs.json"):
            with open("task_logs.json", "r") as log_file:
                return json.load(log_file)
        return []

    def load_tasks(self):
        """Load tasks from the JSON file and populate the listbox."""
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as file:
                data = json.load(file)
                for task in data.get("tasks", []):
                    self.task_listbox.insert(tk.END, task["name"])

    def on_task_select(self, event):
        """Load the selected task's details into the entry fields for editing."""
        selected_index = self.task_listbox.curselection()
        if selected_index:
            selected_task = self.task_listbox.get(selected_index)
            self.task_name_var.set(selected_task)
            self.task_name_entry.configure(state=tk.NORMAL)  # Enable entry for viewing

            # Clear existing commands in the Treeview
            self.command_tree.delete(*self.command_tree.get_children())

            # Find the commands for the selected task
            with open("tasks.json", "r") as file:
                data = json.load(file)
                for task in data.get("tasks", []):
                    if task["name"] == selected_task:
                        # Populate the Treeview with commands
                        for command in task["commands"]:
                            self.command_tree.insert("", tk.END, values=(command,))
                        break
        else:
            self.task_name_entry.configure(state=tk.DISABLED)  # Disable if no task is selected

    def add_command(self):
        """Add a command to the Treeview and update the task in the JSON file."""
        # Check if a task is selected
        selected_index = self.task_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Selection Error", "Please select a task to add a command.")
            return

        # Create the input dialog first without displaying it
        input_dialog = ctk.CTkInputDialog(text="Enter Command", title="Add Command")

        # Retrieve the parent window's geometry
        parent_x = self.winfo_x()  # X position of the parent window
        parent_y = self.winfo_y()  # Y position of the parent window
        parent_width = self.winfo_width()  # Width of the parent window
        parent_height = self.winfo_height()  # Height of the parent window

        # Get the dimensions of the input dialog
        dialog_width = 450  # Set a fixed width or retrieve dynamically if possible
        dialog_height = 150  # Set a fixed height or retrieve dynamically if possible

        # Calculate the center position for the dialog
        x_position = parent_x + (parent_width // 2) - (dialog_width // 2)
        y_position = parent_y + (parent_height // 2) - (dialog_height // 2)

        # Set the position of the dialog
        input_dialog.geometry(f"{dialog_width}x{dialog_height}+{x_position}+{y_position}")

        # Display the dialog and wait for user input
        command = input_dialog.get_input()

        # Check if user pressed OK and provided a command
        if command is None:
            return  # User pressed Cancel, do nothing

        # If command is not empty, insert it into the command tree
        if command:
            self.command_tree.insert("", tk.END, values=(command,))
            self.update_task_file()  # Update the task file after adding command

            # Keep the selected task highlighted
            self.task_listbox.selection_set(selected_index)  # Re-select the same item\

            # Log action
            self.log_action("Added command", self.task_listbox.get(selected_index[0]), new_value=command)


    def edit_command(self):
        """Edit the selected command from the Treeview and update the task in the JSON file."""
        selected_item = self.command_tree.selection()
        selected_index = self.task_listbox.curselection()

        if selected_item:
            # Get the current command value
            current_command = self.command_tree.item(selected_item[0])['values'][0]

            # Create and show the custom input dialog with the current command as the initial value
            dialog = CustomInputDialog(title="Edit Command",
                                       initial_value=current_command, parent=self)
            new_command = dialog.show()

            # Check if the user pressed OK and provided a command
            if new_command is not None:
                # If command is not empty, update it in the command tree
                if new_command:
                    self.command_tree.item(selected_item[0], values=(new_command,))
                    self.update_task_file()  # Update the task file after editing command

                    # Keep the selected task highlighted
                    self.task_listbox.selection_set(selected_index)  # Re-select the same task
                    # Log action
                    if new_command != current_command:
                        self.log_action("Updated command", self.task_listbox.get(selected_index[0]), old_value=current_command, new_value=new_command)

    def remove_command(self):
        """Remove the selected command from the Treeview and update the task in the JSON file."""
        selected_item = self.command_tree.selection()
        selected_index = self.task_listbox.curselection()

        if selected_item:
            # Get the item ID of the selected command
            item_id = selected_item[0]

            # Retrieve the item data before deleting
            item_data = self.command_tree.item(item_id)

            # Delete the selected command
            self.command_tree.delete(item_id)

            # Update the task file after removing the command
            self.update_task_file()

            # Keep the selected task highlighted
            if selected_index:
                self.task_listbox.selection_set(selected_index)  # Re-select the same task

            # Log action with the command data
            self.log_action("Deleted command", self.task_listbox.get(selected_index[0]), old_value=item_data['values'][0])
        else:
            messagebox.showwarning("Selection Error", "Please select a command to remove.")

    def add_task(self):
        """Add a new task. Commands will be added later."""

        # Create the input dialog first without displaying it
        input_dialog = ctk.CTkInputDialog(text="Enter Task Name", title="Add New Task")

        # Retrieve the parent window's geometry
        parent_x = self.winfo_x()  # X position of the parent window
        parent_y = self.winfo_y()  # Y position of the parent window
        parent_width = self.winfo_width()  # Width of the parent window
        parent_height = self.winfo_height()  # Height of the parent window

        # Get the dimensions of the input dialog
        dialog_width = 450  # Set a fixed width or retrieve dynamically if possible
        dialog_height = 150  # Set a fixed height or retrieve dynamically if possible

        # Calculate the center position for the dialog
        x_position = parent_x + (parent_width // 2) - (dialog_width // 2)
        y_position = parent_y + (parent_height // 2) - (dialog_height // 2)

        # Set the position of the dialog
        input_dialog.geometry(f"{dialog_width}x{dialog_height}+{x_position}+{y_position}")

        # Display the dialog and wait for user input
        task_name = input_dialog.get_input()

        # Check if user pressed OK and provided a task name
        if task_name is None:
            return  # User pressed Cancel, do nothing

        # Check if the task name is empty
        if not task_name:
            messagebox.showwarning("Input Error", "Please provide a task name.")
            return

        # Check if the task already exists
        existing_tasks = [self.task_listbox.get(i) for i in range(self.task_listbox.size())]
        if task_name in existing_tasks:
            messagebox.showwarning("Input Error", "Task already exists. Please choose a different name.")
            return

        # Create a new task with an empty command list
        self.update_task_list(task_name, commands=[])

        # Clear entry fields
        self.task_name_var.set("")  # Optionally, you might want to clear the task name entry
        self.command_tree.delete(*self.command_tree.get_children())  # Clear Treeview

        # Optionally, select the newly created task for immediate editing
        self.task_listbox.selection_clear(0, tk.END)
        self.task_listbox.selection_set(tk.END)  # Select the last added task
        self.on_task_select(None)  # Load the new task's details
        self.log_action("Added task", task_name)

    def update_task_list(self, task_name, commands):
        """Update tasks in the JSON file."""
        tasks = []

        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as file:
                tasks_data = json.load(file)
                tasks = tasks_data.get("tasks", [])

        # Check if the task already exists
        for task in tasks:
            if task["name"] == task_name:
                task["commands"] = commands  # Update existing task commands
                break
        else:
            # Add new task
            tasks.append({"name": task_name, "commands": commands})

        # Write updated tasks back to JSON
        with open("tasks.json", "w") as file:
            json.dump({"tasks": tasks}, file, indent=4)

        # Refresh task list in the Listbox
        self.refresh_task_list()

    def refresh_task_list(self):
        """Refresh the task list in the Listbox."""
        self.task_listbox.delete(0, tk.END)  # Clear existing list
        self.load_tasks()  # Load tasks again to populate

    def delete_task(self):
        """Delete the selected task."""
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task_name = self.task_listbox.get(selected_index)
            self.remove_task(task_name)

            # Clear entry fields
            self.task_name_var.set("")
            self.command_tree.delete(*self.command_tree.get_children())  # Clear Treeview
            self.log_action("Deleted task", task_name)

    def remove_task(self, task_name):
        """Remove the task from the JSON file."""
        tasks = []

        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as file:
                tasks_data = json.load(file)
                tasks = tasks_data.get("tasks", [])

        # Remove the selected task
        tasks = [task for task in tasks if task["name"] != task_name]

        # Write updated tasks back to JSON
        with open("tasks.json", "w") as file:
            json.dump({"tasks": tasks}, file, indent=4)

        # Refresh task list in the Listbox
        self.refresh_task_list()

    def update_task_file(self):
        """Update the task in the JSON file based on the selected task."""
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task_name = self.task_listbox.get(selected_index)
            commands = [self.command_tree.item(item)['values'][0] for item in self.command_tree.get_children()]

            # Update the task list
            self.update_task_list(task_name, commands)
