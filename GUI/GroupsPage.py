import pickle
import threading
import tkinter as tk
from tkinter import filedialog as fd
import ttkbootstrap as ttk
from customtkinter import *
from PIL import Image, ImageTk
import datetime
from ttkbootstrap.toast import ToastNotification


class GroupFileFrame(ttk.Frame):
    def __init__(self, master, file_name, file_size, file_date, file_owner, is_folder=False, click_callback=None,
                 favorite_callback=None):
        super().__init__(master)
        self._file_name = file_name
        self._file_size = file_size
        self._file_date = file_date
        self._file_owner = file_owner
        self._is_folder = is_folder
        self._click_callback = click_callback  # Callback function for click event
        self._favorite_callback = favorite_callback

        self._check_var = StringVar(value="off")
        self._check_favorite = StringVar(value="off")

        self.setup_ui()

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        self._file_name = value
        if hasattr(self, "lu_filename"):
            self.lu_filename.configure(text=value)

    @property
    def file_size(self):
        return self._file_size

    @file_size.setter
    def file_size(self, value):
        self._file_size = value
        if hasattr(self, "lu_size"):
            self.lu_size.configure(text=value)

    @property
    def file_date(self):
        return self._file_date

    @file_date.setter
    def file_date(self, value):
        self._file_date = value
        if hasattr(self, "lu_date_mod"):
            self.lu_date_mod.configure(text=value)

    @property
    def file_owner(self):
        return self._file_owner

    @file_owner.setter
    def file_owner(self, value):
        self._file_owner = value
        if hasattr(self, "lu_owner"):
            self.lu_owner.configure(text=value)

    @property
    def is_folder(self):
        return self._is_folder

    @is_folder.setter
    def is_folder(self, value):
        self._is_folder = value

    @property
    def click_callback(self):
        return self._click_callback

    @click_callback.setter
    def click_callback(self, value):
        self._click_callback = value

    @property
    def favorite_callback(self):
        return self._favorite_callback

    @favorite_callback.setter
    def favorite_callback(self, value):
        self._favorite_callback = value

    def setup_ui(self):
        self.create_checkbutton()
        self.create_icon()
        self.create_filename_label()
        self.create_favorite_button()
        self.create_size_label()
        self.create_date_label()
        self.create_owner_label()

    # Other methods remain the same

    def create_checkbutton(self):
        self.mark_for_action = ttk.Checkbutton(self, text="", variable=self._check_var, onvalue="on", offvalue="off")
        self.mark_for_action.pack(side='left', padx=5)

    def create_icon(self):
        icon_path = self.get_icon_path()
        icon_image = Image.open(icon_path).resize((25, 25))
        tk_icon_image = ImageTk.PhotoImage(icon_image)

        icon_label = ttk.Label(master=self, image=tk_icon_image)
        icon_label.image = tk_icon_image
        icon_label.pack(side='left', padx=(0, 5), pady=5)

    def get_icon_path(self):
        if self.is_folder:
            return "../GUI/file_icons/folder_icon.png"

        icon_map = {
            self.is_image: "../GUI/file_icons/image_file_icon.png",
            self.is_document: "../GUI/file_icons/word_file_icon.png",
            self.is_pdf: "../GUI/file_icons/pdf_file_icon.png",
            self.is_powerpoint: "../GUI/file_icons/powerpoint_file_icon.png",
            self.is_text: "../GUI/file_icons/text_file_icon.png",
            self.is_zip: "../GUI/file_icons/zip_file_icon.png",
            self.is_excel: "../GUI/file_icons/excel_file_icon.png",
            self.is_video: "../GUI/file_icons/video_file_icon.png",
            self.is_code: "../GUI/file_icons/code_file_icon.png",
        }
        for check_function, path in icon_map.items():
            if check_function(self.file_name):
                return path

        return "../GUI/file_icons/other_file_icon.png"

    def create_filename_label(self):
        text_size = 12
        self.lu_filename = ttk.Label(master=self, text=self.file_name, font=("Arial", text_size), cursor="hand2")
        self.lu_filename.pack(side='left', padx=(0, 5), pady=5, anchor='w')
        self.lu_filename.bind("<Button-1>", self.on_click)  # Bind left mouse button click event

    def create_favorite_button(self):
        self.favorite_button = CTkButton(
            master=self,
            image=CTkImage(Image.open("../GUI/file_icons/star_icon.png"), size=(20, 20)),
            compound='left',
            text="",
            width=30,
            fg_color='transparent',
            command=self.toggle_favorite  # Assign the command to the function
        )
        self.favorite_button.pack(side='right', padx=5, anchor='e')

    def create_size_label(self):
        text_size = 12
        self.lu_size = ttk.Label(master=self, text=self.file_size, font=("Arial", text_size))
        self.lu_size.pack(side='right', padx=(0, 27), pady=5, anchor='e')  # Adjust padx as needed

    def create_date_label(self):
        text_size = 12
        self.lu_date_mod = ttk.Label(master=self, text=self.file_date, font=("Arial", text_size))
        self.lu_date_mod.pack(side='right', padx=(0, 65), pady=5, anchor='e')

    def create_owner_label(self):
        text_size = 12
        self.lu_owner = ttk.Label(master=self, text=self.file_owner, font=("Arial", text_size))
        self.lu_owner.pack(side='right', padx=(0, 65), pady=5, anchor='e')

    def toggle_favorite(self):
        current_value = self._check_favorite.get()
        new_value = "on" if current_value == "off" else "off"
        self._check_favorite.set(new_value)

        # Change the button icon based on the new value
        new_icon_path = "../GUI/file_icons/star_icon_light.png" if new_value == "on" else "../GUI/file_icons/star_icon.png"
        new_icon = CTkImage(Image.open(new_icon_path), size=(20, 20))
        self.favorite_button.configure(image=new_icon)

        # Notify the callback when the favorite button is pressed
        if self.favorite_callback:
            self.favorite_callback(self, new_value)

    def on_click(self, event):
        if self.is_folder and self.click_callback:
            self.click_callback(self.file_name)
        else:
            self._check_var.set("on")

    def get_checkvar(self) -> bool:
        return self._check_var.get() == "on"

    def get_filename(self):
        return self.file_name

    def set_filename(self, fname):
        self.file_name = fname
        self.lu_filename.configure(text=fname)

    def uncheck(self):
        self._check_var.set("off")

    def kill_frame(self):
        self.destroy()

    def is_image(self, fname):
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        return any(fname.lower().endswith(ext) for ext in image_extensions)

    def is_document(self, fname):
        document_extensions = ['.doc', '.docx']
        return any(fname.lower().endswith(ext) for ext in document_extensions)

    def is_pdf(self, fname):
        pdf_extensions = ['.pdf']
        return any(fname.lower().endswith(ext) for ext in pdf_extensions)

    def is_powerpoint(self, fname):
        powerpoint_extensions = ['.ppt', '.pptx', '.pps', '.pot', '.potx', '.ppsx']
        return any(fname.lower().endswith(ext) for ext in powerpoint_extensions)

    def is_text(self, fname):
        text_extensions = ['.txt']
        return any(fname.lower().endswith(ext) for ext in text_extensions)

    def is_zip(self, fname):
        zip_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz']
        return any(fname.lower().endswith(ext) for ext in zip_extensions)

    def is_excel(self, fname):
        excel_extensions = ['.xlsx', '.dbf', '.csv', '.xls', '.xlsm']
        return any(fname.lower().endswith(ext) for ext in excel_extensions)

    def is_video(self, fname):
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.mp3', '.asd']
        return any(fname.lower().endswith(ext) for ext in video_extensions)

    def is_code(self, fname):
        code_extensions = ['.py', '.c', '.cpp', '.java', '.js', '.php', '.css', '.cs']
        return any(fname.lower().endswith(ext) for ext in code_extensions)


class GroupsPage(ttk.Frame):
    def __init__(self, parent, switch_frame, group_communicator, group_name, permissions, admin):
        super().__init__(parent)
        self.parent_app = parent
        self.switch_frame = switch_frame
        self.group_name = group_name
        self.group_communicator = group_communicator

        self.permissions = self.set_permissions(permissions)
        self.process_running = False
        self.admin = admin
        self.is_admin = False

        # setting up variables
        self.rename_button = None
        self.f_file_list = None
        self.group_file_frames = []
        self.file_frame_counter = 0
        self.save_path = os.path.join(os.path.expanduser("~"), "Downloads")

        self.name_sort_order = 'ascending'  # Keep track of the current sorting order
        self.clicked_folders = []
        self.current_folder = group_name  # Initialize current folder to the group name by default

        # setting up the frame
        self.setup_group_file_actions_frame()
        self.setup_folder_manager_frame()

        self.users_data = None
        self.room_data = None
        self.search_data = None
        self.room_data_event = threading.Event()
        self.users_data_event = threading.Event()
        self.search_data_event = threading.Event()

        self.presenting_files_event = threading.Event()

    def set_permissions(self, permissions):
        if type(permissions) == list:
            return permissions
        permissions_lst = []
        for key, value in permissions.items():
            permissions_lst.append(value)

        return permissions_lst

    def can_upload(self):
        return self.permissions[0] == '1'

    def can_download(self):
        return self.permissions[1] == '1'

    def can_rename(self):
        return self.permissions[2] == '1'

    def can_delete(self):
        return self.permissions[3] == '1'

    def setup_folder_manager_frame(self):
        self.folder_frame = CTkFrame(master=self)
        self.folder_frame.place(relx=0, rely=0, relwidth=1, relheight=0.05)

        self.root_folder_button = CTkButton(self.folder_frame, text=self.group_name, font=('Arial Bold', 20),
                                            fg_color='transparent', anchor='w',
                                            command=lambda: self.focus_on_folder(self.group_name))
        self.root_folder_button.pack(side='left', padx=5)
        self.clicked_folders.append(self.root_folder_button)

    def setup_group_file_actions_frame(self):
        f_action = ttk.Frame(master=self)
        f_action.place(relx=0, rely=0.06, relwidth=1, relheight=0.05)

        delete_button = CTkButton(
            master=f_action,
            image=CTkImage(Image.open("../GUI/file_icons/trash_icon.png"), size=(20, 20)),
            compound='left',
            text="Delete",
            width=30,
            command=self.handle_delete_request_group,
            fg_color='transparent'
        )
        delete_button.pack(side='left', padx=5)

        download_button = CTkButton(
            master=f_action,
            command=self.handle_download_request_group,
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
            command=self.handle_rename_request_group,
            fg_color='transparent'
        )
        self.rename_button.pack(side='left', padx=5)

        combined_frame = CTkFrame(master=self)
        combined_frame.place(relx=0, rely=0.11, relwidth=1, relheight=0.89)

        f_file_properties = CTkFrame(master=combined_frame, fg_color='transparent')
        f_file_properties.place(relx=0, rely=0, relwidth=1, relheight=0.08)

        CTkButton(master=f_file_properties, text="Name").pack(side='left', padx=5)
        CTkButton(master=f_file_properties, text="Size").pack(side='right', padx=10)
        CTkButton(master=f_file_properties, text="Upload date").pack(side='right', padx=10)

        ttk.Separator(combined_frame, orient="horizontal").place(relx=0, rely=0.08, relwidth=1)

        self.f_file_list = CTkScrollableFrame(master=combined_frame, fg_color='transparent')
        self.f_file_list.place(relx=0, rely=0.09, relwidth=1, relheight=0.91)

    def handle_duplicate_names(self, given_name):
        # Extract existing names from file frames
        existing_names = [file_frame.get_filename() for file_frame in self.group_file_frames]

        # Check if the given name already exists
        if given_name in existing_names:
            # Determine the number to append to the given name to make it unique
            count = 1
            new_name = f"{given_name} ({count})"
            while new_name in existing_names:
                count += 1
                new_name = f"{given_name} ({count})"
            return new_name
        else:
            return given_name

    def sort_by_name(self):
        # Toggle the sorting order
        if self.name_sort_order == 'ascending':
            self.group_file_frames.sort(key=lambda x: x.get_filename().lower())
            self.name_sort_order = 'descending'
        else:
            self.group_file_frames.sort(key=lambda x: x.get_filename().lower(), reverse=True)
            self.name_sort_order = 'ascending'

        # Re-pack the file frames in the scrollable frame
        for file_frame in self.group_file_frames:
            file_frame.pack_forget()
            file_frame.pack(expand=True, fill='x', side='top')

    def set_size_format(self, file_size_bytes):
        if file_size_bytes < 1024:
            return f"{file_size_bytes} bytes"
        elif file_size_bytes < 1024 ** 2:
            return f"{file_size_bytes / 1024:.2f} KB"
        elif file_size_bytes < 1024 ** 3:
            return f"{file_size_bytes / (1024 ** 2):.2f} MB"
        else:
            return f"{file_size_bytes / (1024 ** 3):.2f} GB"

    def set_date_format(self, file_uploadate: datetime):
        time_difference = datetime.datetime.now() - file_uploadate

        # Calculate the time difference in minutes
        minutes_difference = int(time_difference.total_seconds() / 60)

        # Format the short date string based on the time difference
        if minutes_difference < 60:
            short_file_date = f"{minutes_difference} minute ago"
        elif minutes_difference < 24 * 60:
            short_file_date = f"{minutes_difference // 60} hours ago"
        elif minutes_difference < 24 * 60 * 7:
            short_file_date = f"{minutes_difference // (24 * 60)}d"
        else:
            short_file_date = file_uploadate.strftime('%B %d, %Y')

        return short_file_date

    def handle_favorite_toggle(self, file_frame, new_value):
        try:
            self.process_running = True
            file_name = file_frame.get_filename()
            if file_frame.is_folder:
                file_name = file_name + " <folder>"
            if new_value == "on":
                favorite_thread = threading.Thread(
                    target=self.group_communicator.handle_set_favorite_request_group,
                    args=(file_name, new_value, self.group_name))
                favorite_thread.start()
            else:
                unfavorite_thread = threading.Thread(
                    target=self.group_communicator.handle_set_favorite_request_group,
                    args=(file_name, new_value, self.group_name))
                unfavorite_thread.start()
        finally:
            self.process_running = False

    def set_frame_properties_for_display(self, file_name, file_bytes, file_uploadate: datetime):
        short_filename = os.path.basename(file_name)
        formatted_file_size = self.set_size_format(file_bytes)
        short_file_date = self.set_date_format(file_uploadate)
        return short_filename, formatted_file_size, short_file_date

    def add_folder_frame(self, real_folder_name, folder_size, folder_date, group_folder_owner, favorite):
        file_frame = GroupFileFrame(self.f_file_list, real_folder_name, folder_size, folder_date, group_folder_owner,
                                    is_folder=True, favorite_callback=self.handle_favorite_toggle,
                                    click_callback=self.folder_clicked)
        file_frame.pack(expand=True, fill='x', side='top')
        self.group_file_frames.append(file_frame)
        self.file_frame_counter += 1

        if favorite == 1:
            file_frame.toggle_favorite()

    def add_file_frame(self, group_file_name, group_file_size, group_file_date, group_file_owner, favorite):
        file_frame = GroupFileFrame(self.f_file_list, group_file_name, group_file_size, group_file_date,
                                    group_file_owner, favorite_callback=self.handle_favorite_toggle)

        file_frame.pack(expand=True, fill='x', side='top')
        self.group_file_frames.append(file_frame)
        self.file_frame_counter += 1

        if favorite == 1:
            file_frame.toggle_favorite()

    def get_file_name_to_rename(self, received_data):
        old_name, new_name, folder = received_data
        for file_frame in self.group_file_frames:
            filename = file_frame.get_filename()
            if filename == old_name:
                file_frame.set_filename(new_name)
                file_frame.update_idletasks()

    def handle_received_item(self, item):
        try:
            if self.presenting_files_event.is_set():
                print("A process is already running. Please wait.")
                return
            self.presenting_files_event.set()
            owner, name, size, date, group_name, folder, favorite = item
            formatted_file_date = self.set_date_format(date)
            formatted_file_size = self.set_size_format(size)
            if folder == self.get_current_folder():
                if " <folder>" in name:
                    formatted_file_size = str(size) + " items"
                    self.add_folder_frame(name.replace(" <folder>", ""), formatted_file_size, formatted_file_date, owner,
                                          favorite)
                else:
                    self.add_file_frame(name.replace(" <folder>", ""), formatted_file_size, formatted_file_date, owner,
                                        favorite)

        finally:
            self.presenting_files_event.clear()

    def folder_clicked(self, folder_name):
        try:
            if self.presenting_files_event.is_set():
                print("A process is already running. Please wait.")
                return
            self.presenting_files_event.set()

            print(f"Folder clicked: {folder_name}")
            # Delete all existing file frames
            for file_frame in self.group_file_frames:
                file_frame.destroy()
            # Clear the file frames list
            self.group_file_frames.clear()
            # Add folder button to the list of clicked folders
            folder_button = CTkButton(self.folder_frame, anchor='w', text=folder_name, fg_color='transparent',
                                      font=('Arial Bold', 20),
                                      command=lambda: self.focus_on_folder(folder_name))
            folder_button.pack(side='left', anchor='w', pady=3)
            self.clicked_folders.append(folder_button)
            self.update_current_folder(folder_name)

            print(f"current folder: {self.current_folder}")

            self.group_communicator.handle_presaved_files_group(self.get_current_folder())
        finally:
            self.presenting_files_event.clear()

    def focus_on_folder(self, folder_name):
        try:
            if self.presenting_files_event.is_set():
                print("A process is already running. Please wait.")
                return
            self.presenting_files_event.set()

            for folder_button in self.clicked_folders:
                if folder_button.cget('text') == folder_name:
                    index_of_folder = self.clicked_folders.index(folder_button)
                    for i in range(index_of_folder + 1, len(self.clicked_folders)):
                        # Destroy each button
                        self.clicked_folders[i].destroy()
            # Clear existing file frames
            for file_frame in self.group_file_frames:
                file_frame.destroy()
            self.group_file_frames.clear()

            # Update the current folder
            self.update_current_folder(folder_name)

            # run handle_presaved_files_group, answer will be picked by handle_broadcast_requests
            self.group_communicator.handle_presaved_files_group(self.get_current_folder())
        finally:
            self.presenting_files_event.clear()

    def get_checked_file_frames(self):
        checked_file_frames_list = []
        for file_frame in self.group_file_frames:
            if file_frame.get_checkvar():
                checked_file_frames_list.append(file_frame)
                file_frame.uncheck()

        return checked_file_frames_list

    def get_and_destroy_checked_file_names(self, names_to_delete_lst):
        for file_frame in self.group_file_frames:
            filename = file_frame.get_filename()
            if filename in names_to_delete_lst:
                file_frame.kill_frame()

        self.file_frame_counter = len(self.group_file_frames)

    def handle_presenting_presaved_files(self, narf_answer):
        try:
            self.presenting_files_event.set()  # Set the event before handling presaved files
            if narf_answer == "<NO_DATA>":
                return
            for individual_file in narf_answer:
                self.handle_received_item(individual_file)
        finally:
            self.presenting_files_event.clear()

    def handle_add_new_folder_request(self, folder_name):
        try:
            if self.presenting_files_event.is_set():
                print("A process is already running. Please wait.")
                return
            self.presenting_files_event.set()

            real_folder_name = folder_name.replace(" <folder>", "")
            folder_date = datetime.datetime.now()
            folder_size = "0"
            folder_folder = self.get_current_folder()

            formatted_folder_date = self.set_date_format(folder_date)

            add_folder_thread = threading.Thread(target=self.group_communicator.handle_add_new_folder_request,
                                                 args=(
                                                     folder_name, folder_size, folder_date, folder_folder,
                                                     self.group_name))
            add_folder_thread.start()

            self.add_folder_frame(real_folder_name, folder_size, formatted_folder_date, "You", 0)
        finally:
            self.presenting_files_event.clear()

    def handle_send_file_request(self):
        try:
            if self.presenting_files_event.is_set():
                print("A process is already running. Please wait.")
                return
            self.presenting_files_event.set()

            if not self.can_upload() and self.is_admin is False:
                print("You are not authorized to upload data.")
                tk.messagebox.showinfo(title="Error", message="You are not authorized to upload data.")
                return
            filetypes = (
                ('All files', '*.*'),
                ('text files', '*.txt'),
                ('All files', '*.*')
            )

            file_name = fd.askopenfilename(
                title='Select a file',
                initialdir='/',
                filetypes=filetypes)

            file_bytes = os.path.getsize(file_name)
            file_date = datetime.datetime.now()

            short_filename, formatted_file_size, short_file_date = \
                self.set_frame_properties_for_display(file_name, file_bytes, file_date)

            send_file_thread = threading.Thread(
                target=self.group_communicator.handle_send_file_request,
                args=(file_name, short_filename, file_date, file_bytes, self.get_current_folder(), True)
            )
            send_file_thread.start()

            self.add_file_frame(short_filename, formatted_file_size, short_file_date, group_file_owner="self",
                                favorite=0)
        finally:
            self.presenting_files_event.clear()

    def handle_download_request_group(self):
        try:
            if self.presenting_files_event.is_set():
                print("A process is already running. Please wait.")
                return
            self.presenting_files_event.set()

            if not self.can_download() and self.is_admin is False:
                print("You are not authorized to download data.")
                tk.messagebox.showinfo(title="Error", message="You are not authorized to download data.")
                return

            select_file_frames = self.get_checked_file_frames()
            select_file_names_lst = [file_frame.get_filename() for file_frame in select_file_frames]

            # Check if any selected file is a folder
            is_folder_selected = any(file_frame.is_folder for file_frame in select_file_frames)

            print(f"select_file_frames: {select_file_frames}")
            print(f"select_file_names_lst: {select_file_names_lst}")
            print(f"self.get_current_folder(): {self.get_current_folder()}")

            if is_folder_selected:
                # If any selected file is a folder, handle folder downloads
                for file_frame in select_file_frames:
                    if file_frame.is_folder:
                        folder_name = file_frame.get_filename()
                        print("Folder name:", folder_name)
                        receive_thread = threading.Thread(
                            target=self.group_communicator.handle_download_folder_request_group,
                            args=(folder_name, self.save_path, self.get_current_folder()))
                        receive_thread.start()
            else:
                # Otherwise, handle file downloads
                receive_thread = threading.Thread(
                    target=self.group_communicator.handle_download_request_group,
                    args=(select_file_names_lst, self.save_path, self.current_folder))
                receive_thread.start()
        finally:
            self.presenting_files_event.clear()

    def handle_saving_broadcasted_files(self, file_data_name_dict):
        for indiv_filename, indiv_filebytes in file_data_name_dict.items():
            file_path = os.path.join(self.save_path, indiv_filename)
            with open(file_path, "wb") as file:
                file.write(indiv_filebytes)
                print(f"File '{indiv_filename}' received successfully.")

    def handle_delete_request_group(self):
        try:
            if self.presenting_files_event.is_set():
                print("A process is already running. Please wait.")
                return
            self.presenting_files_event.set()

            if not self.can_delete() and self.is_admin is False:
                print("You are not authorized to delete data.")
                tk.messagebox.showinfo(title="Error", message="You are not authorized to delete data.")
                return
            frames_to_delete = self.get_checked_file_frames()
            names_to_delete_lst = []
            folders_to_delete_lst = []

            for file_frame in frames_to_delete:
                if file_frame.is_folder:
                    folders_to_delete_lst.append(file_frame.get_filename() + " <folder>")
                else:
                    names_to_delete_lst.append(file_frame.get_filename())

            print(f"names_to_delete_lst: {names_to_delete_lst}")
            print(f"folders_to_delete_lst: {folders_to_delete_lst}")

            delete_thread = threading.Thread(
                target=self.group_communicator.handle_delete_request_group,
                args=(names_to_delete_lst, folders_to_delete_lst, self.get_current_folder())
            ).start()

            for file_frame in frames_to_delete:
                file_frame.kill_frame()

            self.file_frame_counter = len(self.group_file_frames)
        finally:
            self.presenting_files_event.clear()

    def handle_rename_request_group(self):
        try:
            if self.presenting_files_event.is_set():
                print("A process is already running. Please wait.")
                return
            self.presenting_files_event.set()

            if not self.can_rename() and self.is_admin is False:
                print("You are not authorized to rename data.")
                tk.messagebox.showinfo(title="Error", message="You are not authorized to rename data.")
                return
            file_frame = self.get_checked_file_frames()[0]
            old_name = file_frame.get_filename()

            file_format = ""
            if not file_frame.is_folder:
                file_format = os.path.splitext(old_name)[1]

            new_name_dialog = CTkInputDialog(text=f"Replace {old_name} with:",
                                             title="Rename " + ("folder" if file_frame.is_folder else "file"))
            new_name = new_name_dialog.get_input()

            if new_name:
                if file_frame.is_folder:
                    new_name_with_format = f"{new_name} <folder>"
                    rename_thread = threading.Thread(
                        target=self.group_communicator.handle_rename_request_group,
                        args=((old_name + " <folder>", new_name_with_format, self.get_current_folder()), "<FOLDER>")
                    )
                else:
                    new_name_with_format = f"{new_name}{file_format}"
                    rename_thread = threading.Thread(
                        target=self.group_communicator.handle_rename_request_group,
                        args=((old_name, new_name_with_format, self.get_current_folder()), "<FILE>")
                    )

                rename_thread.start()

                # Update the UI
                file_frame.set_filename(new_name_with_format if file_frame.is_folder else new_name_with_format)
                file_frame.update_idletasks()
        except IndexError:
            pass

        finally:
            self.presenting_files_event.clear()

    def set_handle_broadcast_requests_function(self):
        self.group_communicator.handle_broadcast_requests = self.handle_broadcast_requests

    def handle_broadcast_requests(self, pickled_data):
        try:
            try:
                data = pickle.loads(pickled_data)
            except TypeError:
                data = pickled_data

            protocol_flag = data.get("FLAG")
            received_data = data.get("DATA")
            current_folder = data.get("CURRENT_FOLDER")

            if protocol_flag == "<SEND>":
                for item in received_data:
                    self.handle_received_item(item)

            elif protocol_flag == "<NARF>":
                self.handle_presenting_presaved_files(received_data)

            elif protocol_flag == "<DELETE>":
                self.get_and_destroy_checked_file_names(received_data)

            elif protocol_flag == "<RECV>":
                self.handle_saving_broadcasted_files(received_data)

            elif protocol_flag == "<RENAME>":
                self.get_file_name_to_rename(received_data)

            elif protocol_flag == '<GET_USERS>':
                self.users_data = received_data
                # Set the event flag to indicate that data is ready
                self.users_data_event.set()

            elif protocol_flag == "<RECV_FOLDER>":
                self.handle_save_folder(received_data)

            elif protocol_flag == "<CREATE_FOLDER_GROUP>":
                self.create_new_folder(received_data)


            elif protocol_flag == "<GET_ROOMS>":
                self.room_data = received_data

                self.room_data_event.set()

            elif protocol_flag == '<SEARCH_RESULTS>':
                self.search_data = received_data
                self.display_search_results(self.search_data)

        except pickle.UnpicklingError:
            return

    def get_current_folder(self):
        return self.current_folder

    def update_current_folder(self, folder_name):
        self.current_folder = folder_name

    def get_files_and_subdirectories(self, folder_path):
        """
        Recursively gets all files and subdirectories from a folder.

        Args:
        folder_path (str): The path of the folder.

        Returns:
        list: A list of file paths and subdirectory paths.
        """
        paths = []
        for root, directories, files in os.walk(folder_path):
            for directory in directories:
                directory_path = os.path.join(root, directory)
                paths.append(directory_path)
            for file in files:
                file_path = os.path.join(root, file)
                paths.append(file_path)
        return paths

    def handle_folder_upload(self):
        try:
            if not self.can_upload() and self.is_admin is False:
                print("You are not authorized to upload data.")
                tk.messagebox.showerror("Error", "You are not authorized to upload data.")
                return
            count = 0
            folder_path = fd.askdirectory(title='Select a folder')
            if folder_path:
                paths = self.get_files_and_subdirectories(folder_path)
                print(paths)
                for path in paths:
                    if os.path.isdir(path):  # If it's a folder
                        folder_name = os.path.basename(path) + " <folder>"
                        folder_date = datetime.datetime.now()
                        folder_size = len(os.listdir(path))  # Count the number of files in the folder
                        formatted_folder_date = self.set_date_format(folder_date)

                        # Add folder to the database
                        send_folder_thread = threading.Thread(
                            target=self.group_communicator.handle_add_new_folder_request,
                            args=(
                                folder_name, folder_size, folder_date, os.path.basename(os.path.dirname(path)),
                                self.group_name)
                        )
                        send_folder_thread.start()
                    else:  # If it's a file
                        file_bytes = os.path.getsize(path)
                        file_date = datetime.datetime.now()

                        short_filename, formatted_file_size, short_file_date = \
                            self.set_frame_properties_for_display(path, file_bytes, file_date)

                        file_folder = os.path.basename(os.path.dirname(path))

                        # Upload file to the database
                        send_file_thread = threading.Thread(
                            target=self.group_communicator.handle_send_file_request,
                            args=(path, short_filename, file_date, file_bytes, file_folder)
                        )
                        send_file_thread.start()

                        favorite = 0

                    count += 1

                self.handle_add_new_folder_request(os.path.basename(folder_path) + " <folder>")

        except FileNotFoundError:
            return

    def get_all_registered_users(self):
        # Set the flag to False initially
        self.users_data_event.clear()

        # Call the function to request user data
        self.group_communicator.get_all_registered_users(self.get_current_folder())

        # Wait until the event is set (flag received)
        self.users_data_event.wait()

        # Once the event is set, return the received data
        return self.users_data

    def check_if_admin(self, user_email):
        if user_email == self.admin:
            self.is_admin = True

    def get_all_groups(self):
        # Set the flag to False initially
        self.room_data_event.clear()

        threading.Thread(target=self.group_communicator.get_all_groups).start()

        # Wait until the event is set (flag received)
        self.room_data_event.wait()

        # Once the event is set, return the received data
        return self.room_data

    def handle_save_folder(self, recived_data):
        zip_file_name = f"{recived_data[1]}.zip"
        zip_data = recived_data[0]
        zip_file_path = os.path.join(self.save_path, zip_file_name)
        with open(zip_file_path, 'wb') as zip_file:
            zip_file.write(zip_data)

    def perform_search(self, search_query):
        self.current_folder = search_query
        threading.Thread(target=self.group_communicator.handle_search_request, args=(search_query,)).start()

    def display_search_results(self, search_results):
        for file_frame in self.group_file_frames:
            file_frame.destroy()

        for result in search_results:
            owner, fname, fsize, fdate, folder, favorite = result
            formatted_file_size = self.set_size_format(fsize)
            formatted_file_date = self.set_date_format(fdate)

            if " <folder>" in fname:
                formatted_file_size = str(fsize) + " items"
                self.add_folder_frame(fname.replace(" <folder>", ""), formatted_file_size, formatted_file_date, owner,
                                      favorite)
            else:
                self.add_file_frame(fname.replace(" <folder>", ""), formatted_file_size, formatted_file_date, owner,
                                    favorite)

    def create_new_folder(self, recived_data):
        owner, name, size, date, group_name, folder, favorite = recived_data[0]
        formatted_date = self.set_date_format(date)
        formatted_file_size = self.set_size_format(size)
        formatted_file_size = str(size) + " items"
        if folder == self.get_current_folder():
            self.add_folder_frame(name.replace(" <folder>", ""), formatted_file_size, formatted_date, owner, favorite)


    def check_is_process_runs(self):
        return self.presenting_files_event.is_set()