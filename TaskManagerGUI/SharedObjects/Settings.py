import json
import os

class Settings:
    _instance = None  # Class-level variable to store the single instance

    def __new__(cls, *args, **kwargs):
        """Override __new__ to ensure only one instance of Settings exists."""
        if not cls._instance:
            cls._instance = super(Settings, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, file_path="settings.json"):
        self.file_path = file_path
        self.settings = self.load_settings()

    def load_settings(self):
        """Load settings from a JSON file. If the file doesn't exist, return an empty dictionary."""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    print("Invalid JSON format. Starting with empty settings.")
        return {}

    def get(self, key, default=None):
        """Get a setting value with a default fallback."""
        return self.settings.get(key, default)

    def add_or_update(self, key, value):
        """Add or update a setting and save the changes."""
        self.settings[key] = value
        self.save_settings()

    def delete(self, key):
        """Delete a setting if it exists and save the changes."""
        if key in self.settings:
            del self.settings[key]
            self.save_settings()
            print(f"Key '{key}' has been deleted.")
        else:
            print(f"Key '{key}' does not exist.")

    def save_settings(self):
        """Save the current settings to the JSON file."""
        with open(self.file_path, "w") as file:
            json.dump(self.settings, file, indent=4)

