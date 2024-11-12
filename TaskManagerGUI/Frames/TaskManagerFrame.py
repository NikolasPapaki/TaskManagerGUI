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
        self.logs = self.load_logs()

        # Frame title
        title_label = ctk.CTkLabel(self, text="Task Manager", font=("Arial", 24))
        title_label.pack(pady=10)

        # Task and Command Treeview
        self.tree = ttk.Treeview(self, columns=["Type"], show='tree headings')
        self.tree.heading('#0', text='Tasks')
        self.tree.column('#0', width=250)
        self.tree.heading('Type', text='Type')
        self.tree.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        # Load existing tasks
        self.load_tasks()

        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def load_logs(self):
        """Load existing logs from the log file."""
        if os.path.exists("task_logs.json"):
            with open("task_logs.json", "r") as log_file:
                return json.load(log_file)
        return []

    def show_context_menu(self, event):
        """Display appropriate context menu based on selection."""
        item_id = self.tree.identify_row(event.y)
        self.tree.selection_set(item_id)

        # Clear previous menu options
        self.context_menu.delete(0, tk.END)

        if item_id:
            # Determine if it's a task or command based on depth
            if self.tree.parent(item_id):  # Has a parent, so it's a command
                self.context_menu.add_command(label="Edit Command", command=lambda: self.edit_command(item_id))
                self.context_menu.add_command(label="Delete Command", command=lambda: self.delete_command(item_id))
            else:  # No parent, so it's a task
                self.context_menu.add_command(label="Add Command", command=lambda: self.add_command(item_id))
                self.context_menu.add_command(label="Delete Task", command=lambda: self.delete_task(item_id))
        else:
            # Right-clicked on empty space, option to add new task
            self.context_menu.add_command(label="Add New Task", command=self.add_task)

        # Display menu
        self.context_menu.post(event.x_root, event.y_root)

    def load_tasks(self):
        """Load tasks from JSON and display in the tree."""
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as file:
                data = json.load(file)
                for task in data.get("tasks", []):
                    task_id = self.tree.insert("", tk.END, text=task["name"], values=["Task"])
                    for command in task["commands"]:
                        self.tree.insert(task_id, tk.END, text=command, values=["Command"])

    def add_task(self):
        """Prompt user to add a new task."""
        input_dialog = CustomInputDialog(title="Enter Task Name", initial_value="", parent=self)
        task_name = input_dialog.show()
        if task_name:
            # Add task to tree and file
            task_id = self.tree.insert("", tk.END, text=task_name, values=["Task"])
            self.update_task_list(task_name, commands=[])
            self.log_action("Added task", task_name)

    def add_command(self, task_id):
        """Prompt user to add a new command to a task."""
        input_dialog = CustomInputDialog(title="Enter Command", initial_value="", parent=self)
        command_name = input_dialog.show()
        if command_name:
            # Add command to tree and file
            self.tree.insert(task_id, tk.END, text=command_name, values=["Command"])
            task_name = self.tree.item(task_id, 'text')
            self.update_task_file(task_name)
            self.log_action("Added command", task_name, new_value=command_name)

    def edit_command(self, command_id):
        """Edit the selected command."""
        command_name = self.tree.item(command_id, 'text')

        # Optional: Add a confirmation popup for editing
        confirm = messagebox.askyesno("Confirm Edit", f"Are you sure you want to edit the command ?")
        if confirm:
            new_command_name = self.prompt_input("Edit Command", initial_value=command_name)
            if new_command_name and new_command_name != command_name:
                task_id = self.tree.parent(command_id)
                task_name = self.tree.item(task_id, 'text')
                self.tree.item(command_id, text=new_command_name)
                self.update_task_file(task_name)
                self.log_action("Updated command", task_name, old_value=command_name, new_value=new_command_name)

    def delete_task(self, task_id):
        """Delete the selected task and its commands."""
        task_name = self.tree.item(task_id, 'text')

        # Confirmation popup
        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Are you sure you want to delete the task '{task_name}' and all its commands?")
        if confirm:
            self.tree.delete(task_id)
            self.remove_task(task_name)
            self.log_action("Deleted task", task_name)

    def delete_command(self, command_id):
        """Delete the selected command."""
        task_id = self.tree.parent(command_id)
        task_name = self.tree.item(task_id, 'text')
        command_name = self.tree.item(command_id, 'text')

        # Confirmation popup
        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Are you sure you want to delete the command ?")
        if confirm:
            self.tree.delete(command_id)
            self.update_task_file(task_name)
            self.log_action("Deleted command", task_name, old_value=command_name)

    def update_task_list(self, task_name, commands):
        """Update task list in JSON file."""
        tasks = []
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as file:
                tasks = json.load(file).get("tasks", [])

        for task in tasks:
            if task["name"] == task_name:
                task["commands"] = commands
                break
        else:
            tasks.append({"name": task_name, "commands": commands})

        with open("tasks.json", "w") as file:
            json.dump({"tasks": tasks}, file, indent=4)

    def update_task_file(self, task_name):
        """Update commands in the JSON file based on the Treeview."""
        # Find the task ID associated with the given task name
        task_id = None
        for item in self.tree.get_children():
            if self.tree.item(item, 'text') == task_name:
                task_id = item
                break

        # If task_id is not found, exit the function with an error
        if task_id is None:
            messagebox.showerror("Error", f"Task '{task_name}' not found.")
            return

        # Gather all command names under this task
        commands = [self.tree.item(item)["text"] for item in self.tree.get_children(task_id)]
        self.update_task_list(task_name, commands)

    def remove_task(self, task_name):
        """Remove task from JSON file."""
        tasks = []
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as file:
                tasks = json.load(file).get("tasks", [])

        tasks = [task for task in tasks if task["name"] != task_name]
        with open("tasks.json", "w") as file:
            json.dump({"tasks": tasks}, file, indent=4)

    def log_action(self, action, task_name, old_value="", new_value=""):
        """Log action with details."""
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
