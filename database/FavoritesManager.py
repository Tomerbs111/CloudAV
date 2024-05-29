import sqlite3


class FavoritesManager:
    CREATE_TABLE_QUERY_FAVORITES = '''
        CREATE TABLE IF NOT EXISTS Favorites (
            id INTEGER PRIMARY KEY,
            Owner TEXT NOT NULL,
            Name TEXT NOT NULL,
            Type TEXT NOT NULL,
            Favorite INTEGER DEFAULT 0
        );
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

    GET_FAVORITES_STATUS_FROM_TYPE_QUERY = '''
        SELECT Owner, Name, Type, Favorite FROM Favorites WHERE Owner = ? AND Favorite = 1;
    '''

    SEARCH_FAVORITES_QUERY = '''
            SELECT Owner, Name, Type, Favorite FROM Favorites WHERE Owner = ? AND Name LIKE ? AND Favorite = 1;
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

    def insert_favorite(self, name: str, file_type: str, favorite: int):
        self._execute_query(self.INSERT_FAVORITE_QUERY, (self.userid, name, file_type, favorite))
        self.conn.commit()

    def remove_favorite(self, name: str, file_type: str):
        self._execute_query(self.REMOVE_FAVORITE_QUERY, (self.userid, name, file_type))
        self.conn.commit()

    def get_favorite_status(self, name: str, file_type: str):
        status = self._execute_query(self.GET_FAVORITE_STATUS_QUERY, (self.userid, name, file_type))
        return status[0][0] if status else None

    def set_favorite_status(self, name: str, file_type: str, favorite: int):
        try:
            self._execute_query(self.SET_FAVORITE_STATUS_QUERY, (favorite, self.userid, name, file_type))
            self.conn.commit()
        except Exception as e:
            print(f"Error in set_favorite_status: {e}")

    def get_all_favorites(self) -> list:
        query_results = self._execute_query(self.GET_FAVORITES_STATUS_FROM_TYPE_QUERY, (self.userid,))
        return query_results

    def search_favorites(self, keyword: str) -> list:
        search_keyword = f'%{keyword}%'
        results = self._execute_query(self.SEARCH_FAVORITES_QUERY, (self.userid, search_keyword))
        return results

    def close_connection(self):
        self.conn.close()


if __name__ == '__main__':
    test = FavoritesManager('jasaxaf511@fincainc.com')
    print(test.search_favorites("b"))
