#!/usr/bin/python
# encoding:utf-8
"""

"""

import socket
import sys
import thread
from datetime import datetime
from http import Response, Request

__author__ = 'liuyang'


def generateResponse(status, entity):
    http_response = Response()
    http_response.set_status(status)
    http_response.set_entity(entity)
    entityHeaderDict['Content_Length'] = str(len(entity))
    http_response.generalHeader.set_value({'Datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    http_response.responseHeader.set_value(responseHeaderDict)
    http_response.entityHeader.set_value(entityHeaderDict)
    return http_response


def handleRequest(raw_request):
    http_request = Request()
    http_request.unpack(raw_request)
    return http_request


class ChatServer(socket.socket):
    """

    """
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

    def handle_accept(self):
        while True:
            conn, addr = self.sock.accept()
            t = thread.start_new_thread(self.singleConnect, (conn, addr))

    def singleConnect(self, conn, addr):
        print('Accept new connection from: %s, %s' % addr)

        raw_response = generateResponse('202', 'test').pack()

        conn.sendall(raw_response)
        while True:
            raw_request = conn.recv(4096)
            if not raw_request:
                continue
            print(raw_request)
            http_request = handleRequest(raw_request)
            self.cmdHandle(conn, http_request.requestHeader.key_value['User_Agent'],
                           http_method2server_command[http_request.method], http_request.entity)
        conn.close()

    def cmdHandle(self, conn, userName, cmd, content):
        method = getattr(self, 'do_' + cmd, None)
        try:
            method(conn, userName, content)
        except TypeError:
            raw_response = generateResponse('400', 'Unknown...TAT').pack()
            conn.sendall(raw_response)

    def do_login(self, conn, userName, content):
        name = userName.strip()
        if name in server.users:
            raw_response = generateResponse('401', 'Error...T.T').pack()
            conn.sendall(raw_response)
        else:
            self.users[name] = conn
            raw_response = generateResponse('200', 'OK...^.^').pack()
            conn.sendall(raw_response)
            raw_response = generateResponse('200', userName + ' has just entered the chat room...\n').pack()
            self.broadcast(userName, raw_response)

    def do_say(self, conn, userName, content):
        entity = (userName + ' : ' + content + '\n')
        raw_response = generateResponse('200', entity).pack()
        conn.sendall(raw_response)
        raw_response = generateResponse('200', userName + ' : ' + content + '\n').pack()
        self.broadcast(userName, raw_response)

    def do_query(self, conn, userName, content):
        result = 'Online users:\n'
        for key in self.users.keys():
            result += (key + '\n')
        raw_response = generateResponse('200', result).pack()
        conn.sendall(raw_response)

    def do_logout(self, conn, userName, content):
        self.users.pop(userName)
        print('Connection from %s ended...' % userName)
        raw_response = generateResponse('200', userName + ' has just left the chat room...\n').pack()
        self.broadcast(userName, raw_response)

    def broadcast(self, userName, content):
        for name, conn in self.users.items():
            if name != userName:
                conn.sendall(content)


HOST = '127.0.0.1'
PORT = 9994
responseHeaderDict = {'Server': 'Python Socket Server', 'Developer': 'Soros_Liu'}
entityHeaderDict = {'Content_Encoding': 'utf-8', 'Content_Language': 'en',
                    'Content_Length': None, 'Content_Type': 'text'}
http_method2server_command = {'ADD': 'login', 'POST': 'say', 'GET': 'query', 'DELETE': 'logout'}

if __name__ == '__main__':
    server = ChatServer(HOST, PORT)
    try:
        server.handle_accept()
        print('server loop ended')
    except KeyboardInterrupt:
        print('Server shutdown...Done')
    finally:
        server.close()