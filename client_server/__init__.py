# -*- coding: utf-8 -*-

import os
import socket

from client_server import exceptions, settings

class Server(object):

    def __init__(self, address=settings.SOCKET):
        self.address = address
        self.sock = self._setup_socket()

    def _setup_socket(self):
        '''Prepare socket the server will listen on'''
        self._remove_socket() # Needs to be removed first
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(self.address)
        os.chmod(self.address, 0o700)
        sock.listen(1)
        return sock

    def _remove_socket(self):
        '''Ensure the socket file does not exist'''
        try:
            os.unlink(self.address)
        except OSError:
            if os.path.exists(self.address):
                raise exceptions.ServerException

    def run(self):
        try:
            while True:
                connection, client_addr = self.sock.accept()
                try:
                    while True:
                        data = connection.recv(16)
                        if data:
                            print(data)
                        else:
                            print('EOF')
                            break
                finally:
                    connection.close()
        except KeyboardInterrupt:
            print('Killed by user.')

class Client(object):

    def __init__(self, address=settings.SOCKET):
        self.server_address = address
        self.sock = self._connect_socket()

    def _connect_socket(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.server_address)
        return sock

    def send(self, message):
        message_bytes = message.encode('utf-8')
        self.sock.sendall(message_bytes)

