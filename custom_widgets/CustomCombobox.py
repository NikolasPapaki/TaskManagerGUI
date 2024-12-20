import customtkinter as ctk


class CustomComboBox(ctk.CTkFrame):
    def __init__(self, master, options, width=180, height=30, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)

        # Create an input frame for the entry and button
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(side="top", fill="x")

        # Entry for typing or displaying selected item
        self.entry = ctk.CTkEntry(self.input_frame, width=width - 40)  # Adjust width for button
        self.entry.pack(side="left", padx=(0, 5))

        # Dropdown button to toggle options visibility
        self.dropdown_button = ctk.CTkButton(self.input_frame, text="▼", width=20, command=self.toggle_options)
        self.dropdown_button.pack(side="left")

        # Options list
        self.options = options

        # Create an options frame that will be shown/hidden
        self.option_frame = ctk.CTkFrame(self, fg_color=self.cget("fg_color"), corner_radius=5)

    def toggle_options(self):
        # Toggle dropdown visibility
        if self.option_frame.winfo_ismapped():
            self.option_frame.pack_forget()
        else:
            self.show_options()

    def show_options(self):
        # Clear any existing buttons before displaying new options
        for widget in self.option_frame.winfo_children():
            widget.destroy()

        # Populate the dropdown with option buttons
        for option in self.options:
            option_button = ctk.CTkButton(self.option_frame, text=option,
                                          command=lambda opt=option: self.select_option(opt), width=160)
            option_button.pack(fill="both", expand=True)  # Fill both x and y axes

        # Place options frame directly below the input frame with some space
        self.option_frame.pack(side="top", fill="x", pady=(5, 0))  # Add vertical space with pady

    def select_option(self, option):
        # Set entry text to selected option and hide the dropdown
        self.entry.delete(0, ctk.END)
        self.entry.insert(0, option)
        self.option_frame.pack_forget()

    def get_value(self):
        return self.entry.get()
