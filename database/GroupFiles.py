import pickle
import sqlite3
from datetime import datetime

from database.FavoritesManager import FavoritesManager


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

    GET_FILE_DATE_QUERY = '''
        SELECT Date FROM GroupFiles WHERE GroupName = ? AND Owner = ? AND Name = ?;    
    '''

    GET_FILE_SIZE_QUERY = '''
        SELECT Size FROM GroupFiles WHERE GroupName = ? AND Owner = ? AND Name = ?;
    '''

    SEARCH_FILES_QUERY = '''
                SELECT Owner, Name, Size, Date, GroupName, Folder FROM GroupFiles
                WHERE Name LIKE ? AND GroupName = ?;
            '''

    def __init__(self, userid: str, database_path='../database/User_info.db'):
        """
        Initialize the GroupFiles object.

        Parameters:
        - userid (str): The user ID.
        - database_path (str, optional): Path to the database file. Default is '../database/User_info.db'.
        """
        self.conn = sqlite3.connect(database_path)
        self.cur = self.conn.cursor()
        self.owner_id = userid
        self.cur.execute(self.CREATE_TABLE_QUERY_FILES)
        self.conn.commit()
        self.favorite_manager = FavoritesManager(userid)

    def _execute_query(self, query, params=None):
        """
        Execute a database query.

        Parameters:
        - query (str): The SQL query.
        - params (tuple, optional): Parameters for the query. Default is None.

        Returns:
        - list: Results of the query.
        """
        try:
            if params:
                return self.cur.execute(query, params).fetchall()
            else:
                return self.cur.execute(query).fetchall()
        except sqlite3.Error as e:
            print("SQLite error:", e)

    def insert_file(self, name: str, size: int, date: datetime, group_name: str, folder: str, filebytes: bytes):
        """
        Insert a file into the database.

        Parameters:
        - name (str): Name of the file.
        - size (int): Size of the file.
        - date (datetime): Date of the file.
        - group_name (str): Name of the group.
        - folder (str): Folder of the file.
        - filebytes (bytes): Bytes of the file.
        """
        try:
            encoded_date = pickle.dumps(date)  # Serialize datetime object to bytes
            self._execute_query(self.INSERT_FILE_QUERY,
                                (self.owner_id, name, size, encoded_date, group_name, folder, filebytes))
            self.conn.commit()
        except Exception as e:
            print("An error occurred while inserting the file:", e)

    def get_all_files_from_group(self, group_name: str, folder_name: str):
        """
        Retrieve all files from a group.

        Parameters:
        - group_name (str): Name of the group.
        - folder_name (str): Name of the folder.

        Returns:
        - list: List of files in the group.
        """
        try:
            all_files = self._execute_query(self.GET_ALL_FILES_FROM_GROUP_QUERY, (group_name, folder_name))
            formatted_files = []
            for file_info in all_files:
                owner, name, size, date_blob, group_name, folder = file_info
                favorite = self.favorite_manager.get_favorite_status(file_info[1], group_name)
                date = pickle.loads(date_blob)  # Deserialize bytes to datetime object
                formatted_files.append((owner, name, size, date, group_name, folder, favorite))
            return formatted_files if formatted_files else "<NO_DATA>"
        except Exception as e:
            print("An error occurred while retrieving files from the group:", e)

    def get_name_file_from_folder_group(self, group_name: str, folder_name: str):
        """
        Retrieve file names from a group folder.

        Parameters:
        - group_name (str): Name of the group.
        - folder_name (str): Name of the folder.

        Returns:
        - list: List of file names.
        """
        try:
            names = self._execute_query(self.GET_NAMES_FROM_GROUP_QUERY, (group_name, folder_name))
            formatted_names = []
            for name in names:
                formatted_names.append(name[0])
            return formatted_names
        except Exception as e:
            print("An error occurred while retrieving file names from the folder:", e)

    def delete_file(self, group_name: str, name: str, folder: str):
        """
        Delete a file from the database.

        Parameters:
        - group_name (str): Name of the group.
        - name (str): Name of the file.
        - folder (str): Folder of the file.
        """
        try:
            self.cur.execute(self.DELETE_FILE_QUERY, (group_name, name, folder))
            self.conn.commit()
        except Exception as e:
            print("An error occurred while deleting the file:", e)
    def get_file_info(self, group_name: str, name: str, folder: str):
        """
        Retrieve information about a file.

        Parameters:
        - group_name (str): Name of the group.
        - name (str): Name of the file.
        - folder (str): Folder of the file.

        Returns:
        - tuple or None: Information about the file if found, None otherwise.
        """
        try:
            result = self._execute_query(self.GET_FILE_INFO_QUERY, (group_name, self.owner_id, name, folder))
            favorite = self.favorite_manager.get_favorite_status(name, group_name)
            if result:
                return result[0]  # Return the first tuple from the result list
            else:
                return None  # or raise an exception or return a default value
        except Exception as e:
            print("An error occurred while retrieving file information:", e)

    def get_file_data(self, group_name: str, name: str, folder: str):
        """
        Retrieve the data of a file.

        Parameters:
        - group_name (str): Name of the group.
        - name (str): Name of the file.
        - folder (str): Folder of the file.

        Returns:
        - bytes: Data of the file.
        """
        try:
            result = self._execute_query(self.GET_FILE_DATA_QUERY, (group_name, self.owner_id, name, folder))
            return result[0]
        except Exception as e:
            print("An error occurred while retrieving file data:", e)

    def rename_folder_files(self, group_name: str, old_folder_name: str, new_folder_name: str):
        """
        Rename all files in a folder.

        Parameters:
        - group_name (str): Name of the group.
        - old_folder_name (str): Old folder name.
        - new_folder_name (str): New folder name.
        """
        try:
            self._execute_query(self.RENAME_FOLDER_FILES_QUERY,
                                (new_folder_name, self.owner_id, group_name, old_folder_name))
            self.conn.commit()
        except Exception as e:
            print("An error occurred while renaming folder files:", e)

    def get_all_data_for_folder(self, group_name: str, folder: str):
        """
        Retrieve all data for items in a folder.

        Parameters:
        - group_name (str): Name of the group.
        - folder (str): Folder name.

        Returns:
        - dict or str: Dictionary containing file names and data if data found, otherwise "<NO_DATA>".
        """
        try:
            all_details = self._execute_query(self.GET_ALL_DATA_DOWNLOAD_QUERY, (group_name, folder))
            formatted_details = {}
            for detail in all_details:
                name, filebytes = detail
                formatted_details[name] = filebytes
            return formatted_details if formatted_details else "<NO_DATA>"
        except Exception as e:
            print("An error occurred while retrieving all data for the folder:", e)

    def get_file_date(self, group_name: str, name: str):
        """
        Retrieve the date of a file.

        Parameters:
        - group_name (str): Name of the group.
        - name (str): Name of the file.

        Returns:
        - datetime: Date of the file.

        Raises:
        - ValueError: If no date found for the given file name.
        """
        try:
            date_tuple = self._execute_query(self.GET_FILE_DATE_QUERY, (group_name, self.owner_id, name))
            if date_tuple:
                actual_date = date_tuple[0][0]  # Extract the first element from the tuple
                return actual_date
            else:
                raise ValueError("No date found for the given file name.")
        except Exception as e:
            print("An error occurred while retrieving the file date:", e)

    def get_file_size(self, group_name: str, name: str):
        """
        Retrieve the size of a file.

        Parameters:
        - group_name (str): Name of the group.
        - name (str): Name of the file.

        Returns:
        - int: Size of the file.
        """
        try:
            size = self._execute_query(self.GET_FILE_SIZE_QUERY, (group_name, self.owner_id, name))
            if size:
                actual_size = size[0][0]  # Extract the first element from the tuple
                return actual_size
        except Exception as e:
            print("An error occurred while retrieving the file size:", e)

    def search_files(self, keyword: str, favorite_manager, room_lst: list):
        """
        Search for files containing a keyword.

        Parameters:
        - keyword (str): Keyword to search for.
        - favorite_manager: Manager for favorite status.
        - room_lst (list): List of rooms to search in.

        Returns:
        - list: List of files matching the search criteria.
        """
        try:
            formatted_results = []
            for room in room_lst:
                search_keyword = f'%{keyword}%'
                results = self._execute_query(self.SEARCH_FILES_QUERY, (search_keyword, room,))
                for result in results:
                    owner, name, size, date_blob, group_name, folder = result
                    favorite = favorite_manager.get_favorite_status(name, group_name)
                    date = pickle.loads(date_blob)  # Deserialize bytes to datetime object
                    formatted_results.append((folder, name, size, date, folder, favorite))
            return formatted_results
        except Exception as e:
            print("An error occurred while searching files:", e)

    def close_connection(self):
        """
        Close the database connection.
        """
        self.conn.close()

if __name__ == '__main__':
    asf = GroupFiles('jasaxaf511@fincainc.com')
    print(asf.get_file_size('daftpunk enjoyer', 'niggers.docx'))
