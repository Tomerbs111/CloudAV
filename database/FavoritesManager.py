import sqlite3
from datetime import datetime


class FavoritesManager:
    CREATE_TABLE_QUERY_FAVORITES = '''
        CREATE TABLE IF NOT EXISTS Favorites (
            id INTEGER PRIMARY KEY,
            Owner TEXT NOT NULL,
            Name TEXT NOT NULL,
            Type TEXT NOT NULL,
            Size INTEGER,
            Date TEXT,
            Favorite INTEGER DEFAULT 0
        );
    '''

    INSERT_FAVORITE_QUERY = '''
        INSERT INTO Favorites (Owner, Name, Type, Size, Date, Favorite)
        VALUES (?, ?, ?, ?, ?, ?);
    '''

    REMOVE_FAVORITE_QUERY = '''
        DELETE FROM Favorites WHERE Owner = ? AND Name = ? AND Type = ?;
    '''

    GET_FAVORITE_STATUS_QUERY = '''
        SELECT Favorite FROM Favorites WHERE Owner = ? AND Name = ? AND Type = ?;
    '''

    SET_FAVORITE_STATUS_QUERY = '''
        UPDATE Favorites SET Size = ?, Date = ?, Favorite = ? WHERE Owner = ? AND Name = ? AND Type = ?;
    '''

    GET_FAVORITES_STATUS_FROM_TYPE_QUERY = '''
        SELECT Owner, Name, Type, Size, Date, Favorite FROM Favorites WHERE Owner = ?;
    '''

    def __init__(self, userid: str, database_path='../database/User_info.db'):
        self.conn = sqlite3.connect(database_path)
        self.cur = self.conn.cursor()
        self.userid = userid
        self.cur.execute(self.CREATE_TABLE_QUERY_FAVORITES)
        self.conn.commit()

    def _execute_query(self, query, params=None):
        if params:
            return self.cur.execute(query, params).fetchall()
        else:
            return self.cur.execute(query).fetchall()

    def insert_favorite(self, name: str, file_type: str, size: int, date: str, favorite: int):
        self._execute_query(self.INSERT_FAVORITE_QUERY, (self.userid, name, file_type, size, date, favorite))
        self.conn.commit()

    def remove_favorite(self, name: str, file_type: str):
        self._execute_query(self.REMOVE_FAVORITE_QUERY, (self.userid, name, file_type))
        self.conn.commit()

    def get_favorite_status(self, name: str, file_type: str):
        status = self._execute_query(self.GET_FAVORITE_STATUS_QUERY, (self.userid, name, file_type))
        return status[0][0] if status else None

    def set_favorite_status(self, name: str, file_type: str, size: int, date: str, favorite: int):
        try:
            # Check if the favorite record exists
            status = self.get_favorite_status(name, file_type)
            if status[2] is None:
                # If it doesn't exist, insert a new favorite record
                self.insert_favorite(name, file_type, size, date, favorite)
            else:
                # Otherwise, update the existing record
                self._execute_query(self.SET_FAVORITE_STATUS_QUERY,
                                    (size, date, favorite, self.userid, name, file_type))
            self.conn.commit()
        except Exception as e:
            print(f"Error in set_favorite_status: {e}")

    def get_all_favorites(self) -> list:
        query_results = self._execute_query(self.GET_FAVORITES_STATUS_FROM_TYPE_QUERY, (self.userid,))
        return query_results

    def close_connection(self):
        self.conn.close()


if __name__ == '__main__':
    test = FavoritesManager('jasaxaf511@fincainc.com')
    print(test.get_favorite_status('Brain fart meme (slowed).mp4', 'daftpunk enjoyer'))
