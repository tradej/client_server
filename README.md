DevAssistant Client/Server Prototype
====================================

This repository contains a prototype of the DevAssistant client/server
architecture. This piece of software is highly unstable and is likely not to
work at all.

How to test
-----------

To test the server, run `./server.py unix` or `server.py inet` (depends if you
want to test the UNIX sockets or TCP alternative).

To connect to it, run

    socat - UNIX-CONNECT:~/.devassistant-socket

for UNIX sockets, or

    socat - TCP:localhost:7776

for TCP connection.

The only currently accepted command is `QUERY`, which will return the list of
runnables (assistants and actions) available on the machine.
