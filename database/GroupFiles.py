import pickle
import sqlite3
from datetime import datetime


class GroupFiles:
    CREATE_TABLE_QUERY_FILES = '''
        CREATE TABLE IF NOT EXISTS GroupFiles (
            id INTEGER PRIMARY KEY,
            Owner TEXT NOT NULL,
            Name TEXT NOT NULL,
            Size INTEGER NOT NULL,
            Date BLOB NOT NULL,
            GroupName TEXT NOT NULL,
            Folder TEXT,
            FileBytes BLOB
        );
    '''

    CREATE_TABLE_QUERY_FAVORITES = '''
            CREATE TABLE IF NOT EXISTS Favorites (
                id INTEGER PRIMARY KEY,
                Owner TEXT NOT NULL,
                Name TEXT NOT NULL,
                Type TEXT NOT NULL,
                Favorite INTEGER DEFAULT 0
            );
    '''

    INSERT_FILE_QUERY = '''
        INSERT INTO GroupFiles (Owner, Name, Size, Date, GroupName, Folder, FileBytes)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    '''

    REMOVE_FILE_QUERY = '''
        DELETE FROM GroupFiles WHERE GroupName = ? AND Owner = ? AND Name = ? AND Folder = ?;
    '''

    GET_FILE_DATA_QUERY = '''
        SELECT FileBytes FROM GroupFiles WHERE GroupName = ? AND Owner = ? AND Name = ? AND Folder = ?;
    '''

    GET_FILE_INFO_QUERY = '''
        SELECT Owner, Name, Size, Date, GroupName, Folder FROM GroupFiles WHERE GroupName = ? AND Owner = ? AND Name = ? AND Folder = ?;
    '''

    DELETE_FILE_QUERY = '''
        DELETE FROM GroupFiles WHERE GroupName = ? AND Name = ? AND Folder = ?;
    '''

    RENAME_FILE_QUERY = '''
        UPDATE GroupFiles SET Name = ? WHERE GroupName = ? AND Owner = ? AND Name = ? AND Folder = ?;
    '''

    GET_ALL_FILES_FROM_GROUP_QUERY = '''
        SELECT Owner, Name, Size, Date, GroupName, Folder FROM GroupFiles WHERE GroupName = ? AND Folder = ?;
    '''

    GET_NAMES_FROM_GROUP_QUERY = '''
        SELECT Name FROM GroupFiles WHERE GroupName = ? AND Folder = ?;    
    '''

    RENAME_FOLDER_FILES_QUERY = '''
        UPDATE GroupFiles SET Folder = ? WHERE Owner = ? AND GroupName = ? AND Folder = ?;
    '''

    GET_ALL_DATA_DOWNLOAD_QUERY = '''
        SELECT Name, FileBytes FROM GroupFiles WHERE GroupName = ? AND Folder = ?;
    '''

    INSERT_FAVORITE_QUERY = '''
        INSERT INTO Favorites (Owner, Name, Type, Favorite)
        VALUES (?, ?, ?, ?);
    '''

    REMOVE_FAVORITE_QUERY = '''
        DELETE FROM Favorites WHERE Owner = ? AND Name = ? AND Type = ?;
    '''

    GET_FAVORITE_STATUS_QUERY = '''
        SELECT Favorite FROM Favorites WHERE Owner = ? AND Name = ? AND Type = ?;
    '''

    SET_FAVORITE_STATUS_QUERY = '''
        UPDATE Favorites SET Favorite = ? WHERE Owner = ? AND Name = ? AND Type = ?;
    '''

    def __init__(self, userid: str, database_path='../database/User_info.db'):
        self.conn = sqlite3.connect(database_path)
        self.cur = self.conn.cursor()
        self.owner_id = userid
        self.cur.execute(self.CREATE_TABLE_QUERY_FILES)
        self.conn.commit()

    def _execute_query(self, query, params=None):
        if params:
            return self.cur.execute(query, params).fetchall()
        else:
            return self.cur.execute(query).fetchall()

    def insert_file(self, name: str, size: int, date: datetime, group_name: str, folder: str, filebytes: bytes):
        encoded_date = pickle.dumps(date)  # Serialize datetime object to bytes
        self._execute_query(self.INSERT_FILE_QUERY,
                            (self.owner_id, name, size, encoded_date, group_name, folder, filebytes))
        self.conn.commit()

    def get_all_files_from_group(self, group_name: str, folder_name: str):
        all_files = self._execute_query(self.GET_ALL_FILES_FROM_GROUP_QUERY, (group_name, folder_name))
        formatted_files = []
        for file_info in all_files:
            owner, name, size, date_blob, group_name, folder = file_info
            favorite = self.get_favorite_status(file_info[1], group_name)
            print(favorite)
            date = pickle.loads(date_blob)  # Deserialize bytes to datetime object
            formatted_files.append((owner, name, size, date, group_name, folder, favorite))
        return formatted_files

    def get_name_file_from_folder_group(self, group_name: str, folder_name: str):
        names = self._execute_query(self.GET_NAMES_FROM_GROUP_QUERY, (group_name, folder_name))
        formatted_names = []
        for name in names:
            formatted_names.append(name[0])
        return formatted_names

    def delete_file(self, group_name: str, name: str, folder: str):
        self.cur.execute(self.DELETE_FILE_QUERY, (group_name, name, folder))
        self.conn.commit()

    def rename_file(self, group_name: str, old_name: str, new_name: str, folder: str):
        self._execute_query(self.RENAME_FILE_QUERY, (new_name, group_name, self.owner_id, old_name, folder))
        self.conn.commit()

    def get_file_info(self, group_name: str, name: str, folder: str):
        result = self._execute_query(self.GET_FILE_INFO_QUERY, (group_name, self.owner_id, name, folder))
        if result:
            # Assuming that result is a list containing a single tuple
            return result[0]  # Return the first tuple from the result list
        else:
            # Handle the case where no matching records are found
            return None  # or raise an exception or return a default value

    def get_file_data(self, group_name: str, name: str, folder: str):
        result = self._execute_query(self.GET_FILE_DATA_QUERY, (group_name, self.owner_id, name, folder))
        return result[0]

    def rename_folder_files(self, group_name: str, old_folder_name: str, new_folder_name: str):
        self._execute_query(self.RENAME_FOLDER_FILES_QUERY,
                            (new_folder_name, self.owner_id, group_name, old_folder_name))
        self.conn.commit()

    def get_all_data_for_folder(self, group_name: str, folder: str):
        """
        Retrieve all data for items that have the same folder name as the provided name.
        """
        all_details = self._execute_query(self.GET_ALL_DATA_DOWNLOAD_QUERY, (group_name, folder))
        formatted_details = {}
        for detail in all_details:
            name, filebytes = detail
            formatted_details[name] = filebytes
        return formatted_details if formatted_details else "<NO_DATA>"

    def insert_favorite(self, name: str, file_type: str, favorite: int):
        self._execute_query(self.INSERT_FAVORITE_QUERY, (self.owner_id, name, file_type, favorite))
        self.conn.commit()

    def remove_favorite(self, name: str, file_type: str):
        self._execute_query(self.REMOVE_FAVORITE_QUERY, (self.owner_id, name, file_type))
        self.conn.commit()

    def set_favorite_status(self, name: str, file_type: str, favorite: int):
        try:
            # First, check if the file exists in the group files
            file_info = self.get_favorite_status(name, file_type)  # Assuming empty folder for favorites
            if file_info is None:
                # If the file doesn't exist, create it in the favorites folder
                self.insert_favorite(name, file_type, favorite)  # Insert an empty file
            # Now set the favorite status
            self._execute_query(self.SET_FAVORITE_STATUS_QUERY, (favorite, self.owner_id, name, file_type))
            self.conn.commit()
        except Exception as e:
            print(f"Error in set_favorite_status: {e}")

    def get_favorite_status(self, name: str, file_type: str) -> int:
        status = self._execute_query(self.GET_FAVORITE_STATUS_QUERY, (self.owner_id, name, file_type))
        return status[0][0] if status else None

    def close_connection(self):
        self.conn.close()


if __name__ == '__main__':
    asf = GroupFiles('jasaxaf511@fincainc.com')
    print(asf.get_favorite_status('אזרחות <folder>','daftpunk enjoyer'))
