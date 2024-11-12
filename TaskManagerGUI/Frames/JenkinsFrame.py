import os
import json
import requests
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import customtkinter as ctk
from cryptography.fernet import Fernet


def load_settings():
    """Load settings from the JSON file, or return an empty dictionary if the file does not exist."""
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as file:
            return json.load(file)
    return {}


def load_key():
    """Load the encryption key from a file or return None if not found."""
    key_file = ".secret.key"
    if os.path.exists(key_file):
        with open(key_file, "rb") as file:
            return file.read()
    else:
        return None


class JenkinsFrame(ctk.CTkFrame):
    ORDER = 5
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.settings = load_settings()
        self.build_history = []

        # Store the expanded state for each item
        self.expanded_state = {}

        # Load the encryption key
        self.key = load_key()
        if self.key:
            self.cipher_suite = Fernet(self.key)

        # Credentials
        self.username = None
        self.password = None

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
        # Bind right-click event to show context menu
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Create a context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Show Logs", command=self.show_logs)

        # Textbox to show logs
        self.log_textbox = ctk.CTkTextbox(self, wrap="word", height=10)
        self.log_textbox.pack(pady=10, fill="both", expand=True)

        self.load_credential_data()

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


        if not self.username or not self.password:
            messagebox.showerror("Error", "Credentials have not been defined in the settings.")
            return

        # Start log retrieval for the parent build
        self.build_history = []  # Reset history
        self._retrieve_build_logs(build_url, parent=None)

        # Update Treeview
        self._update_treeview()

    def _retrieve_build_logs(self, build_url, parent):
        try:
            # Make a request to retrieve the logs using authentication
            response = requests.get(f"{build_url}/consoleText", auth=(self.username, self.password))
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
                self._retrieve_build_logs(subsequent_build_url, parent=build_entry)

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

    def show_context_menu(self, event):
        """Show context menu on right-click."""
        # Select the item that was right-clicked
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)  # Set the selected item
            self.context_menu.post(event.x_root, event.y_root)

    def show_logs(self):
        """Show logs for the selected build."""
        item_id = self.tree.selection()[0]
        build = self._find_build_by_item(self.build_history, item_id)
        if build:
            # Display the logs in the log_textbox
            self.log_textbox.delete(1.0, tk.END)
            self.log_textbox.insert(tk.END, build['logs'])

    def _find_build_by_item(self, build_list, item_id):
        """Find the build data by treeview item ID."""
        for build in build_list:
            if build.get('treeview_item_id') == item_id:
                return build
            if build['children']:
                result = self._find_build_by_item(build['children'], item_id)
                if result:
                    return result
        return None

    def load_credential_data(self):
        """Load the username and encrypted password from settings.json and decrypt the password."""
        settings = self.settings
        if "username" in settings:
            self.username = self.settings.get("username")
        if "password" in settings:
            self.password = self.decrypt_password(self.settings.get("password"))