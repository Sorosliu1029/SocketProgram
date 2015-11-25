__author__ = 'liuyang'
'''
this server using multiple thread to server client request
in other words, each time server accept a request, server will create a thread to server
'''

import socket
import sys
from thread import *

HOST = ''
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error, msg:
    print('Bind failed. Error Code: ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

print('Socket bind complete')

# Start listening on socket
s.listen(10)
print('Socket now listening')

# Function for handling connection. This will be used to create threads
def client_thread(conn):
    # Send message to connected client
    conn.send('Welcome to the server. Type something and hit enter to send\n')
    # infinite loop so that function do not terminate and thread do not end
    while True:
        # receiving from client
        data = conn.recv(1024)
        reply = 'OK...' + data
        if not data:
            break

        conn.sendall(reply)

    conn.close()

# now keep talking with the client
while 1:
    # wait to accept a connection - blocking call
    conn, addr = s.accept()
    print('Connected with ' + addr[0] + ' : ' + str(addr[1]))

    # start new thread takes 1st argument as function name to be run,
    # second is the tuple of the argument to the funtion
    start_new_thread(client_thread, (conn,))

s.close()