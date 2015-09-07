# -*- coding: utf-8 -*-

import os
import asyncore
import socket

from client_server import exceptions, handlers, settings

class Server(asyncore.dispatcher):

    def __init__(self):
        '''Call this method AFTER you initialize your subclass'''
        asyncore.dispatcher.__init__(self)
        self._prep_socket()
        self.set_reuse_addr()
        self.listen(1) # No concurrent connections

    def _prep_socket(self):
        raise NotImplementedError('You must implement a method that creates a socket and binds to it!')

    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            return
        else:
            sock, addr = pair
            print('LOG: Incoming connection from: {addr}'.format(addr=addr))
            handler = handlers.ServerHandler(sock)

class UnixSocketServer(Server):

    def __init__(self, filename):
        self.filename = filename
        Server.__init__(self)

    def _prep_socket(self):
        self._clean_socket()
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.bind(self.filename)

    def _clean_socket(self):
        try:
            os.unlink(self.filename)
        except OSError:
            pass


class InetSocketServer(Server):

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        Server.__init__(self)

    def _prep_socket(self):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((self.hostname, self.port))

class Client(asyncore.dispatcher):

    def __init__(self, address):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.connect(address)


