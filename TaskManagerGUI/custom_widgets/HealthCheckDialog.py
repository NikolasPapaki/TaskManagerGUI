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
