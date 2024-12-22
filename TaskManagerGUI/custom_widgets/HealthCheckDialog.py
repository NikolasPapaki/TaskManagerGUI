import customtkinter as ctk

class HealthCheckDialog(ctk.CTkToplevel):
    def __init__(self, title, parent, input_defaults=None):
        super().__init__(parent)

        # Set default values
        if input_defaults is None:
            input_defaults = {
                "procedure_name": "",
                "users": "",
                "run_as_sysdba": False,
                "only_local": False,
                "plsql_block": ""
            }

        # Set the title of the dialog
        self.title(title)
        self.result = None

        # Add this attribute to track undo/redo history
        self.text_history = []
        self.text_history_index = -1

        # Set dialog dimensions
        dialog_width = 650
        dialog_height = 500
        self.geometry(f"{dialog_width}x{dialog_height}")

        # Center the dialog on the parent window
        self.center_dialog(parent, dialog_width, dialog_height)

        # Procedure name entry field
        procedure_name_label = ctk.CTkLabel(self, text="Procedure Name:")
        procedure_name_label.pack(padx=10, pady=5, anchor="w")
        self.procedure_name_entry = ctk.CTkEntry(self)
        self.procedure_name_entry.pack(padx=10, pady=5, fill="x")
        self.procedure_name_entry.insert(0,  input_defaults.get("procedure_name", ""))

        # User entry field
        user_label = ctk.CTkLabel(self, text="Users:")
        user_label.pack(padx=10, pady=5, anchor="w")
        self.user_entry = ctk.CTkEntry(self)
        self.user_entry.pack(padx=10, pady=5, fill="x")
        self.user_entry.insert(0, input_defaults.get("users", ""))

        # Run as sysdba toggle
        self.sysdba_var = ctk.StringVar(value="on" if input_defaults.get("run_as_sysdba", False) else "off")
        sysdba_toggle = ctk.CTkSwitch(self, text="Run as sysdba", variable=self.sysdba_var, onvalue="on",
                                      offvalue="off")
        sysdba_toggle.pack(padx=10, pady=5, anchor="w")

        # Only local toggle
        self.local_var = ctk.StringVar(value="on" if input_defaults.get("only_local", False) else "off")
        local_toggle = ctk.CTkSwitch(self, text="Only local", variable=self.local_var, onvalue="on", offvalue="off")
        local_toggle.pack(padx=10, pady=5, anchor="w")

        # Only local toggle
        self.oracle_client_var = ctk.StringVar(value="on" if input_defaults.get("oracle_client", False) else "off")
        oracle_client_toggle = ctk.CTkSwitch(self, text="Use Oracle Client", variable=self.oracle_client_var, onvalue="on", offvalue="off")
        oracle_client_toggle.pack(padx=10, pady=5, anchor="w")

        # PLSQL BLOCK big entry box
        plsql_label = ctk.CTkLabel(self, text="PLSQL BLOCK:")
        plsql_label.pack(padx=10, pady=5, anchor="w")
        self.plsql_textbox = ctk.CTkTextbox(self, height=10)
        self.plsql_textbox.pack(padx=10, pady=5, fill="both", expand=True)
        self.plsql_textbox.insert("0.0", input_defaults.get("plsql_block", ""))

        # Initially track the first state after insert
        initial_text = self.plsql_textbox.get("0.0", "end-1c")
        self.text_history.append(initial_text)
        self.text_history_index = 0

        # Bind events for undo/redo and track text changes
        self.plsql_textbox.bind("<Control-z>", self._undo_textbox)
        self.plsql_textbox.bind("<Control-y>", self._redo_textbox)
        self.plsql_textbox.bind("<<Modified>>", self._track_changes)
        self.plsql_textbox.edit_modified(False)  # Reset the modified flag

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color=self.cget("bg"))
        button_frame.pack(pady=10, fill="x")

        ok_button = ctk.CTkButton(button_frame, text="OK", command=self._on_ok)
        ok_button.pack(side=ctk.LEFT, padx=10)

        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self._on_cancel)
        cancel_button.pack(side=ctk.RIGHT, padx=10)

        # Make the dialog modal
        self.lift()
        self.transient(parent)
        self.grab_set()
        self.wait_window()

    # Track changes to the textbox
    def _track_changes(self, event=None):
        if self.plsql_textbox.edit_modified():  # Check if the text was modified
            current_text = self.plsql_textbox.get("0.0", "end-1c")
            if not self.text_history or self.text_history[self.text_history_index] != current_text:
                # Truncate history after the current index and append the new state
                self.text_history = self.text_history[:self.text_history_index + 1]
                self.text_history.append(current_text)
                self.text_history_index += 1
            self.plsql_textbox.edit_modified(False)  # Reset the modified flag

    # Undo functionality
    def _undo_textbox(self, event=None):
        if self.text_history_index > 0:  # Ensure there is an earlier state
            self.text_history_index -= 1
            previous_text = self.text_history[self.text_history_index]
            self._set_textbox_content(previous_text)

    # Redo functionality
    def _redo_textbox(self, event=None):
        if self.text_history_index < len(self.text_history) - 1:  # Ensure there's a later state
            self.text_history_index += 1
            next_text = self.text_history[self.text_history_index]
            self._set_textbox_content(next_text)

    # Helper method to set textbox content without triggering modification tracking
    def _set_textbox_content(self, text):
        self.plsql_textbox.unbind("<<Modified>>")  # Temporarily unbind the modified tracking
        self.plsql_textbox.delete("0.0", "end")
        self.plsql_textbox.insert("0.0", text)
        self.plsql_textbox.bind("<<Modified>>", self._track_changes)  # Rebind tracking

    def center_dialog(self, parent, width, height):
        """Center the dialog on the parent window or screen."""
        if parent:
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()
            x = parent_x + (parent_width - width) // 2
            y = parent_y + (parent_height - height) // 2
        else:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
        self.geometry(f"+{x}+{y}")

    def _on_ok(self):
        # Collect all values
        self.result = {
            "procedure_name": self.procedure_name_entry.get().strip(),
            "users": self.user_entry.get().strip(),
            "run_as_sysdba": self.sysdba_var.get() == "on",
            "only_local": self.local_var.get() == "on",
            "oracle_client": self.oracle_client_var.get() == "on",
            "plsql_block": self.plsql_textbox.get("0.0", "end").strip(),
        }
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def show(self):
        return self.result
