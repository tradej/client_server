#!/usr/bin/python3

from client_server import Client, exceptions

client = Client()

try:
    client.connect()
    print('Send messages to server, press Ctrl+C to end.')
    while True:
        inp = input('> ')
        reply = client.send(inp)
        print('Received ' + reply)
except exceptions.DisconnectedException as e:
    print(e)
    exit(1)
except KeyboardInterrupt:
    exit(130)
except EOFError:
    pass
finally:
    client.disconnect()
