from datetime import datetime
import sqlite3


class RoomManager:
    """
    Class for managing rooms in a database.
    """

    CREATE_TABLE_QUERY_ROOMS = '''
    CREATE TABLE IF NOT EXISTS Rooms (
        id INTEGER PRIMARY KEY,
        Admin TEXT NOT NULL,
        Name TEXT NOT NULL,
        Participants TEXT NOT NULL,
        Permissions TEXT NOT NULL
    )'''

    INSERT_ROOM_QUERY = '''
        INSERT INTO Rooms (Admin, Name, Participants, Permissions)
        VALUES (?, ?, ?, ?);
    '''

    REMOVE_ROOM_QUERY = '''
        DELETE FROM Rooms WHERE Name = ?;
    '''

    GET_ROOM_PARTICIPANTS_QUERY = '''
        SELECT Participants FROM Rooms WHERE Name = ?;
    '''

    SET_ROOM_PARTICIPANTS_QUERY = '''
        UPDATE Rooms SET Participants = ? WHERE Name = ?;
    '''

    GET_ROOM_ADMIN_QUERY = '''
        SELECT Admin FROM Rooms WHERE Name = ?;
    '''

    GET_ROOMS_BY_PARTICIPANT_QUERY = '''
        SELECT Name FROM Rooms WHERE Participants LIKE ?;
    '''

    GET_ROOM_PERMISSIONS_QUERY = '''
        SELECT Permissions FROM Rooms WHERE Name = ?;
    '''

    def __init__(self, database_path='../database/User_info.db'):
        """
        Initialize the RoomManager object.

        Parameters:
        - database_path (str, optional): Path to the database file. Default is '../database/User_info.db'.
        """
        self.conn = sqlite3.connect(database_path)
        self.cur = self.conn.cursor()
        self.cur.execute(self.CREATE_TABLE_QUERY_ROOMS)
        self.conn.commit()

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

    def insert_room(self, name: str, participants: str, admin: str, permissions: list):
        """
        Insert a room into the database.

        Parameters:
        - name (str): Name of the room.
        - participants (str): Participants of the room.
        - admin (str): Admin of the room.
        - permissions (list): Permissions of the room.
        """
        try:
            self._execute_query(self.INSERT_ROOM_QUERY, (admin, name, participants, ",".join(permissions)))
            self.conn.commit()
        except Exception as e:
            print("An error occurred while inserting the room:", e)

    def remove_room(self, name: str):
        """
        Remove a room from the database.

        Parameters:
        - name (str): Name of the room.
        """
        try:
            self._execute_query(self.REMOVE_ROOM_QUERY, (name,))
            self.conn.commit()
        except Exception as e:
            print("An error occurred while removing the room:", e)

    def get_room_participants(self, name: str):
        """
        Get participants of a room.

        Parameters:
        - name (str): Name of the room.

        Returns:
        - str: Participants of the room.
        """
        try:
            return self._execute_query(self.GET_ROOM_PARTICIPANTS_QUERY, (name,))
        except Exception as e:
            print("An error occurred while getting room participants:", e)

    def set_room_participants(self, room_name, new_participant):
        """
        Add a participant to a room.

        Parameters:
        - room_name (str): Name of the room.
        - new_participant (str): New participant to add to the room.
        """
        try:
            current_participants = self.get_room_participants(room_name)
            updated_participants = current_participants + [new_participant]
            self._execute_query(self.SET_ROOM_PARTICIPANTS_QUERY, (",".join(updated_participants), room_name))
            self.conn.commit()
            print(f"Participants list updated for room '{room_name}'.")
        except Exception as e:
            print(f"Error in set_room_participants: {e}")

    def get_room_admin(self, room_name):
        """
        Get the admin of a room.

        Parameters:
        - room_name (str): Name of the room.

        Returns:
        - str: Admin of the room.
        """
        try:
            admin = self._execute_query(self.GET_ROOM_ADMIN_QUERY, (room_name,))
            return admin[0][0] if admin else None
        except Exception as e:
            print("An error occurred while getting room admin:", e)

    def get_rooms_by_participant(self, user_email):
        """
        Get rooms by participant.

        Parameters:
        - user_email (str): Email of the participant.

        Returns:
        - list: List of rooms in which the participant is involved.
        """
        try:
            query_param = f'%{user_email}%'
            result = self._execute_query(self.GET_ROOMS_BY_PARTICIPANT_QUERY, (query_param,))
            return [row[0] for row in result]
        except Exception as e:
            print("An error occurred while getting rooms by participant:", e)

    def get_room_permissions(self, room_name):
        """
        Get permissions of a room.

        Parameters:
        - room_name (str): Name of the room.

        Returns:
        - list: Permissions of the room.
        """
        try:
            result = self._execute_query(self.GET_ROOM_PERMISSIONS_QUERY, (room_name,))
            return [row[0] for row in result]
        except Exception as e:
            print("An error occurred while getting room permissions:", e)


if __name__ == '__main__':
    rm = RoomManager()
    print(rm.get_rooms_by_participant('jasaxaf511@fincainc.com'))
