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
            SELECT Name, Type, Favorite FROM Favorites WHERE Owner = ? AND Name LIKE ? AND Favorite = 1;
        '''

    def __init__(self, userid: str, database_path='../database/User_info.db'):
        """
        Initializes the FavoritesManager with the user ID and database connection.

        Parameters:
            userid (str): The user ID associated with the favorites.
            database_path (str): The path to the SQLite database file.
        """
        try:
            self.conn = sqlite3.connect(database_path)
            self.cur = self.conn.cursor()
            self.userid = userid
            self.cur.execute(self.CREATE_TABLE_QUERY_FAVORITES)
            self.conn.commit()
        except Exception as e:
            print(f"Error initializing FavoritesManager: {e}")

    def _execute_query(self, query, params=None):
        """
        Executes a SQLite query and fetches the results.

        Parameters:
            query (str): The SQL query to execute.
            params (tuple): Optional parameters for the query.

        Returns:
            list: The query results.
        """
        try:
            if params:
                return self.cur.execute(query, params).fetchall()
            else:
                return self.cur.execute(query).fetchall()
        except Exception as e:
            print(f"Error executing query: {e}")
            return []

    def insert_favorite(self, name: str, file_type: str, favorite: int):
        """
        Inserts a favorite into the database.

        Parameters:
            name (str): The name of the file.
            file_type (str): The type of the file.
            favorite (int): The favorite status (1 for favorite, 0 for not favorite).
        """
        try:
            self._execute_query(self.INSERT_FAVORITE_QUERY, (self.userid, name, file_type, favorite))
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting favorite: {e}")

    def remove_favorite(self, name: str, file_type: str):
        """
        Removes a favorite from the database.

        Parameters:
            name (str): The name of the file.
            file_type (str): The type of the file.
        """
        try:
            self._execute_query(self.REMOVE_FAVORITE_QUERY, (self.userid, name, file_type))
            self.conn.commit()
        except Exception as e:
            print(f"Error removing favorite: {e}")

    def get_favorite_status(self, name: str, file_type: str):
        """
        Retrieves the favorite status of a file.

        Parameters:
            name (str): The name of the file.
            file_type (str): The type of the file.

        Returns:
            int: The favorite status (1 for favorite, 0 for not favorite).
        """
        try:
            status = self._execute_query(self.GET_FAVORITE_STATUS_QUERY, (self.userid, name, file_type))
            return status[0][0] if status else None
        except Exception as e:
            print(f"Error getting favorite status: {e}")
            return None

    def set_favorite_status(self, name: str, file_type: str, favorite: int):
        """
        Sets the favorite status of a file.

        Parameters:
            name (str): The name of the file.
            file_type (str): The type of the file.
            favorite (int): The favorite status (1 for favorite, 0 for not favorite).
        """
        try:
            self._execute_query(self.SET_FAVORITE_STATUS_QUERY, (favorite, self.userid, name, file_type))
            self.conn.commit()
        except Exception as e:
            print(f"Error setting favorite status: {e}")

    def get_all_favorites(self) -> list:
        """
        Retrieves all favorites for the user.

        Returns:
            list: A list of tuples containing favorite information.
        """
        try:
            query_results = self._execute_query(self.GET_FAVORITES_STATUS_FROM_TYPE_QUERY, (self.userid,))
            return query_results
        except Exception as e:
            print(f"Error getting all favorites: {e}")
            return []

    def search_favorites(self, keyword: str) -> list:
        """
        Searches for favorites based on a keyword.

        Parameters:
            keyword (str): The keyword to search for in file names.

        Returns:
            list: A list of tuples containing matching favorite information.
        """
        try:
            search_keyword = f'%{keyword}%'
            results = self._execute_query(self.SEARCH_FAVORITES_QUERY, (self.userid, search_keyword))
            return results
        except Exception as e:
            print(f"Error searching favorites: {e}")
            return []

    def close_connection(self):
        """
        Closes the database connection.
        """
        try:
            self.conn.close()
        except Exception as e:
            print(f"Error closing database connection: {e}")


if __name__ == '__main__':
    test = FavoritesManager('jasaxaf511@fincainc.com')
    print(test.search_favorites("b"))
