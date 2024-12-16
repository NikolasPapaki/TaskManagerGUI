import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import os
import json


class TaskManagementLogsFrame(ctk.CTkFrame):
    ORDER = 97

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.parent = parent

        self.setup_treeview()
        self.load_logs()

        # Area to display details of the selected log
        self.details_frame = ctk.CTkFrame(self)
        self.details_frame.pack(fill=tk.BOTH, padx=10, pady=10)

        self.old_value_label = ctk.CTkLabel(self.details_frame, text="Old Value: ")
        self.old_value_label.pack(anchor='w')

        self.new_value_label = ctk.CTkLabel(self.details_frame, text="New Value: ")
        self.new_value_label.pack(anchor='w')

        # Bind selection event
        self.log_tree.bind("<<TreeviewSelect>>", self.on_log_select)

    def setup_treeview(self):
        """Sets up the Treeview widget to display logs."""
        self.log_tree = ttk.Treeview(self, columns=("timestamp", "action", "task_name", "old_value", "new_value"),
                                     show="headings", height=5)

        # Define the column headings
        self.log_tree.heading("timestamp", text="Timestamp")
        self.log_tree.heading("action", text="Action")
        self.log_tree.heading("task_name", text="Task Name")

        # Set column widths
        self.log_tree.column("timestamp", width=150)
        self.log_tree.column("action", width=150)
        self.log_tree.column("task_name", width=150)

        # Set the old_value and new_value columns to be hidden
        self.log_tree.column("old_value", width=0, stretch=tk.NO)
        self.log_tree.column("new_value", width=0, stretch=tk.NO)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.log_tree.yview)
        self.log_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Pack the Treeview
        self.log_tree.pack(expand=True, fill=tk.BOTH)

    def load_logs(self):
        """Load logs from a JSON file and populate the Treeview."""
        log_file = "task_logs.json"
        if os.path.exists(log_file):
            with open(log_file, "r") as file:
                try:
                    logs = json.load(file)
                    if isinstance(logs, list):
                        for log in logs:
                            # Ensure the log entry has the correct structure
                            if isinstance(log, dict) and all(k in log for k in ["timestamp", "action", "task_name", "old_value", "new_value"]):
                                timestamp = log["timestamp"]
                                action = log["action"]
                                task_name = log["task_name"]
                                old_value = log.get("old_value", "")
                                new_value = log.get("new_value", "")

                                self.log_tree.insert("", tk.END, values=(timestamp, action, task_name, old_value, new_value))
                            else:
                                print("Invalid log entry structure:", log)
                    else:
                        print("Logs object is not a list:", logs)
                except json.JSONDecodeError as e:
                    print("Failed to decode JSON:", e)
                    self.log_tree.insert("", tk.END, values=("Error loading logs.", "", "", "", ""))
        else:
            self.log_tree.insert("", tk.END, values=("No logs found.", "", "", "", ""))

    def on_log_select(self, event):
        """Display the old and new values for the selected log entry."""
        selected_item = self.log_tree.selection()
        if selected_item:
            item_data = self.log_tree.item(selected_item[0])['values']
            if len(item_data) >= 5:
                self.old_value_label.configure(text=f"Old Value: {item_data[3]}")
                self.new_value_label.configure(text=f"New Value: {item_data[4]}")
