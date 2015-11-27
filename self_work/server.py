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
            if not data:
                continue
            self.cmdHandle(conn, data)
            # conn.sendall(reply)
        conn.close()

    def cmdHandle(self, conn, content):
        if not content.strip():
            return
        parts = content.split(' ', 2)
        userName = parts[0]
        cmd = parts[1]
        try:
            remain = parts[2].strip()
        except IndexError:
            remain = ''
        method = getattr(self, 'do_' + cmd, None)
        try:
            method(conn, userName, remain)
        except TypeError:
            conn.sendall('Unknown command: %s\n' % cmd)

    def do_login(self, conn, userName, line):
        name = userName.strip()
        if name in server.users:
            conn.sendall('User Name Exist!')
        else:
            self.users[name] = conn
            conn.sendall('Login Success')
            self.broadcast(userName, userName + ' has just enter chat room...\n')

    def do_say(self, conn, userName, line):
        conn.sendall(userName + ' said just now: ' + line + '\n')
        self.broadcast(userName, userName + ' said ' + line + '\n')

    def do_query(self, conn, userName, line):
        result = 'Online users:\n'
        for key in self.users.keys():
            result += (key + '\n')
        conn.sendall(result)

    def do_logout(self, conn, userName, line):
        self.users.pop(userName)
        print('Connection from %s ended...' % userName)
        self.broadcast(userName, userName + ' has just left chat room...\n')
        # conn.close()

    def broadcast(self, userName, content):
        for item in self.users.items():
            name = item[0]
            conn = item[1]
            if name != userName:
                conn.sendall(content)


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
PORT = 9998

if __name__ == '__main__':
    server = ChatServer(HOST, PORT)
    try:
        server.handle_accept()
        print('server loop ended')
    except KeyboardInterrupt:
        print('Server shutdown...Done')
    finally:
        # server.serverDown()
        server.close()