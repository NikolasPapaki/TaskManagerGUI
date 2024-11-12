import os
import json
import requests
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from cryptography.fernet import Fernet
from tkinter import messagebox

class JenkinsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.settings = self.load_settings()
        self.history_file = "build_history.json"
        self.build_history = [
            {
                'build_number': '123',
                'url': 'https://example.com/job/project/123/',
                'logs': 'Log for build 123. Here is some console output...\n\nNext build: https://example.com/job/project/124/',
                'children': [
                    {
                        'build_number': '124',
                        'url': 'https://example.com/job/project/124/',
                        'logs': 'Log for build 124. More console output...\n\nNext build: https://example.com/job/project/125/',
                        'children': [
                            {
                                'build_number': '126',
                                'url': 'https://example.com/job/project/125/',
                                'logs': 'Log for build 126. Final logs here...',
                                'children': []
                            }
                        ]
                    },
                    {
                        'build_number': '125',
                        'url': 'https://example.com/job/project/124/',
                        'logs': 'Log for build 125. More console output...\n\nNext build: https://example.com/job/project/125/',
                        'children': [
                            {
                                'build_number': '127',
                                'url': 'https://example.com/job/project/125/',
                                'logs': 'Log for build 127. Final logs here...',
                                'children': []
                            }
                        ]
                    }
                ]
            }
        ]

        # Store the expanded state for each item
        self.expanded_state = {}

        # Load the encryption key
        self.key = self.load_key()
        if self.key:
            self.cipher_suite = Fernet(self.key)

        # Decrypt password
        self.password = self.decrypt_password(self.settings.get("password", ""))

        # URL entry box
        self.url_entry = ctk.CTkEntry(self, placeholder_text="Enter Jenkins build URL")
        self.url_entry.pack(pady=10, fill='x')

        # Button to initiate log retrieval
        self.retrieve_button = ctk.CTkButton(self, text="Retrieve Logs", command=self.retrieve_logs)
        self.retrieve_button.pack()

        # Treeview for displaying builds
        self.tree = ttk.Treeview(self, columns=('URL'), show="tree")
        self.tree.heading("#0", text="Build Number")
        self.tree.heading("URL", text="URL")
        self.tree.pack(expand=True, fill="both", pady=10)

        # Bind item click event to expand/collapse
        self.tree.bind("<Button-1>", self.on_treeview_item_click)
        # Bind double-click event to show logs
        self.tree.bind("<Double-1>", self.on_treeview_item_double_click)

        # Textbox to show logs
        self.log_textbox = ctk.CTkTextbox(self, wrap="word", height=10)
        self.log_textbox.pack(pady=10, fill="both", expand=True)
        self._update_treeview()

    def load_settings(self):
        """Load settings from the JSON file, or return an empty dictionary if the file does not exist."""
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as file:
                return json.load(file)
        return {}

    def load_key(self):
        """Load the encryption key from a file or return None if not found."""
        key_file = ".secret.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as file:
                return file.read()
        else:
            return None

    def decrypt_password(self, encrypted_password):
        """Decrypt the encrypted password using the loaded key."""
        if self.cipher_suite and encrypted_password:
            try:
                decrypted_password = self.cipher_suite.decrypt(encrypted_password.encode()).decode()
                return decrypted_password
            except Exception as e:
                print(f"Error decrypting password: {e}")
        return None

    def retrieve_logs(self):
        # Get URL from entry
        build_url = self.url_entry.get().strip()

        if not build_url:
            messagebox.showerror("Error", "Please provide the build URL")
            return

        # Get username from settings and password (decrypted)
        username = self.settings.get("username", "")
        password = self.password

        if not username or not password:
            messagebox.showerror("Error", "Credentials have not been defined in the settings.")
            return

        # Start log retrieval for the parent build
        self.build_history = []  # Reset history
        self._retrieve_build_logs(build_url, parent=None, username=username, password=password)

        # Update Treeview
        self._update_treeview()

    def _retrieve_build_logs(self, build_url, parent, username, password):
        try:
            # Make a request to retrieve the logs using authentication
            response = requests.get(f"{build_url}/consoleText", auth=(username, password))
            response.raise_for_status()
            logs = response.text

            # Extract build number from the URL for display
            build_number = build_url.split('/')[-2]

            # Create a new entry in the history
            build_entry = {
                'build_number': build_number,
                'url': build_url,
                'logs': logs,
                'children': []
            }

            # If we have a parent, add this to the parent's children list
            if parent:
                parent['children'].append(build_entry)
            else:
                self.build_history.append(build_entry)

            # Look for URLs of subsequent builds in the logs
            subsequent_build_url = self._extract_subsequent_build_url(logs)
            if subsequent_build_url:
                self._retrieve_build_logs(subsequent_build_url, parent=build_entry, username=username,
                                          password=password)

        except requests.RequestException as e:
            print(f"Error retrieving logs for {build_url}: {e}")

    def _extract_subsequent_build_url(self, logs):
        # Regex or logic to find subsequent build URLs in the console logs
        import re
        match = re.search(r"(https?://[^\s]+/job/[^\s]+/\d+)", logs)
        return match.group(0) if match else None

    def _update_treeview(self):
        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add history to Treeview with only one root build
        if self.build_history:
            self._add_to_treeview(self.build_history)

    def _add_to_treeview(self, build_list, parent=''):
        for build in build_list:
            # Add the current build as a tree item with build_number, url, and logs
            build_item = self.tree.insert(parent, 'end', text=build['build_number'],
                                          values=(build['url'], build['logs']))

            # Store the item ID with the build entry
            build['treeview_item_id'] = build_item

            # Recursively add children builds
            if build['children']:
                self._add_to_treeview(build['children'], parent=build_item)

    def on_treeview_item_click(self, event):
        """Handle click event to toggle the display of children builds."""
        item_id = self.tree.focus()
        if item_id:
            # Check if the clicked item has children
            children = self.tree.get_children(item_id)
            if children:
                # Toggle the expanded state of the clicked item
                if item_id in self.expanded_state and self.expanded_state[item_id]:
                    self.tree.item(item_id, open=False)
                    self.expanded_state[item_id] = False
                else:
                    self.tree.item(item_id, open=True)
                    self.expanded_state[item_id] = True

    def on_treeview_item_double_click(self, event):
        """Handle double-click event to show logs for the selected build."""
        item_id = self.tree.focus()
        if item_id:
            # Find the build that corresponds to the item_id
            build = self._find_build_by_item(self.build_history, item_id)
            if build:
                # Display the logs in the log_textbox
                self.log_textbox.delete(1.0, tk.END)
                self.log_textbox.insert(tk.END, build['logs'])

    def _find_build_by_item(self, build_list, item_id):
        """Find the build data by treeview item ID."""
        for build in build_list:
            # Check if the current build's item ID matches the selected item
            if item_id == build.get('treeview_item_id'):
                return build
            # Check children recursively
            child_build = self._find_build_by_item(build['children'], item_id)
            if child_build:
                return child_build
        return None
