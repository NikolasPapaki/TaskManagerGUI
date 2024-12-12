import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from SharedObjects import HealthCheck
from custom_widgets import HealthCheckDialog

class HealthCheckConfigurationFrame(ctk.CTkFrame):
    ORDER = 96
    empty_template = {
        "users": "",
        "plsql_block": "",
        "sysdba": "",
        "only_local": ""
    }

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.parent = parent

        # Initialize the shared Tasks object
        self.healthcheck_manager = HealthCheck()

        # Frame title
        title_label = ctk.CTkLabel(self, text="Health Check Configuration", font=("Arial", 24))
        title_label.pack(pady=10)

        # Task and Command Treeview
        self.tree = ttk.Treeview(self)
        self.tree.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        self.context_menu = tk.Menu(self, tearoff=0)
        self.tree.bind("<Button-3>", self.show_context_menu)


        self.display_options()

    def display_options(self):
        """Display options in the treeview widget."""
        # Clear the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Sort tasks alphabetically by their name
        options = self.healthcheck_manager.get_options()

        # Populate the Treeview with options
        for option in options:
            self.tree.insert("", tk.END, text=option)



    def show_context_menu(self, event):
        # Identify the item under the cursor
        item_id = self.tree.identify_row(event.y)
        selected_items = self.tree.selection()

        # If no items are selected, or the right-clicked item is not part of the selection
        if not selected_items or item_id not in selected_items:
            self.tree.selection_set(item_id)
            selected_items = self.tree.selection()

        # Clear the context menu
        self.context_menu.delete(0, tk.END)

        # If no items are selected, show general options
        if not selected_items:
            self.context_menu.add_command(label="Add New Health Check Procedure", command=self.add_procedure)
        else:
            if len(selected_items) == 1:
                self.context_menu.add_command(label="Edit Health Check Procedure",
                                              command=lambda: self.edit_procedure(selected_items[0]))
            else:
                pass

        # Show the context menu
        self.context_menu.post(event.x_root, event.y_root)


    def add_procedure(self):
        pass

    def edit_procedure(self, item_id):
        procedure_name = self.tree.item(item_id, "text")

        config = self.healthcheck_manager.get_config(procedure_name)
        print(config)