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

    def handle_search_request(self, search_query):
        data_dict = {"FLAG": "<SEARCH>", "DATA": search_query}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

        received_data = pickle.loads(self.recv_data(self.client_socket))
        search_results = received_data.get("DATA")
        return search_results



class GroupCommunication:
    def __init__(self, client_socket, handle_broadcast_requests, aes_key):
        self.client_socket = client_socket
        self.current_folder = None
        self.aes_key = aes_key
        self.handle_broadcast_requests = handle_broadcast_requests  # Define the callback function

        self.receive_thread = None  # Thread for receiving broadcasted files
        self.running = False  # Flag to control the thread
        self.lock = threading.Lock()  # Add a lock for synchronization

    def send_data(self, client_socket: socket, data: str | bytes):
        encrypted_data = EncryptionFunctions.encrypt_AES_message(data, self.aes_key)
        CommsFunctions.send_data(client_socket, encrypted_data)

    def recv_data(self, client_socket: socket):
        encrypted_data = CommsFunctions.recv_data(client_socket)
        decrypted_data = EncryptionFunctions.decrypt_AES_message(encrypted_data, self.aes_key)
        return decrypted_data

    def get_all_registered_users(self):
        data_dict = {"FLAG": '<GET_USERS>', "DATA": None}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

    def handle_create_group_request(self, group_name, group_participants):
        data_dict = {"FLAG": '<CREATE_GROUP>', "DATA": [group_name, group_participants]}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

    def handle_join_group_request(self, group_name):
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
        self.send_data(self.client_socket, pickle.dumps({"FLAG": '<LEAVE_GROUP>'}))
        self.running = False
        if self.receive_thread:
            self.receive_thread.join()

    def get_all_groups(self):
        operation_dict = {"FLAG": "<GET_ROOMS>"}
        self.send_data(self.client_socket, pickle.dumps(operation_dict))

    def handle_broadcasted_group_data(self, on_broadcast_callback):
        try:
            while self.running:
                received_data = pickle.loads(self.recv_data(self.client_socket))
                print(f"Received data from broadcast in client: {received_data}")
                flag = received_data.get("FLAG")
                current_folder = received_data.get("CURRENT_FOLDER")
                if self.current_folder == current_folder:
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
        data_dict = {"FLAG": '<CREATE_FOLDER_GROUP>',
                     "DATA": [real_folder_name, folder_size, folder_date, folder_folder, group_name]}
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

    def handle_download_request_group(self, select_file_names_lst, save_path, file_folder):
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
        if switch_value == "on":
            data_dict_on = {"FLAG": '<FAVORITE>', "DATA": [file_name, ftype]}
            self.send_data(self.client_socket, pickle.dumps(data_dict_on))

            print(f"File '{file_name}' favorited.")

        elif switch_value == "off":
            data_dict_off = {"FLAG": '<UNFAVORITE>', "DATA": [file_name, ftype]}
            self.send_data(self.client_socket, pickle.dumps(data_dict_off))

            print(f"File '{file_name}' unfavorited.")

    def handle_download_folder_request_group(self, folder_name, save_path):
        data_dict = {"FLAG": "<RECV_FOLDER>", "DATA": folder_name}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

    def handle_presaved_files_group(self, file_folder):
        self.current_folder = file_folder
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
        data_dict = {"FLAG": '<DELETE>', "DATA": [folders_to_delete, select_file_names_lst, current_folder]}
        self.send_data(self.client_socket, pickle.dumps(data_dict))
        print("Files deleted successfully.")

    def handle_rename_request_group(self, rename_data, type_of_rename):
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

    def handle_search_request(self, search_query):
        self.current_folder = search_query
        data_dict = {"FLAG": "<SEARCH>", "DATA": search_query}
        self.send_data(self.client_socket, pickle.dumps(data_dict))

# ------------Client setup------------
HOST = '127.0.0.1'  # '192.168.1.152'
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
