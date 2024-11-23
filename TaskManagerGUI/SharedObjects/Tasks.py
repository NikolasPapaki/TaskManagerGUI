import json
import os
from tkinter import messagebox


class Tasks:
    _instance = None  # Class-level variable to store the single instance

    def __new__(cls, *args, **kwargs):
        """Override __new__ to ensure only one instance of Tasks exists."""
        if not cls._instance:
            cls._instance = super(Tasks, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.tasks = self.load_tasks()
        self.modified = False  # Track if the tasks have been modified

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

    def set_modified(self):
        """Mark the tasks as modified and call the callback if provided."""
        self.modified = True

    def add_task(self, task_name):
        """Add a new task with the given task name."""
        self.tasks.append({"name": task_name, "commands": []})
        self.set_modified()  # Mark as modified and trigger callback
        self.save_tasks()

    def rename_task(self, old_name, new_name):
        """Rename a task in the task manager."""
        for task in self.get_tasks():
            if task["name"] == old_name:
                task["name"] = new_name
                self.set_modified()  # Mark as modified and trigger callback
                self.save_tasks()
                break

    def add_command(self, task_name, command_name):
        """Adds a new command to the task with the given task_name."""
        task_found = False
        for task in self.tasks:
            if task["name"] == task_name:
                task["commands"].append(command_name)
                task_found = True
                break

        if not task_found:
            # If the task doesn't exist, create it with the given command
            self.tasks.append({"name": task_name, "commands": [command_name]})

        self.set_modified()  # Mark as modified and trigger callback
        self.save_tasks()

    def delete_task(self, task_name):
        """Delete a task by its name."""
        self.tasks = [task for task in self.tasks if task["name"] != task_name]
        self.set_modified()  # Mark as modified and trigger callback
        self.save_tasks()

    def update_task(self, task_name, commands):
        """Update the commands for an existing task."""
        for task in self.tasks:
            if task["name"] == task_name:
                task["commands"] = commands
                self.set_modified()  # Mark as modified and trigger callback
                self.save_tasks()
                break

    def delete_command(self, task_name, command_name):
        """Deletes a command from the task with the given task_name."""
        for task in self.tasks:
            if task["name"] == task_name:
                if command_name in task["commands"]:
                    task["commands"].remove(command_name)
                    self.set_modified()  # Mark as modified and trigger callback
                    self.save_tasks()
                    return True
        return False

    def update_command(self, task_name, old_command, new_command):
        """Updates a command for the task with the given task_name."""
        for task in self.tasks:
            if task["name"] == task_name:
                if old_command in task["commands"]:
                    task["commands"] = [new_command if cmd == old_command else cmd for cmd in task["commands"]]
                    self.set_modified()  # Mark as modified and trigger callback
                    self.save_tasks()
                    return True
        return False

    def get_tasks(self):
        """Return the list of all tasks."""
        return self.tasks

    def get_task(self, task_name):
        for task in self.tasks:
            if task["name"] == task_name:
                return task
        return None

    def is_modified(self):
        """Check if tasks have been modified since the last save."""
        return self.modified

    def reset_modified_flag(self):
        """Reset the modified flag to False."""
        self.modified = False

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