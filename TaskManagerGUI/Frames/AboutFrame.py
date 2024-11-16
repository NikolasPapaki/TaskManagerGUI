import customtkinter as ctk
from Update_module import VERSION

class AboutFrame(ctk.CTkFrame):
    ORDER = 99
    def __init__(self, master=None):
        super().__init__(master)

        self.label = ctk.CTkLabel(self, text="About Page", font=("Arial", 24))
        self.label.pack(pady=20)

        # App Information
        self.app_name = "Task Manager"
        self.version = VERSION
        self.last_updated = "November 11, 2024"
        self.description = "This app allows users to manage and run tasks efficiently."
        self.features = [
            "Feature 1: Task Creation",
            "Feature 2: Task execution",
            "Feature 3: Retrieve Jenkins logs",
            "Feature 4: Call an API (Under development)",
            "Feature 5: Add an oracle error stack and files will be opened in vscode"
        ]
        self.developer_name = "Nikolas Papaki"
        self.developer_email = "nikolaspapakis@hotmail.com"

        # Create Frames
        self.create_frames()

    def create_frames(self):
        # App Info Frame
        app_info_frame = ctk.CTkFrame(self)
        app_info_frame.pack(pady=(10, 5), padx=10, fill="x")

        # Title
        title_label = ctk.CTkLabel(app_info_frame, text=self.app_name, font=("Arial", 16, "bold"))
        title_label.pack(pady=(10, 5))

        # Version and Last Updated
        version_label = ctk.CTkLabel(app_info_frame, text=f"Version: {self.version}")
        version_label.pack(pady=(5, 0))

        last_updated_label = ctk.CTkLabel(app_info_frame, text=f"Last Updated: {self.last_updated}")
        last_updated_label.pack(pady=(0, 10))

        # Description Frame
        description_frame = ctk.CTkFrame(self)
        description_frame.pack(pady=(10, 5), padx=10, fill="x")

        # Description
        description_label = ctk.CTkLabel(description_frame, text="Description:")
        description_label.pack(anchor="w", padx=(10, 0))

        description_text = ctk.CTkLabel(description_frame, text=self.description)
        description_text.pack(anchor="w", padx=(10, 10), pady=(0, 10))

        # Features Frame
        features_frame = ctk.CTkFrame(self)
        features_frame.pack(pady=(10, 5), padx=10, fill="x")

        # Features
        features_label = ctk.CTkLabel(features_frame, text="Features:")
        features_label.pack(anchor="w", padx=(10, 0))

        for feature in self.features:
            feature_label = ctk.CTkLabel(features_frame, text=f"- {feature}")
            feature_label.pack(anchor="w", padx=(20, 0))

        # Developer Information Frame
        developer_frame = ctk.CTkFrame(self)
        developer_frame.pack(pady=(10, 5), padx=10, fill="x")

        # Developer Information
        developer_label = ctk.CTkLabel(developer_frame, text="Developed by:")
        developer_label.pack(anchor="w", padx=(10, 0), pady=(10, 0))

        developer_name_label = ctk.CTkLabel(developer_frame, text=self.developer_name)
        developer_name_label.pack(anchor="w", padx=(10, 0))

        developer_email_label = ctk.CTkLabel(developer_frame, text=self.developer_email)
        developer_email_label.pack(anchor="w", padx=(10, 0))

