import sqlite3
import hashlib


class AuthManager:
    def __init__(self, database_path='../database/User_info.db'):
        """
        Initializes the AuthManager with the database connection and creates the required table if it doesn't exist.

        Parameters:
            database_path (str): The path to the SQLite database file.
        """
        try:
            self.conn = sqlite3.connect(database_path)
            self.cur = self.conn.cursor()
            create_table_query_users = '''
            CREATE TABLE IF NOT EXISTS Authenticated (
                id INTEGER PRIMARY KEY,
                email TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            );
            '''
            self.cur.execute(create_table_query_users)
            self.conn.commit()
        except Exception as e:
            print(f"Error initializing AuthManager: {e}")

    def _email_exists(self, email):
        """
        Checks if an email already exists in the database.

        Parameters:
            email (str): The email to check.

        Returns:
            bool: True if the email exists, False otherwise.
        """
        try:
            query = "SELECT * FROM Authenticated WHERE LOWER(email)=?"
            result = self.cur.execute(query, [email.lower()]).fetchone()
            return result is not None
        except Exception as e:
            print(f"Error checking if email exists: {e}")
            return False

    def login(self, email, password):
        """
        Authenticates a user with the provided email and password.

        Parameters:
            email (str): The user's email.
            password (str): The user's password.

        Returns:
            str: Username if login succeeds, otherwise error message.
        """
        try:
            get_from_query = self.cur.execute("SELECT * FROM Authenticated WHERE LOWER(email)=?",
                                              [email.lower()]).fetchone()
            if get_from_query is not None:
                hashed_password = self._hash_input(password)
                if hashed_password == get_from_query[3]:
                    # Login succeed
                    return get_from_query[2]  # returns username
                else:
                    return "<WRONG_PASSWORD>"
            else:
                return "<NO_EMAIL_EXISTS>"
        except Exception as e:
            print(f"Error in login: {e}")
            return "<LOGIN_ERROR>"

    def register(self, email, username, password):
        """
        Registers a new user with the provided email, username, and password.

        Parameters:
            email (str): The user's email.
            username (str): The user's username.
            password (str): The user's password.

        Returns:
            str: Success message if registration succeeds, otherwise error message.
        """
        try:
            email = email.lower()  # Convert email to lowercase
            if self._email_exists(email):
                # Email already exists in the database.
                return "<EXISTS>"

            hashed_password = self._hash_input(password)
            insert_query = '''
            INSERT INTO Authenticated (email, username, password)
            VALUES (?, ?, ?);
            '''

            self.cur.execute(insert_query, (email, username, hashed_password))
            self.conn.commit()

            return "<SUCCESS>"
        except Exception as e:
            print(f"Error in registration: {e}")
            return "<REGISTRATION_ERROR>"

    def get_userid(self, email):
        """
        Retrieves the user ID associated with the given email.

        Parameters:
            email (str): The user's email.

        Returns:
            tuple: The user ID if found, otherwise None.
        """
        try:
            get_from_query = self.cur.execute("SELECT id FROM Authenticated WHERE LOWER(email)=?",
                                              [email.lower()]).fetchone()
            return get_from_query
        except Exception as e:
            print(f"Error getting user ID: {e}")
            return None

    def get_username(self, user_id):
        """
        Retrieves the username associated with the given user ID.

        Parameters:
            user_id (int): The user ID.

        Returns:
            str: The username if found, otherwise None.
        """
        try:
            get_from_query = self.cur.execute("SELECT username FROM Authenticated WHERE id = ?",
                                              [user_id]).fetchone()
            return get_from_query[0] if get_from_query else None
        except Exception as e:
            print(f"Error getting username: {e}")
            return None

    def get_email(self, user_id):
        """
        Retrieves the email associated with the given user ID.

        Parameters:
            user_id (int): The user ID.

        Returns:
            str: The email if found, otherwise None.
        """
        try:
            get_from_query = self.cur.execute("SELECT email FROM Authenticated WHERE id = ?",
                                              [user_id]).fetchone()
            return get_from_query[0] if get_from_query else None
        except Exception as e:
            print(f"Error getting email: {e}")
            return None

    def get_all_users(self, user_id):
        """
        Retrieves emails of all users except the one with the provided user ID.

        Parameters:
            user_id (int): The user ID.

        Returns:
            list: List of user emails.
        """
        try:
            get_from_query = self.cur.execute("SELECT email FROM Authenticated WHERE id != ?", [user_id]).fetchall()
            user_emails = [result[0] for result in get_from_query]  # Assuming each result is a tuple with one element
            return user_emails
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []

    def close_db(self):
        """
        Closes the database connection.
        """
        try:
            self.conn.close()
        except Exception as e:
            print(f"Error closing database connection: {e}")

    @staticmethod
    def _hash_input(password):
        """
                Hashes the input password using SHA-256.

                Parameters:
                    password (str): The password to hash.

                Returns:
                    str: The hashed password.
                """
        try:
            h = hashlib.sha256()
            h.update(password.encode())
            return h.hexdigest()
        except Exception as e:
            print(f"Error hashing password: {e}")
            return None


if __name__ == '__main__':
    auth = AuthManager()
    print(auth.get_all_users(1))
