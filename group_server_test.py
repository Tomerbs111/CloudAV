import os
import shutil
from datetime import datetime
from exif import Image


def get_creation_date(file_path):
    try:
        with open(file_path, 'rb') as img_file:
            img = Image(img_file)
            if img.has_exif:
                if 'datetime_original' in img.exif_keys:
                    date_str = img['datetime_original']
                    return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"Error reading exif data for {file_path}: {e}")
    return None


def sort_photos_by_date(folder_path):
    photo_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
    photo_dates = {}
    unidentified_photos = []

    for file_name in photo_files:
        file_path = os.path.join(folder_path, file_name)
        creation_date = get_creation_date(file_path)
        if creation_date:
            photo_dates[file_name] = creation_date
        else:
            unidentified_photos.append(file_name)

    sorted_photos = sorted(photo_dates.items(), key=lambda x: x[1])

    # Rename and move identified photos
    for i, (old_name, _) in enumerate(sorted_photos):
        new_name = f"{i}.jpg"  # Rename to numbers with jpg extension
        os.rename(os.path.join(folder_path, old_name), os.path.join(folder_path, new_name))

    # Move unidentified photos to the end
    for file_name in unidentified_photos:
        shutil.move(os.path.join(folder_path, file_name), os.path.join(folder_path, file_name))


if __name__ == "__main__":
    folder_path = input("Enter the folder path containing the photos: ")
    sort_photos_by_date(folder_path)
    print("Photos sorted and renamed successfully.")
