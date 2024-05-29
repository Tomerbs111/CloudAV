import threading
import ttkbootstrap as ttk
from customtkinter import *
from PIL import Image, ImageTk
import tkinter as tk

from GUI.RegistrationApp import RegistrationApp
from GUI.GroupsPage import GroupsPage
from GUI.HomePage import HomePage
from GUI.FavoritesPage import FavoritesPage


class Page(ttk.Frame):
    def __init__(self, master, switch_frame, communicator, current_frame, get_user_info):
        super().__init__(master)

        self.create_group_top = None
        self.f_user_groups = None
        self.group_list_frame = None
        self.f_options = None
        self.current_frame = None
        self.group_menu_frame = None
        self.master = master
        self.switch_frame = switch_frame
        self.communicator = communicator
        self.current_frame = current_frame

        self.room_dictionary = {}

        self.f_data_center = None
        self.f_current_page = None

        self.user_username = None
        self.user_email = None
        self.get_user_info = get_user_info

        self.setup_data_center_frame()
        self.setup_option_frame()
        self.setup_searchbar_frame()
        self.setup_current_page_frame()
        self.setup_groups_segment()

    def setup_searchbar_frame(self):
        # Code for setting up the Searchbar frame
        f_searchbar = ttk.Frame(master=self.f_data_center, style="dark")
        f_searchbar.pack(side="top", fill="both")

        search_button = ttk.Button(f_searchbar, text="Search")
        search_button.pack(side="left", pady=15)

        search_entry = ttk.Entry(f_searchbar, width=70)
        search_entry.pack(side="left", pady=15)

        # Profile Photo Placeholder on the Right
        profile_photo_placeholder = ttk.Label(f_searchbar, text="👤", font=("Arial", 30))
        profile_photo_placeholder.pack(side="right", padx=10, pady=15)

        # Settings Button on the Right
        settings_button = ttk.Button(f_searchbar, text="Settings")
        settings_button.pack(side="right", padx=10, pady=15)

    def setup_data_center_frame(self):
        # Code for setting up the Data center frame
        self.f_data_center = ttk.Frame(master=self, style="default")
        self.f_data_center.pack(side="top", fill="both", expand=True)

    def setup_option_frame(self):
        # Code for setting up the Option frame
        self.f_options = ttk.Frame(master=self.f_data_center, style="dark")
        self.f_options.pack(side="left", fill="y")

        cloudav_image = CTkImage(
            light_image=Image.open(r"../GUI/file_icons/only_logo.png"),
            dark_image=Image.open(r"../GUI/file_icons/only_logo.png"),
            size=(75, 75))
        cav_image_lbl = CTkLabel(master=self.f_options, image=cloudav_image, text="")
        cav_image_lbl.pack(side="top", padx=10)

        self.add_button = CTkButton(
            self.f_options,
            text="     Add",
            font=("Arial", 15),
            image=CTkImage(Image.open("../GUI/file_icons/add_file_plus_icon.png"), size=(20, 20)),
            compound='left',
            anchor='w',
            width=110,
            height=50
        )
        self.add_button.pack(side='top', pady=20, anchor='w', padx=10)
        self.add_button.bind("<Button-1>", self.show_add_menu)

        ttk.Separator(self.f_options, orient="horizontal").pack(side='top', fill='x', pady=5, padx=10)

        CTkButton(
            self.f_options,
            text="Home",
            image=CTkImage(Image.open("../GUI/file_icons/home_icon.png"), size=(20, 20)),
            compound='left',
            command=self.switch_to_home_page,
            anchor='w',
            fg_color='transparent'
        ).pack(side='top', pady=5, anchor='w', fill='x', padx=10)

        CTkButton(
            self.f_options,
            text="Favorites",
            image=CTkImage(Image.open("../GUI/file_icons/star_icon.png"), size=(20, 20)),
            compound='left',
            command=self.switch_to_favorites_page,
            anchor='w',
            fg_color='transparent'
        ).pack(side='top', pady=5, anchor='w', fill='x', padx=10)

        CTkButton(
            self.f_options,
            text="Log out",
            image=CTkImage(Image.open("../GUI/file_icons/log_out_icon.png"), size=(20, 20)),
            compound='left',
            command=self.handle_log_out_action,
            anchor='w',
            fg_color='transparent'

        ).pack(side='top', pady=5, anchor='w', fill='x', padx=10)

        self.group_menu_frame = ttk.Frame(self.f_options, style="dark")
        self.group_button_frame = (CTkScrollableFrame(self.f_options, fg_color="transparent"))

    def show_add_menu(self, event):
        menu = tk.Menu(self.f_options, tearoff=0)
        new_folder_icon = Image.open(
            r"..\GUI\file_icons\add-folder.png")
        new_folder_icon = new_folder_icon.resize((16, 16))
        new_folder_icon = ImageTk.PhotoImage(new_folder_icon)

        upload_folder_icon = Image.open(
            r"..\GUI\file_icons\folder-upload.png")
        upload_folder_icon = upload_folder_icon.resize((16, 16))
        upload_folder_icon = ImageTk.PhotoImage(upload_folder_icon)

        file_icon = Image.open(
            r"..\GUI\file_icons\file-upload.png")
        file_icon = file_icon.resize((16, 16))
        file_icon = ImageTk.PhotoImage(file_icon)

        menu.add_command(label=" New Folder", image=new_folder_icon, compound=tk.LEFT,
                         command=self.setup_new_folder_dialog,
                         font=("Arial", 14))
        menu.add_separator()
        menu.add_command(label=" Upload File", image=file_icon, compound=tk.LEFT, command=self.handle_send_file_request,
                         font=("Arial", 14))
        menu.add_command(label=" Upload Folder", image=upload_folder_icon, compound=tk.LEFT,
                         command=self.handle_upload_folder_request,
                         font=("Arial", 14))

        x = self.f_options.winfo_rootx() + self.add_button.winfo_x()
        y = self.f_options.winfo_rooty() + self.add_button.winfo_y()

        self.f_options.after(100, menu.post(x, y))

    def setup_current_page_frame(self):
        self.f_current_page = ttk.Frame(master=self.f_data_center, style="info")
        self.f_current_page.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    def setup_groups_segment(self):
        # Create a separator
        ttk.Separator(self.f_options, orient="horizontal").pack(side='top', fill='x', pady=5, padx=10)

        # Pack the main frame
        self.group_menu_frame.pack(side='top', fill='x')
        self.group_button_frame.pack(side='top', fill='both', pady=5, padx=10)

        # Create and grid the label
        CTkLabel(
            self.group_menu_frame,
            text="Your groups",
            font=('Arial', 16),
            fg_color='transparent',
        ).grid(row=0, column=0, pady=5, padx=10, sticky='n')

        # Create the "New group" button
        new_group_button = CTkButton(
            self.group_menu_frame,
            text="New group",
            compound='right',
            anchor='w',
            image=CTkImage(Image.open("../GUI/file_icons/add_file_plus_icon.png"), size=(20, 20)),
            width=18,
            command=self.handle_create_group_window
        )
        refresh_button = CTkButton(
            self.group_menu_frame,
            text="",
            compound='right',
            anchor='w',
            image=CTkImage(Image.open("../GUI/file_icons/refresh_icon.png"), size=(20, 20)),
            width=18,
            command=self.get_group_names
        )

        # Grid buttons in the same row
        new_group_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        refresh_button.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

        # Ensure the buttons are the same size
        self.group_menu_frame.grid_columnconfigure(0, weight=1)
        self.group_menu_frame.grid_columnconfigure(1, weight=1)

        # Adjust the padding and alignment as needed
        self.group_menu_frame.grid_rowconfigure(0, weight=1)
        self.group_menu_frame.grid_rowconfigure(1, weight=1)

        ttk.Separator(self.f_options, orient="horizontal").pack(side='top', fill='x', pady=5, padx=10)


    def switch_to_groups_page(self, group_name, permissions, room_admin):
        self.user_username, self.user_email = self.get_user_info()
        if self.current_frame.__class__.__name__ != "GroupsPage":
            print(f"Switching to {group_name}")
            self.switch_frame("GroupsPage", self.communicator, group_name, permissions, room_admin)
            threading.Thread(target=self.current_frame.group_communicator.handle_join_group_request,
                             args=(group_name,)).start()

        elif self.current_frame.group_name != group_name:
            threading.Thread(target=self.current_frame.group_communicator.handle_leave_group_request).start()
            print(f"Switching to {group_name}")
            self.switch_frame("GroupsPage", self.communicator, group_name, permissions, room_admin)
            threading.Thread(target=self.current_frame.group_communicator.handle_join_group_request,
                             args=(group_name,)).start()

        self.current_frame.check_if_admin(self.user_email)

    def switch_to_home_page(self):
        self.user_username, self.user_email = self.get_user_info()
        if self.current_frame.__class__.__name__ == "GroupsPage":
            threading.Thread(target=self.current_frame.group_communicator.handle_leave_group_request).start()
        if self.current_frame.__class__.__name__ != "HomePage":
            print("Switching to home page")
            self.switch_frame("HomePage", self.communicator)

    def switch_to_favorites_page(self):
        self.user_username, self.user_email = self.get_user_info()
        if self.current_frame.__class__.__name__ == "GroupsPage":
            threading.Thread(target=self.current_frame.group_communicator.handle_leave_group_request).start()
        if self.current_frame.__class__.__name__ != "FavoritesPage":
            print("Switching to favorites page")
            self.switch_frame("FavoritesPage", self.communicator, self.set_current_folder_child)

    def setup_new_folder_dialog(self):
        self.add_folder_dialog = CTkToplevel(self)
        self.add_folder_dialog.geometry("300x160")
        self.add_folder_dialog.resizable(False, False)
        self.add_folder_dialog.title("Add Folder")

        title = CTkLabel(self.add_folder_dialog, text="Add Folder", compound="left", font=("Arial", 25))
        title.pack(pady=10, padx=10, side="top", anchor="w")

        self.folder_name_entry = CTkEntry(self.add_folder_dialog, width=280, height=40, placeholder_text="Folder Name")
        self.folder_name_entry.pack(pady=10, padx=10, side="top", anchor="w")

        ok_button = CTkButton(self.add_folder_dialog, text="Add", command=self.handle_add_new_folder_request)
        ok_button.pack(pady=10, padx=10, side="left", anchor="w")

        cancel_button = CTkButton(self.add_folder_dialog, text="Cancel", command=self.add_folder_dialog.destroy)
        cancel_button.pack(pady=10, padx=10, side="left", anchor="w")

        # Center the dialog on the screen
        self.add_folder_dialog.update_idletasks()
        width = self.add_folder_dialog.winfo_width()
        height = self.add_folder_dialog.winfo_height()
        x = (self.add_folder_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.add_folder_dialog.winfo_screenheight() // 2) - (height // 2)
        self.add_folder_dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        # Focus on the add_folder_dialog window
        self.add_folder_dialog.focus_set()

    def handle_log_out_action(self):
        self.communicator.log_out()
        self.pack_forget()
        self.switch_frame("RegistrationApp", self.communicator)

    def set_current_folder_child(self, folder_name, ftype):
        if ftype == "personal":
            self.switch_to_home_page()
            self.current_frame.folder_clicked(folder_name)
        else:
            new_room_dictionary = self.current_frame.get_all_groups()
            for room, permissions in new_room_dictionary.items():
                if room == ftype:
                    self.switch_to_groups_page(ftype, permissions[0], permissions[1])
                    break
            self.current_frame.folder_clicked(folder_name)



    def handle_add_new_folder_request(self):
        folder_name = self.folder_name_entry.get().strip()
        if not folder_name:
            folder_name = "New Folder"
        check_dup = self.current_frame.handle_duplicate_names(folder_name)
        if check_dup != folder_name:
            self.current_frame.handle_add_new_folder_request(check_dup + " <folder>", size=0)
        else:
            self.current_frame.handle_add_new_folder_request(folder_name + " <folder>", size=0)
        self.add_folder_dialog.destroy()

    def handle_send_file_request(self):
        threading.Thread(target=self.current_frame.handle_send_file_request).start()

    def handle_upload_folder_request(self):
        threading.Thread(target=self.current_frame.handle_folder_upload).start()

    def handle_create_group_window(self):
        if self.create_group_top is None or not self.create_group_top.winfo_exists():
            print("1")
            all_user_list = self.current_frame.get_all_registered_users()
            print("2")
            self.create_group_top = CreateGroupWin(self, all_user_list)
            print("3")
            # Wait for the window to be closed or destroyed
            self.create_group_top.wait_window()

            # Check if the window was destroyed without submission
            if not self.create_group_top.submitted:
                return

            group_name = self.create_group_top.selected_name
            submitted_participants = self.create_group_top.submitted_participants
            permissions = self.create_group_top.permissions_answers

            threading.Thread(target=self.communicator.handle_create_group_request,
                             args=(group_name, submitted_participants, permissions,)
                             ).start()

            if group_name and submitted_participants:
                CTkButton(
                    self.group_button_frame,
                    text=group_name,
                    compound='left',
                    fg_color="transparent",
                    command=lambda button_text=group_name: self.switch_to_groups_page(button_text, permissions,
                                                                                      self.user_email)

                ).pack(side='top', pady=5, anchor='w', fill='x', padx=10)

    def get_group_names(self):

        new_room_dictionary = self.current_frame.get_all_groups()
        try:
            print(f"new_room_dictionary: {new_room_dictionary}")

            added_rooms = set(new_room_dictionary.keys()) - set(self.room_dictionary.keys())

            for room, permissions in new_room_dictionary.items():
                if room in added_rooms:
                    CTkButton(
                        self.group_button_frame,
                        text=room,
                        compound='left',
                        fg_color="transparent",
                        command=lambda button_text=room: self.switch_to_groups_page(button_text, permissions[0],
                                                                                    permissions[1])
                    ).pack(side='top', pady=5, anchor='w', fill='x', padx=10)

            # Update the current room dictionary
            self.room_dictionary = new_room_dictionary

        except Exception as e:
            print(f"Error in get_group_names: {e}")
            # Handle errors accordingly


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
        ttk.Label(self, text="Create your shared file group", font=("Calibri bold", 22)
                  ).pack(anchor='w', padx=5, pady=15, fill='x')

        self.setup_group_name_entry()
        self.setup_participants_list()
        self.setup_permissions()  # Fixed method name
        self.setup_buttons()

    def setup_group_name_entry(self):
        container = CTkFrame(self)
        container.pack(fill="both", expand=True, padx=5, pady=5)
        CTkLabel(container, text="Group Name:").pack(anchor='w', padx=10, pady=5)
        self.group_name_entry = CTkEntry(container, textvariable=self.group_name, width=200)
        self.group_name_entry.pack(anchor='w', padx=10)

        # Error label for Group Name entry
        self.group_name_error_label = CTkLabel(container, text="", text_color="red")
        self.group_name_error_label.pack(anchor='w', padx=10)

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
            participant_label.pack(anchor='w', fill='x', expand=True, pady=5)

        # Error label for Participants list
        self.participants_error_label = CTkLabel(participants_list, text="", text_color="red")
        self.participants_error_label.pack(anchor='w', padx=5, pady=5)

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
            return

        self.selected_name = group_name
        # Validate at least one participant is selected
        self.submitted_participants = [name for name, var in self.selected_participants.items() if var.get() == "on"]
        if not self.submitted_participants:
            self.participants_error_label.configure(text="Please select at least one participant.")
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


class MyApp(ttk.Window):
    def __init__(self, client_communicator, group_communicator):
        super().__init__(themename="darkly")
        self.geometry("1150x710")
        self.title("Cloud-AV")

        self.current_frame = None
        self.loaded = False
        self.client_communicator = client_communicator
        self.group_communicator = group_communicator

        self.user_username = None
        self.user_email = None

        self.switch_frame("RegistrationApp", self.client_communicator, self.set_user_info)
        self.page = Page(self, self.switch_frame, self.client_communicator, self.current_frame, self.get_user_info)

    def set_user_info(self, username, email):
        self.user_username = username
        self.user_email = email

    def get_user_info(self):
        return self.user_username, self.user_email

    def switch_frame(self, frame_class, *args):
        if frame_class == "RegistrationApp":
            new_frame = RegistrationApp(self, self.switch_frame, self.client_communicator, self.set_user_info)

            if self.current_frame:
                self.current_frame.pack_forget()

            new_frame.pack(fill="both", expand=True)
            self.current_frame = new_frame

        elif frame_class == "GroupsPage":
            new_frame = GroupsPage(self.page.f_current_page, self.switch_frame, self.group_communicator,
                                   group_name=args[1], permissions=args[2], admin=args[3])

            if self.current_frame:
                self.current_frame.pack_forget()

            self.page.pack(fill="both", expand=True)
            new_frame.pack(fill="both", expand=True)

            self.page.current_frame = new_frame
            self.current_frame = new_frame

            new_frame.set_handle_broadcast_requests_function()

        elif frame_class == "HomePage":
            new_frame = HomePage(self.page.f_current_page, self.switch_frame, self.client_communicator)

            if self.current_frame:
                self.current_frame.pack_forget()

            self.page.pack(fill="both", expand=True)
            new_frame.pack(fill="both", expand=True)

            self.page.current_frame = new_frame
            self.current_frame = new_frame

            if not self.loaded:
                self.page.after(500, self.page.get_group_names)
                self.loaded = True

        elif frame_class == "Logout":
            self.destroy()

        elif frame_class == "FavoritesPage":
            new_frame = FavoritesPage(self.page.f_current_page, self.switch_frame, self.client_communicator
                                      , self.group_communicator, switch_current_folder=args[1])

            if self.current_frame:
                self.current_frame.pack_forget()

            self.page.pack(fill="both", expand=True)
            new_frame.pack(fill="both", expand=True)

            self.page.current_frame = new_frame
            self.current_frame = new_frame

            if not self.loaded:
                self.page.after(500, self.page.get_group_names)
                self.loaded = True

