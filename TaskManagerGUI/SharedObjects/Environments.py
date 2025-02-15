import os
import re
from custom_widgets import CustomInputDialog
from tkinter import messagebox
from SharedObjects import Settings
from Logging import Logger

class Environments:
    _instance = None  # Class-level variable to store the single instance

    def __new__(cls, *args, **kwargs):
        """Override __new__ to ensure only one instance of Environments exists."""
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        self.parent = parent  # Parent window for dialogs
        self.Environments = {}  # Initialize an empty dictionary for environments
        self.settings_manager = Settings()
        # Initialize the logger
        self.logger = Logger()
        tns_path = self.settings_manager.get("tns_path", None)
        if tns_path is None:
            tns_path = self.get_tnsnames_path()

        if tns_path:
            self.settings_manager.add_or_update("tns_path", tns_path)
            self.load_tnsnames(tns_path)

    def get_tnsnames_path(self):
        """Find the tnsnames.ora file or prompt the user to specify its path."""
        # Check the TNS_ADMIN environment variable
        tns_admin = os.getenv("TNS_ADMIN")
        if tns_admin:
            tns_path = os.path.join(tns_admin, "tnsnames.ora")
            if os.path.exists(tns_path):
                return tns_path

        # Fall back to ORACLE_HOME path
        oracle_home = os.getenv("ORACLE_HOME", "")
        if oracle_home:
            default_path = os.path.join(oracle_home, "network", "admin", "tnsnames.ora")
            if os.path.exists(default_path):
                return default_path

        # If not found, prompt the user to specify the path using CustomInputDialog
        if self.parent:
            dialog = CustomInputDialog(
                title="Specify tnsnames.ora Path",
                parent=self.parent,
                fields=["Full Path to tnsnames.ora"],
            )
            result = dialog.show()
            if result and os.path.exists(result[0]):
                return result[0]
            elif result:
                self.logger.warning("Invalid or non-existent file path provided for tnsnames.ora")
                messagebox.showwarning("Warning", "Invalid or non-existent file path provided.")


        return None

    def load_tnsnames(self, tns_path):
        """Load and parse the tnsnames.ora file, capturing all details for each TNS entry."""
        self.Environments = {}
        entry_pattern = re.compile(
            r"(?P<tns_name>\w+)\s*=\s*\(\s*DESCRIPTION\s*=\s*\(.*?ADDRESS\s*=\s*\(.*?HOST\s*=\s*(?P<host>[^\s)]+).*?PORT\s*=\s*(?P<port>[^\s)]+).*?\).*?CONNECT_DATA\s*=\s*\(.*?SERVICE_NAME\s*=\s*(?P<service_name>[^\s)]+).*?\).*?\)",
            re.DOTALL | re.IGNORECASE,
        )

        try:
            with open(tns_path, "r") as file:
                content = file.read()

                # Normalize content for consistent parsing
                normalized_content = re.sub(r"\s+", " ", content)
                matches = entry_pattern.finditer(normalized_content)

                for match in matches:
                    tns_name = match.group("tns_name")
                    host = match.group("host")
                    port = match.group("port")
                    service_name = match.group("service_name")

                    # Store the parsed data in the dictionary
                    self.Environments[tns_name] = {
                        "tns_name": tns_name,
                        "host": host,
                        "port": port,
                        "service_name": service_name
                    }

            if not self.Environments:
                self.logger.warning(f"No valid entries found in {tns_path}.")
                messagebox.showwarning("Warning", f"No valid entries found in {tns_path}.")


        except Exception as e:
            self.logger.warning(f"Error reading tnsnames.ora: {e}")
            messagebox.showwarning("Warning", f"Error reading tnsnames.ora: {e}")


    def get_environment(self, key, default=None):
        """Get an environment by key."""
        # Return copy so that changes made to the result won't affect self.Environments
        if self.Environments.get(key.strip(), None):
            return self.Environments.get(key.strip()).copy()
        else:
            return default

    def get_environments(self):
        """Get a list of all environment keys."""
        return list(self.Environments.keys())

    def get_all_rds(self):
        rds_list = []
        for environment in self.Environments:
            if self.is_rds(environment):
                rds_list.append(environment)

        return rds_list

    def is_rds(self, environment_name) -> bool:
        return True if "rds.amazonaws.com" in self.get_environment(environment_name).get('host', '') else False