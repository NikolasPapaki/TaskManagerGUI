import tkinter as tk
import customtkinter as ctk
import requests
from requests_oauthlib import OAuth2Session
from tkinter import messagebox
import json
import threading
from tkinter import ttk
import os


class ApiRequestFrame(ctk.CTkFrame):
    ORDER = 5
    def __init__(self, parent):
        super().__init__(parent)
        self.history_file = 'api_history.json'

        self.parent = parent

        # OAuth session and token variables
        self.oauth_session = None
        self.access_token = None
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = None
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
        self.params_entry = ctk.CTkTextbox(request_frame, width=400, height=12)  # Increased height for a bigger area
        self.params_entry.pack(fill="both", padx=20, pady=5, expand=True)

        # Response Textbox for displaying the response body
        response_label = ctk.CTkLabel(request_frame, text="Response Body:")
        response_label.pack(anchor="w", padx=10)
        self.response_textbox = ctk.CTkTextbox(request_frame, width=400, height=12)  # Increased height for a bigger area
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

        # Adjust column widths if needed
        self.history_tree.column("type", width=100, anchor="center")
        self.history_tree.column("url", width=300, anchor="w")
        self.history_tree.column("status", width=100, anchor="center")

        self.history_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.history_tree.bind("<Double-1>", self.load_from_history)

        # Create the context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Delete", command=self.delete_item)

        # Bind right-click to show context menu
        self.history_tree.bind("<Button-3>", self.show_context_menu)

        self.selected_item = None

        self.load_history_from_file()

    def open_oauth_popup(self):
        """Open a popup to enter OAuth credentials."""
        popup = ctk.CTkToplevel(self)
        popup.title("OAuth2.0 Credentials")
        popup.attributes("-topmost", True)  # Keep the popup on top of the main UI
        popup.transient(self.parent)  # Make the popup modal relative to the main window

        # Client ID
        client_id_label = ctk.CTkLabel(popup, text="Client ID:")
        client_id_label.pack(padx=10, pady=5)
        client_id_entry = ctk.CTkEntry(popup, width=300)
        client_id_entry.pack(padx=10, pady=5)

        # Client Secret
        client_secret_label = ctk.CTkLabel(popup, text="Client Secret:")
        client_secret_label.pack(padx=10, pady=5)
        client_secret_entry = ctk.CTkEntry(popup, width=300, show="*")
        client_secret_entry.pack(padx=10, pady=5)

        # Redirect URI
        redirect_uri_label = ctk.CTkLabel(popup, text="Redirect URI:")
        redirect_uri_label.pack(padx=10, pady=5)
        redirect_uri_entry = ctk.CTkEntry(popup, width=300)
        redirect_uri_entry.pack(padx=10, pady=5)

        # Save Button
        save_button = ctk.CTkButton(popup, text="Save", command=lambda: self.save_oauth_credentials(
            client_id_entry.get(), client_secret_entry.get(), redirect_uri_entry.get(), popup))
        save_button.pack(pady=10)

    def save_oauth_credentials(self, client_id, client_secret, redirect_uri, popup):
        """Save the OAuth credentials."""
        if client_id and client_secret and redirect_uri:
            self.client_id = client_id
            self.client_secret = client_secret
            self.redirect_uri = redirect_uri
            messagebox.showinfo("OAuth2.0", "OAuth credentials saved successfully!")
            popup.destroy()  # Close the popup
        else:
            messagebox.showerror("Error", "All fields must be filled.")

    def authenticate(self):
        """Authenticate with OAuth2.0 and get the access token."""
        if not self.client_id or not self.client_secret or not self.redirect_uri:
            messagebox.showerror("Error", "OAuth credentials are missing. Please add them first.")
            return

        authorization_base_url = "https://example.com/oauth/authorize"
        token_url = "https://example.com/oauth/token"

        # Create an OAuth2 session
        oauth = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri)

        # Step 1: Get authorization URL
        authorization_url, state = oauth.authorization_url(authorization_base_url)

        # Step 2: Redirect the user to the authorization URL
        messagebox.showinfo("OAuth2.0", f"Please visit this URL to authorize the app:\n{authorization_url}")

        # The user will manually visit the URL and then we get the authorization code
        auth_response = input("Paste the full redirect URL after authorization: ")

        # Step 3: Get the access token
        self.oauth_session = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri, state=state)
        self.access_token = self.oauth_session.fetch_token(
            token_url,
            authorization_response=auth_response,
            client_secret=self.client_secret
        )
        messagebox.showinfo("OAuth2.0", "Authentication successful!")

    def send_request_in_thread(self):
        """Runs the send_request method in a separate thread to keep the UI responsive."""
        threading.Thread(target=self.send_request).start()

    def send_request(self):
        """Send an API request based on user input and display the response status code."""

        # Disable the UI while the request is being sent
        self.response_label.configure(text="Sending request...")
        self.response_textbox.configure(state="normal")
        self.response_textbox.delete("1.0", "end")
        self.response_textbox.configure(state="disabled")

        request_type = self.request_type_var.get()
        url = self.url_entry.get().strip()
        params = self.parse_parameters(self.params_entry.get("1.0", "end-1c").strip())  # Get the JSON body

        try:
            # If oauth_session is not set, attempt to call the API without OAuth
            if self.oauth_session:
                # If oauth_session is available, use it to send the request
                response = None
                if request_type == "GET":
                    response = self.oauth_session.get(url, params=params)
                elif request_type in ["POST", "PUT", "DELETE"]:
                    response = self.oauth_session.request(request_type, url, json=params)
            else:
                # If no oauth_session, proceed without authentication
                response = None
                if request_type == "GET":
                    response = requests.get(url, params=params)
                elif request_type in ["POST", "PUT", "DELETE"]:
                    response = requests.request(request_type, url, json=params)

            # Update the UI with response
            if response is not None:
                self.save_to_history(request_type,url,params,response)
                self.response_label.configure(text=f"Response Code: {response.status_code}")

                try:
                    # Try to parse JSON response and display it prettily
                    response_json = response.json()
                    pretty_json = json.dumps(response_json, indent=4)
                    self.response_textbox.configure(state="normal")
                    self.response_textbox.delete("1.0", "end")
                    self.response_textbox.insert("1.0", pretty_json)
                    self.response_textbox.configure(state="disabled")
                except ValueError:
                    # If the response isn't JSON, show it as text
                    self.response_textbox.configure(state="normal")
                    self.response_textbox.delete("1.0", "end")
                    self.response_textbox.insert("1.0", response.text)
                    self.response_textbox.configure(state="disabled")
            else:
                messagebox.showerror("Error", "Invalid request type selected.")
        except requests.RequestException as e:
            messagebox.showerror("Request Error", f"An error occurred: {e}")

    def parse_parameters(self, param_str):
        """Parse JSON string for the request body."""
        if param_str:
            try:
                return json.loads(param_str)
            except json.JSONDecodeError:
                messagebox.showerror("Invalid JSON", "Please enter a valid JSON format.")
                self.response_label.configure(text=f"Invalid JSON format!")
                exit()
        return {}

    def save_to_history(self, request_type, url, params, response):
        """Insert a history item with an iid."""
        iid = f"item_{len(self.history)}"  # or use UUID or another unique identifier
        history_item = {
            "iid": iid,  # Store iid in the history entry
            "type": request_type,
            "url": url,
            "status": response.status_code,
            "params": params,
            "response": response.text
        }
        self.history.append(history_item)
        self.update_history_treeview()  # Refresh the treeview

    def delete_item(self):
        """Delete the selected item from the Treeview and update the history."""
        if hasattr(self, 'selected_item'):
            iid = self.selected_item  # Get the selected item's iid
            # Find and remove the corresponding history entry based on iid
            self.history = [entry for entry in self.history if entry["iid"] != iid]

            # Delete the item from the Treeview using its iid
            self.history_tree.delete(iid)

            # Save the updated history to file
            self.save_history_to_file()  # Save the updated history to file

    def update_history_treeview(self):
        """Update the Treeview with the current history."""
        # Clear the existing entries in the Treeview
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Add each history entry as a new row in the Treeview with a unique iid
        for entry in self.history:
            iid = entry["iid"]  # Use the iid from the history entry
            self.history_tree.insert("", "end", iid=iid, values=(entry["type"], entry["url"], entry["status"]))

    def save_history_to_file(self):
        """Save request history to a JSON file."""
        try:
            with open(self.history_file, "w") as file:
                json.dump(self.history, file, indent=4)
        except IOError as e:
            print(f"Error saving history: {e}")

    def load_from_history(self, event):
        """Load selected request from history into input fields for replay."""
        selected_item = self.history_tree.selection()
        if selected_item:
            item_index = self.history_tree.index(selected_item[0])  # Get index of selected item
            entry = self.history[item_index]

            # Load request details back into input fields
            self.request_type_var.set(entry["type"])
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, entry["url"])
            self.params_entry.delete("1.0", "end")
            self.params_entry.insert("1.0", json.dumps(entry["params"], indent=4))

            # Display the response in the response textbox
            self.response_textbox.configure(state="normal")
            self.response_textbox.delete("1.0", "end")
            self.response_textbox.insert("1.0", entry["response"])
            self.response_textbox.configure(state="disabled")
            self.response_label.configure(text=f"Response Code: {entry['status']}")

    def load_history_from_file(self):
        """Load request history from a JSON file if it exists."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as file:
                    self.history = json.load(file)
                    # Populate Treeview with loaded history
                    for entry in self.history:
                        # Use the correct keys as per your history structure
                        self.history_tree.insert("", "end",
                                                 values=(entry["type"], entry["url"], entry["status"]))
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error loading history: {e}")
                self.history = []  # Initialize with an empty list if there's an error
        else:
            self.history = []

    def show_context_menu(self, event):
        """Show the context menu when right-clicking on an item."""
        # Get the item under the mouse pointer
        item = self.history_tree.identify_row(event.y)
        if item:
            self.context_menu.post(event.x_root, event.y_root)
            self.selected_item = item  # Store the selected item's iid
