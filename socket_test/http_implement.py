__author__ = 'liuyang'

import socket

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 8001))
    sock.listen(5)
    while True:
        connection, address =  sock.accept()
        content = connection.recv(1024)
        print(content)
        connection.settimeout(5)
        connection.send('''HTTP/1.1 200 OK
                        Context-Type:text/html; charset=uft-8
                        Server: Python-sip version 1.0
                        Context-Length:

                        <h1>Hello world!</h1>''')
        connection.close()