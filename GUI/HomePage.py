import threading
from tkinter import filedialog as fd
import customtkinter
import ttkbootstrap as ttk
from customtkinter import *
from PIL import Image, ImageTk

from GUI.GroupsPage import GroupsPage
import datetime


class FileFrame(ttk.Frame):
    def __init__(self, master, fname, fsize, fdate, favorite_callback=None, is_folder=False, click_callback=None):
        super().__init__(master)
        self.fname = fname
        self.fsize = fsize
        self.fdate = fdate
        self.is_folder = is_folder
        self.click_callback = click_callback  # Callback function for click event

        self.check_var = StringVar(value="off")
        self.mark_for_action = ttk.Checkbutton(self, text="",
                                               variable=self.check_var, onvalue="on", offvalue="off")
        self.mark_for_action.pack(side='left', padx=5)

        # Set the default icon path
        if self.is_folder:
            icon_path = "../GUI/file_icons/folder_icon.png"  # Set folder icon path
        else:
            icon_path = "../GUI/file_icons/other_file_icon.png"

            # Check file type and set icon accordingly
        if not self.is_folder:
            if self.is_image(fname):
                icon_path = "../GUI/file_icons/image_file_icon.png"
            elif self.is_document(fname):
                icon_path = "../GUI/file_icons/word_file_icon.png"
            elif self.is_pdf(fname):
                icon_path = "../GUI/file_icons/pdf_file_icon.png"
            elif self.is_powerpoint(fname):
                icon_path = "../GUI/file_icons/powerpoint_file_icon.png"
            elif self.is_text(fname):
                icon_path = "../GUI/file_icons/text_file_icon.png"
            elif self.is_zip(fname):
                icon_path = "../GUI/file_icons/zip_file_icon.png"
            elif self.is_excel(fname):
                icon_path = "../GUI/file_icons/excel_file_icon.png"
            elif self.is_video(fname):
                icon_path = "../GUI/file_icons/video_file_icon.png"
            elif self.is_code(fname):
                icon_path = "../GUI/file_icons/code_file_icon.png"

        # Load the icon image
        icon_image = Image.open(icon_path)
        icon_image = icon_image.resize((25, 25))

        tk_icon_image = ImageTk.PhotoImage(icon_image)

        # Create a label to display the icon
        icon_label = ttk.Label(master=self, image=tk_icon_image)
        icon_label.image = tk_icon_image
        icon_label.pack(side='left', padx=(0, 5), pady=5)

        text_size = 12

        self.check_favorite = StringVar(value="off")
        self.favorite_callback = favorite_callback

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

        # Create a label for the filename
        self.lu_filename = ttk.Label(
            master=self,
            text=self.fname,
            font=("Arial", text_size),
            cursor="hand2"  # Change cursor to hand2 to indicate it's clickable
        )
        self.lu_filename.pack(side='left', padx=(0, 5), pady=5, anchor='w')
        self.lu_filename.bind("<Button-1>", self.on_click)  # Bind left mouse button click event

        # Pack the size label with proper alignment
        self.lu_size = ttk.Label(
            master=self,
            text=self.fsize,
            font=("Arial", text_size)
        )
        self.lu_size.pack(side='right', padx=(0, 27), pady=5, anchor='e')  # Adjust padx as needed

        # Pack the date label with proper alignment
        self.lu_date_mod = ttk.Label(
            master=self,
            text=self.fdate,
            font=("Arial", text_size)
        )
        self.lu_date_mod.pack(side='right', padx=(0, 65), pady=5, anchor='e')

    def toggle_favorite(self):
        current_value = self.check_favorite.get()
        new_value = "on" if current_value == "off" else "off"
        self.check_favorite.set(new_value)

        # Change the button icon based on the new value
        new_icon_path = "../GUI/file_icons/star_icon_light.png" if new_value == "on" else "../GUI/file_icons/star_icon.png"
        new_icon = CTkImage(Image.open(new_icon_path), size=(20, 20))
        self.favorite_button.configure(image=new_icon)

        # Notify the HomePage when the favorite button is pressed
        if self.favorite_callback:
            self.favorite_callback(self, new_value)

    def on_click(self, event):
        if self.is_folder and self.click_callback:
            self.click_callback(self.fname)
        else:
            self.check_var.set("on")

    def get_checkvar(self) -> bool:
        return self.check_var.get() == "on"

    def get_filename(self):
        return self.fname

    def set_filename(self, fname):
        self.fname = fname
        self.lu_filename.configure(text=fname)

    def uncheck(self):
        self.check_var.set("off")

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


class HomePage(ttk.Frame):
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

    def handle_duplicate_names(self, given_name):
        # Extract existing names from file frames
        existing_names = [file_frame.get_filename() for file_frame in self.file_frames]

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
            self.file_frames.sort(key=lambda x: x.get_filename().lower())
            self.name_sort_order = 'descending'
        else:
            self.file_frames.sort(key=lambda x: x.get_filename().lower(), reverse=True)
            self.name_sort_order = 'ascending'

        # Re-pack the file frames in the scrollable frame
        for file_frame in self.file_frames:
            file_frame.pack_forget()
            file_frame.pack(expand=True, fill='x', side='top')

    @staticmethod
    def set_size_format(file_size_bytes):
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

    def set_frame_properties_for_display(self, file_name, file_bytes, file_uploadate: datetime):
        short_filename = os.path.basename(file_name)

        formatted_file_size = self.set_size_format(file_bytes)
        short_file_date = self.set_date_format(file_uploadate)

        return short_filename, formatted_file_size, short_file_date

    def handle_add_new_folder_request(self, folder_name):
        real_folder_name = folder_name.replace(" <folder>", "")
        folder_size = 0
        folder_date = datetime.datetime.now()
        folder_folder = self.get_current_folder()

        formatted_folder_date = self.set_date_format(folder_date)

        add_folder_thread = threading.Thread(target=self.client_communicator.handle_add_new_folder_request,
                                             args=(folder_name, folder_size, folder_date, folder_folder))
        add_folder_thread.start()

        self.add_folder_frame(real_folder_name, str(folder_size) + " items", formatted_folder_date, 0)

    def add_folder_frame(self, real_folder_name, folder_size, folder_date, favorite):
        file_frame = FileFrame(self.f_file_list, real_folder_name, folder_size, folder_date, favorite_callback=self.handle_favorite_toggle, is_folder=True,
                               click_callback=self.folder_clicked)
        file_frame.pack(expand=True, fill='x', side='top')
        self.file_frames.append(file_frame)
        self.file_frame_counter += 1

        if favorite == 1:
            file_frame.favorite_button.configure(
                image=CTkImage(Image.open("../GUI/file_icons/star_icon_light.png"), size=(20, 20)))
            file_frame.check_favorite.set("on")

    def folder_clicked(self, folder_name):
        print(f"Folder clicked: {folder_name}")
        # Delete all existing file frames
        for file_frame in self.file_frames:
            file_frame.destroy()
        # Clear the file frames list
        self.file_frames.clear()
        # Add folder button to the list of clicked folders
        folder_button = CTkButton(self.folder_frame, anchor='w', text=folder_name, fg_color='transparent',
                                  font=('Arial Bold', 20),
                                  command=lambda: self.focus_on_folder(folder_name))
        folder_button.pack(side='left', anchor='w', pady=3)
        self.clicked_folders.append(folder_button)
        self.update_current_folder(folder_name)

        print(f"current folder: {self.current_folder}")

        narf_thread = threading.Thread(target=self.handle_presenting_presaved_files, args=(self.get_current_folder(),))
        narf_thread.start()

    def focus_on_folder(self, folder_name):
        print(self.clicked_folders)
        for folder_button in self.clicked_folders:
            if folder_button.cget('text') == folder_name:
                index_of_folder = self.clicked_folders.index(folder_button)
                for i in range(index_of_folder + 1, len(self.clicked_folders)):
                    # Destroy each button
                    self.clicked_folders[i].destroy()
        # Clear existing file frames
        for file_frame in self.file_frames:
            file_frame.destroy()
        self.file_frames.clear()

        # Update the current folder
        self.update_current_folder(folder_name)

        # Retrieve files belonging to the clicked folder from your data source
        narf_thread = threading.Thread(target=self.handle_presenting_presaved_files, args=(self.get_current_folder(),))
        narf_thread.start()

    def get_checked_file_frames(self):
        checked_file_frames_list = []
        for file_frame in self.file_frames:
            if file_frame.get_checkvar():
                checked_file_frames_list.append(file_frame)
                file_frame.uncheck()

        return checked_file_frames_list

    def add_file_frame(self, file_name, file_size, file_date, favorite):
        file_frame = FileFrame(self.f_file_list, file_name, file_size, file_date,
                               favorite_callback=self.handle_favorite_toggle)
        file_frame.pack(expand=True, fill='x', side='top')
        self.file_frames.append(file_frame)
        self.file_frame_counter += 1

        if favorite == 1:
            file_frame.favorite_button.configure(
                image=CTkImage(Image.open("../GUI/file_icons/star_icon_light.png"), size=(20, 20)))
            file_frame.check_favorite.set("on")

    def handle_presenting_presaved_files(self, folder_name):
        narf_answer = self.client_communicator.handle_presaved_files_client(folder_name)
        if narf_answer == "<NO_DATA>" or narf_answer is None:
            return
        for individual_file in narf_answer:
            (file_name, file_bytes, file_date, favorite, folder) = individual_file
            print(f"file date{file_date}")
            if folder == self.get_current_folder():
                formatted_file_date = self.set_date_format(file_date)

                if " <folder>" in file_name:
                    formatted_file_size = str(file_bytes) + " items"
                    self.add_folder_frame(file_name.replace(" <folder>", ""), formatted_file_size, formatted_file_date, favorite)
                else:
                    formatted_file_size = self.set_size_format(file_bytes)
                    self.add_file_frame(file_name.replace(" <folder>", ""), formatted_file_size, formatted_file_date,
                                        favorite)

    def handle_send_file_request(self):
        try:
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

            file_folder = self.get_current_folder()

            send_file_thread = threading.Thread(
                target=self.client_communicator.handle_send_file_request(file_name, short_filename, file_date,
                                                                         file_bytes, file_folder))
            send_file_thread.start()

            favorite = 0

            self.add_file_frame(short_filename, formatted_file_size, short_file_date, favorite)

        except FileNotFoundError:
            return

    def handle_download_request_client(self):
        select_file_frames = self.get_checked_file_frames()
        select_file_names_lst = [file_frame.get_filename() for file_frame in select_file_frames]

        # Check if any selected file is a folder
        is_folder_selected = any(file_frame.is_folder for file_frame in select_file_frames)

        if is_folder_selected:
            # If any selected file is a folder, call recv_folder method
            for file_frame in select_file_frames:
                if file_frame.is_folder:
                    folder_name = file_frame.get_filename()
                    print("Folder name:", folder_name)
                    receive_thread = threading.Thread(
                        target=self.client_communicator.handle_download_folder_request_client,
                        args=(folder_name, self.save_path))
                    receive_thread.start()
        else:
            # Otherwise, call handle_download_folder_request_client method
            receive_thread = threading.Thread(
                target=self.client_communicator.handle_download_request_client,
                args=(select_file_names_lst, self.save_path, self.get_current_folder()))
            receive_thread.start()

    def handle_favorite_toggle(self, file_frame, new_value):
        file_name = file_frame.get_filename()
        if file_frame.is_folder:
            file_name = file_name + " <folder>"
        if new_value == "on":
            favorite_thread = threading.Thread(
                target=self.client_communicator.handle_set_favorite_request_client,
                args=(file_name, new_value))
            favorite_thread.start()
        else:
            unfavorite_thread = threading.Thread(
                target=self.client_communicator.handle_set_favorite_request_client,
                args=(file_name, new_value))
            unfavorite_thread.start()

    def handle_rename_request_client(self, is_folder=False):
        try:
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
                        target=self.client_communicator.handle_rename_request_client,
                        args=((old_name + " <folder>", new_name_with_format, self.get_current_folder()), "<FOLDER>")
                    )
                else:
                    new_name_with_format = f"{new_name}{file_format}"
                    rename_thread = threading.Thread(
                        target=self.client_communicator.handle_rename_request_client,
                        args=((old_name, new_name_with_format, self.get_current_folder()), "<FILE>")
                    )

                rename_thread.start()

                # Update the UI
                file_frame.set_filename(new_name_with_format if is_folder else new_name)
                file_frame.update_idletasks()
        except IndexError:
            pass

    def handle_rename_folder_request_client(self):
        try:
            # Get the selected folder
            file_frame = self.get_checked_file_frames()[0]
            old_name = file_frame.get_filename()

            # Open a dialog to get the new folder name
            new_name_dialog = CTkInputDialog(text=f"Replace {old_name} with:", title="Rename folder")
            new_name = new_name_dialog.get_input()

            if new_name:
                # Ensure the new name does not conflict with existing names
                new_name_with_format = f"{new_name} <folder>"

                # Send the rename request to the server
                rename_thread = threading.Thread(
                    target=self.client_communicator.handle_rename_folder_request_client,
                    args=((old_name + " <folder>", new_name_with_format, self.get_current_folder()),)
                )
                rename_thread.start()

                # Update the UI
                file_frame.set_filename(new_name)
                file_frame.update_idletasks()
        except IndexError:
            pass

    def handle_delete_request_client(self):
        frames_to_delete = self.get_checked_file_frames()
        names_to_delete_lst = []
        folders_to_delete_lst = []

        for file_frame in frames_to_delete:
            if file_frame.is_folder:
                folders_to_delete_lst.append(file_frame.get_filename() + " <folder>")
            else:
                names_to_delete_lst.append(file_frame.get_filename())

        self.client_communicator.handle_delete_request_client(names_to_delete_lst, folders_to_delete_lst,
                                                              self.current_folder)
        for file_frame in frames_to_delete:
            file_frame.kill_frame()

        self.file_frame_counter = len(self.file_frames)

    def update_current_folder(self, folder_name):
        self.current_folder = folder_name

    def get_current_folder(self):
        return self.current_folder

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
            folder_path = fd.askdirectory(title='Select a folder')
            if folder_path:
                paths = self.get_files_and_subdirectories(folder_path)
                print(paths)
                for path in paths:
                    if os.path.isdir(path):  # If it's a folder
                        folder_name = os.path.basename(path) + " <folder>"
                        folder_date = datetime.datetime.now()
                        folder_size = len(os.listdir(path))
                        formatted_folder_date = self.set_date_format(folder_date)

                        # Add folder to the database
                        send_folder_thread = threading.Thread(
                            target=self.client_communicator.handle_add_new_folder_request,
                            args=(
                                folder_name, folder_size, folder_date, os.path.basename(os.path.dirname(path)))
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
                            target=self.client_communicator.handle_send_file_request,
                            args=(path, short_filename, file_date, file_bytes, file_folder)
                        )
                        send_file_thread.start()

                        favorite = 0

                self.handle_add_new_folder_request(os.path.basename(folder_path) + " <folder>", len(os.listdir(folder_path)))

        except FileNotFoundError:
            return

    def get_all_registered_users(self):
        return self.client_communicator.get_all_registered_users(self.get_current_folder())

    def get_all_groups(self):
        return self.client_communicator.get_all_groups()

    def perform_search(self, search_query):
        search_results = self.client_communicator.handle_search_request(search_query)
        self.display_search_results(search_results)

    def display_search_results(self, search_results):
        for file_frame in self.file_frames:
            file_frame.destroy()

        for result in search_results:
            owner, fname, fsize, fdate, folder, favorite = result
            formatted_file_size = self.set_size_format(fsize)
            formatted_file_date = self.set_date_format(fdate)

            if " <folder>" in fname:
                formatted_file_size = str(fsize) + " items"
                self.add_folder_frame(fname.replace(" <folder>", ""), formatted_file_size, formatted_file_date,
                                      favorite)
            else:
                self.add_file_frame(fname.replace(" <folder>", ""), formatted_file_size, formatted_file_date,
                                    favorite)