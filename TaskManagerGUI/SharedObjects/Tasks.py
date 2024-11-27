import json
import os
from tkinter import messagebox


class Tasks:
    _instance = None  # Class-level variable to store the single instance
    empty_dict = {
                    "prefix": "",
                    "path": "",
                    "executable": "",
                    "arguments": ""
                }

    def __new__(cls, *args, **kwargs):
        """Override __new__ to ensure only one instance of Tasks exists."""
        if not cls._instance:
            cls._instance = super(Tasks, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.tasks = self.load_tasks()

    def load_tasks(self):
        """Load tasks from the tasks.json file."""
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as file:
                data = json.load(file)
                return data.get("tasks", [])
        return []

    def save_tasks(self):
        """Save the current tasks to tasks.json."""
        with open("tasks.json", "w") as file:
            json.dump({"tasks": self.tasks}, file, indent=4)

    def add_task(self, task_name):
        """Add a new task with the given task name."""
        self.tasks.append({"name": task_name, "commands": []})
        self.save_tasks()

    def rename_task(self, old_name, new_name):
        """Rename a task in the task manager."""
        for task in self.get_tasks():
            if task["name"] == old_name:
                task["name"] = new_name
                self.save_tasks()
                break

    def add_command(self, task_name, command_dict):
        """Adds a new command to the task with the given task_name."""
        task_found = False
        for task in self.tasks:
            if task["name"] == task_name:
                task["commands"].append(command_dict)
                task_found = True
                break

        if not task_found:
            # If the task doesn't exist, create it with the given command
            self.tasks.append({"name": task_name, "commands": [command_dict]})

        self.save_tasks()

    def delete_task(self, task_name):
        """Delete a task by its name."""
        task_found = False
        # Lets delete its commands first
        for task in self.tasks:
            if task["name"] == task_name:
                del task["commands"]
                task_found = True
                break

        if task_found:
            self.tasks = [task for task in self.tasks if task["name"] != task_name]
            self.save_tasks()

    def update_task(self, task_name, command_dict):
        """Update the commands for an existing task."""
        for task in self.tasks:
            if task["name"] == task_name:
                task["commands"] = command_dict
                self.save_tasks()
                break

    def delete_command(self, task_name, command_dict):
        """Deletes a command from the task with the given task_name."""
        for task in self.tasks:
            if task["name"] == task_name:
                if command_dict in task["commands"]:
                    task["commands"].remove(command_dict)
                    self.save_tasks()
                    return True
        return False

    def update_command(self, task_name, old_command_dict, new_command_dict):
        """Updates a command for the task with the given task_name."""
        for task in self.tasks:
            if task["name"] == task_name:
                if old_command_dict in task["commands"]:
                    task["commands"] = [new_command_dict if cmd == old_command_dict else cmd for cmd in task["commands"]]
                    self.save_tasks()

    def get_tasks(self):
        """Return the list of all tasks."""
        return self.tasks

    def get_task(self, task_name):
        for task in self.tasks:
            if task["name"] == task_name:
                return task
        return None

    def get_command(self, task_name, command_name):
        for task in self.tasks:
            if task["name"] == task_name:
                for command in task["commands"]:
                    if command_name == self.generate_command_from_parts(command):
                        return command
        return self.empty_dict

    def add_bulk_tasks(self, new_tasks):
        print(new_tasks)
        """Add multiple tasks from a list of tasks with options to override or append commands."""
        for task in new_tasks.get("tasks"):
            task_name = task.get("name")
            commands = task.get("commands", [])

            # Check if the task already exists
            existing_task = next((t for t in self.tasks if t["name"] == task_name), None)

            if existing_task:
                # Show popup to decide between override or append
                user_choice = messagebox.askyesnocancel(
                    "Task Conflict",
                    f"The task '{task_name}' already exists.\n\n"
                    "Do you want to:\n"
                    "- Yes: Override the task and its commands\n"
                    "- No: Append the commands to the existing task\n"
                    "- Cancel: Skip this task"
                )

                if user_choice is None:
                    # User chose Cancel, skip this task
                    continue
                elif user_choice:  # User chose Yes
                    # Override the task and commands
                    self.delete_task(task_name)  # Remove the existing task
                    self.add_task(task_name)  # Add the new task
                    for command in commands:
                        self.add_command(task_name, command)
                else:  # User chose No
                    # Append commands to the existing task
                    for command in commands:
                        if command not in existing_task["commands"]:
                            self.add_command(task_name, command)
            else:
                # Task does not exist, add it and all its commands
                self.add_task(task_name)
                for command in commands:
                    self.add_command(task_name, command)

    def generate_command_from_parts(self, command_dict):
        """Generate a command string from its dictionary parts."""
        prefix = command_dict.get("prefix", "").strip()
        path = command_dict.get("path", "").strip()
        executable = command_dict.get("executable", "").strip()
        arguments = command_dict.get("arguments", "").strip()

        # Construct the full command
        if path:
            command = f"{prefix} {os.path.join(path, executable)} {arguments}".strip()
        else:
            command = f"{prefix} {executable} {arguments}".strip()
        return command