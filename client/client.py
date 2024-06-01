import socket
import os
import pickle
import struct
import threading
import time

from CommsFunctions import CommsFunctions
from EncryptionFunctions import EncryptionFunctions
from GUI.MyApp import MyApp


class ClientCommunication:
    def __init__(self, client_socket: socket, aes_key):
        self.client_socket = client_socket
        self.aes_key = aes_key
        # add aes key here

    def send_data(self, client_socket: socket, data: str | bytes):
        encrypted_data = EncryptionFunctions.encrypt_AES_message(data, self.aes_key)
        CommsFunctions.send_data(client_socket, encrypted_data)

    def recv_data(self, client_socket: socket):
        encrypted_data = CommsFunctions.recv_data(client_socket)
        decrypted_data = EncryptionFunctions.decrypt_AES_message(encrypted_data, self.aes_key)
        return decrypted_data

    def handle_client_register(self, attempt_type, u_email, u_username, u_password):
        field_dict = {
            'email': u_email,
            'username': u_username,
            'password': u_password,
        }

        data_dict = {"FLAG": attempt_type, "DATA": field_dict}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

        server_answer = pickle.loads(self.recv_data(self.client_socket))
        answer_flag = server_answer.get("FLAG")
        return answer_flag

    def handle_client_login(self, attempt_type, u_email, u_password):
        field_dict = {
            'email': u_email,
            'password': u_password
        }

        data_dict = {"FLAG": attempt_type, "DATA": field_dict}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

        server_answer = pickle.loads(self.recv_data(self.client_socket))
        print(server_answer)
        answer_flag = server_answer.get("FLAG")
        if answer_flag == "<SUCCESS>":
            username = server_answer.get("DATA")
            return username
        else:
            return answer_flag

    def handle_client_2fa(self, u_code):

        data_dict = {"FLAG": '<2FA>', "DATA": u_code}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

        server_answer = pickle.loads(self.recv_data(self.client_socket))
        print(server_answer)
        return server_answer

    def handle_add_new_folder_request(self, real_folder_name, folder_size, folder_date, folder_folder):
        data_dict = {"FLAG": '<CREATE_FOLDER>', "DATA": (real_folder_name, folder_size, folder_date, folder_folder)}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

        print(f"Folder '{real_folder_name}' created successfully")

    def handle_send_file_request(self, file_name, short_filename, short_file_date, file_size, file_folder):
        file_content = b''
        with open(file_name, 'rb') as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                file_content += data

        all_file_content = [short_filename, file_size, short_file_date, file_content, file_folder]
        data_dict = {"FLAG": '<SEND>', "DATA": all_file_content}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

        print(f"File '{file_name}' sent successfully")

    def handle_download_request_client(self, select_file_names_lst, save_path, file_folder):
        try:
            data_dict = {"FLAG": '<RECV>', "DATA": [select_file_names_lst, file_folder]}
            self.send_data(self.client_socket, pickle.dumps(data_dict))

            received_data = pickle.loads(self.recv_data(self.client_socket))
            file_data_name_dict = received_data.get("DATA")

            for indiv_filename, indiv_filebytes in file_data_name_dict.items():
                file_path = os.path.join(save_path, indiv_filename)
                with open(file_path, "wb") as file:
                    file.write(indiv_filebytes)
                    print(f"File '{indiv_filename}' received successfully.")

        except Exception as e:
            print(f"Error in receive_checked_files: {e}")

    def handle_download_folder_request_client(self, folder_name, save_path):
        data_dict = {"FLAG": "<RECV_FOLDER>", "DATA": folder_name}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

        received_data = pickle.loads(self.recv_data(self.client_socket))
        zip_data = received_data.get("DATA")[0]
        print(zip_data)

        zip_file_name = f"{folder_name}.zip"
        zip_file_path = os.path.join(save_path, zip_file_name)
        with open(zip_file_path, 'wb') as zip_file:
            zip_file.write(zip_data)

    def handle_presaved_files_client(self, file_folder):
        operation_dict = {"FLAG": "<NARF>", "DATA": file_folder}
        self.send_data(self.client_socket, pickle.dumps(operation_dict))

        received_data = pickle.loads(self.recv_data(self.client_socket))
        saved_file_prop_lst = received_data.get("DATA")
        print(saved_file_prop_lst)

        return saved_file_prop_lst

    def handle_delete_request_client(self, select_file_names_lst, folders_to_delete, current_folder):
        data_dict = {"FLAG": '<DELETE>', "DATA": [select_file_names_lst, folders_to_delete, current_folder]}
        self.send_data(self.client_socket, pickle.dumps(data_dict))
        print("Files deleted successfully.")

    def handle_rename_request_client(self, rename_data, type_of_rename):
        data_dict = {"FLAG": '<RENAME>', "DATA": rename_data, "TYPE": type_of_rename}
        self.send_data(self.client_socket, pickle.dumps(data_dict))
        print("Files renamed successfully.")

    def handle_set_favorite_request_client(self, file_name, switch_value):
        if switch_value == "on":
            data_dict_on = {"FLAG": '<FAVORITE>', "DATA": [file_name, 'personal']}
            self.send_data(self.client_socket, pickle.dumps(data_dict_on))

            print(f"File '{file_name}' favorited.")

        elif switch_value == "off":
            data_dict_off = {"FLAG": '<UNFAVORITE>', "DATA": [file_name, 'personal']}
            self.send_data(self.client_socket, pickle.dumps(data_dict_off))

            print(f"File '{file_name}' unfavorited.")

    def get_all_registered_users(self):
        data_dict = {"FLAG": "<GET_USERS>"}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

        received_data = pickle.loads(self.recv_data(self.client_socket))
        all_users = received_data.get("DATA")
        return all_users

    def handle_create_group_request(self, group_name, group_participants, permissions):
        group_properties = [group_name, group_participants, permissions]
        data_dict = {"FLAG": '<CREATE_GROUP>', "DATA": group_properties}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

    def get_all_groups(self):
        operation_dict = {"FLAG": "<GET_ROOMS>"}
        self.send_data(self.client_socket, pickle.dumps(operation_dict))

        received_data = pickle.loads(self.recv_data(self.client_socket))
        all_rooms = received_data.get("DATA")
        return all_rooms

    def get_all_favorites(self):
        operation_dict = {"FLAG": "<GET_FAVORITES>"}
        self.send_data(self.client_socket, pickle.dumps(operation_dict))

        received_data = pickle.loads(self.recv_data(self.client_socket))
        all_favorites = received_data.get("DATA")
        return all_favorites

    def log_out(self):
        data_dict = {"FLAG": "<LOGOUT>"}
        self.send_data(self.client_socket, pickle.dumps(data_dict))
        print("Logged out successfully.")


class GroupCommunication:
    def __init__(self, client_socket: socket, handle_broadcast_requests, aes_key):
        """
        Initialize the ClientHandler with the client socket, AES key, and callback function for
        handling broadcast requests.

        Parameters:
            client_socket (socket): The socket object for the client connection.
            handle_broadcast_requests (function): The callback function to handle broadcast requests.
            aes_key (str): The AES key used for encryption.

        Returns:
            None
        """

        self.client_socket = client_socket
        # add aes key here
        self.aes_key = aes_key
        self.handle_broadcast_requests = handle_broadcast_requests  # Define the callback function

        self.receive_thread = None  # Thread for receiving broadcasted files
        self.running = False  # Flag to control the thread
        self.lock = threading.Lock()  # Add a lock for synchronization

    def send_data(self, client_socket: socket, data: str | bytes):
        """
        Send data securely over a client socket using AES encryption.

        Parameters:
            client_socket (socket): The client socket to send data over.
            data (str | bytes): The data to be sent, could be a string or bytes.

        Returns:
            None
        """
        encrypted_data = EncryptionFunctions.encrypt_AES_message(data, self.aes_key)
        CommsFunctions.send_data(client_socket, encrypted_data)

    def recv_data(self, client_socket: socket):
        """
        Receive data from a client socket, decrypt it using AES, and return the decrypted data.

        :param client_socket: A socket object representing the client connection.
        :return: The decrypted data received from the client.
        """
        encrypted_data = CommsFunctions.recv_data(client_socket)
        decrypted_data = EncryptionFunctions.decrypt_AES_message(encrypted_data, self.aes_key)
        return decrypted_data

    def get_all_registered_users(self):
        """
        Get all registered users and send the data through the client socket.
        """
        data_dict = {"FLAG": '<GET_USERS>', "DATA": None}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

    def handle_create_group_request(self, group_name, group_participants):
        """
        Generate a request to create a group with the given name and participants.

        :param group_name: The name of the group to be created.
        :param group_participants: List of participants to be added to the group.
        :return: None
        """
        data_dict = {"FLAG": '<CREATE_GROUP>', "DATA": [group_name, group_participants]}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

    def handle_join_group_request(self, group_name):
        """
        Handles a join group request by sending the group name to the client socket,
        receiving and processing the response, setting the owner email if joined
        successfully, handling pre-saved files for the group, and starting a thread
        to handle broadcasted group data.

        :param group_name: The name of the group to join.
        :return: None
        """
        data_dict = {"FLAG": '<JOIN_GROUP>', "DATA": group_name}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

        received_data = pickle.loads(self.recv_data(self.client_socket))
        print(received_data)
        if received_data.get("FLAG") == '<JOINED>':
            self.owner_email = received_data.get("DATA")
            saved_file_prop_lst = self.handle_presaved_files_group(group_name)
            # Check if the callback is set before calling it
            if self.handle_broadcast_requests:
                self.handle_broadcast_requests(pickle.dumps({"FLAG": "<NARF>", "DATA": saved_file_prop_lst}))

            self.running = True
            self.receive_thread = threading.Thread(target=self.handle_broadcasted_group_data,
                                                   args=(self.handle_broadcast_requests,))
            self.receive_thread.start()

    def handle_leave_group_request(self):
        """
        Send a leave group request to the client and stop the running status.
        """
        self.send_data(self.client_socket, pickle.dumps({"FLAG": '<LEAVE_GROUP>'}))
        self.running = False
        if self.receive_thread:
            self.receive_thread.join()

    def get_all_groups(self):
        """
        Retrieves all groups using the client socket and a specific operation dictionary.
        """
        operation_dict = {"FLAG": "<GET_ROOMS>"}
        self.send_data(self.client_socket, pickle.dumps(operation_dict))

    def handle_broadcasted_group_data(self, on_broadcast_callback):
        """
        Handle broadcasting group data received by the client.

        Parameters:
        - on_broadcast_callback: A callback function to handle the received data.

        Returns:
        None
        """
        try:
            while self.running:
                received_data = pickle.loads(self.recv_data(self.client_socket))
                print(f"Received data from broadcast in client: {received_data}")
                flag = received_data.get("FLAG")
                if flag == "<GET_ROOMS>":
                    print("get users")

                if flag == "<LEFT>":
                    print("left")
                    self.running = False
                    break

                # Check if the callback is set before calling it
                if on_broadcast_callback:
                    on_broadcast_callback(received_data)
        except Exception as e:
            return

    def handle_add_new_folder_request(self, real_folder_name, folder_size, folder_date, folder_folder, group_name):
        """
        This function handles the request to add a new folder. It takes the
        real_folder_name (str), folder_size (int), folder_date (str),
        folder_folder (str), and group_name (str) as parameters. It sends
        the data through the client_socket and prints a success message.
        """
        data_dict = {"FLAG": '<CREATE_FOLDER_GROUP>',
                     "DATA": [real_folder_name, folder_size, folder_date, folder_folder, group_name]}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

        print(f"Folder '{real_folder_name}' created successfully")

    def handle_send_file_request(self, file_name, short_filename, short_file_date, file_size, file_folder, is_broadcast = False):
        """
        Handle sending a file request by reading the file content, creating a data dictionary,
        and sending the data over a client socket using pickle.

        Parameters:
            file_name (str): The full path of the file to be sent.
            short_filename (str): The short name of the file.
            short_file_date (str): The short date of the file.
            file_size (int): The size of the file.
            file_folder (str): The folder where the file is located.

        Returns:
            None
        """
        file_content = b''
        with open(file_name, 'rb') as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                file_content += data

        all_file_content = [short_filename, file_size, short_file_date, file_content, file_folder, is_broadcast]
        data_dict = {"FLAG": '<SEND>', "DATA": all_file_content}

        self.send_data(self.client_socket, pickle.dumps(data_dict))
        print(f"File '{file_name}' sent successfully")


    def handle_download_request_group(self, select_file_names_lst, save_path, file_folder):
        """
        Handle download request group.

        :param select_file_names_lst: List of selected file names.
        :param save_path: Path to save the files.
        :param file_folder: Folder for the files.
        """
        try:
            data_dict = {"FLAG": '<RECV>', "DATA": [select_file_names_lst, file_folder]}
            self.send_data(self.client_socket, pickle.dumps(data_dict))

            if self.running:  # Check if data will end up in broadcast
                return

            received_data = pickle.loads(self.recv_data(self.client_socket))
            file_data_name_dict = received_data.get("DATA")

            for indiv_filename, indiv_filebytes in file_data_name_dict.items():
                file_path = os.path.join(save_path, indiv_filename)
                with open(file_path, "wb") as file:
                    file.write(indiv_filebytes)
                    print(f"File '{indiv_filename}' received successfully.")

        except Exception as e:
            print(f"Error in receive_checked_files: {e}")

    def handle_set_favorite_request_group(self, file_name, switch_value, ftype):
        """
        Handle setting favorite request group by sending data based on switch value.

        Parameters:
            file_name (str): The name of the file.
            switch_value (str): The switch value ('on' or 'off').
            ftype: The type of the file.
        """
        if switch_value == "on":
            data_dict_on = {"FLAG": '<FAVORITE>', "DATA": [file_name, ftype]}
            self.send_data(self.client_socket, pickle.dumps(data_dict_on))

            print(f"File '{file_name}' favorited.")

        elif switch_value == "off":
            data_dict_off = {"FLAG": '<UNFAVORITE>', "DATA": [file_name, ftype]}
            self.send_data(self.client_socket, pickle.dumps(data_dict_off))

            print(f"File '{file_name}' unfavorited.")

    def handle_download_folder_request_group(self, folder_name, save_path):
        """
        A function to handle download folder request group.

        :param folder_name: The name of the folder to download.
        :param save_path: The path to save the downloaded folder.
        """
        data_dict = {"FLAG": "<RECV_FOLDER>", "DATA": folder_name}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

    def handle_presaved_files_group(self, file_folder):
        """
        Handle the processing of a pre-saved files group.

        Args:
            self: The object instance.
            file_folder: The folder containing the files to be processed.

        Returns:
            The list of properties of the saved files after processing.

        Raises:
            Any exception that occurs during the processing.
        """
        try:
            operation_dict = {"FLAG": "<NARF>", "DATA": file_folder}
            self.send_data(self.client_socket, pickle.dumps(operation_dict))

            if self.running:  # Check if data will end up in broadcast
                return

            received_data = pickle.loads(self.recv_data(self.client_socket))
            saved_file_prop_lst = received_data.get("DATA")

            # Release the lock after the operation is completed

            return saved_file_prop_lst

        except Exception as e:
            print(f"Error in handle_presaved_files_group: {e}")

    def handle_delete_request_group(self, select_file_names_lst, folders_to_delete, current_folder):
        """
        Handle delete request group.

        :param select_file_names_lst: list of selected file names
        :param folders_to_delete: folders to be deleted
        :param current_folder: current folder
        """
        data_dict = {"FLAG": '<DELETE>', "DATA": [folders_to_delete, select_file_names_lst, current_folder]}
        self.send_data(self.client_socket, pickle.dumps(data_dict))
        print("Files deleted successfully.")

    def handle_rename_request_group(self, rename_data, type_of_rename):
        """
        Handle a rename request group by sending the rename data and type of rename to the client socket.

        :param rename_data: The data to be renamed.
        :param type_of_rename: The type of renaming operation.
        """
        data_dict = {"FLAG": '<RENAME>', "DATA": rename_data, "TYPE": type_of_rename}
        self.send_data(self.client_socket, pickle.dumps(data_dict))
        print("Files renamed successfully.")

    def log_out(self):
        try:
            self.running = False
            data_dict = {"FLAG": '<LOG_OUT>'}
            self.send_data(self.client_socket, pickle.dumps(data_dict))
            self.receive_thread.join()
            print("Logged out successfully.")
        except Exception as e:
            print(f"Error while logging out: {e}")


# ------------Client setup------------
HOST = '127.0.0.1' #'192.168.1.201'
PORT = 40301


class MainClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))

        # lib.start server coms, save aes key
        self.aes_key = EncryptionFunctions.start_server_communication(self.client_socket)

        self.client_communicator = ClientCommunication(self.client_socket, self.aes_key)  # save aes key as param
        self.group_communicator = GroupCommunication(self.client_socket, None, self.aes_key)

    def run(self):
        try:
            while True:
                app = MyApp(self.client_communicator, self.group_communicator)
                app.mainloop()
                self.client_socket.close()
                break
        except (socket.error, IOError, KeyboardInterrupt) as e:
            print(f"Error: {e}")
        finally:
            self.client_socket.close()


if __name__ == "__main__":
    main_client = MainClient()
    main_client.run()
