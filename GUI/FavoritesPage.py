import threading
from tkinter import filedialog as fd
import customtkinter
import ttkbootstrap as ttk
from customtkinter import *
from PIL import Image, ImageTk

import datetime


class FavoritesPage(ttk.Frame):
    customtkinter.set_appearance_mode("dark")

    def __init__(self, parent, switch_frame, client_communicator):
        super().__init__(parent)
        self.parent_app = parent
        self.switch_frame = switch_frame
        self.client_communicator = client_communicator

        self.f_file_list = None
        self.file_frames = []
        self.file_frame_counter = 0
        self.save_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.rename_button = None
        self.delete_button = None
        self.folder_frame = None

        self.name_sort_order = 'ascending'  # Keep track of the current sorting order
        self.clicked_folders = []
        self.current_folder = "Home"  # Initialize current folder to "Home" by default

        self.setup_folder_manager_frame()
        self.setup_file_actions_frame()

        narf_thread = threading.Thread(target=self.handle_presenting_presaved_files, args=(self.get_current_folder(),))
        narf_thread.start()

    def setup_folder_manager_frame(self):
        self.folder_frame = CTkFrame(master=self)
        self.folder_frame.place(relx=0, rely=0, relwidth=1, relheight=0.05)

        self.home_folder_button = CTkButton(self.folder_frame, text="Home", font=('Arial Bold', 20),
                                            fg_color='transparent', anchor='w',
                                            command=lambda: self.focus_on_folder("Home"))
        self.home_folder_button.pack(side='left', anchor='w', pady=3)

        self.clicked_folders.append(self.home_folder_button)

    def setup_file_actions_frame(self):
        f_action = ttk.Frame(master=self)
        f_action.place(relx=0, rely=0.06, relwidth=1, relheight=0.05)

        delete_button = CTkButton(
            master=f_action,
            image=CTkImage(Image.open("../GUI/file_icons/trash_icon.png"), size=(20, 20)),
            compound='left',
            text="Delete",
            width=30,
            command=self.handle_delete_request_client,
            fg_color='transparent'
        )
        delete_button.pack(side='left', padx=5)

        download_button = CTkButton(
            master=f_action,
            command=self.handle_download_request_client,
            image=CTkImage(Image.open("../GUI/file_icons/download_icon.png"), size=(20, 20)),
            compound='left',
            text="Download",
            width=30,
            fg_color='transparent'
        )
        download_button.pack(side='left', padx=5)

        self.rename_button = CTkButton(
            master=f_action,
            image=CTkImage(Image.open("../GUI/file_icons/rename_icon.png"), size=(20, 20)),
            compound='left',
            text="Rename",
            width=30,
            command=self.handle_rename_request_client,
            fg_color='transparent'
        )
        self.rename_button.pack(side='left', padx=5)

        shared_button = CTkButton(
            master=f_action,
            image=CTkImage(Image.open("../GUI/file_icons/shared_icon.png"), size=(20, 20)),
            compound='left',
            text="Share",
            width=30,
            fg_color='transparent'
        )
        shared_button.pack(side='left', padx=5)

        copy_button = CTkButton(
            master=f_action,
            image=CTkImage(Image.open("../GUI/file_icons/copy_icon.png"), size=(20, 20)),
            compound='left',
            text="Copy",
            width=30,
            fg_color='transparent'
        )
        copy_button.pack(side='left', padx=5)

        combined_frame = CTkFrame(master=self)
        combined_frame.place(relx=0, rely=0.11, relwidth=1, relheight=0.89)

        f_file_properties = CTkFrame(master=combined_frame, fg_color='transparent')
        f_file_properties.place(relx=0, rely=0, relwidth=1, relheight=0.08)

        CTkButton(master=f_file_properties, text="Name", command=self.sort_by_name).pack(side='left', padx=5)
        CTkButton(master=f_file_properties, text="Size").pack(side='right', padx=10)
        CTkButton(master=f_file_properties, text="Upload date").pack(side='right', padx=10)

        ttk.Separator(combined_frame, orient="horizontal").place(relx=0, rely=0.08, relwidth=1)

        self.f_file_list = CTkScrollableFrame(master=combined_frame, fg_color='transparent')
        self.f_file_list.place(relx=0, rely=0.09, relwidth=1, relheight=0.91)
