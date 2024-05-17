import socket
import pickle


class CommsFunctions:
    @staticmethod
    def send_data(client_socket: socket.socket, data: str | bytes):
        if isinstance(data, str):
            data = pickle.dumps(data)

        data_len = len(data).to_bytes(4, byteorder='big')
        client_socket.send(data_len + data)

    @staticmethod
    def recv_data(client_socket: socket.socket):
        try:
            data_len = client_socket.recv(4)

            while len(data_len) < 4:
                data_len += client_socket.recv(4 - len(data_len))
            len_to_int = int.from_bytes(data_len, byteorder='big')
            data = client_socket.recv(len_to_int)

            while len(data) < len_to_int:
                data += client_socket.recv(len_to_int - len(data))

            return data
        except ConnectionAbortedError as e:
            print(f"Error in recv_data: {e}")
