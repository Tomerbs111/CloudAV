import datetime
import pickle
import re
import smtplib
import socket
import struct
import tempfile
import threading
import os
import shutil
import zipfile

from CommsFunctions import CommsFunctions
from EncryptionFunctions import EncryptionFunctions
from database.AuthManager import AuthManager
from database.GroupFiles import GroupFiles
from database.UserFiles import UserFiles
from database.RoomManager import RoomManager
from database.FavoritesManager import FavoritesManager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import pyotp

from GroupUser import GroupUser
from queue import Queue

HOST = '0.0.0.0'
PORT = 40301


# TODO: download folders
# TODO: refresh groups


class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(5)
        print(f"Server listening on {HOST}:{PORT}")

        # Initialize clients list
        self.clients_list = []
        self.base_path = "temp_zips"

        # Message queue for broadcasting
        self.file_queue = Queue()

        # call make keys
        self.public_key, self.private_key = EncryptionFunctions.make_keys()

        # Create a thread for broadcasting messages
        self.broadcast_thread = threading.Thread(target=self.broadcast_files)
        self.broadcast_thread.start()

    # insert encryption/decryption functions here
    def send_data(self, client_socket: socket, data: str | bytes, aes_key):
        encrypted_data = EncryptionFunctions.encrypt_AES_message(data, aes_key)
        CommsFunctions.send_data(client_socket, encrypted_data)

    def recv_data(self, client_socket: socket, aes_key):
        encrypted_data = CommsFunctions.recv_data(client_socket)
        decrypted_data = EncryptionFunctions.decrypt_AES_message(encrypted_data, aes_key)
        return decrypted_data

    def start(self):
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"Accepted connection from {client_address}")

                publicKeyString = self.public_key.save_pkcs1().decode()  # Decoding the public key to str so we can send it
                CommsFunctions.send_data(client_socket, publicKeyString)  # Sending the public key

                aesKeyEncrypted = CommsFunctions.recv_data(client_socket)  # Getting the aes key from the client.
                aes_key = EncryptionFunctions.decrypt_RSA_message(aesKeyEncrypted, self.private_key)

                identifier = None

                client_register_login_handler = threading.Thread(
                    target=self.handle_register_login,
                    args=(client_socket, identifier, aes_key)  # aseKey as parameter
                )
                client_register_login_handler.start()

        except KeyboardInterrupt:
            print("Server terminated by user.")
        except Exception as e:
            print(f"Unexpected error in server start: {e}")
        finally:
            self.server_socket.close()

    def handle_register_login(self, client_socket, identifier, aes_key):
        try:
            while True:
                received_data = pickle.loads(self.recv_data(client_socket, aes_key))
                authentication_flag = received_data.get("FLAG")
                field_dict = received_data.get("DATA")
                db_authentication = AuthManager()

                if authentication_flag == "<REGISTER>":
                    u_email = field_dict['email']
                    u_username = field_dict['username']
                    u_password = field_dict['password']

                    answer_to_send = self.handle_register_info(u_email, u_username, u_password, db_authentication)
                    self.send_data(client_socket, pickle.dumps({"FLAG": answer_to_send.get("FLAG"), "DATA": None}),
                                   aes_key)
                    if answer_to_send.get("FLAG") == "<SUCCESS>":
                        identifier = answer_to_send.get("DATA")

                elif authentication_flag == "<LOGIN>":
                    u_email = field_dict['email']
                    u_password = field_dict['password']

                    answer_to_send = self.handle_login_info(u_email, u_password, db_authentication)
                    self.send_data(client_socket, pickle.dumps({"FLAG": answer_to_send.get("FLAG"), "DATA": None}),
                                   aes_key)

                    # Check if login was successful then starts 2FA
                    if answer_to_send.get("FLAG") == "<SUCCESS>":
                        identifier = answer_to_send.get("DATA")
                        u_username = db_authentication.get_username(identifier)
                        otp_password = self.send_otp_email(u_email, u_username, client_socket)

                        while True:
                            client_response = pickle.loads(self.recv_data(client_socket, aes_key))
                            print(client_response.get("DATA"))
                            print(otp_password)
                            if client_response.get("DATA") == otp_password:
                                print(f"User {u_email} logged in.")
                                self.send_data(client_socket, pickle.dumps(
                                    {"FLAG": "<2FA_SUCCESS>", "DATA": db_authentication.get_username(identifier)}),
                                               aes_key)
                                break

                            else:
                                self.send_data(client_socket, pickle.dumps({"FLAG": "<2FA_FAILED>", "DATA": None}),
                                               aes_key)

                if identifier:
                    # Start a new thread to handle the client
                    client_handler = threading.Thread(
                        target=self.handle_requests,
                        args=(client_socket, identifier, aes_key)
                    )

                    client_handler.start()
                    break  # Break out of the inner loop if registration or login is successful

        except (socket.error, IOError) as e:
            print(f"Error in handle_register_login: {e}")
            client_socket.close()

    def handle_register_info(self, u_email, u_username, u_password, auth):
        try:
            db_answer = auth.register(u_email, u_username, u_password)

            # Create a dictionary with "FLAG" and "DATA" keys
            answer_to_send = {"FLAG": db_answer, "DATA": None}

            if db_answer == "<EXISTS>":
                answer_to_send["DATA"] = "Email already exists"
            elif db_answer == "<SUCCESS>":
                userid = auth.get_userid(u_email)
                answer_to_send["DATA"] = userid[0]

            return answer_to_send

        except Exception as e:
            answer_to_send["FLAG"] = "<FAILED>"
            answer_to_send["DATA"] = f"Unexpected error during registration: {e}"
            return answer_to_send

    def handle_login_info(self, u_email, u_password, auth):
        try:
            db_answer = auth.login(u_email, u_password)

            # Create a dictionary with "FLAG" and "DATA" keys
            answer_to_send = {"FLAG": None, "DATA": None}

            if db_answer == "<NO_EMAIL_EXISTS>":

                answer_to_send["FLAG"] = "<NO_EMAIL_EXISTS>"
                answer_to_send["DATA"] = "Email doesn't exist"

            elif db_answer == "<WRONG_PASSWORD>":
                answer_to_send["FLAG"] = "<WRONG_PASSWORD>"
                answer_to_send["DATA"] = "Wrong password"

            else:
                userid = auth.get_userid(u_email)
                answer_to_send["FLAG"] = "<SUCCESS>"
                answer_to_send["DATA"] = userid[0]

            return answer_to_send

        except Exception as e:
            answer_to_send["FLAG"] = "<FAILED>"
            answer_to_send["DATA"] = f"Unexpected error during login: {e}"
            return answer_to_send

    def broadcast_files(self):
        try:
            while True:
                queued_data = self.file_queue.get()
                sender_socket, file_data, group_name = queued_data

                for g_users in self.clients_list:
                    try:
                        if g_users.user_socket != sender_socket:
                            if g_users.group_name == group_name:
                                self.send_data(g_users.user_socket, pickle.dumps(file_data), g_users.aes_key)

                    except Exception as e:
                        print(f"Error in broadcast_files: {e}")

        except Exception as e:
            print(f"Error in broadcast_files thread: {e}")

    def handle_requests(self, client_socket, identifier, aes_key):
        try:
            user_files_manager = UserFiles(identifier)
            favorite_manager = FavoritesManager(AuthManager().get_email(identifier))

            while True:
                action = None
                received_data = pickle.loads(self.recv_data(client_socket, aes_key))

                if received_data.get("FLAG") == "<NARF>":
                    narf_data = received_data.get("DATA")
                    self.handle_presaved_files_action(client_socket, user_files_manager, favorite_manager, narf_data,
                                                      aes_key)

                elif received_data.get("FLAG") == "<CREATE_FOLDER>":
                    create_folder_data = received_data.get("DATA")
                    self.handle_create_folder_action(client_socket, user_files_manager, create_folder_data)

                elif received_data.get("FLAG") == "<SEND>":
                    send_data = received_data.get("DATA")
                    self.handle_send_file_action(client_socket, user_files_manager, send_data)

                elif received_data.get("FLAG") == "<RECV>":
                    recv_data = received_data.get("DATA")
                    self.handle_receive_files_action(client_socket, user_files_manager, recv_data, aes_key)

                elif received_data.get("FLAG") == "<RECV_FOLDER>":
                    recv_folder_data = received_data.get("DATA")
                    self.handle_receive_folder_action(client_socket, user_files_manager, recv_folder_data, aes_key)

                elif received_data.get("FLAG") == "<DELETE>":
                    delete_data = received_data.get("DATA")
                    self.handle_delete_file_action(client_socket, user_files_manager, delete_data)

                elif received_data.get("FLAG") == "<RENAME>":
                    rename_data = received_data.get("DATA")
                    type_of_rename = received_data.get("TYPE")
                    self.handle_rename_file_action(client_socket, user_files_manager, rename_data, type_of_rename)

                elif received_data.get("FLAG") == "<FAVORITE>":
                    favorite_data = received_data.get("DATA")
                    self.handle_favorite_file_action(client_socket, user_files_manager, favorite_manager, favorite_data)

                elif received_data.get("FLAG") == "<UNFAVORITE>":
                    unfavorite_data = received_data.get("DATA")
                    self.handle_unfavorite_file_action(client_socket, user_files_manager, favorite_manager,
                                                       unfavorite_data)

                elif received_data.get("FLAG") == "<GET_USERS>":
                    current_folder = received_data.get("DATA")
                    self.handle_get_users_action(client_socket, identifier, aes_key, current_folder)

                elif received_data.get("FLAG") == "<CREATE_GROUP>":
                    create_group_data = received_data.get("DATA")
                    self.handle_create_group_action(client_socket, identifier, create_group_data)

                elif received_data.get("FLAG") == "<GET_ROOMS>":
                    self.handle_get_rooms_action(client_socket, identifier, aes_key)

                elif received_data.get("FLAG") == "<GET_FAVORITES>":
                    self.handle_get_all_favorites_action(client_socket, favorite_manager, aes_key)

                elif received_data.get("FLAG") == "<JOIN_GROUP>":
                    join_group_data = received_data.get("DATA")
                    self.handle_join_group_action(client_socket, identifier, join_group_data, aes_key)
                    break

                elif received_data.get("FLAG") == "<LOGOUT>":
                    self.handle_logout_action(client_socket, aes_key)
                    break

                elif received_data.get("FLAG") == "<SEARCH>":
                    search_data = received_data.get("DATA")
                    self.handle_personal_search_action(client_socket, user_files_manager, identifier, search_data, aes_key)

                elif received_data.get("FLAG") == "<SEARCH_FAVORITES>":
                    search_data = received_data.get("DATA")
                    self.handle_search_favorites_action(client_socket, favorite_manager, search_data, aes_key)



        except (socket.error, IOError) as e:
            print(f"Error in handle_requests: {e}")
            client_socket.close()

    def handle_group_requests(self, client_socket: socket, identifier, aes_key):
        try:
            group_manager = GroupFiles(AuthManager().get_email(identifier))
            favorite_manager = FavoritesManager(AuthManager().get_email(identifier))

            while True:
                received_data = pickle.loads(self.recv_data(client_socket, aes_key))

                if received_data.get("FLAG") == "<NARF>":
                    narf_data = received_data.get("DATA")
                    self.handle_presaved_files_action(client_socket, group_manager, favorite_manager, narf_data,
                                                      aes_key)

                elif received_data.get("FLAG") == "<CREATE_FOLDER_GROUP>":
                    create_folder_data = received_data.get("DATA")
                    self.handle_create_folder_action(client_socket, group_manager, create_folder_data)

                elif received_data.get("FLAG") == "<RECV>":
                    recv_data = received_data.get("DATA")
                    self.handle_receive_files_action(client_socket, group_manager, recv_data, aes_key)

                elif received_data.get("FLAG") == "<SEND>":
                    send_data = received_data.get("DATA")
                    self.handle_send_file_action(client_socket, group_manager, send_data)

                elif received_data.get("FLAG") == "<DELETE>":
                    delete_data = received_data.get("DATA")
                    self.handle_delete_file_action(client_socket, group_manager, delete_data)

                elif received_data.get("FLAG") == "<RENAME>":
                    rename_data = received_data.get("DATA")
                    type_of_rename = received_data.get("TYPE")
                    self.handle_rename_file_action(client_socket, group_manager, rename_data, type_of_rename)

                elif received_data.get("FLAG") == "<FAVORITE>":
                    favorite_data = received_data.get("DATA")
                    self.handle_favorite_file_action(client_socket, group_manager, favorite_manager, favorite_data)

                elif received_data.get("FLAG") == "<UNFAVORITE>":
                    unfavorite_data = received_data.get("DATA")
                    self.handle_unfavorite_file_action(client_socket, group_manager, favorite_manager, unfavorite_data)

                elif received_data.get("FLAG") == "<GET_USERS>":
                    current_folder = received_data.get("DATA")
                    self.handle_get_users_action(client_socket, identifier, aes_key, current_folder)

                elif received_data.get("FLAG") == "<CREATE_GROUP>":
                    create_group_data = received_data.get("DATA")
                    self.handle_create_group_action(client_socket, identifier, create_group_data)

                elif received_data.get("FLAG") == "<LEAVE_GROUP>":
                    self.handle_leave_group_action(client_socket, identifier, aes_key)
                    break

                elif received_data.get("FLAG") == "<GET_ROOMS>":
                    self.handle_get_rooms_action(client_socket, identifier, aes_key)

                elif received_data.get("FLAG") == "<RECV_FOLDER>":
                    recv_folder_data = received_data.get("DATA")
                    self.handle_receive_folder_action(client_socket, group_manager, recv_folder_data, aes_key)

                elif received_data.get("FLAG") == "<LOGOUT>":
                    self.handle_logout_action(client_socket, aes_key)
                    break

                elif received_data.get("FLAG") == "<SEARCH>":
                    search_data = received_data.get("DATA")
                    self.handle_group_search_action(client_socket, group_manager, identifier, search_data, aes_key, favorite_manager)


        except (socket.error, IOError) as e:
            print(f"Error in handle_group_requests: {e}")
            client_socket.close()

    def handle_personal_search_action(self, client_socket, user_files_manager, identifier, search_data, aes_key):
        try:
            print("in personal search")
            # Perform search on user files
            user_results = user_files_manager.search_files(search_data)

            # Initialize results as an empty list if they are None
            if user_results is None:
                user_results = []

            # Send the search results back to the client
            response_data = {
                "FLAG": "<SEARCH_RESULTS>",
                "DATA": user_results
            }
            print(response_data)
            self.send_data(client_socket, pickle.dumps(response_data), aes_key)
        except Exception as e:
            print(f"Error in personal search action: {e}")
            client_socket.close()

    def handle_group_search_action(self, client_socket, group_manager, identifier, search_data, aes_key,
                                   favorite_manager):
        try:
            print("in group search")
            user_email = AuthManager().get_email(identifier)
            room_manager = RoomManager()

            room_lst = room_manager.get_rooms_by_participant(user_email)

            # Perform search on group files
            group_results = group_manager.search_files(search_data, favorite_manager, room_lst)

            # Initialize results as an empty list if they are None
            if group_results is None:
                group_results = []

            # Send the search results back to the client
            response_data = {
                "FLAG": "<SEARCH_RESULTS>",
                "DATA": group_results,
                "CURRENT_FOLDER": search_data
            }
            print(response_data)
            self.send_data(client_socket, pickle.dumps(response_data), aes_key)
        except Exception as e:
            print(f"Error in group search action: {e}")
            client_socket.close()

    def handle_search_favorites_action(self, client_socket, favorite_manager, search_data, aes_key):
        try:
            print("in search favorites")

            favorite_results = favorite_manager.search_favorites(search_data)

            # Initialize results as an empty list if they are None
            if favorite_results is None:
                favorite_results = []
            # Send the search results back to the client
            response_data = {
                "FLAG": "<SEARCH_FAVORITES>",
                "DATA": favorite_results
            }
            print(response_data)
            self.send_data(client_socket, pickle.dumps(response_data), aes_key)

            print("out of search favorites")
        except Exception as e:
            print(f"Error in search favorites action: {e}")
            client_socket.close()

    def handle_presaved_files_action(self, client_socket, db_manager, favorite_manager, folder_name, aes_key):
        try:
            print(folder_name)
            saved_file_prop_lst = []
            if isinstance(db_manager, GroupFiles):
                group_name = self.get_group_name(client_socket)
                saved_file_prop_lst = db_manager.get_all_files_from_group(group_name, folder_name)
                print(saved_file_prop_lst)

            elif isinstance(db_manager, UserFiles):
                saved_file_prop_lst = db_manager.get_all_data(folder_name)

            data_to_send = {"FLAG": "<NARF>", "DATA": saved_file_prop_lst, "CURRENT_FOLDER": folder_name}

            self.send_data(client_socket, pickle.dumps(data_to_send), aes_key)
        except Exception as e:
            print(f"Error in presaved files action: {e}")
            client_socket.close()

    def handle_create_folder_action(self, client_socket, db_manager, create_folder_data):
        try:
            folder_name = create_folder_data[0]
            folder_size = create_folder_data[1]
            folder_date = create_folder_data[2]
            folder_bytes = b""
            folder_folder = create_folder_data[3]

            if isinstance(db_manager, UserFiles):
                db_manager.insert_file(folder_name, folder_size, folder_date, folder_bytes, folder_folder)

            elif isinstance(db_manager, GroupFiles):
                print(create_folder_data)
                group_name = create_folder_data[4]
                db_manager.insert_file(folder_name, folder_size, folder_date, group_name, folder_folder, folder_bytes)
                folder_info = db_manager.get_file_info(group_name, folder_name, folder_folder)
                queued_info = {"FLAG": '<CREATE_FOLDER_GROUP>', "DATA": [folder_info], "CURRENT_FOLDER": folder_folder}

                self.file_queue.put((client_socket, queued_info, group_name))
        except Exception as e:
            print(f"Error in create folder action: {e}")
            client_socket.close()

    def handle_send_file_action(self, client_socket, db_manager, all_file_content):
        try:
            file_name = all_file_content[0]
            file_size = all_file_content[1]
            file_date = all_file_content[2]
            file_bytes = all_file_content[3]
            file_folder = all_file_content[4]

            if isinstance(db_manager, GroupFiles):
                group_name = self.get_group_name(client_socket)
                db_manager.insert_file(file_name, file_size, file_date, group_name, file_folder, file_bytes)
                file_info = db_manager.get_file_info(group_name, file_name, file_folder)
                print(f"File info: {file_info}")
                queued_info = {"FLAG": "<SEND>", "DATA": [file_info], "CURRENT_FOLDER": file_folder}

                self.file_queue.put((client_socket, queued_info, group_name))

            elif isinstance(db_manager, UserFiles):
                db_manager.insert_file(file_name, file_size, file_date, file_bytes, file_folder)

            print(f"File '{file_name}' received and saved in the database")

        except Exception as e:
            print(f"Error in handle_save_file_action: {e}")
            client_socket.close()

    def handle_receive_files_action(self, client_socket, db_manager, recv_data, aes_key):
        try:
            file_data_name_dict = {}
            for folder_name, select_file_names_lst in recv_data.items():
                if isinstance(db_manager, GroupFiles):
                    for individual_file in select_file_names_lst:
                        file_data = db_manager.get_file_data(self.get_group_name(client_socket), individual_file,
                                                             folder_name)
                        file_data_name_dict[individual_file] = file_data

                elif isinstance(db_manager, UserFiles):
                    for individual_file in select_file_names_lst:
                        file_data = db_manager.get_file_data(individual_file, folder_name)[0]
                        file_data_name_dict[individual_file] = file_data

            data_dict = {"FLAG": '<RECV>', "DATA": file_data_name_dict, "CURRENT_FOLDER": folder_name}
            self.send_data(client_socket, pickle.dumps(data_dict), aes_key)

            print("Files sent successfully.")

        except Exception as e:
            print(f"Error in handle_read_files_action: {e}")

    def handle_delete_file_action(self, client_socket, db_manager, delete_data):
        try:
            file_names_lst = delete_data[0]
            folder_names_lst = delete_data[1]
            current_folder = delete_data[2]

            if isinstance(db_manager, GroupFiles):
                group_name = self.get_group_name(client_socket)
                for individual_file in file_names_lst:
                    db_manager.delete_file(self.get_group_name(client_socket), individual_file, current_folder)
                    queued_info = {"FLAG": "<DELETE>", "DATA": individual_file, "CURRENT_FOLDER": current_folder}
                    self.file_queue.put((client_socket, queued_info, group_name))

                for individual_folder in folder_names_lst:
                    queued_info = {"FLAG": "<DELETE>", "DATA": individual_folder, "CURRENT_FOLDER": current_folder }
                    self.file_queue.put((client_socket, queued_info, group_name))

                    def delete_folder_recursive(current_folder, folder_name):
                        all_files = db_manager.get_name_file_from_folder_group(self.get_group_name(client_socket),
                                                                               folder_name)
                        print(f"all_files: {all_files}")
                        if len(all_files) == 0:
                            return
                        for files_in_folder in all_files:
                            print(files_in_folder)
                            if " <folder>" in files_in_folder:
                                delete_folder_recursive(folder_name, files_in_folder.replace(" <folder>", ""))
                            db_manager.delete_file(self.get_group_name(client_socket), files_in_folder, folder_name)

                    delete_folder_recursive(current_folder, individual_folder.replace(" <folder>", ""))
                    db_manager.delete_file(self.get_group_name(client_socket), individual_folder, current_folder)


            elif isinstance(db_manager, UserFiles):
                for individual_file in file_names_lst:
                    db_manager.delete_file(individual_file, current_folder)
                for individual_folder in folder_names_lst:
                    def delete_folder_recursive(current_folder, folder_name):
                        all_files = db_manager.get_folder_data(folder_name)
                        print(f"all_files: {all_files}")
                        if len(all_files) == 0:
                            return
                        for files_in_folder in all_files:
                            print(files_in_folder)
                            if " <folder>" in files_in_folder:
                                delete_folder_recursive(folder_name, files_in_folder.replace(" <folder>", ""))
                            db_manager.delete_file(files_in_folder, folder_name)

                        db_manager.delete_folder(folder_name)

                    delete_folder_recursive(current_folder, individual_folder.replace(" <folder>", ""))
                    db_manager.delete_file(individual_folder, current_folder)
            print("Files deleted successfully.")

        except Exception as e:
            print(f"Error in handle_delete_action: {e}")
            client_socket.close()

    def handle_rename_file_action(self, client_socket, db_manager, rename_data, type_of_rename):
        try:
            old_name = rename_data[0]
            new_name = rename_data[1]
            file_folder = rename_data[2]

            print(old_name, new_name, file_folder, type_of_rename)
            if type_of_rename == "<FILE>":
                if isinstance(db_manager, GroupFiles):
                    group_name = self.get_group_name(client_socket)
                    db_manager.rename_file(group_name, old_name, new_name, file_folder)

                    queued_info = {"FLAG": "<RENAME>", "DATA": rename_data, "CURRENT_FOLDER": file_folder}
                    self.file_queue.put((client_socket, queued_info, group_name))

                if isinstance(db_manager, UserFiles):
                    db_manager.rename_file(old_name, new_name, file_folder)
                print("File renamed successfully.")

            elif type_of_rename == "<FOLDER>":
                if isinstance(db_manager, GroupFiles):
                    group_name = self.get_group_name(client_socket)
                    db_manager.rename_file(group_name, old_name, new_name, file_folder)
                    db_manager.rename_folder_files(group_name, old_name.replace(" <folder>", ""),
                                                   new_name.replace(" <folder>", ""))

                    queued_info = {"FLAG": "<RENAME>", "DATA": rename_data, "CURRENT_FOLDER": file_folder}
                    self.file_queue.put((client_socket, queued_info, group_name))

                if isinstance(db_manager, UserFiles):
                    db_manager.rename_file(old_name, new_name, file_folder)
                    db_manager.rename_folder_files(old_name.replace(" <folder>", ""), new_name.replace(" <folder>", ""))
                print("Folder renamed successfully.")
        except Exception as e:
            print(f"Error in rename file action: {e}")
            client_socket.close()


    def handle_favorite_file_action(self, client_socket, db_manager, favorite_manager, favorite_data):
        try:
            favorite_file_name = favorite_data[0]
            favorite_file_type = favorite_data[1]

            favorite_manager.set_favorite_status(favorite_file_name, favorite_file_type, 1)

            if isinstance(db_manager, UserFiles):
                db_manager.set_favorite_status(favorite_file_name, 1)
                if favorite_manager.get_favorite_status(favorite_file_name, 'personal') is None:
                    favorite_manager.insert_favorite(favorite_file_name, 'personal', 1)

            elif isinstance(db_manager, GroupFiles):
                group_name = self.get_group_name(client_socket)
                if favorite_manager.get_favorite_status(favorite_file_name, group_name) is None:
                    favorite_manager.insert_favorite(favorite_file_name, group_name, 1)
            else:
                print("Unknown database manager type.")
        except Exception as e:
            print(f"Error in favorite file action: {e}")
            client_socket.close()

    def handle_unfavorite_file_action(self, client_socket, db_manager, favorite_manager, favorite_data):
        try:
            unfavorite_file_name = favorite_data[0]
            unfavorite_file_type = favorite_data[1]

            favorite_manager.set_favorite_status(unfavorite_file_name, unfavorite_file_type, 0)

            if isinstance(db_manager, UserFiles):
                db_manager.set_favorite_status(unfavorite_file_name, 0)
                if favorite_manager.get_favorite_status(unfavorite_file_name, 'personal') is None:
                    favorite_manager.insert_favorite(unfavorite_file_name, 'personal', 0)

            elif isinstance(db_manager, GroupFiles):
                group_name = self.get_group_name(client_socket)
                if favorite_manager.get_favorite_status(unfavorite_file_name, group_name) is None:
                    favorite_manager.insert_favorite(unfavorite_file_name, group_name, 0)
            else:
                print("Unknown database manager type.")
        except Exception as e:
            print(f"Error in unfavorite file action: {e}")
            client_socket.close()

    def handle_get_all_favorites_action(self, client_socket, favorite_manager, aes_key):
        try:
            all_favorites = favorite_manager.get_all_favorites()

            data_to_send = {"FLAG": "<GET_ALL_FAVORITES>", "DATA": all_favorites}
            self.send_data(client_socket, pickle.dumps(data_to_send), aes_key)
            print(f"Sent all favorites to the client.")
        except Exception as e:
            print(f"Error in get all favorites action: {e}")
            client_socket.close()

    def handle_get_users_action(self, client_socket, identifier, aes_key, current_folder):
        try:
            all_users = AuthManager().get_all_users(identifier)
            print(f"this is all users {all_users}")
            data_to_send = {"FLAG": "<GET_USERS>", "DATA": all_users, "CURRENT_FOLDER": current_folder}
            self.send_data(client_socket, pickle.dumps(data_to_send), aes_key)
            print(f"Sent users list to the client.")
        except Exception as e:
            print(f"Error in get users action: {e}")
            client_socket.close()

    def handle_create_group_action(self, client_socket, identifier, group_data):
        try:
            user_email = AuthManager().get_email(identifier)

            group_name = group_data[0]
            group_participants = group_data[1]
            group_participants.append(user_email)
            group_permissions = group_data[2]
            permission_values = []

            for permission in group_permissions:
                permission_values.append(str(group_permissions[permission]))

            print(permission_values)

            # Create a room in the database using RoomManager
            room_manager = RoomManager()
            room_manager.insert_room(group_name, ",".join(group_participants), user_email, permission_values)
            print(f"Group created successfully.")
        except Exception as e:
            print(f"Error in create group action: {e}")
            client_socket.close()

    def handle_get_rooms_action(self, client_socket, identifier, aes_key):
        try:
            user_email = AuthManager().get_email(identifier)
            room_manager = RoomManager()

            rooms_containing_user = room_manager.get_rooms_by_participant(user_email)

            # Create a dictionary with room names as keys and permissions as values
            rooms_dict = {}
            for room in rooms_containing_user:
                room_permissions = room_manager.get_room_permissions(room)
                # Split the permission string into a list of strings
                permissions_list = room_permissions[0].split(',')
                room_admin = room_manager.get_room_admin(room)
                rooms_dict[room] = [permissions_list, room_admin]
            # Pickle and send the dictionary over the socket
            data_to_send = {"FLAG": "<GET_ROOMS>", "DATA": rooms_dict}
            self.send_data(client_socket, pickle.dumps(data_to_send), aes_key)

            print(f"Sent rooms containing {user_email} to the client.")

        except Exception as e:
            print(f"Error in fetch_rooms_for_user: {e}")
            client_socket.close()

    def handle_receive_folder_action(self, client_socket, db_manager, folder_name, aes_key):
        try:
            """
            Create a folder with the given name and initialize it with all associated files.
            Then compress the folder into a zip file and delete the original folder.

            :param folder_name: The name of the folder to create
            :param db_manager: Database manager to fetch files
            :param aes_key: AES key for encryption
            """
            print(f"Receiving folder '{folder_name}'...")
            # Ensure the base path exists
            if not os.path.exists(self.base_path):
                os.makedirs(self.base_path)

            # Path to the new folder
            folder_path = os.path.join(self.base_path, folder_name)

            # Create the folder if it doesn't exist
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # Check if db_manager is UserFiles or GroupFiles and get data accordingly
            if isinstance(db_manager, UserFiles):
                all_files = db_manager.get_all_data_for_folder(folder_name)
            elif isinstance(db_manager, GroupFiles):
                group_name = self.get_group_name(client_socket)
                all_files = db_manager.get_all_data_for_folder(group_name, folder_name)
            else:
                print("Unsupported db_manager type")
                return

            if all_files == "<NO_DATA>":
                print(f"No files found for folder '{folder_name}'")
                return

            # Iterate through the files and save them to the new folder
            def recursive_save(data, current_path):
                for name, f_bytes in data.items():
                    if " <folder>" in name:
                        # Remove the "<folder>" suffix
                        name = name.replace(" <folder>", "")
                        new_path = os.path.join(current_path, name)
                        os.makedirs(new_path, exist_ok=True)
                        if isinstance(db_manager, UserFiles):
                            all_files_r = db_manager.get_all_data_for_folder(name)
                        elif isinstance(db_manager, GroupFiles):
                            all_files_r = db_manager.get_all_data_for_folder(group_name, name)
                        recursive_save(all_files_r, new_path)
                    else:
                        # Write the file f_bytes
                        file_path = os.path.join(current_path, name)
                        with open(file_path, 'wb') as file:
                            file.write(f_bytes)

            # Start recursive save
            recursive_save(all_files, folder_path)

            print(f"Folder '{folder_name}' created with {len(all_files)} files.")

            # Compress the folder into a zip file
            zip_file_path = os.path.join(self.base_path, f"{folder_name}.zip")
            shutil.make_archive(folder_path, 'zip', self.base_path, folder_name)

            # Remove the original folder
            shutil.rmtree(folder_path)

            print(f"Folder '{folder_name}' compressed into '{zip_file_path}' and original folder deleted.")

            # Read the zip file into memory
            with open(zip_file_path, 'rb') as zip_file:
                zip_data = zip_file.read()

            # Prepare data dictionary with the zip data bytes
            data_dict = {"FLAG": "<RECV_FOLDER>", "DATA": [zip_data, folder_name]}

            # Send the data to the client
            self.send_data(client_socket, pickle.dumps(data_dict), aes_key)

            # Optionally, delete the zip file after sending
            os.remove(zip_file_path)

        except Exception as e:
            print(f"Error in handle_receive_folder_action: {e}")
            client_socket.close()

    def is_user_admin(self, username, group_name):
        try:
            room_manager = RoomManager()
            admin_email = room_manager.get_room_admin(group_name)

            if admin_email == AuthManager().get_email(username):
                return True
            else:
                return False

        except Exception as e:
            print(f"Error in is_user_admin: {e}")
            return False

    def handle_join_group_action(self, client_socket, identifier, group_name, aes_key):
        try:
            user_email = AuthManager().get_email(identifier)

            # Check if the user is already in the clients_list with a different group name
            user_found = False
            for group_user in self.clients_list:
                if group_user.user_socket == client_socket:
                    if group_user.group_name != group_name:
                        group_user.group_name = group_name  # Change the group_name to the new one
                    user_found = True
                    break

            if not user_found:
                # If the user is not in the list, append with the received group name
                self.clients_list.append(GroupUser(client_socket, user_email, group_name, aes_key))

            self.send_data(client_socket, pickle.dumps({"FLAG": "<JOINED>", "DATA": user_email}), aes_key)
            print(f"User {user_email} joined the group '{group_name}'.")

            group_handler = threading.Thread(
                target=self.handle_group_requests,
                args=(client_socket, identifier, aes_key)
            )
            group_handler.start()

        except Exception as e:
            print(f"Error in handle_join_group_action: {e}")
            client_socket.close()

    def handle_leave_group_action(self, client_socket, identifier, aes_key):
        try:
            for group_user in self.clients_list:
                if group_user.user_socket == client_socket:
                    self.clients_list.remove(group_user)
                    break
            self.send_data(client_socket, pickle.dumps({"FLAG": "<LEFT>"}), aes_key)
            client_handler = threading.Thread(
                target=self.handle_requests,
                args=(client_socket, identifier, aes_key)
            )
            client_handler.start()

        except Exception as e:
            print(f"Error in handle_leave_group_action: {e}")
            client_socket.close()

    import pyotp


    def get_group_name(self, client_socket):
        try:
            for index, group_user in enumerate(self.clients_list):
                if group_user.user_socket == client_socket:
                    return group_user.group_name
        except Exception as e:
            print(f"Error getting group name: {e}")
            return None

    def create_verification_code(self):
        try:
            key = "TomerBenShushanSecretKey"
            totp = pyotp.TOTP(key)

            # return totp.now()
            return "123456"
        except Exception as e:
            print(f"Error creating verification code: {e}")
            return None

    def send_otp_email(self, u_email, u_username, client_socket):
        # Generate a random password of the specified length
        password = self.create_verification_code()
        try:
            client_ip = client_socket.getpeername()[0]

            # Create a MIME multipart message
            msg = MIMEMultipart()
            msg['From'] = 'cloudav03@gmail.com'
            msg['To'] = u_email
            msg['Subject'] = 'Two-Factor Authentication'

            # Read HTML content from file
            with open('../GUI/2fa mail.html', 'r') as file:
                html_content = file.read()

            # Replace placeholders with actual data
            html_content = html_content.replace('[Client Name]', u_username)
            html_content = html_content.replace('[Client Location]', 'Petah Tikva, Israel')
            html_content = html_content.replace('[Client IP]', client_ip)
            html_content = html_content.replace('[Client Device]', 'Windows Desktop')
            html_content = html_content.replace('[Client Time]', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            html_content = html_content.replace('[Client Code]', password)

            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))

            # Attach the logo image
            img_path = "../GUI/file_icons/logo_cloudav_2.png"
            with open(img_path, 'rb') as f:
                logo_image = MIMEImage(f.read())
                logo_image.add_header('Content-ID', '<logo>')
                msg.attach(logo_image)

            # Connect to SMTP server and send email
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login('cloudav03@gmail.com', 'ivdr wron fhzc xjgo')
            server.sendmail('cloudav03@gmail.com', u_email, msg.as_string())
            server.quit()

            print("Email sent successfully!")

            return password
        except Exception as e:
            print(e)
            print("Email failed to send.")

    def handle_logout_action(self, client_socket, aes_key):
        try:
            for group_user in self.clients_list:
                if group_user.user_socket == client_socket:
                    self.clients_list.remove(group_user)
                    break
            self.send_data(client_socket, pickle.dumps({"FLAG": "<LEFT>"}), aes_key)
            identifier = None
            self.handle_register_login(client_socket, identifier, aes_key)

        except Exception as e:
            print(f"Error in handle_leave_group_action: {e}")
            client_socket.close()


if __name__ == "__main__":
    server = Server()
    server.start()
