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
        self.conn = sqlite3.connect(database_path)
        self.cur = self.conn.cursor()
        self.userid_db = userid
        self.cur.execute(self.CREATE_TABLE_QUERY_FILES)
        self.conn.commit()

    def _execute_query(self, query, params=None):
        if params:
            return self.cur.execute(query, params).fetchall()
        else:
            return self.cur.execute(query).fetchall()

    def insert_file(self, name: str, size: int, date: datetime, filebytes: bytes, folder: str):
        encoded_date = pickle.dumps(date)  # Serialize datetime object to bytes
        self._execute_query(self.INSERT_FILE_QUERY, (self.userid_db, name, size, encoded_date, filebytes, folder))
        self.conn.commit()

    def get_all_data(self, folder: str):
        all_details = self._execute_query(self.GET_ALL_DATA_QUERY, (self.userid_db, folder))
        formatted_details = []
        for detail in all_details:
            name, size, date_blob, favorite, folder = detail
            date = pickle.loads(date_blob)  # Deserialize bytes to datetime object
            formatted_details.append((name, size, date, favorite, folder))
        return formatted_details if formatted_details else "<NO_DATA>"

    def delete_file(self, name: str, folder: str):
        self._execute_query(self.REMOVE_FILE_QUERY, (self.userid_db, name, folder))
        self.conn.commit()

    def delete_folder(self, folder: str):
        self._execute_query(self.REMOVE_FOLDER_QUERY, (self.userid_db, folder))
        self.conn.commit()

    def rename_file(self, old_name: str, new_name: str, folder: str):
        self._execute_query(self.RENAME_FILE_QUERY, (new_name, self.userid_db, old_name, folder))
        self.conn.commit()

    def rename_folder_files(self, old_folder_name: str, new_folder_name: str):
        self._execute_query(self.RENAME_FOLDER_FILES_QUERY, (new_folder_name, self.userid_db, old_folder_name))
        self.conn.commit()

    def get_file_data(self, file_name: str, folder: str) -> bytes:
        data = self._execute_query(self.GET_FILE_DATA_QUERY, (self.userid_db, file_name, folder))
        return data[0] if data else None

    def get_file_size(self, file_name: str) -> int:
        size = self._execute_query(self.GET_FILE_SIZE_QUERY, (self.userid_db, file_name))
        if size:
            actual_size = size[0][0]  # Extract the first element from the tuple
        return actual_size

    def get_file_date(self, file_name: str) -> datetime:
        date_tuple = self._execute_query(self.GET_FILE_DATE_QUERY, (self.userid_db, file_name))
        if date_tuple:
            actual_date = date_tuple[0][0]  # Extract the first element from the tuple
            return actual_date
        else:
            return datetime.now()

    def get_favorite_status(self, file_name: str) -> int:
        status = self._execute_query(self.GET_FAVORITE_STATUS_QUERY, (self.userid_db, file_name))
        return status[0] if status else None

    def set_favorite_status(self, file_name: str, favorite: int):
        self._execute_query(self.SET_FAVORITE_STATUS_QUERY, (favorite, self.userid_db, file_name))
        self.conn.commit()

    def get_folder(self, file_name: str) -> str:
        folder = self._execute_query(self.GET_FOLDER_QUERY, (self.userid_db, file_name))
        return folder[0] if folder else None

    def get_folder_data(self, folder: str):
        data = self._execute_query(self.GET_FOLDER_DATA_QUERY, (self.userid_db, folder))
        return [name[0] for name in data]

    def set_folder(self, file_name: str, folder: str):
        self._execute_query(self.SET_FOLDER_QUERY, (folder, self.userid_db, file_name))
        self.conn.commit()

    def get_all_data_for_folder(self, folder: str):
        """
        Retrieve all data for items that have the same folder name as the provided name.
        """
        all_details = self._execute_query(self.GET_ALL_DATA_DOWNLOAD_QUERY, (self.userid_db, folder))
        formatted_details = {}
        for detail in all_details:
            name, filebytes = detail
            formatted_details[name] = filebytes
        return formatted_details if formatted_details else "<NO_DATA>"

    def search_files(self, keyword: str):
        search_keyword = f'%{keyword}%'

        results = self._execute_query(self.SEARCH_FILES_QUERY, (search_keyword, self.userid_db))
        formatted_results = []
        for result in results:
            name, size, date_blob, folder, favorite = result
            date = pickle.loads(date_blob)  # Deserialize bytes to datetime object
            # Change the order of fields in the tuple
            formatted_results.append(('personal', name, size, date, folder, favorite))

        return formatted_results

    def close_connection(self):
        self.conn.close()


if __name__ == '__main__':
    db_manager = UserFiles('1')
    print(db_manager.get_file_date('Untitled.png'))
