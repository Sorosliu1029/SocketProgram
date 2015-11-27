__author__ = 'liuyang'
import socket
import sys
import time
import thread

class ChatServer(socket.socket):
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket created...')
        try:
            self.sock.bind((host, port))
            print('Socket bind complete...')
        except socket.error, e:
            print('Bind Failed.\nError Code: ' +
                  str(e[0]) + ' Message: ' + e[1])
            sys.exit(0)
        self.sock.listen(5)
        print('Socket now listening...')
        self.conn = None
        self.users = {}
        # self.main_room = ChatRoom(self)

    def handle_accept(self):
        while True:
            conn, addr = self.sock.accept()
            t = thread.start_new_thread(self.singleConnect, (conn, addr))

    def singleConnect(self, conn, addr):
        print('Accept new connection from: %s, %s' % addr)
        conn.sendall('Connect Success')
        while True:
            data = conn.recv(4096)
            reply = 'OK...' + data
            if not data:
                continue
            conn.sendall(reply)
        conn.close()


    # def loop(self):
    #     self.conn, addr = self.sock.accept()
    #     print('Connected with ' + addr[0] + ' : ' + str(addr[1]))
    #     self.conn.sendall('Connect Success')
    #     while True:
    #         data = self.conn.recv(4096)
    #         reply = 'OK...' + data
    #         if not data:
    #             continue
    #         self.conn.sendall(reply)

    # def serverDown(self):
    #     self.conn.close()


HOST = '127.0.0.1'
PORT = 9999

if __name__ == '__main__':
    server = ChatServer(HOST, PORT)
    try:
        server.handle_accept()
        print('server loop ended')
    except KeyboardInterrupt:
        print('Server down...')
    finally:
        # server.serverDown()
        server.close()