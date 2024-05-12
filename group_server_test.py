import tkinter as tk
from PIL import Image, ImageTk
from customtkinter import *


def create_new_folder():
    add_folder_dialog = CTkToplevel(root)
    add_folder_dialog.geometry("300x160")
    add_folder_dialog.resizable(False, False)
    add_folder_dialog.title("Add Folder")

    title = CTkLabel(add_folder_dialog, text="Add Folder", compound="left", font=("Arial", 25))
    title.pack(pady=10, padx=10, side="top", anchor="w")

    folder_name_entry = CTkEntry(add_folder_dialog, width=280, height=40, placeholder_text="Folder Name")
    folder_name_entry.pack(pady=10, padx=10, side="top", anchor="w")

    ok_button = CTkButton(add_folder_dialog, text="Add", command=add_folder_dialog.destroy)
    ok_button.pack(pady=10, padx=10, side="left", anchor="w")

    cancel_button = CTkButton(add_folder_dialog, text="Cancel", command=add_folder_dialog.destroy)
    cancel_button.pack(pady=10, padx=10, side="left", anchor="w")


def add_file():
    print("Add File")


def add_folder():
    print("Add Folder")


def show_menu(event):
    menu.post(event.x_root, event.y_root)


root = tk.Tk()

# Create a menu
menu = tk.Menu(root, tearoff=0)

# Load and resize icons
new_folder_icon = Image.open(
    r"C:\Users\shoon\OneDrive - פורטל החינוך פתח תקווה\שולחן העבודה\Cyber-CloudAV\GUI\file_icons\add-folder.png")
new_folder_icon = new_folder_icon.resize((16, 16))
new_folder_icon = ImageTk.PhotoImage(new_folder_icon)

upload_folder_icon = Image.open(
    r"C:\Users\shoon\OneDrive - פורטל החינוך פתח תקווה\שולחן העבודה\Cyber-CloudAV\GUI\file_icons\folder-upload.png")
upload_folder_icon = upload_folder_icon.resize((16, 16))
upload_folder_icon = ImageTk.PhotoImage(upload_folder_icon)

file_icon = Image.open(
    r"C:\Users\shoon\OneDrive - פורטל החינוך פתח תקווה\שולחן העבודה\Cyber-CloudAV\GUI\file_icons\file-upload.png")
file_icon = file_icon.resize((16, 16))
file_icon = ImageTk.PhotoImage(file_icon)

# Add options with resized icons to the menu
menu.add_command(label=" New Folder", image=new_folder_icon, compound=tk.LEFT, command=create_new_folder,
                 font=("Helvetica", 12))
menu.add_separator()
menu.add_command(label="  Upload File", image=file_icon, compound=tk.LEFT, command=add_file, font=("Helvetica", 12))
menu.add_command(label="  Upload Folder", image=upload_folder_icon, compound=tk.LEFT, command=add_folder,
                 font=("Helvetica", 12))

# Create a frame to attach the menu
frame = tk.Frame(root, width=200, height=200)
frame.pack()

# Attach the menu to the frame
frame.bind("<Button-3>", show_menu)  # Right-click to show the menu

root.mainloop()
