import pickle
import threading
import tkinter as tk
from tkinter import filedialog as fd
import ttkbootstrap as ttk
from customtkinter import *
from PIL import Image, ImageTk
import datetime


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
                image=CTkImage(Image.open(
                    r"C:\Users\shoon\OneDrive - פורטל החינוך פתח תקווה\Documents\הנדסת תוכנה\הנדסת תוכנה - פרוייקט גמר\CloudAV\GUI\file_icons\kick_icon.png"),
                               size=(20, 20)),
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


class CreateGroupWin(CTkToplevel):
    def __init__(self, master, participant_names):

        super().__init__(master)
        self.geometry("500x670")
        self.title("Create New Group")

        self.group_name = StringVar(value="")

        self.selected_participants = {}
        self.participant_names = participant_names
        self.selected_name = None
        self.group_name_error_label = None
        self.participants_error_label = None
        self.submitted_participants = None
        self.permissions_answers = None
        self.submitted = False  # Track if the form was submitted
        ttk.Label(self, text=f"Manage {group_name}", font=("Calibri bold", 22)
                  ).pack(anchor='w', padx=5, pady=15, fill='x')

        self.setup_group_name_entry()
        self.setup_participants_list()
        self.setup_permissions()  # Fixed method name
        self.setup_buttons()

    def setup_group_name_entry(self):
        container = CTkFrame(self)
        container.pack(fill="both", expand=True, padx=5, pady=5)
        CTkLabel(container, text="Edit Group Name:").pack(anchor='w', padx=10, pady=5)
        self.group_name_entry = CTkEntry(container, textvariable=self.group_name, width=200)
        self.group_name_entry.pack(anchor='w', padx=10)

        # Error label for Group Name entry
        self.group_name_error_label = CTkLabel(container, text="", text_color="red")
    def setup_permissions(self):
        permission_frame = CTkFrame(self)
        permission_frame.pack(fill="both", expand=True, padx=5, pady=5)

        ttk.Label(permission_frame, text="Permissions:").pack(anchor='w', padx=10, pady=5)

        # Create a frame to organize switches in rows
        switches_frame = CTkFrame(permission_frame)
        switches_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Create two switches in each row
        self.upload_permission = CTkSwitch(switches_frame, text="Upload Data")
        self.upload_permission.pack(side='left', padx=5)

        self.download_permission = CTkSwitch(switches_frame, text="Download Data")
        self.download_permission.pack(side='left', padx=5)

        # Create a new row for the next set of switches
        switches_frame = CTkFrame(permission_frame)
        switches_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.rename_permission = CTkSwitch(switches_frame, text="Rename Data")
        self.rename_permission.pack(side='left', padx=5)

        self.delete_permission = CTkSwitch(switches_frame, text="Delete Data")
        self.delete_permission.pack(side='left', padx=5)

    def setup_participants_list(self):
        participants_list = CTkScrollableFrame(self, label_anchor="w", label_text="Participants:",
                                               label_fg_color='transparent')
        participants_list.pack(fill="both", expand=True, padx=5)

        for name in self.participant_names:
            participant_var = ttk.StringVar(value="off")
            self.selected_participants[name] = participant_var

            participants_container = CTkFrame(participants_list)
            participants_container.pack(fill='x', expand=True)

            # Checkbutton for participant selection
            checkbox = ttk.Checkbutton(participants_container, text="", variable=participant_var,
                                       onvalue="on", offvalue="off")
            checkbox.pack(side='left', padx=5, pady=5)

            # Label for participant name
            participant_label = ttk.Label(participants_container, text=name)
            participant_label.pack(side='left',anchor='w', fill='x', expand=True, pady=5)

            CTkButton(
                participants_container,
                text="",
                image=CTkImage(Image.open(
                    r"C:\Users\shoon\OneDrive - פורטל החינוך פתח תקווה\Documents\הנדסת תוכנה\הנדסת תוכנה - פרוייקט גמר\CloudAV\GUI\file_icons\kick_icon.png"),
                               size=(20, 20)),
                width=20, height=20,
                fg_color='transparent'
            ).pack(side='left',anchor='e', padx=5)  # Right side

        # Error label for Participants list
        self.participants_error_label = CTkLabel(participants_list, text="", text_color="red")
    def setup_buttons(self):
        container = CTkFrame(self, bg_color='transparent')
        container.pack(fill="x", expand=True, padx=5, pady=5, side="bottom")

        submit_button = CTkButton(container, text="Submit", width=20, command=self.on_submit)
        submit_button.pack(side="left", padx=5)

        cancel_button = CTkButton(container, text="Cancel", width=20, command=self.on_cancel)
        cancel_button.pack(side="left", padx=5)

    def on_submit(self):
        # Clear previous error messages
        self.group_name_error_label.configure(text="")
        self.participants_error_label.configure(text="")

        # Validate Group Name
        group_name = self.group_name.get()
        if not group_name:
            self.group_name_error_label.configure(text="Please enter a group name.")
            self.group_name_error_label.pack(anchor='w', padx=5, pady=5)
            return

        self.selected_name = group_name
        # Validate at least one participant is selected
        self.submitted_participants = [name for name, var in self.selected_participants.items() if var.get() == "on"]
        if not self.submitted_participants:
            self.participants_error_label.configure(text="Please select at least one participant.")
            self.participants_error_label.pack(anchor='w', padx=5, pady=5)
            return

        self.permissions_answers = {
            "Upload Data": self.upload_permission.get(),
            "Download Data": self.download_permission.get(),
            "Rename Data": self.rename_permission.get(),
            "Delete Data": self.delete_permission.get()
        }

        print(f"Group Name: {self.selected_name}")
        print(f"Selected Participants: {self.submitted_participants}")
        print(f"Permissions: {self.permissions_answers}")
        self.submitted = True  # Set submitted flag to True
        self.destroy()

    def on_cancel(self):
        self.destroy()


# Example Usage
if __name__ == "__main__":
    root = tk.Tk()
    group_name = "Group 1"
    participants = ["Participant 1", "Participant 2", "Participant 3", "Participant 4", "Participant 5"]
    permissions = ['1', '0', '1', '0']

    #control_panel = ControlPanel(root, group_name, participants, permissions)
    create_group = CreateGroupWin(root, participants)
    root.mainloop()
