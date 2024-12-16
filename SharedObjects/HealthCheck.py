import os
import json
from tkinter import messagebox


def load_healthcheck_dict(filepath='healthcheck.json'):
    healthcheck_dict = {}
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            try:
                healthcheck_dict = json.load(file)
            except json.JSONDecodeError:
                messagebox.showinfo("Invalid JSON format", "Healthcheck options are not loaded.")
    return healthcheck_dict


def save_healthcheck_dict(healthcheck_dict, filepath='healthcheck.json'):
    """Save the healthcheck options back to the JSON file."""
    with open(filepath, "w") as file:
        json.dump(healthcheck_dict, file, indent=4)


class HealthCheck:
    _instance = None  # Class-level variable to store the single instance

    def __new__(cls, *args, **kwargs):
        """Override __new__ to ensure only one instance of HealthCheck exists."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.healthcheck_dict = load_healthcheck_dict()

    def get_config(self, key, default=None):
        """Get configuration of an action."""
        return self.healthcheck_dict.get(key, default).copy()

    def get_options(self):
        """Get a list of all environment keys."""
        return list(self.healthcheck_dict.keys())

    def add_new_option(self, key, config):
        """Add a new health check option."""
        if key in self.healthcheck_dict:
            messagebox.showinfo("Duplicate Key", f"Option '{key}' already exists.")
        else:
            self.healthcheck_dict[key] = config
            save_healthcheck_dict(self.healthcheck_dict)

    def edit_option(self, key, new_config):
        """Edit an existing health check option."""
        if key not in self.healthcheck_dict:
            messagebox.showinfo("Option Not Found", f"No option found for '{key}'.")
            return

        # Update the option
        self.healthcheck_dict[key] = new_config
        save_healthcheck_dict(self.healthcheck_dict)

    def delete_option(self, key):
        """Delete an existing health check option."""
        if key not in self.healthcheck_dict:
            messagebox.showinfo("Option Not Found", f"No option found for '{key}'.")
            return
        del self.healthcheck_dict[key]
        save_healthcheck_dict(self.healthcheck_dict)


