import tkinter as tk
from tkinter import filedialog
import os
import datetime

def get_files_from_folder(folder_path):
    """
    Recursively gets all files from a folder including files from subfolders.

    Args:
    folder_path (str): The path of the folder.

    Returns:
    list: A list of file paths.
    """
    file_paths = []
    for root, directories, files in os.walk(folder_path):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def handle_folder_upload():
    try:
        folder_path = filedialog.askdirectory(title='Select a folder')
        if folder_path:
            file_paths = get_files_from_folder(folder_path)
            print(file_paths)
    except FileNotFoundError:
        return


# Create the main window
root = tk.Tk()
root.title("Open Folder Dialog")

# Create a button to trigger the folder dialog
button = tk.Button(root, text="Open Folder Dialog", command=handle_folder_upload)
button.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()
