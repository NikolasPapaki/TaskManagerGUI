import customtkinter as ctk
import json
from custom_widgets import CustomInputDialog
from SharedObjects import *
import requests
from tkinter import messagebox


def _pad_names(names, max_length):
    return [name.ljust(max_length) for name in names]


class PasswordRetrieverFrame(ctk.CTkFrame):
    def __init__(self, parent, main_window):
        super().__init__(parent)

        self.parent = parent
        self.environment_manager = Environments(parent=self)
        self.settings_manager = Settings()
        self.credential_manager = EnvironmentCredentials()

        self.users = []
        self.client_token = None

        # Frame title
        title_label = ctk.CTkLabel(self, text="Password Retriever", font=("Arial", 24))
        title_label.pack(pady=10)

        self.combobox_width = 350
        # Pad environment options for consistent dropdown width
        self.environments = _pad_names(
            self.environment_manager.get_environments(),
            int(self.combobox_width // 4.3)
        )

        # Create an environment frame
        self.environment_frame = ctk.CTkFrame(self,  fg_color=self.cget("fg_color"))
        self.environment_frame.pack(pady=20, padx=20, fill="x", expand=False)

        # Add a label above the combobox
        self.environment_label = ctk.CTkLabel(
            self.environment_frame,
            text="Select Environment:",
            font=("Arial", 14)
        )
        self.environment_label.pack(pady=(10, 5), padx=10)

        # Create and configure the combobox inside the environment frame
        self.environment_combobox = ctk.CTkComboBox(
            master=self.environment_frame,
            values=self.environments,
            width=self.combobox_width,
            state="readonly"
        )
        if self.environments:
            self.environment_combobox.set(self.environments[0])
        self.environment_combobox.pack(pady=10, padx=10)

        # Frame for buttons
        self.button_frame = ctk.CTkFrame(self,  fg_color=self.cget("fg_color"))
        self.button_frame.pack(fill="x", pady=5, padx=10, anchor="w")

        # Buttons (next to each other)
        self.app_users_button = ctk.CTkButton(self.button_frame, text="App Users", command=lambda :self.get_app_users_password())
        self.app_users_button.pack(side="left", padx=5)

        self.admin_users_button = ctk.CTkButton(self.button_frame, text="Admin Users", command=lambda :self.get_admin_users_password())
        self.admin_users_button.pack(side="left", padx=5)

        self.specific_user_button = ctk.CTkButton(self.button_frame, text="Specific User", command=lambda :self.get_specific_user_password())
        self.specific_user_button.pack(side="left", padx=5)

        # Text entry for JSON display
        self.result_textbox = ctk.CTkTextbox(self)
        self.result_textbox.pack(padx=5, pady=5, expand=True, fill='both')

    def load_json_file(self, filepath):
        """Load JSON file and display it in the text box."""
        try:
            with open(filepath, "r") as file:
                data = json.load(file)
                formatted_data = json.dumps(data, indent=4)
                self.users = formatted_data
        except FileNotFoundError:
            self.result_textbox.delete("1.0", ctk.END)
            self.result_textbox.insert("1.0", "File not found.")
        except json.JSONDecodeError:
            self.result_textbox.delete("1.0", ctk.END)
            self.result_textbox.insert("1.0", "Error decoding JSON.")

    def get_app_users_password(self):
        """Load app users JSON."""
        self.load_json_file("users/app.json")

    def get_admin_users_password(self):
        """Load admin users JSON."""
        self.load_json_file("users/admin.json")

    def get_specific_user_password(self):
        """Show a dialog to add a specific user and display placeholder JSON."""
        dialog = CustomInputDialog(parent=self, fields=["Username"], title="Add Specific User")
        username = dialog.show()
        if username:
            specific_user_data = {"username": username[0], "password": "********"}
            formatted_data = json.dumps(specific_user_data, indent=4)
            self.result_textbox.delete("1.0", ctk.END)
            self.result_textbox.insert("1.0", formatted_data)



    def get_passwords(self):
        self.result_textbox.delete("1.0", ctk.END)

        selected_environment = self.environment_combobox.get().strip()
        environment_details = self.environment_manager.get_environment(selected_environment)
        host = environment_details.get("host", None)
        service = environment_details.get("service_name", None)
        unique_name = str(host) + "_" + str(service)

        for user in self.users:
            success, password, local = self.get_credentials(user, service, unique_name)

            if success:
                formatted_data = json.dumps({"username": user, "password": password}, indent=4)
                self.result_textbox.insert("1.0", formatted_data)



    def get_credentials(self, username, service_name, unique_name):
        if self.credential_manager.exists(unique_name, username):
            return True, self.credential_manager.get(unique_name).get(username), True

        elif self.vault_defined() and self.is_rds():

            if self.client_token is None:

                decrypted_role_id = self.cipher_suite.decrypt(self.settings_manager.settings["role_id"].encode()).decode()
                decrypted_secret_id = self.cipher_suite.decrypt(self.settings_manager.settings["secret_id"].encode()).decode()

                build_data = f'"role_id": "{str(decrypted_role_id)}", "secret_id": "{str(decrypted_secret_id)}"'

                client_token_response = requests.post(self.settings_manager.get("vault_url") + "/v1/auth/approle/login",
                                                      headers={"Content-Type": "application/json"},
                                                      data="{" + build_data + "}",
                                                      verify=False)

                if client_token_response.status_code != 200:
                    messagebox.showerror("Error",
                                         f"Failed to retrieve client token for vault. Status code {client_token_response.status_code}")
                    return False, None, None

                self.client_token = client_token_response.json().get("auth").get("client_token")

            user_category = "app" if "app" in username.lower() else "admin"
            prime_pattern = r"\w+pd\d+"
            system = "prime" if re.match(prime_pattern, service_name.lower()) else "online"
            url = f"{self.settings_manager.get('vault_url')}/v1/secret/tct{system}%2Fdb%2Foracle%2F{user_category}%2Feu-central-1-{service_name.lower()}%2F{system}%2F{username.lower()}"
            response = requests.get(url, headers={"X-Vault-Token": self.client_token}, verify=False)

            if response.status_code != 200:
                messagebox.showerror("Error",
                                     f"Failed to retrieve credentials for {service_name}. Status code {response.status_code}")
                return False, None, None

            password = response.json().get('data').get('password')

            if self.settings_manager.get("save_healthcheck_credentials_locally", False):
                self.credential_manager.add_or_update(unique_name, username, password)

            return True, password, False

        elif self.is_rds():
            if messagebox.askyesno("Input Required", f"It appears that neither vault settings or default passwords have not been configured\n Would you like to provide password manually"):
                dialog = CustomInputDialog(
                    title=f"Provide Password for {username.upper()} of {service_name}",
                    parent=self,
                    fields=["Password"]
                )
                result = dialog.show()

                # If the user cancels the dialog, return the original template
                if result is None or result == "":
                    return False, None, None

                else:
                    if self.settings_manager.get("save_healthcheck_credentials_locally", False):
                        self.credential_manager.add_or_update(unique_name, username, result[0])
                    return True, result[0], True  # We only have password here
            else:
                return False, None, None
        else:
            if messagebox.askyesno("Input Required", f"It appears this is not an RDS instance and default passwords have not been configured\n Would you like to provide password manually"):
                dialog = CustomInputDialog(
                    title=f"Provide Password for {username.upper()} of {service_name}",
                    parent=self,
                    fields=["Password"]
                )
                result = dialog.show()

                # If the user cancels the dialog, return the original template
                if result is None or result == "":
                    return False, None, None

                else:
                    if self.settings_manager.get("save_healthcheck_credentials_locally", False):
                        self.credential_manager.add_or_update(unique_name, username, result[0])
                    return True, result[0], True  # We only have password here
            else:
                return False, None, None


    def vault_defined(self) -> bool:
        return self.settings_manager.exists("role_id") and self.settings_manager.exists("secret_id") and self.settings_manager.exists("vault_url")
