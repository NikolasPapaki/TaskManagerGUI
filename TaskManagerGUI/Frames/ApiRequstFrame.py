import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import json
import threading
from tkinter import ttk
import os
import base64

import certifi
import sys

# Use the bundled certifi file if running as an executable
if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller bundle
    certifi_path = os.path.join(sys._MEIPASS, 'certifi', 'cacert.pem')
else:  # Fallback for normal Python execution
    certifi_path = certifi.where()

# Set the path for requests
import requests
requests.utils.DEFAULT_CA_BUNDLE_PATH = certifi_path


class ApiRequestFrame(ctk.CTkFrame):
    ORDER = 6

    def __init__(self, parent):
        super().__init__(parent)
        self.history_file = 'api_history.json'

        self.parent = parent
        self.access_token_url = None
        self.client_id = None
        self.client_secret = None
        self.scope = None
        self.access_token = None
        self.history = []

        # Title for the API Request Tool
        title_label = ctk.CTkLabel(self, text="API Request Tool", font=("Arial", 24))
        title_label.pack(pady=20)

        # Frame to contain both request details and history side-by-side
        main_content_frame = ctk.CTkFrame(self)
        main_content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left frame for request inputs
        request_frame = ctk.CTkFrame(main_content_frame)
        request_frame.pack(side="left", fill="both", expand=True)

        # Request Type Dropdown (GET, POST, PUT, DELETE)
        self.request_type_var = tk.StringVar(value="GET")
        request_type_label = ctk.CTkLabel(request_frame, text="Request Type:")
        request_type_label.pack(anchor="w", padx=10)
        self.request_type_menu = ctk.CTkOptionMenu(request_frame, variable=self.request_type_var,
                                                   values=["GET", "POST", "PUT", "DELETE"])
        self.request_type_menu.pack(fill="x", padx=20, pady=5)

        # URL Entry
        url_label = ctk.CTkLabel(request_frame, text="API URL:")
        url_label.pack(anchor="w", padx=10)
        self.url_entry = ctk.CTkEntry(request_frame, width=400)
        self.url_entry.pack(fill="x", padx=20, pady=5)

        # Parameters Entry (JSON format)
        params_label = ctk.CTkLabel(request_frame, text="Request Body (JSON format):")
        params_label.pack(anchor="w", padx=10)
        self.params_entry = ctk.CTkTextbox(request_frame, width=400, height=12)
        self.params_entry.pack(fill="both", padx=20, pady=5, expand=True)

        # Response Textbox for displaying the response body
        response_label = ctk.CTkLabel(request_frame, text="Response Body:")
        response_label.pack(anchor="w", padx=10)
        self.response_textbox = ctk.CTkTextbox(request_frame, width=400, height=12)
        self.response_textbox.pack(fill="both", padx=20, pady=5, expand=True)
        self.response_textbox.configure(state="disabled")

        # Response Status Label
        self.response_label = ctk.CTkLabel(request_frame, text="")
        self.response_label.pack(pady=10)

        # Send Request Button
        send_button = ctk.CTkButton(request_frame, text="Send Request", command=self.send_request_in_thread)
        send_button.pack(side="left", padx=10, pady=20)

        # OAuth Button
        self.auth_button = ctk.CTkButton(request_frame, text="OAuth Settings", command=self.open_oauth_popup)
        self.auth_button.pack(side="left", padx=10, pady=20)

        # Right frame for request history
        history_frame = ctk.CTkFrame(main_content_frame)
        history_frame.pack(side="right", fill="y", padx=(10, 0))

        # Request History Label and Treeview in history_frame
        history_label = ctk.CTkLabel(history_frame, text="Request History:")
        history_label.pack(anchor="w", padx=10, pady=(20, 0))

        self.history_tree = ttk.Treeview(history_frame, columns=("type", "url", "status"), show="headings", height=20)
        self.history_tree.heading("type", text="Request Type")
        self.history_tree.heading("url", text="URL")
        self.history_tree.heading("status", text="Status Code")

        self.history_tree.column("type", width=100, anchor="center")
        self.history_tree.column("url", width=300, anchor="w")
        self.history_tree.column("status", width=100, anchor="center")

        self.history_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.history_tree.bind("<Double-1>", self.load_from_history)

        self.load_history_from_file()

    def open_oauth_popup(self):
        """Open a popup to enter OAuth credentials."""
        popup = ctk.CTkToplevel(self)
        popup.title("OAuth2.0 Credentials")
        popup.attributes("-topmost", True)
        popup.transient(self.parent)

        # Access Token URL
        access_token_url_label = ctk.CTkLabel(popup, text="Access Token URL:")
        access_token_url_label.pack(padx=10, pady=5)
        access_token_url_entry = ctk.CTkEntry(popup, width=300)
        access_token_url_entry.pack(padx=10, pady=5)
        access_token_url_entry.insert(0, self.access_token_url or "")

        # Client ID
        client_id_label = ctk.CTkLabel(popup, text="Client ID:")
        client_id_label.pack(padx=10, pady=5)
        client_id_entry = ctk.CTkEntry(popup, width=300)
        client_id_entry.pack(padx=10, pady=5)
        client_id_entry.insert(0, self.client_id or "")

        # Client Secret
        client_secret_label = ctk.CTkLabel(popup, text="Client Secret:")
        client_secret_label.pack(padx=10, pady=5)
        client_secret_entry = ctk.CTkEntry(popup, width=300, show="*")
        client_secret_entry.pack(padx=10, pady=5)
        client_secret_entry.insert(0, self.client_secret or "")

        # Scope
        scope_label = ctk.CTkLabel(popup, text="Scope:")
        scope_label.pack(padx=10, pady=5)
        scope_entry = ctk.CTkEntry(popup, width=300)
        scope_entry.pack(padx=10, pady=5)
        scope_entry.insert(0, self.scope or "")

        # Save Button
        save_button = ctk.CTkButton(popup, text="Save", command=lambda: self.save_oauth_credentials(
            access_token_url_entry.get(), client_id_entry.get(), client_secret_entry.get(), scope_entry.get(), popup))
        save_button.pack(pady=10)

    def save_oauth_credentials(self, access_token_url, client_id, client_secret, scope, popup):
        """Save the OAuth credentials and authenticate to retrieve the access token."""
        if access_token_url and client_id and client_secret and scope:
            self.access_token_url = access_token_url
            self.client_id = client_id
            self.client_secret = client_secret
            self.scope = scope

            # Attempt to authenticate immediately after saving credentials
            try:
                self.authenticate()
                messagebox.showinfo("OAuth2.0", "OAuth credentials saved and authenticated successfully!")
            except Exception as e:
                messagebox.showerror("Authentication Error", f"Failed to authenticate: {e}")

            popup.destroy()
        else:
            messagebox.showerror("Error", "All fields must be filled.")

    def authenticate(self):
        """Authenticate with OAuth2.0 using Basic Auth and retrieve the access token."""
        if not self.access_token_url or not self.client_id or not self.client_secret or not self.scope:
            messagebox.showerror("Error", "OAuth credentials are missing. Please add them first.")
            return

        # Basic Authentication header
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
            "scope": self.scope
        }

        try:
            response = requests.post(self.access_token_url, headers=headers, data=data)
            response.raise_for_status()
            self.access_token = response.json().get("access_token")
            messagebox.showinfo("OAuth2.0", f"Authentication successful! Access Token:\n{self.access_token}")
        except requests.RequestException as e:
            messagebox.showerror("Authentication Error", f"An error occurred: {e}")

    def send_request_in_thread(self):
        """Runs the send_request method in a separate thread to keep the UI responsive."""
        threading.Thread(target=self.send_request).start()

    def send_request(self):
        """Send an API request based on user input and display the response status code."""

        self.response_label.configure(text="Sending request...")
        self.response_textbox.configure(state="normal")
        self.response_textbox.delete("1.0", "end")
        self.response_textbox.configure(state="disabled")

        request_type = self.request_type_var.get()
        url = self.url_entry.get().strip()
        params = self.parse_parameters(self.params_entry.get("1.0", "end-1c").strip())
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}

        try:
            response = requests.request(request_type, url, headers=headers, json=params)
            self.response_label.configure(text=f"Status Code: {response.status_code}")

            # Check if the status code is not 404
            if response.status_code != 404:
                try:
                    response_json = response.json()
                    pretty_json = json.dumps(response_json, indent=4)
                    self.response_textbox.configure(state="normal")
                    self.response_textbox.insert("1.0", pretty_json)
                    self.response_textbox.configure(state="disabled")
                    self.save_to_history(request_type, url, response.status_code, params, pretty_json)
                except ValueError:
                    self.response_textbox.configure(state="normal")
                    self.response_textbox.insert("1.0", response.text)
                    self.response_textbox.configure(state="disabled")
                    self.save_to_history(request_type, url, response.status_code, params, response.text)
            else:
                self.response_textbox.configure(state="normal")
                self.response_textbox.insert("1.0", "Not Found (404)")
                self.response_textbox.configure(state="disabled")
                self.save_to_history(request_type, url, response.status_code, params, "Not Found (404)")

        except requests.RequestException as e:
            messagebox.showerror("Request Error", f"An error occurred: {e}")

    def save_to_history(self, request_type, url, status_code, params, response_body):
        """Save request details to the history file."""
        history_item = {
            "type": request_type,
            "url": url,
            "status_code": status_code,
            "params": params,
            "response_body": response_body,
            "oauth_credentials": {
                "access_token_url": self.access_token_url,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": self.scope
            }
        }
        self.history.append(history_item)
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

        self.history_tree.insert("", "end", values=(request_type, url, status_code))

    def load_history_from_file(self):
        """Load request history from the file."""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
                for item in self.history:
                    self.history_tree.insert("", "end", values=(item["type"], item["url"], item["status_code"]))

    def load_from_history(self, event):
        """Load request details from the selected history item."""
        selected_item = self.history_tree.selection()
        if selected_item:
            index = self.history_tree.index(selected_item[0])
            history_item = self.history[index]

            # Load request details
            self.request_type_var.set(history_item["type"])
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, history_item["url"])
            self.params_entry.delete("1.0", "end")
            self.params_entry.insert("1.0", json.dumps(history_item["params"], indent=4))

            # Load OAuth settings (excluding access token)
            oauth_credentials = history_item.get("oauth_credentials", {})
            self.access_token_url = oauth_credentials.get("access_token_url", "")
            self.client_id = oauth_credentials.get("client_id", "")
            self.client_secret = oauth_credentials.get("client_secret", "")
            self.scope = oauth_credentials.get("scope", "")

            self.response_textbox.configure(state="normal")
            self.response_textbox.delete("1.0", "end")
            self.response_textbox.insert("1.0", history_item.get("response_body", ""))
            self.response_textbox.configure(state="disabled")

    def parse_parameters(self, params_text):
        """Parse the JSON formatted parameters."""
        if not params_text.strip():  # Check if the input is empty or just whitespace
            return {}

        try:
            return json.loads(params_text)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format in parameters, ignored")
            return {}
