import json
import os
from cryptography.fernet import Fernet


def load_or_generate_key():
    """Load the encryption key from a file or generate a new one if not found."""
    key_file = ".secret.key"
    if os.path.exists(key_file):
        with open(key_file, "rb") as file:
            return file.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as file:
            file.write(key)
        return key

class EnvironmentCredentials:
    _instance = None  # Class-level variable to store the single instance

    def __new__(cls, *args, **kwargs):
        """Override __new__ to ensure only one instance of Settings exists."""
        if not cls._instance:
            cls._instance = super(EnvironmentCredentials, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, file_path="config/environment_credentials.json"):
        self.file_path = file_path
        # Load or generate encryption key and initialize cipher suite
        self.key = load_or_generate_key()
        self.cipher_suite = Fernet(self.key)

        self.credentials = self.load_credentials()

    def load_credentials(self):
        """Load settings from a JSON file. If the file doesn't exist, return an empty dictionary."""
        decrypted_credentials = {}
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                try:
                    encrypted_credentials = dict(json.load(file))
                    for tns_name, users in encrypted_credentials.items():
                        decrypted_credentials[tns_name] = {
                            user: self.cipher_suite.decrypt(password.encode()).decode()
                            for user, password in users.items()
                        }
                except json.JSONDecodeError:
                    pass
        return decrypted_credentials

    def get(self, service, default=None):
        """Get a credentials value with a default fallback."""
        return self.credentials.get(service, default).copy()

    def exists(self, name, user):
        if name in self.credentials:
            if self.credentials[name].get(user.strip(), None) is not None:
                return True

        return False

    def add_or_update(self, service, username, password):
        """Add or update a credentials and save the changes."""
        if service not in self.credentials:
            self.credentials[service] = {}
        self.credentials[service][username] = password
        self.save_credentials()

    def delete(self, key):
        """Delete a setting if it exists and save the changes."""
        if key in self.credentials:
            del self.credentials[key]
            self.save_credentials()

    def save_credentials(self):
        """Save the current settings to the JSON file."""
        encrypted_credentials = {}

        for tns_name, users in self.credentials.items():
            encrypted_credentials[tns_name] = {
                user: self.cipher_suite.encrypt(password.encode()).decode()
                for user, password in users.items()
            }

        with open(self.file_path, "w") as file:
            json.dump(encrypted_credentials, file, indent=4)

