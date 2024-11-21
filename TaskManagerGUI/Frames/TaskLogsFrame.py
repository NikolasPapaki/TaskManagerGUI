import tkinter as tk
import customtkinter as ctk
import os
import threading
import datetime
from tkinter import messagebox
from tkinter import ttk, messagebox

class TaskLogsFrame(ctk.CTkFrame):
    ORDER = 96

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.filter_timer = None

        # Frame title
        title_label = ctk.CTkLabel(self, text="Task Logs", font=("Arial", 24))
        title_label.pack(pady=10)

        search_label = ctk.CTkLabel(self, text="Search tasks by name:", font=("Arial", 14))
        search_label.pack(pady=5, padx=10, anchor="w")

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.filter_logs)

        search_entry = ctk.CTkEntry(self, textvariable=self.search_var, placeholder_text="Search tasks")
        search_entry.pack(pady=10, padx=10, fill=ctk.X)

        # Treeview widget (replacing Listbox)
        self.logs_treeview = ttk.Treeview(self, columns=("Log File",), show="headings", height=10)
        self.logs_treeview.heading("Log File", text="Log File")
        self.logs_treeview.pack(expand=True, fill="both", padx=10, pady=10)

        # Initialize the filtered_log_files list
        self.filtered_log_files = []

        # Load log files from the task_logs directory
        self.load_logs()

        # Bind right-click to show context menu
        self.logs_treeview.bind("<Button-3>", self.show_context_menu)

        # Create the context menu using tkinter.Menu
        self.context_menu = tk.Menu(self, tearoff=False)
        self.context_menu.add_command(label="View Log", command=self.view_log)
        self.context_menu.add_command(label="Delete Log", command=self.delete_log)

    def load_logs(self):
        """Load log files from the task_logs directory."""
        logs_dir = "task_logs"

        if not os.path.exists(logs_dir):
            messagebox.showerror("Error", f"'{logs_dir}' directory does not exist.")
            return

        # List all files in the directory and filter for .log files
        self.log_files = [f for f in os.listdir(logs_dir) if f.endswith(".log")]

        # Sort the log files by timestamp (extract timestamp from filename)
        self.log_files.sort(key=self.extract_timestamp, reverse=True)

        # Initialize the filtered log files
        self.filtered_log_files = self.log_files

        # Insert log file names into the treeview
        if self.filtered_log_files:
            self.update_log_treeview()
        else:
            messagebox.showinfo("No Logs", "No log files found in the 'task_logs' directory.")

    def extract_timestamp(self, log_file_name):
        """Extract the timestamp from the log file name."""
        try:
            # Remove the '.log' extension
            log_file_name_without_extension = log_file_name[:-4]  # Remove the last 4 characters ('.log')

            # The timestamp is always the part after the task name and before the file extension
            timestamp_str = log_file_name_without_extension.split('_')[-2:]  # Take the last two parts
            timestamp = "_".join(timestamp_str)  # Join back to get the full timestamp

            # Parse the timestamp into a datetime object for comparison
            return datetime.datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
        except Exception as e:
            print(f"Error extracting timestamp from {log_file_name}: {e}")
            return datetime.datetime.min  # Return a very old date in case of error

    def update_log_treeview(self):
        """Update the treeview with log files."""
        for row in self.logs_treeview.get_children():
            self.logs_treeview.delete(row)  # Clear existing entries
        for log_file in self.filtered_log_files:
            self.logs_treeview.insert("", "end", values=(log_file,))  # Insert log files into the treeview

    def filter_logs(self, *args):
        """Filter log files based on the search box input."""
        if self.filter_timer:
            self.after_cancel(self.filter_timer)  # Cancel the previous timer if any

        # Start a new timer to delay the filtering
        self.filter_timer = self.after(500, self.apply_filter)  # Delay for 500ms

    def apply_filter(self):
        """Apply the filtering logic on a separate thread to keep the UI responsive."""
        search_term = self.search_var.get().lower()  # Get the search term (lowercase)

        # Run the filtering logic in a separate thread to avoid blocking the UI
        filter_thread = threading.Thread(target=self.perform_filter, args=(search_term,))
        filter_thread.start()

    def perform_filter(self, search_term):
        """Perform the filtering of log files in a background thread."""
        # Remove underscores from the search term
        cleaned_search_term = search_term.replace("_", " ").lower()

        # Filter log files by removing underscores and performing a case-insensitive match
        filtered_files = [
            f for f in self.log_files
            if cleaned_search_term in f.replace("_", " ").lower()  # Remove underscores for comparison
        ]

        # Update the treeview with the filtered files (must be done on the main thread)
        self.after(0, self.update_filtered_list, filtered_files)

    def update_filtered_list(self, filtered_files):
        """Update the treeview with the filtered files."""
        self.filtered_log_files = filtered_files
        self.update_log_treeview()

    def show_context_menu(self, event):
        """Show the context menu on right-click."""
        # Identify the item at the row where the right-click occurred
        item_id = self.logs_treeview.identify_row(event.y)

        try:
            if item_id:  # If an item is identified (clicked)
                # Select the item programmatically
                self.logs_treeview.selection_set(item_id)

                # Get the selected item after selecting it
                selected_item = self.logs_treeview.selection()[0]  # We expect one selected item

                # Show the context menu
                if selected_item:
                    self.context_menu.post(event.x_root, event.y_root)  # Show the context menu
                else:
                    print("No item selected, context menu will not be shown.")
            else:
                print("No item identified at the click location.")
        except Exception as e:
            print(f"Error showing context menu: {e}")

    def view_log(self):
        """View the log file content in a popup when selected from the context menu."""
        selected_item = self.logs_treeview.selection()  # Get the selected item

        if selected_item:
            log_file_name = self.logs_treeview.item(selected_item[0])["values"][0]  # Get the log file name
            log_file_path = os.path.join("task_logs", log_file_name)  # Build the full path to the log file

            if os.path.exists(log_file_path):
                # Read the log file content
                with open(log_file_path, "r") as file:
                    log_content = file.read()

                # Now, call show_log_popup with both the log content and log file path
                self.show_log_popup(log_file_name, log_content, log_file_path)
            else:
                messagebox.showerror("Error", f"Log file '{log_file_name}' does not exist.")

    def show_log_popup(self, log_file_name, log_content, log_file_path):
        """Display the log content in a modal, scrollable popup window using CustomTkinter."""
        log_window = ctk.CTkToplevel(self)
        log_window.title(log_file_name)

        # Center the popup in the parent window
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        popup_width = 600
        popup_height = 400
        position_x = parent_x + (parent_width - popup_width) // 2
        position_y = parent_y + (parent_height - popup_height) // 2

        log_window.geometry(f"{popup_width}x{popup_height}+{position_x}+{position_y}")

        # Make the popup modal
        log_window.transient(self)  # Set the popup as a child of the parent window
        log_window.grab_set()  # Disable interaction with the parent window

        # Create a frame to hold the Textbox and scrollbar
        frame = ctk.CTkFrame(log_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create the CTkTextbox
        text_widget = ctk.CTkTextbox(frame, wrap="word", font=("Arial", 12))
        text_widget.insert("0.0", log_content)  # Insert the log content at the start
        text_widget.configure(state="disabled")  # Make the textbox read-only
        text_widget.pack(side="left", fill="both", expand=True)

        # Create Show in Directory button
        show_in_dir_button = ctk.CTkButton(log_window, text="Show in Directory",
                                           command=lambda: self.show_in_directory(log_file_path))
        show_in_dir_button.pack(pady=(5,20), fill='x', padx=20)

        # Wait for the popup to close
        log_window.wait_window()

    def show_in_directory(self, log_file_path):
        """Open the directory containing the log file in Explorer."""
        directory = os.path.dirname(log_file_path)
        os.startfile(directory)  # Open the directory in Windows Explorer

    def delete_log(self):
        """Delete the selected log file after confirmation."""
        selected_item = self.logs_treeview.selection()  # Get the selected item
        if not selected_item:
            messagebox.showerror("Error", "No log file selected.")
            return

        log_file_name = self.logs_treeview.item(selected_item, "values")[0]  # Get the log file name
        log_file_path = os.path.join("task_logs", log_file_name)  # Build the full path to the log file

        # Show a confirmation dialog before deleting
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{log_file_name}'? This action cannot be undone!"):
            try:
                os.remove(log_file_path)  # Delete the log file
                self.filtered_log_files.remove(log_file_name)  # Remove from the filtered list
                self.update_log_treeview()  # Update the Treeview
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete log file: {e}")

    def on_show(self):
        self.load_logs()