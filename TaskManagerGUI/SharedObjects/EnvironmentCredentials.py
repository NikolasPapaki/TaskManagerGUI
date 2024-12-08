import json
import os

class EnvironmentCredentials:
    _instance = None  # Class-level variable to store the single instance

    def __new__(cls, *args, **kwargs):
        """Override __new__ to ensure only one instance of Settings exists."""
        if not cls._instance:
            cls._instance = super(EnvironmentCredentials, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, file_path="environment_credentials.json"):
        self.file_path = file_path
        self.credentials = self.load_credentials()

    def load_credentials(self):
        """Load settings from a JSON file. If the file doesn't exist, return an empty dictionary."""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    pass
        return {}

    def get(self, service, default=None):
        """Get a credentials value with a default fallback."""
        return self.credentials.get(service, default)

    def exists(self, service, user):
        if service in self.credentials:
            if self.credentials[service].get(user, None) is not None:
                return True

        return False

    def add_or_update(self, service, username, password):
        """Add or update a credentials and save the changes."""
        self.credentials[service][username] = password
        print(self.credentials)

        self.save_credentials()

    def delete(self, key):
        """Delete a setting if it exists and save the changes."""
        if key in self.credentials:
            del self.credentials[key]
            self.save_credentials()


    def save_credentials(self):
        """Save the current settings to the JSON file."""
        with open(self.file_path, "w") as file:
            json.dump(self.credentials, file, indent=4)

