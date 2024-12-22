import customtkinter as ctk
from Update_module import VERSION

class AboutFrame(ctk.CTkFrame):
    ORDER = 99
    def __init__(self, parent, main_window):
        super().__init__(parent)

        self.label = ctk.CTkLabel(self, text="About Page", font=("Arial", 24))
        self.label.pack(pady=20)

        # App Information
        self.app_name = "Core Dev Dashboard"
        self.version = VERSION
        self.last_updated = "December 22, 2024"
        self.description = "This app allows users to easily execute actions that would be done manually in the past, through a user interface."
        self.features = [
            "Feature 1: Task Creation",
            "Feature 2: Task execution",
            "Feature 3: Health Check Configuration",
            "Feature 4: Health Check Execution",
            "Feature 5: Password Retriever for RDS instances",
        ]
        self.developer_name = "Nikolas Papaki"
        self.developer_email = "npapaki@tsys.com"

        # Create Frame
        self.create_frame()

    def create_frame(self):
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

