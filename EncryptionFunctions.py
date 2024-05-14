import pickle

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import rsa
import os

from CommsFunctions import CommsFunctions


# create class for send and recv

class EncryptionFunctions:
    @staticmethod
    def make_keys():
        """
        Make both a private key and a public key from the private key.
        :return: Both keys.
        """
        publicKey, privateKey = rsa.newkeys(512)
        return publicKey, privateKey

    @staticmethod
    def encrypt_RSA_message(message, publicKey):
        """
        Encrypt an RSA encrypted message.
        :param message: The original message.
        :param publicKey: The public key.
        :return: An RSA encrypted message.
        """
        return rsa.encrypt(message, publicKey)

    @staticmethod
    def decrypt_RSA_message(encryptedMessage, privateKey):
        """
        Decrypt an RSA encrypted message.
        :param encryptedMessage: The original encrypted message.
        :param privateKey: The private key.
        :return: The original decrypted message.
        """
        return rsa.decrypt(encryptedMessage, privateKey)

    @staticmethod
    def encrypt_AES_message(message, key):
        """
        Encrypting a message using AES encryption.
        :param message: The message.
        :param key: The key.
        :return: The encrypted message.
        """
        message = pickle.dumps(message)  # Encoding the message to bytes using pickle.
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        paddedData = padder.update(message) + padder.finalize()
        encryptedData = encryptor.update(paddedData) + encryptor.finalize()
        return iv + encryptedData

    @staticmethod
    def decrypt_AES_message(encryptedMessage, key):
        """
        Decrypting an encrypted AES message using the key.
        :param encryptedMessage: The encrypted message.
        :param key: The key.
        :return: The original decrypted message.
        """
        iv = encryptedMessage[:16]
        encryptedData = encryptedMessage[16:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decryptedData = decryptor.update(encryptedData) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        unpaddedData = unpadder.update(decryptedData) + unpadder.finalize()

        return pickle.loads(unpaddedData)  # Decode the decrypted bytes using pickle.

    @staticmethod
    def start_server_communication(sock):
        """
        This function handles the RSA communication when connecting to the server.
        It will get the public key and decrypt
        the AES key with it and send it to the server again,
        so both the server and the client will have an AES key that only they have.
        :param sock: The socket that is connected to the server.
        :return: The AES key, so we can save it and use it to encrypt messages to the server.
        """
        publicKeyString = pickle.loads(CommsFunctions.recv_data(sock))
        publicKey = rsa.PublicKey.load_pkcs1(
            publicKeyString.encode())  # converting the key from str back to the public key object.
        aesKey = os.urandom(16)  # Generating a new aes key

        aesKeyEncrypted = EncryptionFunctions.encrypt_RSA_message(aesKey, publicKey)
        CommsFunctions.send_data(sock, aesKeyEncrypted)
        # in the server side we will convert it to bytes back.
        return aesKey
