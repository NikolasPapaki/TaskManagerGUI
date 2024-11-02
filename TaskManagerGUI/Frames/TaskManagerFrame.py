import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import os

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

        # Label for task name entry
        task_name_label = ctk.CTkLabel(self.configuration_frame, text="Task Name:")
        task_name_label.pack(pady=(5, 0), padx=10, anchor=tk.W)

        # Entry for task name
        self.task_name_var = ctk.StringVar()
        self.task_name_entry = ctk.CTkEntry(self.configuration_frame, textvariable=self.task_name_var, placeholder_text="Task Name",
                                            state=tk.DISABLED)
        self.task_name_entry.pack(pady=5, padx=10, fill=ctk.X)

        # Label for command input
        command_label = ctk.CTkLabel(self.configuration_frame, text="Commands:")
        command_label.pack(pady=(5, 0), padx=10, anchor=tk.W)

        # Treeview for command input
        self.command_tree = ttk.Treeview(self.configuration_frame, columns=("Commands"), show='headings', height=6)
        self.command_tree.heading("Commands", text="Commands")
        self.command_tree.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        # Buttons frame for action buttons
        self.buttons_frame = ctk.CTkFrame(self)
        self.buttons_frame.pack(pady=10, padx=10, fill=tk.BOTH)

        # Button to add command
        self.add_command_button = ctk.CTkButton(self.buttons_frame, text="Add Command", command=self.add_command)
        self.add_command_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Button to remove selected command
        self.remove_command_button = ctk.CTkButton(self.buttons_frame, text="Remove Command",
                                                   command=self.remove_command)
        self.remove_command_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Button to add or update task
        self.add_task_button = ctk.CTkButton(self.buttons_frame, text="Add Task", command=self.add_task)
        self.add_task_button.pack(side=tk.LEFT, padx=10, expand=True)

        # Tasks frame for existing tasks and delete task button
        self.tasks_frame = ctk.CTkFrame(self)
        self.tasks_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Label for tasks list
        task_list_label = ctk.CTkLabel(self.tasks_frame, text="Existing Tasks:")
        task_list_label.pack(pady=(10, 0), padx=10, anchor=tk.W)

        # Listbox to display tasks
        self.task_listbox = tk.Listbox(self.tasks_frame)
        self.task_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.task_listbox.bind("<<ListboxSelect>>", self.on_task_select)

        # Button to delete task
        self.delete_task_button = ctk.CTkButton(self.tasks_frame, text="Delete Task", command=self.delete_task)
        self.delete_task_button.pack(pady=(5, 20), padx=10)

        # Load existing tasks
        self.load_tasks()

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

        command = ctk.CTkInputDialog(text="Enter Command", title="Add Command").get_input()
        if command:
            self.command_tree.insert("", tk.END, values=(command,))
            self.update_task_file()  # Update the task file after adding command

            # Keep the selected task highlighted
            self.task_listbox.selection_set(selected_index)  # Re-select the same item

    def remove_command(self):
        """Remove the selected command from the Treeview and update the task in the JSON file."""
        selected_item = self.command_tree.selection()
        if selected_item:
            self.command_tree.delete(selected_item)
            self.update_task_file()  # Update the task file after removing command

    def add_task(self):
        """Add a new task. Commands will be added later."""
        # Show an input dialog to enter a new task name
        task_name = ctk.CTkInputDialog(text="Enter Task Name", title="Add New Task").get_input()

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
