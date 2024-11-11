import tkinter

import customtkinter as ctk
import requests
from tkinter import messagebox
from tkinter import ttk
import os
import json
from cryptography.fernet import Fernet

class JenkinsFrame(ctk.CTkFrame):
    HISTORY_FILE = "job_history.json"  # File to store job history
    ORDER = 5
    def __init__(self, parent):
        super().__init__(parent)

        # Load the encryption key (this key should be kept secret or stored securely)
        self.key = self.load_key()
        if self.key:
            self.cipher_suite = Fernet(self.key)

        # Title frame and label
        title_frame = ctk.CTkFrame(self)
        title_frame.pack(pady=(10, 5), padx=10, fill="x")

        label = ctk.CTkLabel(title_frame, text="Jenkins Job Trigger", font=("Arial", 24))
        label.pack(pady=20)

        # Body frame
        body_frame = ctk.CTkFrame(self)
        body_frame.pack(pady=(10, 5), padx=10, fill="x")

        # Set the default text color for error messages based on frame color
        default_text_color = self.cget('fg_color')  # Get the frame's foreground color (text color)

        # Jenkins URL Entry
        self.url_entry_frame = ctk.CTkFrame(body_frame)
        self.url_entry_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(self.url_entry_frame, text="Jenkins URL:").pack(side="left", anchor="w", padx=10)
        self.url_entry = ctk.CTkEntry(self.url_entry_frame, width=300)
        self.url_entry.pack(side="left", pady=5)
        self.url_error_message = ctk.CTkLabel(self.url_entry_frame, text="Field URL is required", text_color=default_text_color)
        self.url_error_message.pack(side="left", padx=5, anchor="w")

        # Username Entry
        self.username_entry_frame = ctk.CTkFrame(body_frame)
        self.username_entry_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(self.username_entry_frame, text="Username:").pack(side="left", anchor="w", padx=10)
        self.username_entry = ctk.CTkEntry(self.username_entry_frame, width=300)
        self.username_entry.pack(side="left", pady=5)
        self.username_error_message = ctk.CTkLabel(self.username_entry_frame, text="Field Username is required", text_color=default_text_color)
        self.username_error_message.pack(side="left", padx=5, anchor="w")

        # Password Entry
        self.password_entry_frame = ctk.CTkFrame(body_frame)
        self.password_entry_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(self.password_entry_frame, text="Password:").pack(side="left", anchor="w", padx=10)
        self.password_entry = ctk.CTkEntry(self.password_entry_frame, width=300, show="*")
        self.password_entry.pack(side="left", pady=5)
        self.password_error_message = ctk.CTkLabel(self.password_entry_frame, text="Field Password is required", text_color=default_text_color)
        self.password_error_message.pack(side="left", padx=5, anchor="w")

        # Job Name Entry
        self.job_entry_frame = ctk.CTkFrame(body_frame)
        self.job_entry_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(self.job_entry_frame, text="Job Name:").pack(side="left", anchor="w", padx=10)
        self.job_entry = ctk.CTkEntry(self.job_entry_frame, width=300)
        self.job_entry.pack(side="left", pady=5)
        self.job_error_message = ctk.CTkLabel(self.job_entry_frame, text="Field Job Name is required", text_color=default_text_color)
        self.job_error_message.pack(side="left", padx=5, anchor="w")

        # Parameters Entry (optional) with Enable/Disable checkbox
        self.params_entry_frame = ctk.CTkFrame(body_frame)
        self.params_entry_frame.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(self.params_entry_frame, text="Parameters (optional):").pack(side="left", anchor="w", padx=10)
        self.params_entry = ctk.CTkEntry(self.params_entry_frame, width=300)
        self.params_entry.pack(side="left", pady=5)

        # Checkbox to enable/disable parameters entry
        self.params_checkbox = ctk.CTkCheckBox(
            self.params_entry_frame,
            text="Enable Parameters",
            command=self.toggle_params_entry
        )
        self.params_checkbox.pack(side="left", padx=10)

        # Set initial state of the parameters entry and checkbox
        self.params_entry.configure(state="disabled")
        self.params_checkbox.deselect()

        # Trigger Button
        trigger_button = ctk.CTkButton(body_frame, text="Trigger Job", command=self.trigger_jenkins_job)
        trigger_button.pack(pady=20)

        # Frame for displaying previously triggered jobs (Treeview)
        self.previous_jobs_frame = ctk.CTkFrame(self)
        self.previous_jobs_frame.pack(pady=(10, 5), padx=10, fill="both", expand=True)

        # Title label for previous jobs
        prev_jobs_label = ctk.CTkLabel(self.previous_jobs_frame, text="Previously Triggered Jobs", font=("Arial", 18))
        prev_jobs_label.pack(pady=10)

        # Create the Treeview widget for displaying job history
        self.treeview = ttk.Treeview(self.previous_jobs_frame, columns=("Job Name", "URL", "Parameters"), show="headings")
        self.treeview.pack(pady=10, padx=20, fill="both", expand=True)

        # Bind the treeview selection event to the function
        self.treeview.bind("<<TreeviewSelect>>", self.select_job_from_history)

        # Create a right-click menu
        self.treeview_menu = tkinter.Menu(self, tearoff=0)
        self.treeview_menu.add_command(label="Delete", command=self.delete_selected_job)

        # Bind right-click to display the context menu
        self.treeview.bind("<Button-3>", self.show_treeview_menu)

        # Set up the column headings
        self.treeview.heading("Job Name", text="Job Name")
        self.treeview.heading("URL", text="URL")
        self.treeview.heading("Parameters", text="Parameters")

        # Load settings
        self.settings = self.load_settings()

        # Load previous job history on startup
        self.load_job_history()

        # Load credentials if are saved
        self.load_credential_data()

    def show_treeview_menu(self, event):
        # Select the row under the cursor and display the menu
        row_id = self.treeview.identify_row(event.y)
        if row_id:
            self.treeview.selection_set(row_id)
            self.treeview_menu.post(event.x_root, event.y_root)

    def toggle_params_entry(self):
        if self.params_checkbox.get():
            self.params_entry.configure(state="normal")
        else:
            self.params_entry.delete(0,tkinter.END)
            self.params_entry.configure(state="disabled")


    def trigger_jenkins_job(self):
        # Check validation
        if not self.validate_entries():
            return

        # Give option to save credentials
        if "username" not in self.settings or "password" not in self.settings:
            confirm = messagebox.askyesno("Confirm", "Would you like to save credentials")
            if confirm:
                self.save_credential_data()

        # Show confirmation dialog
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to trigger this job?")

        if confirm:
            # Retrieve the input values
            url = self.url_entry.get().strip("/")
            username = self.username_entry.get()
            password = self.password_entry.get()
            job_name = self.job_entry.get()
            parameters = self.params_entry.get()

            # Build the Jenkins job URL
            job_url = f"{url}/job/{job_name}/buildWithParameters"

            # Prepare parameters if provided
            params = {}
            if self.params_checkbox.get():
                # Expecting parameters in the form key=value,key2=value2
                try:
                    param_pairs = parameters.split(",")
                    params = dict(pair.split("=") for pair in param_pairs)
                except Exception:
                    messagebox.showwarning("Error", "An error occurred parsing the parameter.")
                    return

            self.add_job_to_history(job_name, url, parameters)  # Add job to history if successful

            try:
                # Send the POST request to trigger the Jenkins job
                response = requests.post(job_url, auth=(username, password), params=params if params else None)

                # Check the response status
                if response.status_code == 201:
                    # The URL of the triggered build will be in the response's 'Location' header
                    build_url = response.headers.get('Location')

                    if build_url:
                        # Now, we can make a GET request to the build URL to fetch build information
                        build_response = requests.get(build_url, auth=(username, password))

                        if build_response.status_code == 200:
                            build_data = build_response.json()
                            build_number = build_data.get('number')  # Get the build number
                            messagebox.showinfo("Success", f"Job triggered successfully! Build number: {build_number}")

                            # You can store the build number in your job history if needed
                            self.add_job_to_history(job_name, url, parameters)  # Add job to history if successful

                        else:
                            messagebox.showerror("Error",
                                                 f"Failed to fetch build details. Status code: {build_response.status_code}")
                    else:
                        messagebox.showerror("Error", "Failed to get the build URL.")

                elif response.status_code == 404:
                    messagebox.showerror("Error", "Job not found. Check the job name.")
                else:
                    messagebox.showerror("Error", f"Failed to trigger job. Status code: {response.status_code}")
            except requests.RequestException as e:
                messagebox.showerror("Request Error", f"An error occurred: {e}")

    def validate_entries(self):
        """Checks that all required fields are filled and highlights any empty ones."""
        # Set border color back to gray as default before validation
        default_border_color = "gray"

        # Reset each entry’s border color and error message color
        for entry_attr, error_message_attr in [
            ("url_entry", "url_error_message"),
            ("username_entry", "username_error_message"),
            ("password_entry", "password_error_message"),
            ("job_entry", "job_error_message"),
        ]:
            entry = getattr(self, entry_attr)
            error_message = getattr(self, error_message_attr)
            entry.configure(border_color=default_border_color)  # Reset to default gray color
            error_message.configure(text_color="gray")  # Reset error message color to default (gray)
            error_message.pack_forget()  # Hide error message initially

        # Validate each entry and set border color to red if empty
        is_valid = True
        if not self.url_entry.get():
            self.url_entry.configure(border_color="red")
            self.url_error_message.configure(text_color="red")  # Change to red on error
            self.url_error_message.pack(side="left", padx=5, anchor="w")  # Show the error message
            is_valid = False
        if not self.username_entry.get():
            self.username_entry.configure(border_color="red")
            self.username_error_message.configure(text_color="red")  # Change to red on error
            self.username_error_message.pack(side="left", padx=5, anchor="w")  # Show the error message
            is_valid = False
        if not self.password_entry.get():
            self.password_entry.configure(border_color="red")
            self.password_error_message.configure(text_color="red")  # Change to red on error
            self.password_error_message.pack(side="left", padx=5, anchor="w")  # Show the error message
            is_valid = False
        if not self.job_entry.get():
            self.job_entry.configure(border_color="red")
            self.job_error_message.configure(text_color="red")  # Change to red on error
            self.job_error_message.pack(side="left", padx=5, anchor="w")  # Show the error message
            is_valid = False

        return is_valid

    def load_job_history(self):
        """Loads the job history from the HISTORY_FILE."""
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "r") as file:
                job_history = json.load(file)
                for job in job_history:
                    self.treeview.insert("", "end", values=(job["job_name"], job["url"], job.get("parameters", "")))

    def add_job_to_history(self, job_name, url, parameters):
        """Saves the triggered job to history and adds it to the Treeview, but doesn't add duplicates."""
        # Load current job history
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "r") as file:
                job_history = json.load(file)
        else:
            job_history = []

        # Check if the job already exists in history (same job_name, url, and parameters)
        for job in job_history:
            if job["job_name"] == job_name and job["url"] == url and job["parameters"] == parameters:
                # If the job already exists, do not add it again
                return

        # Save the new job history excluding sensitive data
        job_history.append({
            "job_name": job_name,
            "url": url,
            "parameters": parameters,
        })

        # Write updated history back to the file
        with open(self.HISTORY_FILE, "w") as file:
            json.dump(job_history, file, indent=4)

        # Add the job to the Treeview
        self.treeview.insert("", "end", values=(job_name, url, parameters))

    def select_job_from_history(self, event):
        """Populate the entry fields when a job is selected from the Treeview."""
        # Get selected item
        selected_item = self.treeview.selection()

        if selected_item:
            # Get values of the selected row
            job_name, url, parameters = self.treeview.item(selected_item, "values")

            # Populate the fields
            self.job_entry.delete(0, "end")  # Clear the existing value
            self.job_entry.insert(0, job_name)  # Set the job name

            self.url_entry.delete(0, "end")  # Clear the existing value
            self.url_entry.insert(0, url)  # Set the URL

            # Params checkbox is enabled so just add the value
            if parameters:
                if not self.params_checkbox.get():
                    self.params_checkbox.select()
                    self.toggle_params_entry()

                self.params_entry.delete(0, "end")  # Clear the existing value
                self.params_entry.insert(0, parameters)  # Set the parameters
            else:
                self.params_checkbox.deselect()
                self.params_entry.delete(0, "end")  # Clear the existing value




    def load_settings(self):
        """Load settings from the JSON file, or return an empty dictionary if the file does not exist."""
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as file:
                return json.load(file)
        return {}

    def load_credential_data(self):
        """Load the username and encrypted password from settings.json and decrypt the password."""
        settings = self.settings
        if "username" in settings:
            self.username_entry.insert(0, settings["username"])
        if "password" in settings:
            encrypted_password = settings["password"]
            decrypted_password = self.cipher_suite.decrypt(encrypted_password.encode()).decode()
            self.password_entry.insert(0, decrypted_password)

    def load_key(self):
        """Load the encryption key from a file or generate a new one if not found."""
        key_file = ".secret.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as file:
                return file.read()
        else:
            return None

    def save_credential_data(self):
        """Save the username and encrypted password to settings.json."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Encrypt the password
        encrypted_password = self.cipher_suite.encrypt(password.encode()).decode()

        # Save to settings.json
        self.save_settings("username", username)
        self.save_settings("password", encrypted_password)


    def save_settings(self, key, value):
        settings = self.settings
        settings[key] = value  # Update the specific setting

        with open("settings.json", "w") as file:
            json.dump(settings, file, indent=4)

    def delete_selected_job(self):
        # Get the selected item from the Treeview
        selected_item = self.treeview.selection()
        if selected_item:
            # Get values of the selected item to match in history
            job_name, url, parameters = self.treeview.item(selected_item, "values")

            # Delete the selected item from the Treeview
            self.treeview.delete(selected_item)

            # Load current job history
            if os.path.exists(self.HISTORY_FILE):
                with open(self.HISTORY_FILE, "r") as file:
                    job_history = json.load(file)

                # Remove the matching job from the job history list
                updated_history = [
                    job for job in job_history
                    if
                    not (job["job_name"] == job_name and job["url"] == url and job.get("parameters", "") == parameters)
                ]

                # Write the updated history back to the file
                with open(self.HISTORY_FILE, "w") as file:
                    json.dump(updated_history, file, indent=4)
