import json
import os

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

    def is_modified(self):
        """Check if tasks have been modified since the last save."""
        return self.modified

    def reset_modified_flag(self):
        """Reset the modified flag to False."""
        self.modified = False
