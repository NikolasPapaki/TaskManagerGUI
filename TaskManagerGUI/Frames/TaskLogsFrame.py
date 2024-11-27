import tkinter as tk
import customtkinter as ctk
import os
import threading
import datetime
from tkinter import messagebox
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

class TaskLogsFrame(ctk.CTkFrame):
    ORDER = 96

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.parent = parent
        self.filter_timer = None

        # Frame title
        title_label = ctk.CTkLabel(self, text="Task Logs", font=("Arial", 24))
        title_label.pack(pady=10)

        # Search by name
        search_label = ctk.CTkLabel(self, text="Search tasks by name:", font=("Arial", 14))
        search_label.pack(pady=5, padx=10, anchor="w")

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.filter_logs)

        search_entry = ctk.CTkEntry(self, textvariable=self.search_var, placeholder_text="Search tasks")
        search_entry.pack(pady=10, padx=10, fill=ctk.X)

        # Date range filtering
        date_frame = ctk.CTkFrame(self)
        date_frame.pack(pady=10, padx=10, fill=ctk.X)

        # Start Date
        start_date_label = ctk.CTkLabel(date_frame, text="Start Date:", font=("Arial", 12))
        start_date_label.grid(row=0, column=0, padx=(10, 5))

        self.start_date = DateEntry(date_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern="dd/MM/yyyy")
        self.start_date.grid(row=0, column=1, padx=5)

        # End Date
        end_date_label = ctk.CTkLabel(date_frame, text="End Date:", font=("Arial", 12))
        end_date_label.grid(row=0, column=2, padx=(20, 5))

        self.end_date = DateEntry(date_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern="dd/MM/yyyy")
        self.end_date.grid(row=0, column=3, padx=5)

        # Apply date range filter button
        date_filter_button = ctk.CTkButton(date_frame, text="Apply Date Filter", command=self.filter_logs)
        date_filter_button.grid(row=0, column=4, padx=(20, 10))

        # Treeview widget
        self.logs_treeview = ttk.Treeview(
            self,
            columns=("Log File", "File Size", "Creation Date"),
            show="headings",
            height=10,
            selectmode="extended",
        )

        # Define column headings
        # Bind a sorting function to the column headers
        self.logs_treeview.heading("Log File", text="Log File", command=lambda: self.sort_treeview("Log File", False))
        self.logs_treeview.heading("File Size", text="File Size",
                                   command=lambda: self.sort_treeview("File Size", False))
        self.logs_treeview.heading("Creation Date", text="Creation Date",
                                   command=lambda: self.sort_treeview("Creation Date", False))

        # Adjust column widths
        self.logs_treeview.column("Log File", width=300)
        self.logs_treeview.column("File Size", width=100, anchor="center")
        self.logs_treeview.column("Creation Date", width=150, anchor="center")

        self.logs_treeview.pack(expand=True, fill="both", padx=10, pady=10)

        # Initialize the filtered_log_files list
        self.filtered_log_files = []

        # Load log files from the task_logs directory
        self.load_logs()

        # Bind right-click to show context menu
        self.logs_treeview.bind("<Button-3>", self.show_context_menu)


        # Create the context menu
        self.context_menu = tk.Menu(self, tearoff=False)

    def load_logs(self):
        """Load log files from the task_logs directory."""
        logs_dir = "task_logs"

        if not os.path.exists(logs_dir):
            return

        # List all files in the directory and filter for .log files
        self.log_files = [
            {
                "name": f,
                "size": os.path.getsize(os.path.join(logs_dir, f)),
                "creation_date": datetime.datetime.fromtimestamp(
                    os.path.getctime(os.path.join(logs_dir, f))
                ),
            }
            for f in os.listdir(logs_dir)
            if f.endswith(".log")
        ]

        # Sort the log files by timestamp (extracted from the filename)
        self.log_files.sort(key=lambda x: self.extract_timestamp(x["name"]), reverse=True)

        # Initialize the filtered log files
        self.filtered_log_files = self.log_files

        # Insert log file names into the treeview
        if self.filtered_log_files:
            self.update_log_treeview()

    def filter_logs(self, *args):
        if self.filter_timer:
            self.after_cancel(self.filter_timer)

        self.filter_timer = self.after(500, self.apply_filter)

    def apply_filter(self):
        search_term = self.search_var.get().lower()
        start_date = self.start_date.get_date() if self.start_date.get() else None
        end_date = self.end_date.get_date() if self.end_date.get() else None

        filter_thread = threading.Thread(target=self.perform_filter, args=(search_term, start_date, end_date))
        filter_thread.start()

    def perform_filter(self, search_term, start_date, end_date):
        def match_date(file_info):
            """Check if the log file matches the selected date range."""
            try:
                # Extract timestamp from file name (assuming it's in the 'Log File' field)
                timestamp = self.extract_timestamp(file_info["name"])  # Adjust for correct key
                if not timestamp:
                    return False

                # Convert timestamp to a date object
                file_date = timestamp.date()

                # Compare dates
                if start_date and file_date < start_date:
                    return False
                if end_date and file_date > end_date:
                    return False

                return True
            except Exception as e:
                print(f"Error in match_date: {e}")
                return False


        filtered_files = [
            f for f in self.log_files
            if search_term in f["name"].replace("_", " ").lower() and match_date(f)
        ]

        self.after(0, self.update_filtered_list, filtered_files)

    def extract_timestamp(self, log_file_name):
        try:
            log_file_name_without_extension = log_file_name[:-4]
            timestamp_str = "_".join(log_file_name_without_extension.split('_')[-2:])
            return datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        except Exception as e:
            print(f"Error extracting timestamp: {e}")
            return datetime.datetime.min

    def update_filtered_list(self, filtered_files):
        self.filtered_log_files = filtered_files
        self.update_log_treeview()

    def update_log_treeview(self):
        """Update the treeview with log files."""
        # Clear existing entries
        for row in self.logs_treeview.get_children():
            self.logs_treeview.delete(row)

        # Populate the Treeview with log files
        for log_file in self.filtered_log_files:
            self.logs_treeview.insert(
                "",
                "end",
                values=(
                    log_file["name"],
                    f"{log_file['size'] / 1024:.2f} KB",  # Convert size to KB
                    log_file["creation_date"].strftime("%d/%m/%Y %H:%M:%S"),
                ),
            )

    def show_context_menu(self, event):
        """Show the context menu on right-click."""
        # Identify the item at the row where the right-click occurred
        item_id = self.logs_treeview.identify_row(event.y)

        try:
            # Get the currently selected items (allow multiple selections)
            selected_items = self.logs_treeview.selection()

            # If no item is selected yet, select the item under the cursor
            if not selected_items and item_id:
                self.logs_treeview.selection_add(item_id)

            # Clear the existing context menu options
            self.context_menu.delete(0, tk.END)

            # Show options based on the number of selected items
            if len(self.logs_treeview.selection()) == 1:  # If only one item is selected
                self.context_menu.add_command(label="View Log", command=self.view_log)
                self.context_menu.add_command(label="Delete Log", command=self.delete_log)
            elif len(self.logs_treeview.selection()) > 1:  # If multiple items are selected
                self.context_menu.add_command(label="Delete Selected Logs", command=self.delete_multiple_logs)

            # Show the context menu
            self.context_menu.post(event.x_root, event.y_root)

        except Exception as e:
            print(f"Error showing context menu: {e}")

    def delete_multiple_logs(self):
        """Delete the selected multiple log files after confirmation."""
        selected_items = self.logs_treeview.selection()  # Get the selected items
        if not selected_items:
            messagebox.showerror("Error", "No log files selected.")
            return

        log_files_to_delete = []
        for item in selected_items:
            log_file_name = self.logs_treeview.item(item, "values")[0]  # Get the log file name
            log_file_path = os.path.join("task_logs", log_file_name)  # Build the full path to the log file
            log_files_to_delete.append((log_file_name, log_file_path))

        # Show a confirmation dialog before deleting
        if messagebox.askyesno("Confirm Deletion",
                               f"Are you sure you want to delete the following logs?\nThis action cannot be undone!"):
            try:
                for log_file_name, log_file_path in log_files_to_delete:
                    if os.path.exists(log_file_path):
                        os.remove(log_file_path)  # Delete the log file
                    else:
                        print(f"File not found: {log_file_path}")

                    # Find and remove the dictionary that has 'name': log_file_name
                    self.filtered_log_files = [log for log in self.filtered_log_files if
                                               log.get('name') != log_file_name]

                self.update_log_treeview()  # Update the Treeview
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete log file(s): {e}")

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

    def sort_treeview(self, column, reverse):
        """Sort the Treeview by the specified column."""
        # Retrieve all rows from the Treeview
        rows = [
            (self.logs_treeview.set(row_id, column), row_id)
            for row_id in self.logs_treeview.get_children()
        ]

        # Sort the rows based on the column's data type
        if column == "File Size":
            # Convert file size to float for sorting
            rows.sort(key=lambda x: float(x[0].replace(" KB", "")), reverse=reverse)
        elif column == "Creation Date":
            # Convert date string to datetime for sorting
            rows.sort(key=lambda x: datetime.datetime.strptime(x[0], "%d/%m/%Y %H:%M:%S"), reverse=reverse)
        else:
            # Default string sorting for "Log File"
            rows.sort(key=lambda x: x[0].lower(), reverse=reverse)

        # Rearrange rows in the Treeview
        for index, (_, row_id) in enumerate(rows):
            self.logs_treeview.move(row_id, "", index)

        # Reverse the sorting order for the next click
        self.logs_treeview.heading(column, command=lambda: self.sort_treeview(column, not reverse))


    def on_show(self):
        self.load_logs()