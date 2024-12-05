import json
import os

class Environments:
    _instance = None  # Class-level variable to store the single instance

    def __new__(cls, *args, **kwargs):
        """Override __new__ to ensure only one instance of Environments exists."""
        if not cls._instance:
            cls._instance = super(Environments, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, file_path="Environments.json"):
        self.file_path = file_path
        self.Environments = self.load_Environments()

    def load_Environments(self):
        """Load Environments from a JSON file. If the file doesn't exist, return an empty dictionary."""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    print("Invalid JSON format. Starting with empty Environments.")
        return {}

    def get_environment(self, key, default=None):
        """Get a setting value with a default fallback."""
        return self.Environments.get(key, default)


    def get_environments(self):
        return list(self.Environments.keys())

    def add_or_update(self, key, value):
        """Add or update a setting and save the changes."""
        self.Environments[key] = value
        self.save_Environments()

    def delete(self, key):
        """Delete a setting if it exists and save the changes."""
        if key in self.Environments:
            del self.Environments[key]
            self.save_Environments()
            print(f"Key '{key}' has been deleted.")
        else:
            print(f"Key '{key}' does not exist.")

    def save_Environments(self):
        """Save the current Environments to the JSON file."""
        with open(self.file_path, "w") as file:
            json.dump(self.Environments, file, indent=4)

