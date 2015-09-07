
import asyncore
from client_server import InetSocketServer

try:
    server = InetSocketServer('localhost', 7776)
    asyncore.loop()
except KeyboardInterrupt:
    print('Killed by user')

