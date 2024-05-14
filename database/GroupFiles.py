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
        DELETE FROM GroupFiles WHERE GroupName = ? AND Owner = ? AND Name = ? AND Folder = ?;
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
        self._execute_query(self.INSERT_FILE_QUERY, (self.owner_id, name, size, encoded_date, group_name, folder, filebytes))
        self.conn.commit()

    def get_all_files_from_group(self, group_name: str, folder_name: str):
        all_files = self._execute_query(self.GET_ALL_FILES_FROM_GROUP_QUERY, (group_name, folder_name))
        formatted_files = []
        for file_info in all_files:
            owner, name, size, date_blob, group_name, folder = file_info
            date = pickle.loads(date_blob)  # Deserialize bytes to datetime object
            formatted_files.append((owner, name, size, date, group_name, folder))
        return formatted_files

    def get_name_file_from_folder_group(self, group_name: str, folder_name: str):
        names = self._execute_query(self.GET_NAMES_FROM_GROUP_QUERY, (group_name, folder_name))
        formatted_names = []
        for name in names:
            formatted_names.append(name[0])
        return formatted_names

    def delete_file(self, group_name: str, name: str, folder: str):
        self._execute_query(self.REMOVE_FILE_QUERY, (group_name, self.owner_id, name, folder))
        self.conn.commit()

    def rename_file(self, group_name: str, old_name: str, new_name: str, folder: str):
        self._execute_query(self.RENAME_FILE_QUERY, (new_name, group_name, self.owner_id, old_name, folder))
        self.conn.commit()

    def get_file_info(self, group_name: str, name: str, folder: str):
        return self._execute_query(self.GET_FILE_INFO_QUERY, (group_name, self.owner_id, name, folder))

    def get_file_data(self, group_name: str, name: str, folder: str):
        result = self._execute_query(self.GET_FILE_DATA_QUERY, (group_name, self.owner_id, name, folder))
        if result:
            # Assuming that result is a list containing a single tuple
            return result[0]
        else:
            # Handle the case where no matching records are found
            return None  # or raise an exception or return a default value

    def rename_folder_files(self, group_name: str, old_folder_name: str, new_folder_name: str):
        self._execute_query(self.RENAME_FOLDER_FILES_QUERY,
                            (new_folder_name, self.owner_id, group_name, old_folder_name))
        self.conn.commit()
    def close_connection(self):
        self.conn.close()


if __name__ == '__main__':
    asf = GroupFiles('tomerbs1810@gmail.com')
    print(asf.get_name_file_from_folder_group('group1', 'Room'))