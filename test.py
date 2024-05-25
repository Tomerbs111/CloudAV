class ControlPanel(CTkToplevel):
    PERMISSION_NAMES = ["Upload Data", "Download Data", "Rename Data", "Delete Data"]

    def __init__(self, master, group_name, participants, permissions):
        super().__init__(master)
        self.title("ControlPanel")
        self.geometry("600x450")  # Set initial size

        self.group_name = group_name
        self.participants = participants
        self.permissions = permissions

        self.setup_ui()

    def setup_ui(self):
        # Header Label
        header_label = CTkLabel(self, text=self.group_name, font=("Calibri bold", 26), compound='left')
        header_label.pack(side='top', padx=5, fill='x')
        header_label = CTkLabel(self, text=self.group_name, font=("Calibri bold", 20), compound='left')
        header_label.pack(side='top', padx=5, pady=15, fill='x', anchor='w')
        # Participants List
        participants_frame = CTkFrame(self)
        participants_frame.pack(anchor='w', padx=5, pady=5, fill='x', expand=True)

        participants_label = CTkLabel(participants_frame, text="Participants:",
                                       font=("Calibri bold", 14))  # Bigger and bold
        participants_label.pack(anchor='w', padx=10, pady=5)

        for participant in self.participants:
            participant_frame = CTkFrame(participants_frame)
            participant_frame.pack(anchor='w', padx=10, pady=2, fill='x')

            CTkLabel(participant_frame, text=participant).pack(side='left')
            CTkButton(
                participant_frame,
                text="",
                image=CTkImage(Image.open("../GUI/file_icons/kick_icon.png"), size=(20, 20)),
                width=20, height=20,
                fg_color='transparent'
            ).pack(side='right', padx=5)  # Right side

        # Add Participant Button
        add_participant_button = CTkButton(participants_frame, text="Add Participant")
        add_participant_button.pack(anchor='w', padx=10, pady=5)

        # Permissions List with Switches
        permissions_frame = CTkFrame(self)
        permissions_frame.pack(anchor='w', padx=5, pady=5, fill='both', expand=True)

        CTkLabel(permissions_frame, text="Permissions:", font=("Calibri bold", 14)).pack(anchor='w', padx=10,
                                                                                          pady=5)  # Bigger and bold
        # Create two switches in each row
        self.upload_permission = CTkSwitch(permissions_frame, text="Upload Data")
        self.upload_permission.pack(side='left', padx=5)

        self.download_permission = CTkSwitch(permissions_frame, text="Download Data")
        self.download_permission.pack(side='left', padx=5)

        self.rename_permission = CTkSwitch(permissions_frame, text="Rename Data")
        self.rename_permission.pack(side='left', padx=5)

        self.delete_permission = CTkSwitch(permissions_frame, text="Delete Data")
        self.delete_permission.pack(side='left', padx=5)

        # Save Button
        save_frame = CTkFrame(self)
        save_frame.pack(side='bottom', padx=5, pady=5, fill='x', expand=True)
        save_button = CTkButton(save_frame, text="Save")
        save_button.pack(fill='x', expand=True)

# Example Usage
if __name__ == "__main__":
    root = tk.Tk()
    group_name = "Group 1"
    participants = ["Participant 1", "Participant 2", "Participant 3", "Participant 4", "Participant 5"]
    permissions = ['1', '0', '1', '0']

    control_panel = ControlPanel(root, group_name, participants, permissions)
    root.mainloop()