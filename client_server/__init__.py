# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import socket
import sys

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

    def _process_input(self, inp):
        message = inp[:-3]
        return 'Server reply: "{msg} SERVER"'.format(msg=message)

    def run(self):
        try:
            while True:
                connection, client_addr = self.sock.accept()
                try:
                    message = ''
                    while not message.endswith('EOF'):
                        datagram = connection.recv(16)
                        if datagram:
                            print('Received {data}'.format(data=datagram), file=sys.stderr)
                            message += datagram.decode('utf-8')
                        else:
                            print('Transmission terminated.', file=sys.stderr)
                            break
                    result = self._process_input(message)
                    print(result, file=sys.stderr)
                    connection.sendall((result + 'EOF').encode('utf-8'))
                except BrokenPipeError:
                    print('Connection to client lost', file=sys.stderr)
                finally:
                    connection.close()
        except KeyboardInterrupt:
            print('Killed by user.')


class Client(object):

    def __init__(self, address=settings.SOCKET):
        self.server_address = address
        self.sock = None

    def connect(self):
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.server_address)
            self.sock = sock
        except ConnectionRefusedError as e:
            raise exceptions.DisconnectedException(e)

    def disconnect(self):
        if self.sock:
            self.sock.close()

    def send(self, message):
        message_bytes = (message + 'EOF').encode('utf-8')
        self.sock.sendall(message_bytes)
        reply = ''
        while not reply.endswith('EOF'):
            datagram = self.sock.recv(1024).decode('utf-8')
            if datagram:
                print(datagram)
                reply += datagram
            else:
                raise exceptions.DisconnectedException('Connection closed by server. (Disconnected)')
        return reply



