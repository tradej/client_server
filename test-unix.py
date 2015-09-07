
import asyncore
from client_server import UnixSocketServer

try:
    server = UnixSocketServer('/home/tradej/.devassistant-socket')
    asyncore.loop()
except KeyboardInterrupt:
    print('Killed by user')

