from database.UserFiles import UserFiles
import os
import shutil


def create_folder_with_files(folder_name: str, base_path: str, db_manager):
    """
    Create a folder with the given name and initialize it with all associated files.
    Then compress the folder into a zip file and delete the original folder.

    :param folder_name: The name of the folder to create
    :param base_path: The base path where the folder should be created
    """
    # Ensure the base path exists
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    # Path to the new folder
    folder_path = os.path.join(base_path, folder_name)

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Get all data for the given folder from the database
    all_files = db_manager.get_all_data_for_folder(folder_name)

    if all_files == "<NO_DATA>":
        print(f"No files found for folder '{folder_name}'")
        return

    # Iterate through the files and save them to the new folder
    def recursive_save(data, current_path):
        for name, f_bytes in data.items():
            if " <folder>" in name:
                # Remove the "<folder>" suffix
                name = name.replace(" <folder>", "")
                new_path = os.path.join(current_path, name)
                os.makedirs(new_path, exist_ok=True)
                all_files_r = db_manager.get_all_data_for_folder(name)
                recursive_save(all_files_r, new_path)
            else:
                # Write the file f_bytes
                file_path = os.path.join(current_path, name)
                with open(file_path, 'wb') as file:
                    file.write(f_bytes)

    # Start recursive save
    recursive_save(all_files, folder_path)

    print(f"Folder '{folder_name}' created with {len(all_files)} files.")

    # Compress the folder into a zip file
    zip_file_path = os.path.join(base_path, f"{folder_name}.zip")
    shutil.make_archive(folder_path, 'zip', base_path, folder_name)

    # Remove the original folder
    shutil.rmtree(folder_path)

    print(f"Folder '{folder_name}' compressed into '{zip_file_path}' and original folder deleted.")


# Example usage
if __name__ == '__main__':
    db_manager = UserFiles('1')
    create_folder_with_files("Room", "temp_zips", db_manager)
