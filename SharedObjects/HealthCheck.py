import os
import json
from tkinter import messagebox


def load_healthcheck_dict(filepath='healthcheck.json'):
    buttons_dict = {}
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            try:
                buttons_dict = json.load(file)
            except json.JSONDecodeError:
                messagebox.showinfo("Invalid JSON format", "Healthcheck options are not loaded.")

    return buttons_dict


class HealthCheck:
    _instance = None  # Class-level variable to store the single instance

    def __new__(cls, *args, **kwargs):
        """Override __new__ to ensure only one instance of Environments exists."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        self.parent = parent  # Parent window for dialogs
        self.buttons_dict = load_healthcheck_dict()

    def get_config(self, key, default=None):
        """Get configuration of an action."""
        return self.buttons_dict.get(key, default).copy()

    def get_options(self):
        """Get a list of all environment keys."""
        return list(self.buttons_dict.keys())

    def add_new_option(self, key, config):
        pass
