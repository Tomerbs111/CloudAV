import pickle
from datetime import datetime
import sqlite3


class UserFiles:
    CREATE_TABLE_QUERY_FILES = '''
        CREATE TABLE IF NOT EXISTS Files (
            id INTEGER PRIMARY KEY,
            Owner TEXT NOT NULL,
            Name TEXT NOT NULL,
            Size INTEGER NOT NULL,
            Date BLOB NOT NULL,
            Favorite INTEGER DEFAULT 0,
            FileBytes BLOB,
            Folder TEXT
        );
    '''

    INSERT_FILE_QUERY = '''
        INSERT INTO Files (Owner, Name, Size, Date, FileBytes, Folder)
        VALUES (?, ?, ?, ?, ?, ?);
    '''

    REMOVE_FILE_QUERY = '''
        DELETE FROM Files WHERE Owner = ? AND Name = ? AND Folder = ?;
    '''

    REMOVE_FOLDER_QUERY = '''
        DELETE FROM Files WHERE Owner = ? AND Folder = ?;
    '''

    GET_FOLDER_DATA_QUERY = '''
        SELECT Name FROM Files WHERE Owner = ? AND Folder = ?;
    '''

    GET_FILE_DATA_QUERY = '''
        SELECT FileBytes FROM Files WHERE Owner = ? AND Name = ? AND Folder = ?;
    '''

    GET_FILE_SIZE_QUERY = '''
        SELECT Size FROM Files WHERE Owner = ? AND Name = ?;
    '''

    GET_ALL_DATA_QUERY = '''
        SELECT Name, Size, Date, Favorite, Folder FROM Files WHERE Owner = ? AND Folder = ?;
    '''

    GET_ALL_DATA_DOWNLOAD_QUERY = '''
        SELECT Name, FileBytes FROM Files WHERE Owner = ? AND Folder = ?;
    '''

    RENAME_FILE_QUERY = '''
        UPDATE Files SET Name = ? WHERE Owner = ? AND Name = ? AND Folder = ?;
    '''

    GET_FAVORITE_STATUS_QUERY = '''
        SELECT Favorite FROM Files WHERE Owner = ? AND Name = ?;
    '''

    SET_FAVORITE_STATUS_QUERY = '''
        UPDATE Files SET Favorite = ? WHERE Owner = ? AND Name = ?;
    '''

    GET_FOLDER_QUERY = '''
        SELECT Folder FROM Files WHERE Owner = ? AND Name = ?;
    '''

    SET_FOLDER_QUERY = '''
        UPDATE Files SET Folder = ? WHERE Owner = ? AND Name = ?;
    '''

    RENAME_FOLDER_FILES_QUERY = '''
        UPDATE Files SET Folder = ? WHERE Owner = ? AND Folder = ?;
    '''

    GET_FILE_DATE_QUERY = '''
        SELECT Date FROM Files WHERE Owner = ? AND Name = ?;
    '''

    SEARCH_FILES_QUERY = '''
               SELECT Name, Size, Date, Folder, Favorite FROM Files
               WHERE Name LIKE ? AND Owner = ?;
           '''

    def __init__(self, userid: str, database_path='../database/User_info.db'):
        """
        Initialize the UserFiles object.

        Parameters:
        - userid (str): The user ID.
        - database_path (str, optional): Path to the database file. Default is '../database/User_info.db'.
        """
        try:
            self.conn = sqlite3.connect(database_path)
            self.cur = self.conn.cursor()
            self.userid_db = userid
            self.cur.execute(self.CREATE_TABLE_QUERY_FILES)
            self.conn.commit()
        except sqlite3.Error as e:
            print("SQLite error:", e)

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

    def insert_file(self, name: str, size: int, date: datetime, filebytes: bytes, folder: str):
        """
        Insert a file into the database.

        Parameters:
        - name (str): Name of the file.
        - size (int): Size of the file.
        - date (datetime): Date of the file.
        - filebytes (bytes): File content.
        - folder (str): Folder name.
        """
        try:
            encoded_date = pickle.dumps(date)  # Serialize datetime object to bytes
            self._execute_query(self.INSERT_FILE_QUERY, (self.userid_db, name, size, encoded_date, filebytes, folder))
            self.conn.commit()
        except Exception as e:
            print("An error occurred while inserting the file:", e)

    def get_all_data(self, folder: str):
        """
        Retrieve all data for files in a specific folder.

        Parameters:
        - folder (str): Folder name.

        Returns:
        - list: List of tuples containing file details.
        """
        try:
            all_details = self._execute_query(self.GET_ALL_DATA_QUERY, (self.userid_db, folder))
            formatted_details = []
            for detail in all_details:
                name, size, date_blob, favorite, folder = detail
                date = pickle.loads(date_blob)  # Deserialize bytes to datetime object
                formatted_details.append((name, size, date, favorite, folder))
            return formatted_details if formatted_details else "<NO_DATA>"
        except Exception as e:
            print("An error occurred while retrieving data:", e)
            return []

    def delete_file(self, name: str, folder: str):
        """
        Delete a file from the database.

        Parameters:
        - name (str): Name of the file.
        - folder (str): Folder name.
        """
        try:
            self._execute_query(self.REMOVE_FILE_QUERY, (self.userid_db, name, folder))
            self.conn.commit()
        except Exception as e:
            print("An error occurred while deleting the file:", e)

    def delete_folder(self, folder: str):
        """
        Delete all files in a folder from the database.

        Parameters:
        - folder (str): Folder name.
        """
        try:
            self._execute_query(self.REMOVE_FOLDER_QUERY, (self.userid_db, folder))
            self.conn.commit()
        except Exception as e:
            print("An error occurred while deleting the folder:", e)

    def rename_file(self, old_name: str, new_name: str, folder: str):
        """
        Rename a file in the database.

        Parameters:
        - old_name (str): Old name of the file.
        - new_name (str): New name of the file.
        - folder (str): Folder name.
        """
        try:
            self._execute_query(self.RENAME_FILE_QUERY, (new_name, self.userid_db, old_name, folder))
            self.conn.commit()
        except Exception as e:
            print("An error occurred while renaming the file:", e)

    def rename_folder_files(self, old_folder_name: str, new_folder_name: str):
        """
        Rename all files in a folder in the database.

        Parameters:
        - old_folder_name (str): Old folder name.
        - new_folder_name (str): New folder name.
        """
        try:
            self._execute_query(self.RENAME_FOLDER_FILES_QUERY, (new_folder_name, self.userid_db, old_folder_name))
            self.conn.commit()
        except Exception as e:
            print("An error occurred while renaming the folder files:", e)

    def get_file_data(self, file_name: str, folder: str) -> bytes:
        """
        Retrieve the data of a file.

        Parameters:
        - file_name (str): Name of the file.
        - folder (str): Folder name.

        Returns:
        - bytes: File content.
        """
        try:
            data = self._execute_query(self.GET_FILE_DATA_QUERY, (self.userid_db, file_name, folder))
            return data[0] if data else None
        except Exception as e:
            print("An error occurred while retrieving file data:", e)
            return None

    def get_file_size(self, file_name: str) -> int:
        """
        Retrieve the size of a file.

        Parameters:
        - file_name (str): Name of the file.

        Returns:
        - int: Size of the file.
        """
        try:
            size = self._execute_query(self.GET_FILE_SIZE_QUERY, (self.userid_db, file_name))
            if size:
                actual_size = size[0][0]  # Extract the first element from the tuple
            return actual_size
        except Exception as e:
            print("An error occurred while retrieving file size:", e)
            return 0

    def get_file_date(self, file_name: str) -> datetime:
        """
        Retrieve the date of a file.

        Parameters:
        - file_name (str): Name of the file.

        Returns:
        - datetime: Date of the file.
        """
        try:
            date_tuple = self._execute_query(self.GET_FILE_DATE_QUERY, (self.userid_db, file_name))
            if date_tuple:
                actual_date = date_tuple[0][0]  # Extract the first element from the tuple
                return actual_date
            else:
                return datetime.now()
        except Exception as e:
            print("An error occurred while retrieving file date:", e)
            return datetime.now()

    def get_favorite_status(self, file_name: str) -> int:
        """
        Retrieve the favorite status of a file.

        Parameters:
        - file_name (str): Name of the file.

        Returns:
        - int: Favorite status (0 for not favorite, 1 for favorite).
        """
        try:
            status = self._execute_query(self.GET_FAVORITE_STATUS_QUERY, (self.userid_db, file_name))
            return status[0] if status else None
        except Exception as e:
            print("An error occurred while retrieving favorite status:", e)
            return None

    def set_favorite_status(self, file_name: str, favorite: int):
        """
        Set the favorite status of a file.

        Parameters:
        - file_name (str): Name of the file.
        - favorite (int): Favorite status (0 for not favorite, 1 for favorite).
        """
        try:
            self._execute_query(self.SET_FAVORITE_STATUS_QUERY, (favorite, self.userid_db, file_name))
            self.conn.commit()
        except Exception as e:
            print("An error occurred while setting favorite status:", e)

    def get_folder(self, file_name: str) -> str:
        """
        Retrieve the folder of a file.

        Parameters:
        - file_name (str): Name of the file.

        Returns:
        - str: Folder name.
        """
        try:
            folder = self._execute_query(self.GET_FOLDER_QUERY, (self.userid_db, file_name))
            return folder[0] if folder else None
        except Exception as e:
            print("An error occurred while retrieving folder:", e)
            return None

    def get_folder_data(self, folder: str):
        """
        Retrieve the names of files in a folder.

        Parameters:
        - folder (str): Folder name.

        Returns:
        - list: List of file names in the folder.
        """
        try:
            data = self._execute_query(self.GET_FOLDER_DATA_QUERY, (self.userid_db, folder))
            return [name[0] for name in data]
        except Exception as e:
            print("An error occurred while retrieving folder data:", e)
            return []

    def set_folder(self, file_name: str, folder: str):
        """
        Set the folder of a file.

        Parameters:
        - file_name (str): Name of the file.
        - folder (str): Folder name.
        """
        try:
            self._execute_query(self.SET_FOLDER_QUERY, (folder, self.userid_db, file_name))
            self.conn.commit()
        except Exception as e:
            print("An error occurred while setting folder:", e)

    def get_all_data_for_folder(self, folder: str):
        """
        Retrieve all data for items in a folder.

        Parameters:
        - folder (str): Folder name.

        Returns:
        - dict: Dictionary containing file names and their content.
        """
        try:
            all_details = self._execute_query(self.GET_ALL_DATA_DOWNLOAD_QUERY, (self.userid_db, folder))
            formatted_details = {}
            for detail in all_details:
                name, filebytes = detail
                formatted_details[name] = filebytes
            return formatted_details if formatted_details else "<NO_DATA>"
        except Exception as e:
            print("An error occurred while retrieving data for folder:", e)
            return {}

    def search_files(self, keyword: str):
        """
        Search files by keyword.

        Parameters:
        - keyword (str): Keyword to search.

        Returns:
        - list: List of tuples containing file details.
        """
        try:
            search_keyword = f'%{keyword}%'

            results = self._execute_query(self.SEARCH_FILES_QUERY, (search_keyword, self.userid_db))
            formatted_results = []
            for result in results:
                name, size, date_blob, folder, favorite = result
                date = pickle.loads(date_blob)  # Deserialize bytes to datetime object
                # Change the order of fields in the tuple
                formatted_results.append(('personal', name, size, date, folder, favorite))

            return formatted_results
        except Exception as e:
            print("An error occurred while searching files:", e)
            return []

    def close_connection(self):
        """
        Close the database connection.
        """
        try:
            self.conn.close()
        except Exception as e:
            print("An error occurred while closing the connection:", e)


if __name__ == '__main__':
    db_manager = UserFiles('1')
    print(db_manager.get_file_date('Untitled.png'))
