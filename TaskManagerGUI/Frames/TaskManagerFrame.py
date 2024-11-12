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

        # Initialize tasks
        self.tasks = self.load_tasks()

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

    def load_logs(self):
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
                self.context_menu.add_command(label="Delete Command", command=lambda: self.delete_command(item_id))
            else:
                self.context_menu.add_command(label="Add Command", command=lambda: self.add_command(item_id))
                self.context_menu.add_command(label="Delete Task", command=lambda: self.delete_task(item_id))
        else:
            self.context_menu.add_command(label="Add New Task", command=self.add_task)

        self.context_menu.post(event.x_root, event.y_root)

    def load_tasks(self):
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as file:
                data = json.load(file)
                return data.get("tasks", [])
        return []

    def save_tasks(self):
        with open("tasks.json", "w") as file:
            json.dump({"tasks": self.tasks}, file, indent=4)

    def display_tasks(self):
        for task in self.tasks:
            task_id = self.tree.insert("", tk.END, text=task["name"], values=["Task"])
            for command in task["commands"]:
                self.tree.insert(task_id, tk.END, text=command, values=["Command"])

    def add_task(self):
        input_dialog = CustomInputDialog(title="Enter Task Name", initial_value="", parent=self)
        task_name = input_dialog.show()
        if task_name:
            task_id = self.tree.insert("", tk.END, text=task_name, values=["Task"])
            self.tasks.append({"name": task_name, "commands": []})
            self.save_tasks()
            self.log_action("Added task", task_name)

    def add_command(self, task_id):
        input_dialog = CustomInputDialog(title="Enter Command", initial_value="", parent=self)
        command_name = input_dialog.show()
        if command_name:
            self.tree.insert(task_id, tk.END, text=command_name, values=["Command"])
            task_name = self.tree.item(task_id, 'text')
            for task in self.tasks:
                if task["name"] == task_name:
                    task["commands"].append(command_name)
                    break
            self.save_tasks()
            self.log_action("Added command", task_name, new_value=command_name)

    def edit_command(self, command_id):
        command_name = self.tree.item(command_id, 'text')
        input_dialog = CustomInputDialog(title="Edit Command", initial_value=command_name, parent=self)
        new_command_name = input_dialog.show()
        if new_command_name and new_command_name != command_name:
            confirm = messagebox.askyesno("Confirm Edit", "Are you sure you want to edit the command?")
            if confirm:
                task_id = self.tree.parent(command_id)
                task_name = self.tree.item(task_id, 'text')
                self.tree.item(command_id, text=new_command_name)
                for task in self.tasks:
                    if task["name"] == task_name:
                        task["commands"] = [new_command_name if cmd == command_name else cmd for cmd in
                                            task["commands"]]
                        break
                self.save_tasks()
                self.log_action("Updated command", task_name, old_value=command_name, new_value=new_command_name)

    def delete_task(self, task_id):
        task_name = self.tree.item(task_id, 'text')
        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Are you sure you want to delete the task '{task_name}' and all its commands?")
        if confirm:
            self.tree.delete(task_id)
            self.tasks = [task for task in self.tasks if task["name"] != task_name]
            self.save_tasks()
            self.log_action("Deleted task", task_name)

    def delete_command(self, command_id):
        task_id = self.tree.parent(command_id)
        task_name = self.tree.item(task_id, 'text')
        command_name = self.tree.item(command_id, 'text')
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the command?")
        if confirm:
            self.tree.delete(command_id)
            for task in self.tasks:
                if task["name"] == task_name:
                    task["commands"].remove(command_name)
                    break
            self.save_tasks()
            self.log_action("Deleted command", task_name, old_value=command_name)

    def log_action(self, action, task_name, old_value="", new_value=""):
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
